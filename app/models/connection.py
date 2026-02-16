"""
Connection-related data models
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


class ConnectionInput(BaseModel):
    """
    Incoming network connection data
    
    Attributes:
        source_ip: IP address of the initiating device
        destination_ip: IP address of the target device
        destination_port: Target port number (1-65535)
        protocol: Network protocol (TCP or UDP)
        timestamp: Connection timestamp
    """
    source_ip: str = Field(..., description="Source IP address")
    destination_ip: str = Field(..., description="Destination IP address")
    destination_port: int = Field(..., ge=1, le=65535, description="Destination port")
    protocol: Literal["TCP", "UDP"] = Field(..., description="Network protocol")
    timestamp: datetime = Field(..., description="Connection timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "source_ip": "192.168.1.10",
                "destination_ip": "10.0.0.5",
                "destination_port": 443,
                "protocol": "TCP",
                "timestamp": "2025-04-30T12:34:56Z"
            }
        }


class ConnectionResponse(BaseModel):
    """
    Response model for connection evaluation
    
    Attributes:
        connection_id: Unique identifier for this connection
        decision: Security decision (allow, alert, or block)
        anomaly_score: AI-generated anomaly score (0.0-1.0)
        matched_policy: ID of the matched policy, if any
    """
    connection_id: str = Field(..., description="Unique connection identifier")
    decision: Literal["allow", "block", "alert"] = Field(..., description="Security decision")
    anomaly_score: float = Field(..., ge=0.0, le=1.0, description="Anomaly score")
    matched_policy: Optional[str] = Field(None, description="Matched policy ID")

    class Config:
        json_schema_extra = {
            "example": {
                "connection_id": "550e8400-e29b-41d4-a716-446655440000",
                "decision": "block",
                "anomaly_score": 0.92,
                "matched_policy": "P-002"
            }
        }


class ConnectionDetail(BaseModel):
    """
    Detailed connection information with evaluation results
    
    Used for storage and retrieval of connection history
    """
    connection_id: str = Field(..., description="Unique connection identifier")
    source_ip: str = Field(..., description="Source IP address")
    destination_ip: str = Field(..., description="Destination IP address")
    destination_port: int = Field(..., ge=1, le=65535, description="Destination port")
    protocol: Literal["TCP", "UDP"] = Field(..., description="Network protocol")
    timestamp: datetime = Field(..., description="Connection timestamp")
    decision: Literal["allow", "block", "alert"] = Field(..., description="Security decision")
    anomaly_score: float = Field(..., ge=0.0, le=1.0, description="Anomaly score")
    matched_policy: Optional[str] = Field(None, description="Matched policy ID")
    evaluated_at: datetime = Field(..., description="Evaluation timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "connection_id": "550e8400-e29b-41d4-a716-446655440000",
                "source_ip": "192.168.1.10",
                "destination_ip": "10.0.0.5",
                "destination_port": 443,
                "protocol": "TCP",
                "timestamp": "2025-04-30T12:34:56Z",
                "decision": "block",
                "anomaly_score": 0.92,
                "matched_policy": "P-002",
                "evaluated_at": "2025-04-30T12:34:56.123Z"
            }
        }
