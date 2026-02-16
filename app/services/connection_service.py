"""
Connection Service

Handles business logic for connection processing and evaluation
"""
import logging
import uuid
from datetime import datetime
from app.models import (
    ConnectionInput,
    ConnectionResponse,
    ConnectionDetail
)
from app.repositories.storage import storage_repository
from app.services.ai_service import ai_anomaly_service
from app.services.decision_service import decision_service
from app.services.policy_service import policy_service
from app.utils.exceptions import ConnectionNotFoundException

logger = logging.getLogger(__name__)


class ConnectionService:
    """
    Service for processing and evaluating network connections
    
    Coordinates between policy evaluation, AI scoring, and decision making
    """
    
    def __init__(
        self,
        repository=storage_repository,
        ai_service=ai_anomaly_service,
        dec_service=decision_service,
        pol_service=policy_service
    ):
        """
        Initialize the connection service with dependencies
        
        Args:
            repository: Storage repository
            ai_service: AI anomaly scoring service
            dec_service: Decision service
            pol_service: Policy service
        """
        self.repository = repository
        self.ai_service = ai_service
        self.decision_service = dec_service
        self.policy_service = pol_service
        logger.info("Connection Service initialized")
    
    def process_connection(self, connection: ConnectionInput) -> ConnectionResponse:
        """
        Process an incoming connection and make a security decision
        
        This is the main entry point for connection evaluation.
        
        Args:
            connection: The connection data to process
            
        Returns:
            ConnectionResponse with decision and details
        """
        # Generate unique connection ID
        connection_id = str(uuid.uuid4())
        evaluated_at = datetime.utcnow()
        
        logger.info(
            f"Processing connection {connection_id}: "
            f"{connection.source_ip} -> "
            f"{connection.destination_ip}:{connection.destination_port}"
        )
        
        # Get all active policies
        policies = self.policy_service.get_all_policies()
        
        # Step 1: Evaluate against policies
        decision, matched_policy_id, needs_ai = self.decision_service.make_decision(
            connection=connection,
            policies=policies,
            anomaly_score=None  # Don't provide score yet
        )
        
        # Step 2: Get AI score if needed
        if needs_ai:
            logger.debug("AI scoring required for final decision")
            anomaly_score = self.ai_service.calculate_anomaly_score(connection)
            
            # Re-evaluate with AI score
            decision, matched_policy_id, _ = self.decision_service.make_decision(
                connection=connection,
                policies=policies,
                anomaly_score=anomaly_score
            )
        else:
            # Policy made immediate decision, set nominal AI score
            anomaly_score = 0.0
            logger.debug("Policy made immediate decision, AI scoring skipped")
        
        # Step 3: Store connection details
        connection_detail = ConnectionDetail(
            connection_id=connection_id,
            source_ip=connection.source_ip,
            destination_ip=connection.destination_ip,
            destination_port=connection.destination_port,
            protocol=connection.protocol,
            timestamp=connection.timestamp,
            decision=decision,
            anomaly_score=anomaly_score,
            matched_policy=matched_policy_id,
            evaluated_at=evaluated_at
        )
        
        self.repository.store_connection(connection_detail)
        
        logger.info(
            f"Connection {connection_id} processed: "
            f"decision={decision}, score={anomaly_score:.2f}"
        )
        
        # Step 4: Return response
        return ConnectionResponse(
            connection_id=connection_id,
            decision=decision,
            anomaly_score=anomaly_score,
            matched_policy=matched_policy_id
        )
    
    def get_connection(self, connection_id: str) -> ConnectionDetail:
        """
        Retrieve details of a previously evaluated connection
        
        Args:
            connection_id: The connection ID to retrieve
            
        Returns:
            ConnectionDetail with full connection information
            
        Raises:
            ConnectionNotFoundException: If connection doesn't exist
        """
        logger.debug(f"Retrieving connection: {connection_id}")
        
        connection = self.repository.get_connection(connection_id)
        
        if connection is None:
            logger.error(f"Connection not found: {connection_id}")
            raise ConnectionNotFoundException(
                f"Connection with ID '{connection_id}' not found"
            )
        
        return connection


# Global singleton instance
connection_service = ConnectionService()
