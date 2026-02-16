"""
PostgreSQL storage repository for policies and connections

This serves as the data access layer, abstracting storage operations
from business logic using raw SQL queries for optimal performance.
"""
import json
from typing import Optional, List
from datetime import datetime
import psycopg
from psycopg.rows import dict_row

from app.models import Policy, ConnectionDetail, PolicyCondition
from app.utils.exceptions import PolicyNotFoundException, PolicyAlreadyExistsException
from app.database.connection import db_manager


class StorageRepository:
    """
    Repository for managing PostgreSQL storage of policies and connections.
    
    Uses raw SQL queries for optimal performance and full control.
    Follows the Repository pattern to keep business logic separate from data access.
    """
    
    # SQL Queries - organized for maintainability
    
    # Policy queries
    SQL_INSERT_POLICY = """
        INSERT INTO policies (policy_id, conditions, action, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s)
    """
    
    SQL_UPDATE_POLICY = """
        UPDATE policies
        SET conditions = %s, action = %s, updated_at = %s
        WHERE policy_id = %s
    """
    
    SQL_SELECT_POLICY = """
        SELECT policy_id, conditions, action, created_at, updated_at
        FROM policies
        WHERE policy_id = %s
    """
    
    SQL_SELECT_ALL_POLICIES = """
        SELECT policy_id, conditions, action, created_at, updated_at
        FROM policies
        ORDER BY created_at DESC
    """
    
    SQL_DELETE_POLICY = """
        DELETE FROM policies
        WHERE policy_id = %s
    """
    
    SQL_CHECK_POLICY_EXISTS = """
        SELECT EXISTS(SELECT 1 FROM policies WHERE policy_id = %s)
    """
    
    # Connection queries
    SQL_INSERT_CONNECTION = """
        INSERT INTO connections (
            connection_id, source_ip, destination_ip, destination_port,
            protocol, timestamp, decision, anomaly_score, matched_policy, evaluated_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (connection_id) DO UPDATE SET
            source_ip = EXCLUDED.source_ip,
            destination_ip = EXCLUDED.destination_ip,
            destination_port = EXCLUDED.destination_port,
            protocol = EXCLUDED.protocol,
            timestamp = EXCLUDED.timestamp,
            decision = EXCLUDED.decision,
            anomaly_score = EXCLUDED.anomaly_score,
            matched_policy = EXCLUDED.matched_policy,
            evaluated_at = EXCLUDED.evaluated_at
    """
    
    SQL_SELECT_CONNECTION = """
        SELECT 
            connection_id, source_ip, destination_ip, destination_port,
            protocol, timestamp, decision, anomaly_score, matched_policy, evaluated_at
        FROM connections
        WHERE connection_id = %s
    """
    
    SQL_SELECT_ALL_CONNECTIONS = """
        SELECT 
            connection_id, source_ip, destination_ip, destination_port,
            protocol, timestamp, decision, anomaly_score, matched_policy, evaluated_at
        FROM connections
        ORDER BY evaluated_at DESC
    """
    
    # Policy operations
    
    def create_policy(self, policy: Policy) -> None:
        """
        Create a new policy in the database.
        
        Args:
            policy: Policy object to store
            
        Raises:
            PolicyAlreadyExistsException: If policy_id already exists
        """
        # Check if policy already exists
        if self.policy_exists(policy.policy_id):
            raise PolicyAlreadyExistsException(
                f"Policy with ID '{policy.policy_id}' already exists"
            )
        
        # Convert conditions to JSON
        conditions_json = json.dumps([cond.model_dump() for cond in policy.conditions])
        now = datetime.utcnow()
        
        with db_manager.get_cursor() as cur:
            cur.execute(
                self.SQL_INSERT_POLICY,
                (policy.policy_id, conditions_json, policy.action, now, now)
            )
    
    def update_policy(self, policy_id: str, policy: Policy) -> None:
        """
        Update an existing policy in the database.
        
        Args:
            policy_id: ID of policy to update
            policy: New policy data
            
        Raises:
            PolicyNotFoundException: If policy doesn't exist
        """
        # Check if policy exists
        if not self.policy_exists(policy_id):
            raise PolicyNotFoundException(
                f"Policy with ID '{policy_id}' not found"
            )
        
        # Convert conditions to JSON
        conditions_json = json.dumps([cond.model_dump() for cond in policy.conditions])
        now = datetime.utcnow()
        
        with db_manager.get_cursor() as cur:
            cur.execute(
                self.SQL_UPDATE_POLICY,
                (conditions_json, policy.action, now, policy_id)
            )
    
    def get_policy(self, policy_id: str) -> Policy:
        """
        Retrieve a policy by ID from the database.
        
        Args:
            policy_id: ID of policy to retrieve
            
        Returns:
            Policy object
            
        Raises:
            PolicyNotFoundException: If policy doesn't exist
        """
        with db_manager.get_cursor() as cur:
            cur.execute(self.SQL_SELECT_POLICY, (policy_id,))
            row = cur.fetchone()
        
        if row is None:
            raise PolicyNotFoundException(
                f"Policy with ID '{policy_id}' not found"
            )
        
        return self._row_to_policy(row)
    
    def get_all_policies(self) -> List[Policy]:
        """
        Get all policies from the database.
        
        Returns:
            List of all Policy objects
        """
        with db_manager.get_cursor() as cur:
            cur.execute(self.SQL_SELECT_ALL_POLICIES)
            rows = cur.fetchall()
        
        return [self._row_to_policy(row) for row in rows]
    
    def delete_policy(self, policy_id: str) -> None:
        """
        Delete a policy from the database.
        
        Args:
            policy_id: ID of policy to delete
            
        Raises:
            PolicyNotFoundException: If policy doesn't exist
        """
        if not self.policy_exists(policy_id):
            raise PolicyNotFoundException(
                f"Policy with ID '{policy_id}' not found"
            )
        
        with db_manager.get_cursor() as cur:
            cur.execute(self.SQL_DELETE_POLICY, (policy_id,))
    
    def policy_exists(self, policy_id: str) -> bool:
        """
        Check if a policy exists in the database.
        
        Args:
            policy_id: ID to check
            
        Returns:
            True if policy exists, False otherwise
        """
        with db_manager.get_cursor() as cur:
            cur.execute(self.SQL_CHECK_POLICY_EXISTS, (policy_id,))
            result = cur.fetchone()
            return result['exists'] if result else False
    
    # Connection operations
    
    def store_connection(self, connection: ConnectionDetail) -> None:
        """
        Store a connection decision in the database.
        
        Uses UPSERT to handle duplicate connection IDs gracefully.
        
        Args:
            connection: ConnectionDetail object to store
        """
        with db_manager.get_cursor() as cur:
            cur.execute(
                self.SQL_INSERT_CONNECTION,
                (
                    connection.connection_id,
                    str(connection.source_ip),
                    str(connection.destination_ip),
                    connection.destination_port,
                    connection.protocol,
                    connection.timestamp,
                    connection.decision,
                    float(connection.anomaly_score),
                    connection.matched_policy,
                    connection.evaluated_at
                )
            )
    
    def get_connection(self, connection_id: str) -> Optional[ConnectionDetail]:
        """
        Retrieve a connection by ID from the database.
        
        Args:
            connection_id: ID of connection to retrieve
            
        Returns:
            ConnectionDetail object or None if not found
        """
        with db_manager.get_cursor() as cur:
            cur.execute(self.SQL_SELECT_CONNECTION, (connection_id,))
            row = cur.fetchone()
        
        if row is None:
            return None
        
        return self._row_to_connection(row)
    
    def get_all_connections(self) -> List[ConnectionDetail]:
        """
        Get all stored connections from the database.
        
        Returns:
            List of all ConnectionDetail objects
        """
        with db_manager.get_cursor() as cur:
            cur.execute(self.SQL_SELECT_ALL_CONNECTIONS)
            rows = cur.fetchall()
        
        return [self._row_to_connection(row) for row in rows]
    
    # Helper methods for data conversion
    
    @staticmethod
    def _row_to_policy(row: dict) -> Policy:
        """Convert database row to Policy object"""
        conditions_data = json.loads(row['conditions']) if isinstance(row['conditions'], str) else row['conditions']
        conditions = [PolicyCondition(**cond) for cond in conditions_data]
        
        return Policy(
            policy_id=row['policy_id'],
            conditions=conditions,
            action=row['action']
        )
    
    @staticmethod
    def _row_to_connection(row: dict) -> ConnectionDetail:
        """Convert database row to ConnectionDetail object"""
        return ConnectionDetail(
            connection_id=row['connection_id'],
            source_ip=str(row['source_ip']),
            destination_ip=str(row['destination_ip']),
            destination_port=row['destination_port'],
            protocol=row['protocol'],
            timestamp=row['timestamp'],
            decision=row['decision'],
            anomaly_score=float(row['anomaly_score']),
            matched_policy=row['matched_policy'],
            evaluated_at=row['evaluated_at']
        )


# Global singleton instance
storage_repository = StorageRepository()
