"""
AI Anomaly Scoring Service

This service provides anomaly detection for network connections.
In a production environment, this would integrate with an actual ML model or external service.
"""
import random
import logging
from typing import Dict
from app.models import ConnectionInput

logger = logging.getLogger(__name__)


class AIAnomalyService:
    """
    Service for calculating anomaly scores for network connections
    
    This is a mock implementation that simulates ML model behavior.
    In production, this would call a real ML model or external API.
    """
    
    def __init__(self):
        """Initialize the AI service with baseline threat intelligence"""
        # Simulated threat intelligence: known suspicious IPs and their base scores
        self._suspicious_ips: Dict[str, float] = {
            "192.168.1.100": 0.85,
            "10.0.0.99": 0.75,
            "172.16.0.50": 0.65,
        }
        
        # Simulated threat intelligence: suspicious ports
        self._suspicious_ports: Dict[int, float] = {
            22: 0.6,    # SSH - often targeted
            23: 0.8,    # Telnet - insecure protocol
            3389: 0.7,  # RDP - frequently attacked
            445: 0.75,  # SMB - common attack vector
            1433: 0.65, # MSSQL - database exposure
        }
        
        logger.info("AI Anomaly Service initialized")
    
    def calculate_anomaly_score(self, connection: ConnectionInput) -> float:
        """
        Calculate an anomaly score for a network connection
        
        The score is based on multiple factors:
        - Source IP reputation
        - Destination IP reputation  
        - Port usage patterns
        - Protocol analysis
        
        Args:
            connection: The connection data to analyze
            
        Returns:
            Anomaly score between 0.0 (safe) and 1.0 (highly suspicious)
        """
        logger.debug(
            f"Calculating anomaly score for connection: "
            f"{connection.source_ip} -> {connection.destination_ip}:{connection.destination_port}"
        )
        
        # Start with a low baseline score
        base_score = random.uniform(0.1, 0.3)
        
        # Factor 1: Check source IP reputation
        if connection.source_ip in self._suspicious_ips:
            source_score = self._suspicious_ips[connection.source_ip]
            base_score = max(base_score, source_score)
            logger.debug(f"Suspicious source IP detected: {connection.source_ip} (score: {source_score})")
        
        # Factor 2: Check destination IP reputation
        if connection.destination_ip in self._suspicious_ips:
            dest_score = self._suspicious_ips[connection.destination_ip]
            base_score = max(base_score, dest_score)
            logger.debug(f"Suspicious destination IP detected: {connection.destination_ip} (score: {dest_score})")
        
        # Factor 3: Analyze destination port
        if connection.destination_port in self._suspicious_ports:
            port_score = self._suspicious_ports[connection.destination_port]
            base_score = max(base_score, port_score)
            logger.debug(f"Suspicious port detected: {connection.destination_port} (score: {port_score})")
        
        # Factor 4: Protocol-based adjustment
        # UDP is slightly more suspicious for certain ports
        if connection.protocol == "UDP" and connection.destination_port not in [53, 123]:
            base_score = min(base_score + 0.1, 1.0)
        
        # Add slight randomness to simulate ML model variance
        final_score = base_score + random.uniform(-0.05, 0.05)
        
        # Ensure score is within valid range
        final_score = max(0.0, min(1.0, final_score))
        
        logger.debug(f"Final anomaly score: {final_score:.2f}")
        return round(final_score, 2)
    
    def add_suspicious_ip(self, ip: str, score: float) -> None:
        """
        Add an IP to the suspicious IP list
        
        Args:
            ip: IP address to add
            score: Base anomaly score for this IP (0.0-1.0)
        """
        self._suspicious_ips[ip] = max(0.0, min(1.0, score))
        logger.info(f"Added suspicious IP: {ip} with score {score}")
    
    def add_suspicious_port(self, port: int, score: float) -> None:
        """
        Add a port to the suspicious port list
        
        Args:
            port: Port number to add
            score: Base anomaly score for this port (0.0-1.0)
        """
        self._suspicious_ports[port] = max(0.0, min(1.0, score))
        logger.info(f"Added suspicious port: {port} with score {score}")


# Global singleton instance
ai_anomaly_service = AIAnomalyService()
