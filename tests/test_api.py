"""
API Integration Tests for Connection and Policy endpoints

Run with: pytest tests/test_api.py -v
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from app.main import app

client = TestClient(app)


class TestPolicyAPI:
    """Test Policy Management API endpoints"""
    
    def test_create_policy_success(self):
        """Test successful policy creation"""
        response = client.post(
            "/policy",
            json={
                "policy_id": "TEST-001",
                "conditions": [
                    {"field": "destination_port", "operator": "=", "value": "22"}
                ],
                "action": "block"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["policy_id"] == "TEST-001"
        assert data["status"] == "created"
        
        # Cleanup
        client.delete("/policy/TEST-001")
    
    def test_create_policy_duplicate(self):
        """Test creating duplicate policy returns 409"""
        # Create first policy
        client.post(
            "/policy",
            json={
                "policy_id": "TEST-DUP",
                "conditions": [
                    {"field": "destination_port", "operator": "=", "value": "80"}
                ],
                "action": "allow"
            }
        )
        
        # Try to create duplicate
        response = client.post(
            "/policy",
            json={
                "policy_id": "TEST-DUP",
                "conditions": [
                    {"field": "destination_port", "operator": "=", "value": "443"}
                ],
                "action": "block"
            }
        )
        
        assert response.status_code == 409
        
        # Cleanup
        client.delete("/policy/TEST-DUP")
    
    def test_update_policy_success(self):
        """Test successful policy update"""
        # Create policy
        client.post(
            "/policy",
            json={
                "policy_id": "TEST-UPD",
                "conditions": [
                    {"field": "destination_port", "operator": "=", "value": "80"}
                ],
                "action": "allow"
            }
        )
        
        # Update policy
        response = client.put(
            "/policy/TEST-UPD",
            json={
                "conditions": [
                    {"field": "destination_port", "operator": "=", "value": "443"}
                ],
                "action": "block"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "updated"
        
        # Cleanup
        client.delete("/policy/TEST-UPD")
    
    def test_update_policy_not_found(self):
        """Test updating non-existent policy returns 404"""
        response = client.put(
            "/policy/NONEXISTENT",
            json={
                "conditions": [
                    {"field": "destination_port", "operator": "=", "value": "80"}
                ],
                "action": "allow"
            }
        )
        
        assert response.status_code == 404
    
    def test_get_policy_success(self):
        """Test retrieving a policy"""
        # Create policy
        client.post(
            "/policy",
            json={
                "policy_id": "TEST-GET",
                "conditions": [
                    {"field": "destination_port", "operator": "=", "value": "22"}
                ],
                "action": "block"
            }
        )
        
        # Get policy
        response = client.get("/policy/TEST-GET")
        
        assert response.status_code == 200
        data = response.json()
        assert data["policy_id"] == "TEST-GET"
        assert data["action"] == "block"
        assert len(data["conditions"]) == 1
        
        # Cleanup
        client.delete("/policy/TEST-GET")
    
    def test_get_policy_not_found(self):
        """Test getting non-existent policy returns 404"""
        response = client.get("/policy/NONEXISTENT")
        assert response.status_code == 404
    
    def test_delete_policy_success(self):
        """Test successful policy deletion"""
        # Create policy
        client.post(
            "/policy",
            json={
                "policy_id": "TEST-DEL",
                "conditions": [
                    {"field": "destination_port", "operator": "=", "value": "80"}
                ],
                "action": "allow"
            }
        )
        
        # Delete policy
        response = client.delete("/policy/TEST-DEL")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "deleted"
        
        # Verify it's deleted
        get_response = client.get("/policy/TEST-DEL")
        assert get_response.status_code == 404
    
    def test_delete_policy_not_found(self):
        """Test deleting non-existent policy returns 404"""
        response = client.delete("/policy/NONEXISTENT")
        assert response.status_code == 404
    
    def test_create_policy_invalid_data(self):
        """Test creating policy with invalid data returns 422"""
        response = client.post(
            "/policy",
            json={
                "policy_id": "TEST-INVALID",
                "conditions": [],  # Empty conditions
                "action": "block"
            }
        )
        
        assert response.status_code == 422


class TestConnectionAPI:
    """Test Connection Evaluation API endpoints"""
    
    def test_submit_connection_no_policy(self):
        """Test connection submission with no matching policy"""
        response = client.post(
            "/connection",
            json={
                "source_ip": "192.168.1.10",
                "destination_ip": "10.0.0.5",
                "destination_port": 8080,
                "protocol": "TCP",
                "timestamp": "2025-04-30T12:34:56Z"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "connection_id" in data
        assert data["decision"] in ["allow", "alert", "block"]
        assert 0.0 <= data["anomaly_score"] <= 1.0
        assert data["matched_policy"] is None
    
    def test_submit_connection_with_block_policy(self):
        """Test connection that matches block policy"""
        # Create block policy
        client.post(
            "/policy",
            json={
                "policy_id": "TEST-BLOCK",
                "conditions": [
                    {"field": "destination_port", "operator": "=", "value": "22"}
                ],
                "action": "block"
            }
        )
        
        # Submit connection
        response = client.post(
            "/connection",
            json={
                "source_ip": "192.168.1.10",
                "destination_ip": "10.0.0.5",
                "destination_port": 22,
                "protocol": "TCP",
                "timestamp": "2025-04-30T12:34:56Z"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["decision"] == "block"
        assert data["matched_policy"] == "TEST-BLOCK"
        
        # Cleanup
        client.delete("/policy/TEST-BLOCK")
    
    def test_submit_connection_with_allow_policy(self):
        """Test connection that matches allow policy"""
        # Create allow policy
        client.post(
            "/policy",
            json={
                "policy_id": "TEST-ALLOW",
                "conditions": [
                    {"field": "destination_port", "operator": "=", "value": "80"}
                ],
                "action": "allow"
            }
        )
        
        # Submit connection
        response = client.post(
            "/connection",
            json={
                "source_ip": "192.168.1.10",
                "destination_ip": "10.0.0.5",
                "destination_port": 80,
                "protocol": "TCP",
                "timestamp": "2025-04-30T12:34:56Z"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["decision"] == "allow"
        assert data["matched_policy"] == "TEST-ALLOW"
        
        # Cleanup
        client.delete("/policy/TEST-ALLOW")
    
    def test_submit_connection_with_alert_policy(self):
        """Test connection that matches alert policy (requires AI)"""
        # Create alert policy
        client.post(
            "/policy",
            json={
                "policy_id": "TEST-ALERT",
                "conditions": [
                    {"field": "destination_port", "operator": "=", "value": "23"}
                ],
                "action": "alert"
            }
        )
        
        # Submit connection
        response = client.post(
            "/connection",
            json={
                "source_ip": "192.168.1.10",
                "destination_ip": "10.0.0.5",
                "destination_port": 23,
                "protocol": "TCP",
                "timestamp": "2025-04-30T12:34:56Z"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["decision"] in ["allow", "alert", "block"]
        assert data["matched_policy"] == "TEST-ALERT"
        assert data["anomaly_score"] > 0.0  # AI score should be calculated
        
        # Cleanup
        client.delete("/policy/TEST-ALERT")
    
    def test_get_connection_details(self):
        """Test retrieving connection details"""
        # Submit connection
        submit_response = client.post(
            "/connection",
            json={
                "source_ip": "192.168.1.10",
                "destination_ip": "10.0.0.5",
                "destination_port": 443,
                "protocol": "TCP",
                "timestamp": "2025-04-30T12:34:56Z"
            }
        )
        
        connection_id = submit_response.json()["connection_id"]
        
        # Get connection details
        response = client.get(f"/connection/{connection_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["connection_id"] == connection_id
        assert data["source_ip"] == "192.168.1.10"
        assert data["destination_ip"] == "10.0.0.5"
        assert data["destination_port"] == 443
        assert "evaluated_at" in data
    
    def test_get_connection_not_found(self):
        """Test getting non-existent connection returns 404"""
        response = client.get("/connection/nonexistent-id")
        assert response.status_code == 404
    
    def test_submit_connection_invalid_port(self):
        """Test connection with invalid port number"""
        response = client.post(
            "/connection",
            json={
                "source_ip": "192.168.1.10",
                "destination_ip": "10.0.0.5",
                "destination_port": 99999,  # Invalid port
                "protocol": "TCP",
                "timestamp": "2025-04-30T12:34:56Z"
            }
        )
        
        assert response.status_code == 422
    
    def test_submit_connection_invalid_protocol(self):
        """Test connection with invalid protocol"""
        response = client.post(
            "/connection",
            json={
                "source_ip": "192.168.1.10",
                "destination_ip": "10.0.0.5",
                "destination_port": 443,
                "protocol": "ICMP",  # Invalid, only TCP/UDP allowed
                "timestamp": "2025-04-30T12:34:56Z"
            }
        )
        
        assert response.status_code == 422


class TestHealthEndpoints:
    """Test health and root endpoints"""
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data
        assert "version" in data
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
