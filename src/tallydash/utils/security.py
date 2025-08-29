import re
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

# List of dangerous SQL keywords and patterns
DANGEROUS_KEYWORDS = [
    'DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 'CREATE', 'TRUNCATE',
    'EXEC', 'EXECUTE', 'SHUTDOWN', 'GRANT', 'REVOKE', 'DENY',
    'SP_', 'XP_', 'OPENROWSET', 'OPENDATASOURCE', 'OPENQUERY',
    '--', '/*', '*/', 'UNION', 'HAVING'
]

# Patterns that might indicate SQL injection attempts
INJECTION_PATTERNS = [
    r"('|\"|`;|--|/\*|\*/|union|select.*from|insert.*into|delete.*from|update.*set|drop.*table)",
    r"(exec|execute|sp_|xp_)",
    r"(script|javascript|vbscript)",
    r"(\bor\b.*=.*\bor\b|\band\b.*=.*\band\b)",
    r"(1=1|1\s*=\s*1|true|false)"
]


def validate_sql_query(query: str) -> bool:
    """
    Validate SQL query for potential security threats.
    
    Args:
        query: SQL query string to validate
        
    Returns:
        bool: True if query is safe, False if potentially dangerous
    """
    if not query or not isinstance(query, str):
        logger.warning("Empty or invalid query provided")
        return False
    
    query_upper = query.upper().strip()
    
    # Check for dangerous keywords
    for keyword in DANGEROUS_KEYWORDS:
        if keyword in query_upper:
            logger.warning(f"Dangerous keyword '{keyword}' found in query")
            return False
    
    # Check for injection patterns
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, query, re.IGNORECASE):
            logger.warning(f"Potential SQL injection pattern found: {pattern}")
            return False
    
    # Ensure query starts with SELECT (read-only operations only)
    if not query_upper.startswith('SELECT'):
        logger.warning("Only SELECT queries are allowed")
        return False
    
    # Additional checks for Tally-specific patterns
    if not _validate_tally_query_structure(query):
        return False
    
    logger.debug("Query validation passed")
    return True


def _validate_tally_query_structure(query: str) -> bool:
    """
    Validate Tally-specific query structure.
    
    Args:
        query: SQL query string
        
    Returns:
        bool: True if query structure is valid for Tally ODBC
    """
    # Check for valid Tally table names
    valid_tables = [
        'Company', 'Ledger', 'Voucher', 'VoucherItem', 'StockItem', 
        'StockGroup', 'Group', 'Currency', 'GoDown', 'Unit'
    ]
    
    # Extract table names from FROM clause
    from_match = re.search(r'FROM\s+(\w+)', query, re.IGNORECASE)
    if from_match:
        table_name = from_match.group(1)
        if table_name not in valid_tables:
            logger.warning(f"Invalid table name '{table_name}' for Tally ODBC")
            return False
    
    # Check for valid Tally field patterns (starting with $)
    tally_fields = re.findall(r'\$\w+', query)
    if not tally_fields:
        logger.warning("No Tally fields ($FieldName) found in query")
        return False
    
    return True


def sanitize_input(input_value: str, max_length: int = 255) -> str:
    """
    Sanitize user input to prevent injection attacks.
    
    Args:
        input_value: Input string to sanitize
        max_length: Maximum allowed length
        
    Returns:
        str: Sanitized input string
    """
    if not input_value:
        return ""
    
    # Limit length
    sanitized = str(input_value)[:max_length]
    
    # Remove potentially dangerous characters
    sanitized = re.sub(r"[<>\"';\\]", "", sanitized)
    
    # Remove multiple spaces
    sanitized = re.sub(r'\s+', ' ', sanitized)
    
    return sanitized.strip()


def validate_date_input(date_str: str) -> bool:
    """
    Validate date input format.
    
    Args:
        date_str: Date string to validate
        
    Returns:
        bool: True if date format is valid
    """
    if not date_str:
        return True  # Empty dates are allowed
    
    # Allow common date formats
    date_patterns = [
        r'^\d{4}-\d{2}-\d{2}$',  # YYYY-MM-DD
        r'^\d{2}/\d{2}/\d{4}$',  # DD/MM/YYYY
        r'^\d{2}-\d{2}-\d{4}$',  # DD-MM-YYYY
    ]
    
    return any(re.match(pattern, date_str) for pattern in date_patterns)


def validate_amount_input(amount_str: str) -> bool:
    """
    Validate amount/number input.
    
    Args:
        amount_str: Amount string to validate
        
    Returns:
        bool: True if amount format is valid
    """
    if not amount_str:
        return True  # Empty amounts are allowed
    
    # Allow numbers with optional decimals and commas
    amount_pattern = r'^\d{1,3}(,\d{3})*(\.\d{2})?$|^\d+(\.\d{2})?$'
    return re.match(amount_pattern, amount_str) is not None


def create_safe_query_params(params: dict) -> dict:
    """
    Create safe query parameters by sanitizing inputs.
    
    Args:
        params: Dictionary of query parameters
        
    Returns:
        dict: Sanitized parameters
    """
    safe_params = {}
    
    for key, value in params.items():
        if isinstance(value, str):
            safe_params[key] = sanitize_input(value)
        elif isinstance(value, (int, float)):
            safe_params[key] = value
        else:
            safe_params[key] = str(value) if value is not None else None
    
    return safe_params


def log_security_event(event_type: str, details: str, severity: str = "WARNING"):
    """
    Log security-related events.
    
    Args:
        event_type: Type of security event
        details: Event details
        severity: Event severity level
    """
    logger.log(
        getattr(logging, severity.upper(), logging.WARNING),
        f"SECURITY EVENT - {event_type}: {details}"
    )


class SecurityValidator:
    """Class-based security validator with configurable rules."""
    
    def __init__(self, strict_mode: bool = True):
        self.strict_mode = strict_mode
        self.allowed_functions = {
            'SUM', 'COUNT', 'AVG', 'MAX', 'MIN', 'UPPER', 'LOWER',
            'LEN', 'SUBSTRING', 'CAST', 'CONVERT', 'YEAR', 'MONTH', 'DAY'
        }
        
    def validate_query(self, query: str) -> tuple[bool, Optional[str]]:
        """
        Comprehensive query validation with detailed error messages.
        
        Returns:
            tuple: (is_valid, error_message)
        """
        if not validate_sql_query(query):
            return False, "Query failed basic security validation"
        
        # Additional strict mode checks
        if self.strict_mode:
            if not self._check_function_whitelist(query):
                return False, "Query contains non-whitelisted functions"
            
            if not self._check_complexity(query):
                return False, "Query is too complex"
        
        return True, None
    
    def _check_function_whitelist(self, query: str) -> bool:
        """Check if query only uses whitelisted functions."""
        # Extract function calls
        functions = re.findall(r'(\w+)\s*\(', query, re.IGNORECASE)
        
        for func in functions:
            if func.upper() not in self.allowed_functions:
                log_security_event(
                    "UNAUTHORIZED_FUNCTION", 
                    f"Function '{func}' not in whitelist"
                )
                return False
        
        return True
    
    def _check_complexity(self, query: str) -> bool:
        """Check query complexity to prevent resource abuse."""
        # Count subqueries
        subquery_count = len(re.findall(r'\(.*SELECT.*\)', query, re.IGNORECASE))
        if subquery_count > 2:
            return False
        
        # Count JOINs
        join_count = len(re.findall(r'\bJOIN\b', query, re.IGNORECASE))
        if join_count > 3:
            return False
        
        # Check query length
        if len(query) > 2000:
            return False
        
        return True