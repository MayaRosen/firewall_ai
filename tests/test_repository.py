"""
Repository Layer Tests

Tests for data access layer and storage operations
"""
import pytest
from app.models import Policy, PolicyCondition, ConnectionDetail
from app.repositories.storage import StorageRepository
from app.utils.exceptions import PolicyNotFoundException, PolicyAlreadyExistsException
from datetime import datetime


class TestPolicyRepository:
    """Test policy repository operations"""
    
    @pytest.fixture
    def repository(self):
        """Create a fresh repository for each test"""
        return StorageRepository()
    
    @pytest.fixture
    def sample_policy(self):
        """Create a sample policy"""
        return Policy(
            policy_id="TEST-001",
            conditions=[
                PolicyCondition(field="destination_port", operator="=", value="443")
            ],
            action="block"
        )
    
    def test_create_policy(self, repository, sample_policy):
        """Test creating a policy"""
        repository.create_policy(sample_policy)
        
        retrieved = repository.get_policy("TEST-001")
        assert retrieved.policy_id == "TEST-001"
        assert retrieved.action == "block"
    
    def test_create_duplicate_policy_raises_exception(self, repository, sample_policy):
        """Test that creating duplicate policy raises exception"""
        repository.create_policy(sample_policy)
        
        with pytest.raises(PolicyAlreadyExistsException):
            repository.create_policy(sample_policy)
    
    def test_update_policy(self, repository, sample_policy):
        """Test updating a policy"""
        repository.create_policy(sample_policy)
        
        updated_policy = Policy(
            policy_id="TEST-001",
            conditions=[
                PolicyCondition(field="destination_port", operator="=", value="80")
            ],
            action="allow"
        )
        
        repository.update_policy("TEST-001", updated_policy)
        
        retrieved = repository.get_policy("TEST-001")
        assert retrieved.action == "allow"
        assert retrieved.conditions[0].value == "80"
    
    def test_update_nonexistent_policy_raises_exception(self, repository):
        """Test that updating non-existent policy raises exception"""
        updated_policy = Policy(
            policy_id="NONEXISTENT",
            conditions=[
                PolicyCondition(field="destination_port", operator="=", value="80")
            ],
            action="allow"
        )
        
        with pytest.raises(PolicyNotFoundException):
            repository.update_policy("NONEXISTENT", updated_policy)
    
    def test_get_nonexistent_policy_raises_exception(self, repository):
        """Test that getting non-existent policy raises exception"""
        with pytest.raises(PolicyNotFoundException):
            repository.get_policy("NONEXISTENT")
    
    def test_get_all_policies(self, repository):
        """Test getting all policies"""
        policy1 = Policy(
            policy_id="TEST-001",
            conditions=[PolicyCondition(field="destination_port", operator="=", value="80")],
            action="allow"
        )
        policy2 = Policy(
            policy_id="TEST-002",
            conditions=[PolicyCondition(field="destination_port", operator="=", value="443")],
            action="block"
        )
        
        repository.create_policy(policy1)
        repository.create_policy(policy2)
        
        all_policies = repository.get_all_policies()
        assert len(all_policies) == 2
        assert any(p.policy_id == "TEST-001" for p in all_policies)
        assert any(p.policy_id == "TEST-002" for p in all_policies)
    
    def test_delete_policy(self, repository, sample_policy):
        """Test deleting a policy"""
        repository.create_policy(sample_policy)
        repository.delete_policy("TEST-001")
        
        with pytest.raises(PolicyNotFoundException):
            repository.get_policy("TEST-001")
    
    def test_delete_nonexistent_policy_raises_exception(self, repository):
        """Test that deleting non-existent policy raises exception"""
        with pytest.raises(PolicyNotFoundException):
            repository.delete_policy("NONEXISTENT")
    
    def test_policy_exists(self, repository, sample_policy):
        """Test checking if policy exists"""
        assert not repository.policy_exists("TEST-001")
        
        repository.create_policy(sample_policy)
        assert repository.policy_exists("TEST-001")
        
        repository.delete_policy("TEST-001")
        assert not repository.policy_exists("TEST-001")


class TestConnectionRepository:
    """Test connection repository operations"""
    
    @pytest.fixture
    def repository(self):
        """Create a fresh repository for each test"""
        return StorageRepository()
    
    @pytest.fixture
    def sample_connection(self):
        """Create a sample connection"""
        return ConnectionDetail(
            connection_id="conn-001",
            source_ip="192.168.1.10",
            destination_ip="10.0.0.5",
            destination_port=443,
            protocol="TCP",
            timestamp=datetime.utcnow(),
            decision="allow",
            anomaly_score=0.25,
            matched_policy=None,
            evaluated_at=datetime.utcnow()
        )
    
    def test_store_connection(self, repository, sample_connection):
        """Test storing a connection"""
        repository.store_connection(sample_connection)
        
        retrieved = repository.get_connection("conn-001")
        assert retrieved is not None
        assert retrieved.connection_id == "conn-001"
        assert retrieved.decision == "allow"
    
    def test_get_nonexistent_connection(self, repository):
        """Test getting non-existent connection returns None"""
        result = repository.get_connection("nonexistent")
        assert result is None
    
    def test_get_all_connections(self, repository):
        """Test getting all connections"""
        conn1 = ConnectionDetail(
            connection_id="conn-001",
            source_ip="192.168.1.10",
            destination_ip="10.0.0.5",
            destination_port=443,
            protocol="TCP",
            timestamp=datetime.utcnow(),
            decision="allow",
            anomaly_score=0.25,
            matched_policy=None,
            evaluated_at=datetime.utcnow()
        )
        
        conn2 = ConnectionDetail(
            connection_id="conn-002",
            source_ip="192.168.1.20",
            destination_ip="10.0.0.10",
            destination_port=22,
            protocol="TCP",
            timestamp=datetime.utcnow(),
            decision="block",
            anomaly_score=0.95,
            matched_policy=None,
            evaluated_at=datetime.utcnow()
        )
        
        repository.store_connection(conn1)
        repository.store_connection(conn2)
        
        all_connections = repository.get_all_connections()
        assert len(all_connections) == 2
        assert any(c.connection_id == "conn-001" for c in all_connections)
        assert any(c.connection_id == "conn-002" for c in all_connections)
    
    def test_overwrite_connection(self, repository, sample_connection):
        """Test that storing same connection ID overwrites previous"""
        repository.store_connection(sample_connection)
        
        updated_connection = ConnectionDetail(
            connection_id="conn-001",
            source_ip="192.168.1.10",
            destination_ip="10.0.0.5",
            destination_port=443,
            protocol="TCP",
            timestamp=datetime.utcnow(),
            decision="block",  # Changed
            anomaly_score=0.85,  # Changed
            matched_policy=None,  # Changed
            evaluated_at=datetime.utcnow()
        )
        
        repository.store_connection(updated_connection)
        
        retrieved = repository.get_connection("conn-001")
        assert retrieved.decision == "block"
        assert retrieved.anomaly_score == 0.85


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
