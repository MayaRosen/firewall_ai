"""
Database Connection Manager

Manages PostgreSQL connections using connection pooling for optimal performance.
Uses psycopg3 with connection pooling for efficient resource management.
"""
import logging
from typing import Optional
from contextlib import contextmanager
import psycopg
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from app.config import settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Professional database connection manager with connection pooling.
    
    Implements the connection pool pattern for efficient database access.
    Provides context managers for automatic connection lifecycle management.
    """
    
    _instance: Optional['DatabaseManager'] = None
    _pool: Optional[ConnectionPool] = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one connection pool exists"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def initialize(self):
        """
        Initialize the connection pool.
        
        Should be called during application startup.
        Creates a connection pool with configurable min/max connections.
        """
        if self._pool is not None:
            logger.warning("Database pool already initialized")
            return
        
        try:
            connection_string = (
                f"postgresql://{settings.db_user}:{settings.db_password}"
                f"@{settings.db_host}:{settings.db_port}/{settings.db_name}"
            )
            
            self._pool = ConnectionPool(
                conninfo=connection_string,
                min_size=settings.db_pool_min_size,
                max_size=settings.db_pool_max_size,
                timeout=30,
                max_idle=300,
                kwargs={
                    "row_factory": dict_row,  # Return results as dictionaries
                    "autocommit": False,  # Explicit transaction control
                }
            )
            
            logger.info(
                f"Database connection pool initialized "
                f"(min={settings.db_pool_min_size}, max={settings.db_pool_max_size})"
            )
            
        except Exception as e:
            logger.error(f"Failed to initialize database pool: {e}")
            raise
    
    def close(self):
        """
        Close the connection pool.
        
        Should be called during application shutdown.
        Ensures all connections are properly closed.
        """
        if self._pool is not None:
            self._pool.close()
            self._pool = None
            logger.info("Database connection pool closed")
    
    @contextmanager
    def get_connection(self):
        """
        Get a database connection from the pool.
        
        Usage:
            with db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM policies")
                    results = cur.fetchall()
                conn.commit()
        
        Yields:
            psycopg.Connection: Database connection with dict_row factory
        
        Raises:
            RuntimeError: If pool is not initialized
        """
        if self._pool is None:
            raise RuntimeError(
                "Database pool not initialized. Call initialize() first."
            )
        
        connection = None
        try:
            connection = self._pool.getconn()
            yield connection
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"Database operation failed: {e}")
            raise
        finally:
            if connection:
                self._pool.putconn(connection)
    
    @contextmanager
    def get_cursor(self):
        """
        Get a database cursor with automatic connection and transaction management.
        
        Usage:
            with db_manager.get_cursor() as cur:
                cur.execute("SELECT * FROM policies")
                results = cur.fetchall()
                # Auto-commits on success, rolls back on error
        
        Yields:
            psycopg.Cursor: Database cursor ready for queries
        """
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                try:
                    yield cursor
                    conn.commit()
                except Exception as e:
                    conn.rollback()
                    raise
    
    def execute_script(self, sql_script: str):
        """
        Execute a SQL script (for initialization/migrations).
        
        Args:
            sql_script: Multi-statement SQL script
        
        Raises:
            Exception: If script execution fails
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute(sql_script)
                    conn.commit()
                    logger.info("SQL script executed successfully")
                except Exception as e:
                    conn.rollback()
                    logger.error(f"Failed to execute SQL script: {e}")
                    raise
    
    def health_check(self) -> bool:
        """
        Check if database connection is healthy.
        
        Returns:
            bool: True if database is accessible, False otherwise
        """
        try:
            with self.get_cursor() as cur:
                cur.execute("SELECT 1")
                result = cur.fetchone()
                return result is not None
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False


# Global database manager instance
db_manager = DatabaseManager()
