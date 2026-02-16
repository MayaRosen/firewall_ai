"""
Policy Management Service

Handles business logic for security policy operations
"""
import logging
from typing import List
from app.models import (
    Policy,
    PolicyCreateRequest,
    PolicyUpdateRequest,
    PolicyResponse
)
from app.repositories.storage import storage_repository
from app.utils.exceptions import PolicyNotFoundException, PolicyAlreadyExistsException

logger = logging.getLogger(__name__)


class PolicyService:
    """
    Service for managing security policies
    
    This service encapsulates all business logic related to policy management,
    separating it from data access and API layers.
    """
    
    def __init__(self, repository=storage_repository):
        """
        Initialize the policy service
        
        Args:
            repository: Storage repository instance (injected for testability)
        """
        self.repository = repository
        logger.info("Policy Service initialized")
    
    def create_policy(self, request: PolicyCreateRequest) -> PolicyResponse:
        """
        Create a new security policy
        
        Args:
            request: Policy creation request
            
        Returns:
            PolicyResponse with creation status
            
        Raises:
            PolicyAlreadyExistsException: If policy ID already exists
        """
        logger.info(f"Creating new policy: {request.policy_id}")
        
        # Create policy object
        policy = Policy(
            policy_id=request.policy_id,
            conditions=request.conditions,
            action=request.action
        )
        
        # Store in repository
        try:
            self.repository.create_policy(policy)
            logger.info(f"Policy created successfully: {request.policy_id}")
            
            return PolicyResponse(
                policy_id=request.policy_id,
                status="created",
                message="Policy successfully created"
            )
        except PolicyAlreadyExistsException as e:
            logger.error(f"Failed to create policy: {str(e)}")
            raise
    
    def update_policy(self, policy_id: str, request: PolicyUpdateRequest) -> PolicyResponse:
        """
        Update an existing security policy
        
        Args:
            policy_id: ID of policy to update
            request: Policy update request
            
        Returns:
            PolicyResponse with update status
            
        Raises:
            PolicyNotFoundException: If policy doesn't exist
        """
        logger.info(f"Updating policy: {policy_id}")
        
        # Create updated policy object
        updated_policy = Policy(
            policy_id=policy_id,
            conditions=request.conditions,
            action=request.action
        )
        
        # Update in repository
        try:
            self.repository.update_policy(policy_id, updated_policy)
            logger.info(f"Policy updated successfully: {policy_id}")
            
            return PolicyResponse(
                policy_id=policy_id,
                status="updated",
                message="Policy successfully updated"
            )
        except PolicyNotFoundException as e:
            logger.error(f"Failed to update policy: {str(e)}")
            raise
    
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
        logger.debug(f"Retrieving policy: {policy_id}")
        return self.repository.get_policy(policy_id)
    
    def get_all_policies(self) -> List[Policy]:
        """
        Get all policies
        
        Returns:
            List of all policies
        """
        logger.debug("Retrieving all policies")
        return self.repository.get_all_policies()
    
    def delete_policy(self, policy_id: str) -> PolicyResponse:
        """
        Delete a policy
        
        Args:
            policy_id: ID of policy to delete
            
        Returns:
            PolicyResponse with deletion status
            
        Raises:
            PolicyNotFoundException: If policy doesn't exist
        """
        logger.info(f"Deleting policy: {policy_id}")
        
        try:
            self.repository.delete_policy(policy_id)
            logger.info(f"Policy deleted successfully: {policy_id}")
            
            return PolicyResponse(
                policy_id=policy_id,
                status="deleted",
                message="Policy successfully deleted"
            )
        except PolicyNotFoundException as e:
            logger.error(f"Failed to delete policy: {str(e)}")
            raise


# Global singleton instance
policy_service = PolicyService()
