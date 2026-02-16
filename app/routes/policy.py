"""
Policy Management Routes

API endpoints for creating and managing security policies
"""
import logging
from fastapi import APIRouter, HTTPException, status
from app.models import (
    PolicyCreateRequest,
    PolicyUpdateRequest,
    PolicyResponse,
    Policy
)
from app.services.policy_service import policy_service
from app.utils.exceptions import PolicyNotFoundException, PolicyAlreadyExistsException

logger = logging.getLogger(__name__)

# Create router with prefix and tags for API organization
router = APIRouter(
    prefix="/policy",
    tags=["policies"],
    responses={404: {"description": "Policy not found"}}
)


@router.post(
    "",
    response_model=PolicyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new security policy",
    responses={
        201: {"description": "Policy created successfully"},
        409: {"description": "Policy already exists"}
    }
)
async def create_policy(request: PolicyCreateRequest) -> PolicyResponse:
    """
    Create a new security policy
    
    - **policy_id**: Unique identifier for the policy
    - **conditions**: List of conditions (ANY condition matching triggers the policy)
    - **action**: Action to take when policy matches (allow, alert, or block)
    
    Example:
    ```json
    {
        "policy_id": "P-002",
        "conditions": [
            {"field": "destination_port", "operator": "=", "value": "443"}
        ],
        "action": "block"
    }
    ```
    """
    try:
        response = policy_service.create_policy(request)
        logger.info(f"Policy created via API: {request.policy_id}")
        return response
        
    except PolicyAlreadyExistsException as e:
        logger.warning(f"Policy creation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error creating policy: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.put(
    "/{policy_id}",
    response_model=PolicyResponse,
    status_code=status.HTTP_200_OK,
    summary="Update an existing security policy",
    responses={
        200: {"description": "Policy updated successfully"},
        404: {"description": "Policy not found"}
    }
)
async def update_policy(
    policy_id: str,
    request: PolicyUpdateRequest
) -> PolicyResponse:
    """
    Update an existing security policy
    
    - **policy_id**: ID of the policy to update (from path)
    - **conditions**: Updated list of conditions
    - **action**: Updated action
    
    Example:
    ```json
    {
        "conditions": [
            {"field": "destination_port", "operator": "=", "value": "443"}
        ],
        "action": "allow"
    }
    ```
    """
    try:
        response = policy_service.update_policy(policy_id, request)
        logger.info(f"Policy updated via API: {policy_id}")
        return response
        
    except PolicyNotFoundException as e:
        logger.warning(f"Policy update failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error updating policy: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get(
    "/{policy_id}",
    response_model=Policy,
    status_code=status.HTTP_200_OK,
    summary="Get a specific policy",
    responses={
        200: {"description": "Policy retrieved successfully"},
        404: {"description": "Policy not found"}
    }
)
async def get_policy(policy_id: str) -> Policy:
    """
    Retrieve a specific policy by ID
    
    - **policy_id**: ID of the policy to retrieve
    """
    try:
        policy = policy_service.get_policy(policy_id)
        return policy
        
    except PolicyNotFoundException as e:
        logger.warning(f"Policy retrieval failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error retrieving policy: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete(
    "/{policy_id}",
    response_model=PolicyResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete a policy",
    responses={
        200: {"description": "Policy deleted successfully"},
        404: {"description": "Policy not found"}
    }
)
async def delete_policy(policy_id: str) -> PolicyResponse:
    """
    Delete a security policy
    
    - **policy_id**: ID of the policy to delete
    """
    try:
        response = policy_service.delete_policy(policy_id)
        logger.info(f"Policy deleted via API: {policy_id}")
        return response
        
    except PolicyNotFoundException as e:
        logger.warning(f"Policy deletion failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error deleting policy: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
