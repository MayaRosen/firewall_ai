"""
In-memory storage repository for policies and connections

This serves as the data access layer, abstracting storage operations
from business logic. In production, this could be replaced with a database.
"""
from typing import Dict, Optional, List
from app.models import Policy, ConnectionDetail
from app.utils.exceptions import PolicyNotFoundException, PolicyAlreadyExistsException


class StorageRepository:
    """
    Repository for managing in-memory storage of policies and connections
    
    This class follows the Repository pattern, providing a clean interface
    for data operations while hiding implementation details.
    """
    
    def __init__(self):
        """Initialize empty storage"""
        self._policies: Dict[str, Policy] = {}
        self._connections: Dict[str, ConnectionDetail] = {}
    
    # Policy operations
    
    def create_policy(self, policy: Policy) -> None:
        """
        Create a new policy
        
        Args:
            policy: Policy object to store
            
        Raises:
            PolicyAlreadyExistsException: If policy_id already exists
        """
        if policy.policy_id in self._policies:
            raise PolicyAlreadyExistsException(
                f"Policy with ID '{policy.policy_id}' already exists"
            )
        self._policies[policy.policy_id] = policy
    
    def update_policy(self, policy_id: str, policy: Policy) -> None:
        """
        Update an existing policy
        
        Args:
            policy_id: ID of policy to update
            policy: New policy data
            
        Raises:
            PolicyNotFoundException: If policy doesn't exist
        """
        if policy_id not in self._policies:
            raise PolicyNotFoundException(
                f"Policy with ID '{policy_id}' not found"
            )
        self._policies[policy_id] = policy
    
    def get_policy(self, policy_id: str) -> Policy:
        """
        Retrieve a policy by ID
        
        Args:
            policy_id: ID of policy to retrieve
            
        Returns:
            Policy object
            
        Raises:
            PolicyNotFoundException: If policy doesn't exist
        """
        policy = self._policies.get(policy_id)
        if policy is None:
            raise PolicyNotFoundException(
                f"Policy with ID '{policy_id}' not found"
            )
        return policy
    
    def get_all_policies(self) -> List[Policy]:
        """
        Get all policies
        
        Returns:
            List of all Policy objects
        """
        return list(self._policies.values())
    
    def delete_policy(self, policy_id: str) -> None:
        """
        Delete a policy
        
        Args:
            policy_id: ID of policy to delete
            
        Raises:
            PolicyNotFoundException: If policy doesn't exist
        """
        if policy_id not in self._policies:
            raise PolicyNotFoundException(
                f"Policy with ID '{policy_id}' not found"
            )
        del self._policies[policy_id]
    
    def policy_exists(self, policy_id: str) -> bool:
        """
        Check if a policy exists
        
        Args:
            policy_id: ID to check
            
        Returns:
            True if policy exists, False otherwise
        """
        return policy_id in self._policies
    
    # Connection operations
    
    def store_connection(self, connection: ConnectionDetail) -> None:
        """
        Store a connection decision
        
        Args:
            connection: ConnectionDetail object to store
        """
        self._connections[connection.connection_id] = connection
    
    def get_connection(self, connection_id: str) -> Optional[ConnectionDetail]:
        """
        Retrieve a connection by ID
        
        Args:
            connection_id: ID of connection to retrieve
            
        Returns:
            ConnectionDetail object or None if not found
        """
        return self._connections.get(connection_id)
    
    def get_all_connections(self) -> List[ConnectionDetail]:
        """
        Get all stored connections
        
        Returns:
            List of all ConnectionDetail objects
        """
        return list(self._connections.values())


# Global singleton instance
# In production, this would be managed by dependency injection
storage_repository = StorageRepository()
