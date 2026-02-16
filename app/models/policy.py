"""
Policy-related data models
"""
from pydantic import BaseModel, Field
from typing import List, Literal


class PolicyCondition(BaseModel):
    """
    A single condition in a security policy
    
    Attributes:
        field: The connection field to evaluate
        operator: The comparison operator
        value: The value to compare against
    """
    field: Literal["source_ip", "destination_ip", "destination_port", "protocol"] = Field(
        ..., description="Connection field to evaluate"
    )
    operator: Literal["=", "!=", ">", "<", ">=", "<="] = Field(
        ..., description="Comparison operator"
    )
    value: str = Field(..., description="Value to compare against")

    class Config:
        json_schema_extra = {
            "example": {
                "field": "destination_port",
                "operator": "=",
                "value": "443"
            }
        }


class Policy(BaseModel):
    """
    Security policy definition
    
    Attributes:
        policy_id: Unique identifier for the policy
        conditions: List of conditions (ANY match triggers policy)
        action: Security action to take when policy matches
    """
    policy_id: str = Field(..., description="Unique policy identifier")
    conditions: List[PolicyCondition] = Field(..., min_length=1, description="Policy conditions")
    action: Literal["allow", "block", "alert"] = Field(..., description="Action to take")

    class Config:
        json_schema_extra = {
            "example": {
                "policy_id": "P-002",
                "conditions": [
                    {"field": "destination_port", "operator": "=", "value": "443"},
                    {"field": "source_ip", "operator": "=", "value": "192.168.1.10"}
                ],
                "action": "block"
            }
        }


class PolicyCreateRequest(BaseModel):
    """Request model for creating a new policy"""
    policy_id: str = Field(..., min_length=1, description="Unique policy identifier")
    conditions: List[PolicyCondition] = Field(..., min_length=1, description="Policy conditions")
    action: Literal["allow", "block", "alert"] = Field(..., description="Action to take")


class PolicyUpdateRequest(BaseModel):
    """Request model for updating an existing policy"""
    conditions: List[PolicyCondition] = Field(..., min_length=1, description="Updated conditions")
    action: Literal["allow", "block", "alert"] = Field(..., description="Updated action")


class PolicyResponse(BaseModel):
    """Response model for policy operations"""
    policy_id: str = Field(..., description="Policy identifier")
    status: str = Field(..., description="Operation status")
    message: str = Field(..., description="Human-readable message")

    class Config:
        json_schema_extra = {
            "example": {
                "policy_id": "P-002",
                "status": "created",
                "message": "Policy successfully created"
            }
        }
