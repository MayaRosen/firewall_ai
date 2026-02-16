"""
Connection Evaluation Routes

API endpoints for submitting and retrieving network connection evaluations
"""
import logging
from fastapi import APIRouter, HTTPException, status
from app.models import (
    ConnectionInput,
    ConnectionResponse,
    ConnectionDetail
)
from app.services.connection_service import connection_service
from app.utils.exceptions import ConnectionNotFoundException

logger = logging.getLogger(__name__)

# Create router with prefix and tags for API organization
router = APIRouter(
    prefix="/connection",
    tags=["connections"],
    responses={404: {"description": "Connection not found"}}
)


@router.post(
    "",
    response_model=ConnectionResponse,
    status_code=status.HTTP_200_OK,
    summary="Submit a connection for evaluation",
    responses={
        200: {"description": "Connection evaluated successfully"},
        422: {"description": "Invalid connection data"}
    }
)
async def submit_connection(connection: ConnectionInput) -> ConnectionResponse:
    """
    Submit a network connection for security evaluation
    
    The connection will be evaluated against active security policies and
    AI-based anomaly detection to determine if it should be allowed, alerted, or blocked.
    
    - **source_ip**: Source IP address of the connection
    - **destination_ip**: Destination IP address
    - **destination_port**: Destination port number (1-65535)
    - **protocol**: Network protocol (TCP or UDP)
    - **timestamp**: Connection timestamp in ISO 8601 format
    
    **Decision Logic:**
    1. Check if connection matches any policy
    2. If policy action is allow/block → immediate decision
    3. If policy action is alert or no match → AI scoring
    4. AI Thresholds: >0.8=block, 0.5-0.8=alert, <0.5=allow
    
    Example:
    ```json
    {
        "source_ip": "192.168.1.10",
        "destination_ip": "10.0.0.5",
        "destination_port": 443,
        "protocol": "TCP",
        "timestamp": "2025-04-30T12:34:56Z"
    }
    ```
    """
    try:
        response = connection_service.process_connection(connection)
        logger.info(
            f"Connection evaluated via API: {response.connection_id} "
            f"-> {response.decision}"
        )
        return response
        
    except Exception as e:
        logger.error(f"Unexpected error processing connection: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while processing connection"
        )


@router.get(
    "/{connection_id}",
    response_model=ConnectionDetail,
    status_code=status.HTTP_200_OK,
    summary="Retrieve connection evaluation details",
    responses={
        200: {"description": "Connection details retrieved successfully"},
        404: {"description": "Connection not found"}
    }
)
async def get_connection(connection_id: str) -> ConnectionDetail:
    """
    Retrieve detailed information about a previously evaluated connection
    
    Returns complete connection data including:
    - Original connection parameters
    - Security decision (allow/alert/block)
    - AI anomaly score
    - Matched policy (if any)
    - Evaluation timestamp
    
    - **connection_id**: UUID of the connection to retrieve
    
    Example response:
    ```json
    {
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
    ```
    """
    try:
        connection = connection_service.get_connection(connection_id)
        return connection
        
    except ConnectionNotFoundException as e:
        logger.warning(f"Connection retrieval failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error retrieving connection: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
