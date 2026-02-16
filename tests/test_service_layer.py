"""
Service Layer Tests

Tests for business logic in service classes
"""
import pytest
from datetime import datetime
from app.models import (
    Policy,
    PolicyCondition,
    PolicyCreateRequest,
    PolicyUpdateRequest,
    ConnectionInput
)
from app.services.policy_service import PolicyService
from app.services.connection_service import ConnectionService
from app.services.decision_service import DecisionService
from app.services.ai_service import AIAnomalyService
from app.repositories.storage import StorageRepository
from app.utils.exceptions import PolicyNotFoundException, PolicyAlreadyExistsException


class TestPolicyService:
    """Test policy service business logic"""
    
    @pytest.fixture
    def service(self):
        """Create a fresh policy service for each test"""
        repository = StorageRepository()
        return PolicyService(repository=repository)
    
    def test_create_policy(self, service):
        """Test creating a policy through service"""
        request = PolicyCreateRequest(
            policy_id="SVC-001",
            conditions=[
                PolicyCondition(field="destination_port", operator="=", value="80")
            ],
            action="allow"
        )
        
        response = service.create_policy(request)
        
        assert response.policy_id == "SVC-001"
        assert response.status == "created"
        
        # Verify it was stored
        policy = service.get_policy("SVC-001")
        assert policy.action == "allow"
    
    def test_create_duplicate_policy_fails(self, service):
        """Test that creating duplicate policy fails"""
        request = PolicyCreateRequest(
            policy_id="SVC-DUP",
            conditions=[
                PolicyCondition(field="destination_port", operator="=", value="80")
            ],
            action="allow"
        )
        
        service.create_policy(request)
        
        with pytest.raises(PolicyAlreadyExistsException):
            service.create_policy(request)
    
    def test_update_policy(self, service):
        """Test updating a policy through service"""
        # Create initial policy
        create_request = PolicyCreateRequest(
            policy_id="SVC-UPD",
            conditions=[
                PolicyCondition(field="destination_port", operator="=", value="80")
            ],
            action="allow"
        )
        service.create_policy(create_request)
        
        # Update policy
        update_request = PolicyUpdateRequest(
            conditions=[
                PolicyCondition(field="destination_port", operator="=", value="443")
            ],
            action="block"
        )
        
        response = service.update_policy("SVC-UPD", update_request)
        
        assert response.status == "updated"
        
        # Verify changes
        policy = service.get_policy("SVC-UPD")
        assert policy.action == "block"
        assert policy.conditions[0].value == "443"
    
    def test_delete_policy(self, service):
        """Test deleting a policy through service"""
        request = PolicyCreateRequest(
            policy_id="SVC-DEL",
            conditions=[
                PolicyCondition(field="destination_port", operator="=", value="80")
            ],
            action="allow"
        )
        service.create_policy(request)
        
        response = service.delete_policy("SVC-DEL")
        
        assert response.status == "deleted"
        
        with pytest.raises(PolicyNotFoundException):
            service.get_policy("SVC-DEL")


class TestConnectionService:
    """Test connection service business logic"""
    
    @pytest.fixture
    def service(self):
        """Create a fresh connection service for each test"""
        repository = StorageRepository()
        ai_service = AIAnomalyService()
        decision_service = DecisionService()
        policy_service = PolicyService(repository=repository)
        return ConnectionService(
            repository=repository,
            ai_service=ai_service,
            dec_service=decision_service,
            pol_service=policy_service
        )
    
    def test_process_connection_no_policy(self, service):
        """Test processing connection with no matching policy"""
        connection = ConnectionInput(
            source_ip="192.168.1.10",
            destination_ip="10.0.0.5",
            destination_port=8080,
            protocol="TCP",
            timestamp=datetime.utcnow()
        )
        
        response = service.process_connection(connection)
        
        assert response.connection_id is not None
        assert response.decision in ["allow", "alert", "block"]
        assert 0.0 <= response.anomaly_score <= 1.0
        assert response.matched_policy is None
    
    def test_process_connection_with_block_policy(self, service):
        """Test processing connection that matches block policy"""
        # Create block policy
        policy_request = PolicyCreateRequest(
            policy_id="CONN-BLOCK",
            conditions=[
                PolicyCondition(field="destination_port", operator="=", value="22")
            ],
            action="block"
        )
        service.policy_service.create_policy(policy_request)
        
        # Process connection
        connection = ConnectionInput(
            source_ip="192.168.1.10",
            destination_ip="10.0.0.5",
            destination_port=22,
            protocol="TCP",
            timestamp=datetime.utcnow()
        )
        
        response = service.process_connection(connection)
        
        assert response.decision == "block"
        assert response.matched_policy == "CONN-BLOCK"
        assert response.anomaly_score == 0.0  # AI not used
    
    def test_process_connection_with_allow_policy(self, service):
        """Test processing connection that matches allow policy"""
        # Create allow policy
        policy_request = PolicyCreateRequest(
            policy_id="CONN-ALLOW",
            conditions=[
                PolicyCondition(field="destination_port", operator="=", value="80")
            ],
            action="allow"
        )
        service.policy_service.create_policy(policy_request)
        
        # Process connection
        connection = ConnectionInput(
            source_ip="192.168.1.10",
            destination_ip="10.0.0.5",
            destination_port=80,
            protocol="TCP",
            timestamp=datetime.utcnow()
        )
        
        response = service.process_connection(connection)
        
        assert response.decision == "allow"
        assert response.matched_policy == "CONN-ALLOW"
        assert response.anomaly_score == 0.0  # AI not used
    
    def test_process_connection_with_alert_policy(self, service):
        """Test processing connection with alert policy (uses AI)"""
        # Create alert policy
        policy_request = PolicyCreateRequest(
            policy_id="CONN-ALERT",
            conditions=[
                PolicyCondition(field="destination_port", operator="=", value="23")
            ],
            action="alert"
        )
        service.policy_service.create_policy(policy_request)
        
        # Process connection
        connection = ConnectionInput(
            source_ip="192.168.1.10",
            destination_ip="10.0.0.5",
            destination_port=23,
            protocol="TCP",
            timestamp=datetime.utcnow()
        )
        
        response = service.process_connection(connection)
        
        assert response.matched_policy == "CONN-ALERT"
        assert response.anomaly_score > 0.0  # AI was used
        assert response.decision in ["allow", "alert", "block"]
    
    def test_get_connection(self, service):
        """Test retrieving connection by ID"""
        # Process a connection
        connection = ConnectionInput(
            source_ip="192.168.1.10",
            destination_ip="10.0.0.5",
            destination_port=443,
            protocol="TCP",
            timestamp=datetime.utcnow()
        )
        
        response = service.process_connection(connection)
        connection_id = response.connection_id
        
        # Retrieve it
        retrieved = service.get_connection(connection_id)
        
        assert retrieved.connection_id == connection_id
        assert retrieved.source_ip == "192.168.1.10"
        assert retrieved.destination_port == 443


class TestDecisionServiceAdvanced:
    """Advanced tests for decision service"""
    
    @pytest.fixture
    def service(self):
        """Create decision service"""
        return DecisionService()
    
    def test_multiple_conditions_or_logic(self, service):
        """Test that ANY condition matching triggers policy"""
        policy = Policy(
            policy_id="MULTI",
            conditions=[
                PolicyCondition(field="destination_port", operator="=", value="80"),
                PolicyCondition(field="destination_port", operator="=", value="443"),
                PolicyCondition(field="source_ip", operator="=", value="192.168.1.100")
            ],
            action="block"
        )
        
        # Test connection matches second condition
        connection = ConnectionInput(
            source_ip="192.168.1.10",
            destination_ip="10.0.0.5",
            destination_port=443,
            protocol="TCP",
            timestamp=datetime.utcnow()
        )
        
        result = service.evaluate_policy(policy, connection)
        assert result is True
    
    def test_no_conditions_match(self, service):
        """Test when no conditions match"""
        policy = Policy(
            policy_id="NO-MATCH",
            conditions=[
                PolicyCondition(field="destination_port", operator="=", value="80"),
                PolicyCondition(field="source_ip", operator="=", value="192.168.1.100")
            ],
            action="block"
        )
        
        connection = ConnectionInput(
            source_ip="192.168.1.10",
            destination_ip="10.0.0.5",
            destination_port=443,
            protocol="TCP",
            timestamp=datetime.utcnow()
        )
        
        result = service.evaluate_policy(policy, connection)
        assert result is False
    
    def test_comparison_operators(self, service):
        """Test different comparison operators"""
        # Test greater than
        condition_gt = PolicyCondition(field="destination_port", operator=">", value="100")
        connection = ConnectionInput(
            source_ip="192.168.1.10",
            destination_ip="10.0.0.5",
            destination_port=443,
            protocol="TCP",
            timestamp=datetime.utcnow()
        )
        assert service.evaluate_condition(condition_gt, connection) is True
        
        # Test less than
        condition_lt = PolicyCondition(field="destination_port", operator="<", value="1000")
        assert service.evaluate_condition(condition_lt, connection) is True
        
        # Test not equal
        condition_ne = PolicyCondition(field="destination_port", operator="!=", value="80")
        assert service.evaluate_condition(condition_ne, connection) is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
