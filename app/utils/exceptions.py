"""
Custom exceptions for the AI Firewall service
"""


class FirewallException(Exception):
    """Base exception for firewall service errors"""
    pass


class PolicyNotFoundException(FirewallException):
    """Raised when a policy is not found"""
    pass


class PolicyAlreadyExistsException(FirewallException):
    """Raised when attempting to create a policy that already exists"""
    pass


class ConnectionNotFoundException(FirewallException):
    """Raised when a connection is not found"""
    pass


class InvalidPolicyException(FirewallException):
    """Raised when a policy is invalid"""
    pass


class AIServiceException(FirewallException):
    """Raised when the AI service encounters an error"""
    pass
