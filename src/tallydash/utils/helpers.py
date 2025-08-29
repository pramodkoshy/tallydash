import functools
import time
import re
from typing import Any, Callable, Optional, Tuple, Dict, Union
from datetime import datetime, date, timedelta
from decimal import Decimal
import diskcache
from ..config import settings

# Global cache instance
cache = diskcache.Cache('.cache')


def cache_result(ttl: int = 300):
    """
    Decorator to cache function results.
    
    Args:
        ttl: Time to live in seconds
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, expire=ttl)
            return result
        
        return wrapper
    return decorator


def format_currency(amount: Union[float, Decimal, int], currency_code: str = "₹") -> str:
    """
    Format amount as currency string.
    
    Args:
        amount: Amount to format
        currency_code: Currency symbol
        
    Returns:
        str: Formatted currency string
    """
    if amount is None:
        return f"{currency_code}0.00"
    
    try:
        # Convert to float for formatting
        amount_float = float(amount)
        
        # Handle negative amounts
        is_negative = amount_float < 0
        amount_float = abs(amount_float)
        
        # Format with commas for thousands
        if amount_float >= 10000000:  # 1 crore
            formatted = f"{amount_float/10000000:.2f} Cr"
        elif amount_float >= 100000:  # 1 lakh
            formatted = f"{amount_float/100000:.2f} L"
        elif amount_float >= 1000:
            formatted = f"{amount_float:,.2f}"
        else:
            formatted = f"{amount_float:.2f}"
        
        result = f"{currency_code}{formatted}"
        return f"(-{result[1:]})" if is_negative else result
        
    except (ValueError, TypeError):
        return f"{currency_code}0.00"


def extract_date_range(text: str) -> Optional[Tuple[date, date]]:
    """
    Extract date range from natural language text.
    
    Args:
        text: Text containing date expressions
        
    Returns:
        tuple: (start_date, end_date) or None if no dates found
    """
    text_lower = text.lower()
    today = date.today()
    
    # Handle relative date expressions
    if "today" in text_lower:
        return today, today
    
    if "yesterday" in text_lower:
        yesterday = today - timedelta(days=1)
        return yesterday, yesterday
    
    if "this week" in text_lower:
        start_of_week = today - timedelta(days=today.weekday())
        return start_of_week, today
    
    if "last week" in text_lower:
        start_of_last_week = today - timedelta(days=today.weekday() + 7)
        end_of_last_week = start_of_last_week + timedelta(days=6)
        return start_of_last_week, end_of_last_week
    
    if "this month" in text_lower:
        start_of_month = today.replace(day=1)
        return start_of_month, today
    
    if "last month" in text_lower:
        first_day_last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
        last_day_last_month = today.replace(day=1) - timedelta(days=1)
        return first_day_last_month, last_day_last_month
    
    if "this year" in text_lower:
        start_of_year = today.replace(month=1, day=1)
        return start_of_year, today
    
    if "last year" in text_lower:
        start_of_last_year = today.replace(year=today.year-1, month=1, day=1)
        end_of_last_year = today.replace(year=today.year-1, month=12, day=31)
        return start_of_last_year, end_of_last_year
    
    # Handle "last X days" pattern
    days_match = re.search(r"last (\d+) days?", text_lower)
    if days_match:
        days = int(days_match.group(1))
        start_date = today - timedelta(days=days-1)
        return start_date, today
    
    # Handle "past X months" pattern
    months_match = re.search(r"(?:past|last) (\d+) months?", text_lower)
    if months_match:
        months = int(months_match.group(1))
        start_date = today - timedelta(days=30*months)
        return start_date, today
    
    # Try to extract specific dates
    date_patterns = [
        r"(\d{4}-\d{2}-\d{2})",  # YYYY-MM-DD
        r"(\d{2}/\d{2}/\d{4})",  # DD/MM/YYYY
        r"(\d{2}-\d{2}-\d{4})",  # DD-MM-YYYY
    ]
    
    dates_found = []
    for pattern in date_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            try:
                if "-" in match and len(match.split("-")[0]) == 4:
                    # YYYY-MM-DD format
                    parsed_date = datetime.strptime(match, "%Y-%m-%d").date()
                elif "/" in match:
                    # DD/MM/YYYY format
                    parsed_date = datetime.strptime(match, "%d/%m/%Y").date()
                else:
                    # DD-MM-YYYY format
                    parsed_date = datetime.strptime(match, "%d-%m-%Y").date()
                dates_found.append(parsed_date)
            except ValueError:
                continue
    
    if len(dates_found) >= 2:
        return min(dates_found), max(dates_found)
    elif len(dates_found) == 1:
        return dates_found[0], dates_found[0]
    
    return None


def parse_natural_language_query(query: str) -> Dict[str, Any]:
    """
    Parse natural language query to extract structured information.
    
    Args:
        query: Natural language query string
        
    Returns:
        dict: Parsed query components
    """
    query_lower = query.lower().strip()
    parsed = {
        "intent": None,
        "entities": {},
        "filters": {},
        "aggregation": None,
        "limit": None,
        "sort_order": None
    }
    
    # Extract intent
    intent_patterns = {
        "sales": ["sales", "revenue", "income", "selling"],
        "purchases": ["purchase", "buy", "procurement"],
        "expenses": ["expense", "cost", "expenditure", "spending"],
        "profit": ["profit", "loss", "earnings", "pnl", "p&l"],
        "cash_flow": ["cash", "receipt", "payment", "cash flow"],
        "customers": ["customer", "debtor", "client", "party"],
        "suppliers": ["supplier", "creditor", "vendor"],
        "vouchers": ["voucher", "transaction", "entry"],
        "ledgers": ["ledger", "account", "balance"],
        "inventory": ["stock", "inventory", "item", "goods"]
    }
    
    for intent_key, keywords in intent_patterns.items():
        if any(keyword in query_lower for keyword in keywords):
            parsed["intent"] = intent_key
            break
    
    # Extract numerical entities
    numbers = re.findall(r'\b\d+(?:,\d{3})*(?:\.\d{2})?\b', query)
    if numbers:
        parsed["entities"]["amounts"] = [float(n.replace(',', '')) for n in numbers]
    
    # Extract limits/top N
    top_patterns = [
        r"top (\d+)",
        r"first (\d+)",
        r"(\d+) (?:top|best|largest|highest)"
    ]
    
    for pattern in top_patterns:
        match = re.search(pattern, query_lower)
        if match:
            parsed["limit"] = int(match.group(1))
            break
    
    # Extract comparison operators
    comparison_patterns = {
        "greater_than": [r"(?:greater than|above|more than|over) ([\d,]+(?:\.\d{2})?)"],
        "less_than": [r"(?:less than|below|under|fewer than) ([\d,]+(?:\.\d{2})?)"],
        "equal_to": [r"(?:equal to|exactly|equals?) ([\d,]+(?:\.\d{2})?)"]
    }
    
    for comp_type, patterns in comparison_patterns.items():
        for pattern in patterns:
            match = re.search(pattern, query_lower)
            if match:
                amount = float(match.group(1).replace(',', ''))
                parsed["filters"]["amount_filter"] = {
                    "type": comp_type,
                    "value": amount
                }
                break
    
    # Extract date ranges
    date_range = extract_date_range(query)
    if date_range:
        parsed["filters"]["date_range"] = {
            "start": date_range[0].isoformat(),
            "end": date_range[1].isoformat()
        }
    
    # Extract sort order
    if any(word in query_lower for word in ["highest", "largest", "most", "desc"]):
        parsed["sort_order"] = "desc"
    elif any(word in query_lower for word in ["lowest", "smallest", "least", "asc"]):
        parsed["sort_order"] = "asc"
    
    # Extract aggregation type
    agg_patterns = {
        "sum": ["total", "sum", "aggregate"],
        "average": ["average", "avg", "mean"],
        "count": ["count", "number of", "how many"],
        "max": ["maximum", "max", "highest"],
        "min": ["minimum", "min", "lowest"]
    }
    
    for agg_type, keywords in agg_patterns.items():
        if any(keyword in query_lower for keyword in keywords):
            parsed["aggregation"] = agg_type
            break
    
    # Extract specific voucher types
    voucher_types = {
        "Sales": ["sales", "sale"],
        "Purchase": ["purchase", "buy"],
        "Payment": ["payment", "paid"],
        "Receipt": ["receipt", "received"],
        "Journal": ["journal", "adjustment"],
        "Contra": ["contra", "transfer"]
    }
    
    for v_type, keywords in voucher_types.items():
        if any(keyword in query_lower for keyword in keywords):
            parsed["entities"]["voucher_type"] = v_type
            break
    
    return parsed


def convert_to_chart_data(data: list, chart_type: str = "bar") -> Dict[str, Any]:
    """
    Convert query results to chart-friendly format.
    
    Args:
        data: List of dictionaries containing data
        chart_type: Type of chart (bar, line, pie, etc.)
        
    Returns:
        dict: Chart data in format expected by frontend
    """
    if not data:
        return {"labels": [], "datasets": []}
    
    # Try to auto-detect appropriate fields for chart
    first_row = data[0]
    
    # Look for common field patterns
    label_fields = ["name", "ledger_name", "customer_name", "party_name", "date", "period"]
    value_fields = ["amount", "balance", "total", "value", "quantity", "closing_balance"]
    
    label_field = None
    value_field = None
    
    for field in label_fields:
        if field in first_row:
            label_field = field
            break
    
    for field in value_fields:
        if field in first_row:
            value_field = field
            break
    
    if not label_field or not value_field:
        # Fall back to first two fields
        fields = list(first_row.keys())
        label_field = fields[0] if len(fields) > 0 else "label"
        value_field = fields[1] if len(fields) > 1 else "value"
    
    labels = [str(row.get(label_field, "")) for row in data]
    values = [float(row.get(value_field, 0)) for row in data]
    
    chart_data = {
        "labels": labels,
        "datasets": [{
            "label": value_field.replace("_", " ").title(),
            "data": values
        }]
    }
    
    # Add chart-specific properties
    if chart_type == "pie":
        chart_data["datasets"][0]["backgroundColor"] = [
            "#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF",
            "#FF9F40", "#FF6384", "#C9CBCF", "#4BC0C0", "#36A2EB"
        ]
    elif chart_type == "line":
        chart_data["datasets"][0]["borderColor"] = "#36A2EB"
        chart_data["datasets"][0]["fill"] = False
    else:  # bar chart
        chart_data["datasets"][0]["backgroundColor"] = "#36A2EB"
    
    return chart_data


def validate_and_clean_data(data: list) -> list:
    """
    Validate and clean data from database queries.
    
    Args:
        data: List of dictionaries from database
        
    Returns:
        list: Cleaned data
    """
    cleaned_data = []
    
    for row in data:
        if not isinstance(row, dict):
            continue
        
        cleaned_row = {}
        for key, value in row.items():
            # Convert None values
            if value is None:
                cleaned_row[key] = ""
            # Convert decimal/float values
            elif isinstance(value, (Decimal, float)):
                cleaned_row[key] = float(value)
            # Convert date objects
            elif isinstance(value, (date, datetime)):
                cleaned_row[key] = value.isoformat()
            # Convert other types to string
            else:
                cleaned_row[key] = str(value)
        
        cleaned_data.append(cleaned_row)
    
    return cleaned_data


def calculate_percentage_change(current: float, previous: float) -> float:
    """
    Calculate percentage change between two values.
    
    Args:
        current: Current value
        previous: Previous value
        
    Returns:
        float: Percentage change
    """
    if previous == 0:
        return 100.0 if current > 0 else 0.0
    
    return ((current - previous) / previous) * 100


def get_financial_year_dates(year: Optional[int] = None) -> Tuple[date, date]:
    """
    Get start and end dates for financial year.
    
    Args:
        year: Financial year (if None, uses current)
        
    Returns:
        tuple: (start_date, end_date)
    """
    if year is None:
        today = date.today()
        if today.month >= 4:  # April onwards
            year = today.year
        else:  # Jan-March
            year = today.year - 1
    
    start_date = date(year, 4, 1)  # April 1st
    end_date = date(year + 1, 3, 31)  # March 31st next year
    
    return start_date, end_date


def truncate_text(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Truncate text to specified length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        str: Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix