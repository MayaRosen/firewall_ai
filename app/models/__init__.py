"""
Data models for the AI Firewall service
"""
from .connection import ConnectionInput, ConnectionResponse, ConnectionDetail
from .policy import (
    PolicyCondition,
    Policy,
    PolicyCreateRequest,
    PolicyUpdateRequest,
    PolicyResponse
)

__all__ = [
    "ConnectionInput",
    "ConnectionResponse",
    "ConnectionDetail",
    "PolicyCondition",
    "Policy",
    "PolicyCreateRequest",
    "PolicyUpdateRequest",
    "PolicyResponse",
]
