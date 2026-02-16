"""
Unit tests for the AI Firewall service

Run with: pytest
"""
import pytest
from datetime import datetime
from app.models import ConnectionInput, PolicyCondition, Policy
from app.services.decision_service import decision_service
from app.services.ai_service import ai_anomaly_service


class TestPolicyEvaluation:
    """Test policy evaluation logic"""
    
    def test_evaluate_condition_equals(self):
        """Test equality condition evaluation"""
        condition = PolicyCondition(
            field="destination_port",
            operator="=",
            value="443"
        )
        
        connection = ConnectionInput(
            source_ip="192.168.1.10",
            destination_ip="10.0.0.5",
            destination_port=443,
            protocol="TCP",
            timestamp=datetime.utcnow()
        )
        
        result = decision_service.evaluate_condition(condition, connection)
        assert result is True
    
    def test_evaluate_condition_not_equals(self):
        """Test inequality condition evaluation"""
        condition = PolicyCondition(
            field="destination_port",
            operator="!=",
            value="80"
        )
        
        connection = ConnectionInput(
            source_ip="192.168.1.10",
            destination_ip="10.0.0.5",
            destination_port=443,
            protocol="TCP",
            timestamp=datetime.utcnow()
        )
        
        result = decision_service.evaluate_condition(condition, connection)
        assert result is True
    
    def test_evaluate_condition_greater_than(self):
        """Test greater than condition evaluation"""
        condition = PolicyCondition(
            field="destination_port",
            operator=">",
            value="80"
        )
        
        connection = ConnectionInput(
            source_ip="192.168.1.10",
            destination_ip="10.0.0.5",
            destination_port=443,
            protocol="TCP",
            timestamp=datetime.utcnow()
        )
        
        result = decision_service.evaluate_condition(condition, connection)
        assert result is True
    
    def test_evaluate_policy_or_logic(self):
        """Test that ANY condition matching triggers the policy"""
        policy = Policy(
            policy_id="P-TEST",
            conditions=[
                PolicyCondition(field="destination_port", operator="=", value="443"),
                PolicyCondition(field="source_ip", operator="=", value="192.168.1.100")
            ],
            action="block"
        )
        
        # Connection matches first condition (port 443)
        connection = ConnectionInput(
            source_ip="192.168.1.10",  # Different IP
            destination_ip="10.0.0.5",
            destination_port=443,       # Matches!
            protocol="TCP",
            timestamp=datetime.utcnow()
        )
        
        result = decision_service.evaluate_policy(policy, connection)
        assert result is True  # Should match because of OR logic


class TestAIScoring:
    """Test AI anomaly scoring"""
    
    def test_ai_score_range(self):
        """Test that AI scores are within valid range"""
        connection = ConnectionInput(
            source_ip="192.168.1.10",
            destination_ip="10.0.0.5",
            destination_port=443,
            protocol="TCP",
            timestamp=datetime.utcnow()
        )
        
        score = ai_anomaly_service.calculate_anomaly_score(connection)
        assert 0.0 <= score <= 1.0
    
    def test_suspicious_ip_higher_score(self):
        """Test that suspicious IPs get higher scores"""
        # Normal IP
        normal_connection = ConnectionInput(
            source_ip="192.168.1.10",
            destination_ip="10.0.0.5",
            destination_port=80,
            protocol="TCP",
            timestamp=datetime.utcnow()
        )
        
        # Suspicious IP (configured in ai_service)
        suspicious_connection = ConnectionInput(
            source_ip="192.168.1.100",  # Known suspicious
            destination_ip="10.0.0.5",
            destination_port=80,
            protocol="TCP",
            timestamp=datetime.utcnow()
        )
        
        normal_score = ai_anomaly_service.calculate_anomaly_score(normal_connection)
        suspicious_score = ai_anomaly_service.calculate_anomaly_score(suspicious_connection)
        
        assert suspicious_score >= normal_score
    
    def test_suspicious_port_higher_score(self):
        """Test that suspicious ports get higher scores"""
        # Normal port (443)
        normal_connection = ConnectionInput(
            source_ip="192.168.1.10",
            destination_ip="10.0.0.5",
            destination_port=443,
            protocol="TCP",
            timestamp=datetime.utcnow()
        )
        
        # Suspicious port (Telnet - 23)
        suspicious_connection = ConnectionInput(
            source_ip="192.168.1.10",
            destination_ip="10.0.0.5",
            destination_port=23,  # Telnet
            protocol="TCP",
            timestamp=datetime.utcnow()
        )
        
        normal_score = ai_anomaly_service.calculate_anomaly_score(normal_connection)
        suspicious_score = ai_anomaly_service.calculate_anomaly_score(suspicious_connection)
        
        assert suspicious_score >= normal_score


class TestDecisionLogic:
    """Test decision-making logic"""
    
    def test_ai_thresholds_block(self):
        """Test that high scores result in BLOCK"""
        decision = decision_service.apply_ai_thresholds(0.9)
        assert decision == "block"
    
    def test_ai_thresholds_alert(self):
        """Test that medium scores result in ALERT"""
        decision = decision_service.apply_ai_thresholds(0.6)
        assert decision == "alert"
    
    def test_ai_thresholds_allow(self):
        """Test that low scores result in ALLOW"""
        decision = decision_service.apply_ai_thresholds(0.3)
        assert decision == "allow"
    
    def test_policy_block_immediate(self):
        """Test that block policies return immediately without AI"""
        policy = Policy(
            policy_id="P-BLOCK",
            conditions=[
                PolicyCondition(field="destination_port", operator="=", value="22")
            ],
            action="block"
        )
        
        connection = ConnectionInput(
            source_ip="192.168.1.10",
            destination_ip="10.0.0.5",
            destination_port=22,
            protocol="TCP",
            timestamp=datetime.utcnow()
        )
        
        decision, matched_policy, needs_ai = decision_service.make_decision(
            connection=connection,
            policies=[policy],
            anomaly_score=None
        )
        
        assert decision == "block"
        assert matched_policy == "P-BLOCK"
        assert needs_ai is False  # Should not need AI for block policy


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
