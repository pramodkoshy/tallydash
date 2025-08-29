import pyodbc
import logging
from typing import List, Dict, Any, Optional, Union
from contextlib import contextmanager
import time
from ..config import settings
from ..utils.security import validate_sql_query


logger = logging.getLogger(__name__)


class TallyDatabase:
    """Manages ODBC connections to Tally ERP."""
    
    def __init__(self):
        self.connection_string = settings.tally_connection_string
        self.timeout = settings.connection_timeout
        self.retry_attempts = settings.retry_attempts
        
    def _create_connection(self) -> pyodbc.Connection:
        """Create a new ODBC connection to Tally."""
        try:
            conn = pyodbc.connect(
                self.connection_string,
                timeout=self.timeout
            )
            conn.setencoding('utf-8')
            return conn
        except pyodbc.Error as e:
            logger.error(f"Failed to connect to Tally ODBC: {e}")
            raise ConnectionError(f"Could not connect to Tally: {e}")
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections with automatic cleanup."""
        conn = None
        try:
            conn = self._create_connection()
            logger.debug("Successfully connected to Tally ODBC")
            yield conn
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if conn:
                try:
                    conn.close()
                    logger.debug("Database connection closed")
                except Exception as e:
                    logger.warning(f"Error closing connection: {e}")
    
    def execute_query(
        self, 
        query: str, 
        params: Optional[tuple] = None,
        fetch_all: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Execute a SQL query against Tally ODBC with security validation.
        
        Args:
            query: SQL query string
            params: Query parameters (optional)
            fetch_all: Whether to fetch all results or just first row
            
        Returns:
            List of dictionaries containing query results
        """
        # Validate query for security
        if not validate_sql_query(query):
            raise ValueError("Query validation failed - potential SQL injection detected")
        
        results = []
        attempt = 0
        
        while attempt < self.retry_attempts:
            try:
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    
                    # Execute query with parameters if provided
                    if params:
                        cursor.execute(query, params)
                    else:
                        cursor.execute(query)
                    
                    # Get column names
                    columns = [column[0] for column in cursor.description]
                    
                    # Fetch results
                    if fetch_all:
                        rows = cursor.fetchall()
                    else:
                        rows = [cursor.fetchone()] if cursor.fetchone() else []
                    
                    # Convert to list of dictionaries
                    for row in rows:
                        if row:  # Skip None rows
                            results.append(dict(zip(columns, row)))
                    
                    logger.info(f"Query executed successfully, returned {len(results)} rows")
                    return results
                    
            except pyodbc.Error as e:
                attempt += 1
                logger.warning(f"Query attempt {attempt} failed: {e}")
                if attempt >= self.retry_attempts:
                    logger.error(f"All {self.retry_attempts} attempts failed for query")
                    raise ConnectionError(f"Query failed after {self.retry_attempts} attempts: {e}")
                time.sleep(1)  # Brief delay before retry
        
        return results
    
    def test_connection(self) -> bool:
        """Test if connection to Tally ODBC is working."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                logger.info("Tally ODBC connection test successful")
                return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def get_companies(self) -> List[Dict[str, Any]]:
        """Get list of companies from Tally."""
        query = "SELECT $Name as company_name FROM Company"
        return self.execute_query(query)
    
    def get_ledgers(self, company: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get list of ledgers from Tally."""
        query = "SELECT $Name as ledger_name, $Parent as parent, $ClosingBalance as closing_balance FROM Ledger"
        if company:
            # Note: Company filtering would depend on Tally ODBC implementation
            query += f" WHERE $Company = '{company}'"
        return self.execute_query(query)
    
    def get_vouchers(
        self, 
        voucher_type: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get vouchers from Tally with optional filters."""
        query = """
        SELECT 
            $Date as voucher_date,
            $VoucherNumber as voucher_number,
            $VoucherType as voucher_type,
            $Amount as amount,
            $Reference as reference
        FROM Voucher
        WHERE 1=1
        """
        
        params = []
        if voucher_type:
            query += " AND $VoucherType = ?"
            params.append(voucher_type)
        
        if date_from:
            query += " AND $Date >= ?"
            params.append(date_from)
            
        if date_to:
            query += " AND $Date <= ?"
            params.append(date_to)
        
        query += " ORDER BY $Date DESC"
        
        if limit:
            query += f" LIMIT {limit}"
        
        return self.execute_query(query, tuple(params) if params else None)