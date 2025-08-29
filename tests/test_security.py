import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tallydash.utils.security import (
    validate_sql_query,
    sanitize_input,
    validate_date_input,
    validate_amount_input,
    SecurityValidator
)


class TestSecurityValidation:
    """Test cases for security validation functions."""
    
    def test_valid_select_queries(self):
        """Test that valid SELECT queries pass validation."""
        valid_queries = [
            "SELECT $Name FROM Ledger",
            "SELECT $Name, $ClosingBalance FROM Ledger WHERE $Parent = 'Assets'",
            "SELECT COUNT(*) FROM Voucher",
            "SELECT $Date, $Amount FROM Voucher ORDER BY $Date DESC"
        ]
        
        for query in valid_queries:
            assert validate_sql_query(query), f"Valid query failed: {query}"
    
    def test_dangerous_queries_blocked(self):
        """Test that dangerous SQL operations are blocked."""
        dangerous_queries = [
            "DROP TABLE Ledger",
            "DELETE FROM Voucher",
            "INSERT INTO Ledger VALUES ('Test')",
            "UPDATE Voucher SET $Amount = 0",
            "EXEC sp_helpdb",
            "SELECT * FROM Ledger; DROP TABLE Voucher;",
            "SELECT * FROM Ledger WHERE 1=1 OR 1=1",
            "SELECT * FROM Ledger UNION SELECT * FROM Voucher"
        ]
        
        for query in dangerous_queries:
            assert not validate_sql_query(query), f"Dangerous query passed: {query}"
    
    def test_injection_patterns_blocked(self):
        """Test that SQL injection patterns are blocked."""
        injection_queries = [
            "SELECT * FROM Ledger WHERE $Name = 'Test'; DROP TABLE Voucher; --'",
            "SELECT * FROM Ledger WHERE $Name = 'Test' OR 1=1",
            "SELECT * FROM Ledger WHERE $Name = 'Test' UNION SELECT password FROM users",
            "SELECT * FROM Ledger /* comment */ WHERE $Name = 'Test'"
        ]
        
        for query in injection_queries:
            assert not validate_sql_query(query), f"Injection pattern passed: {query}"
    
    def test_non_select_queries_blocked(self):
        """Test that non-SELECT queries are blocked."""
        non_select_queries = [
            "CREATE TABLE test (id int)",
            "ALTER TABLE Ledger ADD COLUMN test varchar(50)",
            "GRANT SELECT ON Ledger TO user",
            "TRUNCATE TABLE Voucher"
        ]
        
        for query in non_select_queries:
            assert not validate_sql_query(query), f"Non-SELECT query passed: {query}"
    
    def test_empty_invalid_queries(self):
        """Test that empty or invalid queries are blocked."""
        invalid_queries = [
            "",
            None,
            "   ",
            123,
            [],
            {}
        ]
        
        for query in invalid_queries:
            assert not validate_sql_query(query), f"Invalid query passed: {query}"
    
    def test_tally_field_validation(self):
        """Test that queries without Tally fields are flagged."""
        # Valid query with Tally fields
        valid_query = "SELECT $Name, $ClosingBalance FROM Ledger"
        assert validate_sql_query(valid_query)
        
        # Invalid query without Tally fields
        invalid_query = "SELECT Name, ClosingBalance FROM Ledger"
        assert not validate_sql_query(invalid_query)
    
    def test_input_sanitization(self):
        """Test input sanitization function."""
        test_cases = [
            ("normal text", "normal text"),
            ("text with <script>", "text with script"),
            ("text with 'quotes'", "text with quotes"),
            ("text with \"double quotes\"", "text with double quotes"),
            ("text   with   spaces", "text with spaces"),
            ("text with; semicolon", "text with semicolon"),
            ("very long " + "x" * 300 + " text", "very long " + "x" * 239 + " text")
        ]
        
        for input_text, expected in test_cases:
            result = sanitize_input(input_text)
            assert result == expected, f"Sanitization failed: {input_text} -> {result}"
    
    def test_date_validation(self):
        """Test date input validation."""
        valid_dates = [
            "2024-01-15",
            "15/01/2024",
            "15-01-2024",
            ""  # Empty date should be allowed
        ]
        
        invalid_dates = [
            "2024-13-01",  # Invalid month
            "15/13/2024",  # Invalid month
            "2024/01/15",  # Wrong format
            "January 15, 2024",  # Text format
            "not-a-date"
        ]
        
        for date_str in valid_dates:
            assert validate_date_input(date_str), f"Valid date rejected: {date_str}"
        
        for date_str in invalid_dates:
            assert not validate_date_input(date_str), f"Invalid date accepted: {date_str}"
    
    def test_amount_validation(self):
        """Test amount input validation."""
        valid_amounts = [
            "1000",
            "1,000",
            "1,000.00",
            "100000.50",
            "1,23,456.78",
            ""  # Empty amount should be allowed
        ]
        
        invalid_amounts = [
            "1,00,000.123",  # Too many decimals
            "1,0000",  # Wrong comma placement
            "abc",  # Text
            "1000.5.5",  # Multiple decimals
            "-1000"  # Negative (depending on requirements)
        ]
        
        for amount in valid_amounts:
            assert validate_amount_input(amount), f"Valid amount rejected: {amount}"
        
        for amount in invalid_amounts:
            assert not validate_amount_input(amount), f"Invalid amount accepted: {amount}"
    
    def test_security_validator_class(self):
        """Test SecurityValidator class functionality."""
        validator = SecurityValidator(strict_mode=True)
        
        # Test valid query
        valid_query = "SELECT $Name, SUM($ClosingBalance) FROM Ledger GROUP BY $Parent"
        is_valid, error = validator.validate_query(valid_query)
        assert is_valid, f"Valid query failed: {error}"
        
        # Test invalid function
        invalid_query = "SELECT $Name, EXEC('malicious') FROM Ledger"
        is_valid, error = validator.validate_query(invalid_query)
        assert not is_valid
        assert error is not None
    
    def test_function_whitelist(self):
        """Test function whitelist in strict mode."""
        validator = SecurityValidator(strict_mode=True)
        
        # Allowed functions
        allowed_query = "SELECT $Name, SUM($Amount), COUNT(*), MAX($Date) FROM Voucher"
        is_valid, error = validator.validate_query(allowed_query)
        assert is_valid
        
        # Disallowed function
        disallowed_query = "SELECT $Name, EXEC('command') FROM Ledger"
        is_valid, error = validator.validate_query(disallowed_query)
        assert not is_valid
    
    def test_query_complexity_limits(self):
        """Test query complexity limits."""
        validator = SecurityValidator(strict_mode=True)
        
        # Simple query should pass
        simple_query = "SELECT $Name FROM Ledger"
        is_valid, error = validator.validate_query(simple_query)
        assert is_valid
        
        # Very long query should fail
        long_query = "SELECT $Name FROM Ledger WHERE " + " AND ".join([f"$Field{i} = 'value'" for i in range(100)])
        is_valid, error = validator.validate_query(long_query)
        assert not is_valid