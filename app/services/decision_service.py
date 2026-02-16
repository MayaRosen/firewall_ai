"""
Decision Service

Implements the core firewall decision logic by evaluating connections
against policies and AI anomaly scores
"""
import logging
from typing import Tuple, Optional, Literal, List
from app.models import ConnectionInput, Policy, PolicyCondition

logger = logging.getLogger(__name__)


class DecisionService:
    """
    Service for making security decisions on network connections
    
    Implements the decision logic:
    1. Check policies (OR logic - any condition match wins)
    2. If policy action is allow/block -> return immediately
    3. If policy action is alert or no match -> get AI score
    4. Apply AI score thresholds
    """
    
    def evaluate_condition(
        self, 
        condition: PolicyCondition, 
        connection: ConnectionInput
    ) -> bool:
        """
        Evaluate a single policy condition against a connection
        
        Args:
            condition: The policy condition to check
            connection: The connection data
            
        Returns:
            True if condition matches, False otherwise
        """
        # Extract the connection field value
        field_value_map = {
            "source_ip": connection.source_ip,
            "destination_ip": connection.destination_ip,
            "destination_port": str(connection.destination_port),
            "protocol": connection.protocol
        }
        
        conn_value = field_value_map.get(condition.field)
        if conn_value is None:
            logger.warning(f"Unknown field in condition: {condition.field}")
            return False
        
        # Perform comparison based on operator
        try:
            if condition.operator == "=":
                return conn_value == condition.value
            elif condition.operator == "!=":
                return conn_value != condition.value
            elif condition.operator in [">", "<", ">=", "<="]:
                # Numeric comparison
                conn_num = float(conn_value)
                cond_num = float(condition.value)
                
                if condition.operator == ">":
                    return conn_num > cond_num
                elif condition.operator == "<":
                    return conn_num < cond_num
                elif condition.operator == ">=":
                    return conn_num >= cond_num
                elif condition.operator == "<=":
                    return conn_num <= cond_num
            
            return False
            
        except (ValueError, TypeError) as e:
            logger.warning(
                f"Comparison failed for condition {condition.field} "
                f"{condition.operator} {condition.value}: {str(e)}"
            )
            return False
    
    def evaluate_policy(
        self, 
        policy: Policy, 
        connection: ConnectionInput
    ) -> bool:
        """
        Check if a connection matches a policy
        
        Uses OR logic: if ANY condition matches, the policy matches
        
        Args:
            policy: The policy to evaluate
            connection: The connection data
            
        Returns:
            True if policy matches (any condition matches), False otherwise
        """
        for condition in policy.conditions:
            if self.evaluate_condition(condition, connection):
                logger.debug(
                    f"Policy {policy.policy_id} matched on condition: "
                    f"{condition.field} {condition.operator} {condition.value}"
                )
                return True  # ANY condition matches = policy matches
        
        return False
    
    def find_matching_policy(
        self, 
        connection: ConnectionInput, 
        policies: List[Policy]
    ) -> Optional[Policy]:
        """
        Find the first policy that matches the connection
        
        Args:
            connection: The connection data
            policies: List of all policies to check
            
        Returns:
            First matching Policy, or None if no match
        """
        for policy in policies:
            if self.evaluate_policy(policy, connection):
                logger.info(f"Connection matched policy: {policy.policy_id}")
                return policy
        
        logger.debug("No matching policy found for connection")
        return None
    
    def apply_ai_thresholds(
        self, 
        anomaly_score: float
    ) -> Literal["allow", "alert", "block"]:
        """
        Apply AI score thresholds to determine action
        
        Thresholds:
        - > 0.8: BLOCK
        - 0.5 to 0.8: ALERT
        - < 0.5: ALLOW
        
        Args:
            anomaly_score: The AI-calculated anomaly score (0.0-1.0)
            
        Returns:
            Security action to take
        """
        if anomaly_score > 0.8:
            decision = "block"
        elif anomaly_score >= 0.5:
            decision = "alert"
        else:
            decision = "allow"
        
        logger.debug(
            f"AI score {anomaly_score:.2f} -> decision: {decision}"
        )
        return decision
    
    def make_decision(
        self,
        connection: ConnectionInput,
        policies: List[Policy],
        anomaly_score: Optional[float] = None
    ) -> Tuple[Literal["allow", "alert", "block"], Optional[str], bool]:
        """
        Make a security decision for a connection
        
        Decision flow:
        1. Find matching policy
        2. If matched and action is allow/block -> return immediately
        3. If matched and action is alert OR no match -> use AI score
        
        Args:
            connection: The connection to evaluate
            policies: List of all policies
            anomaly_score: Pre-calculated AI score (if already obtained)
            
        Returns:
            Tuple of (decision, matched_policy_id, needs_ai_score)
            - decision: The security action to take
            - matched_policy_id: ID of matched policy, or None
            - needs_ai_score: True if AI score is needed for final decision
        """
        logger.info(
            f"Evaluating connection: {connection.source_ip} -> "
            f"{connection.destination_ip}:{connection.destination_port}/{connection.protocol}"
        )
        
        # Step 1: Find matching policy
        matched_policy = self.find_matching_policy(connection, policies)
        
        # Step 2: If policy matched with allow/block, return immediately
        if matched_policy and matched_policy.action in ["allow", "block"]:
            logger.info(
                f"Immediate decision from policy {matched_policy.policy_id}: "
                f"{matched_policy.action}"
            )
            return matched_policy.action, matched_policy.policy_id, False
        
        # Step 3: Need AI score (either no match or alert action)
        if matched_policy and matched_policy.action == "alert":
            logger.info(
                f"Policy {matched_policy.policy_id} requires AI evaluation (alert action)"
            )
        
        # If AI score not provided, indicate it's needed
        if anomaly_score is None:
            matched_id = matched_policy.policy_id if matched_policy else None
            return "alert", matched_id, True  # Signal that AI score is needed
        
        # Step 4: Apply AI score thresholds
        decision = self.apply_ai_thresholds(anomaly_score)
        matched_policy_id = matched_policy.policy_id if matched_policy else None
        
        logger.info(f"Final decision: {decision} (AI score: {anomaly_score:.2f})")
        return decision, matched_policy_id, False


# Global singleton instance
decision_service = DecisionService()
