# API Reference

This document provides comprehensive API reference for TallyDash services and endpoints.

## Table of Contents

- [Authentication](#authentication)
- [Data Models](#data-models)
- [TallyService API](#tallyservice-api)
- [AIService API](#aiservice-api)
- [REST Endpoints](#rest-endpoints)
- [WebSocket Events](#websocket-events)
- [Error Handling](#error-handling)

## Authentication

TallyDash uses session-based authentication for web interface and API key authentication for programmatic access.

### Session Authentication
```python
# Used automatically in web interface
# Sessions are managed by Reflex framework
```

### API Key Authentication
```python
# For programmatic access (future feature)
headers = {
    "Authorization": "Bearer your-api-key",
    "Content-Type": "application/json"
}
```

## Data Models

### Core Models

#### Company
```python
class Company(BaseModel):
    company_name: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    currency: Optional[str] = None
```

#### Ledger  
```python
class Ledger(BaseModel):
    ledger_name: str
    parent: Optional[str] = None
    opening_balance: Optional[Decimal] = None
    closing_balance: Optional[Decimal] = None
    is_revenue: Optional[bool] = None
    is_expense: Optional[bool] = None
    is_asset: Optional[bool] = None
    is_liability: Optional[bool] = None
    is_debit: Optional[bool] = None
```

#### Voucher
```python
class Voucher(BaseModel):
    voucher_date: date
    voucher_number: str
    voucher_type: VoucherType  # Enum: Sales, Purchase, Payment, Receipt, Journal, Contra
    amount: Optional[Decimal] = None
    reference: Optional[str] = None
    narration: Optional[str] = None
    party_name: Optional[str] = None
    entries: Optional[List[VoucherEntry]] = None
```

#### VoucherEntry
```python
class VoucherEntry(BaseModel):
    ledger_name: str
    amount: Decimal
    is_debit: bool
```

#### StockItem
```python
class StockItem(BaseModel):
    item_name: str
    group_name: Optional[str] = None
    closing_stock: Optional[Decimal] = None
    closing_value: Optional[Decimal] = None
    unit: Optional[str] = None
```

### Response Models

#### TallyDataResponse
```python
class TallyDataResponse(BaseModel):
    success: bool
    message: str = ""
    data: Union[List[Dict[str, Any]], Dict[str, Any], None] = None
    count: Optional[int] = None
    query_time: Optional[float] = None
```

#### QueryResponse
```python
class QueryResponse(BaseModel):
    success: bool
    message: str = ""
    data: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None
    chart_data: Optional[ChartData] = None
    sql_query: Optional[str] = None
    execution_time: Optional[float] = None
```

## TallyService API

### Connection Management

#### `test_connection()`
Test ODBC connection to Tally.

**Returns:**
```python
{
    "success": bool,
    "message": str,
    "response_time": float
}
```

**Example:**
```python
from tallydash.services import TallyService

service = TallyService()
result = service.test_connection()
print(result)  # {"success": True, "message": "Connection successful", "response_time": 0.123}
```

### Company Operations

#### `get_companies()`
Retrieve list of companies from Tally.

**Returns:** `TallyDataResponse`

**Example:**
```python
response = service.get_companies()
if response.success:
    for company in response.data:
        print(f"Company: {company['company_name']}")
```

### Ledger Operations

#### `get_ledgers(group_filter: Optional[str] = None)`
Retrieve ledgers with optional group filtering.

**Parameters:**
- `group_filter` (str, optional): Filter by parent group name

**Returns:** `TallyDataResponse`

**Example:**
```python
# Get all ledgers
response = service.get_ledgers()

# Get ledgers by group
response = service.get_ledgers(group_filter="Sundry Debtors")
```

### Voucher Operations

#### `get_vouchers(voucher_type, date_from, date_to, limit)`
Retrieve vouchers with filtering options.

**Parameters:**
- `voucher_type` (str, optional): Filter by voucher type (Sales, Purchase, etc.)
- `date_from` (date, optional): Start date filter
- `date_to` (date, optional): End date filter  
- `limit` (int, optional): Maximum number of results

**Returns:** `TallyDataResponse`

**Example:**
```python
from datetime import date

# Get sales vouchers for current month
response = service.get_vouchers(
    voucher_type="Sales",
    date_from=date(2024, 1, 1),
    date_to=date(2024, 1, 31),
    limit=100
)
```

### Financial Analysis

#### `get_financial_summary()`
Get comprehensive financial summary.

**Returns:**
```python
{
    "success": bool,
    "data": {
        "total_sales": Decimal,
        "total_purchases": Decimal,
        "total_receipts": Decimal,
        "total_payments": Decimal,
        "net_profit": Decimal,
        "total_debtors": Decimal,
        "total_creditors": Decimal,
        "cash_balance": Decimal
    },
    "message": str
}
```

#### `get_top_customers(limit: int = 10)`
Get top customers by sales amount.

**Parameters:**
- `limit` (int): Number of customers to return

**Returns:** `TallyDataResponse`

#### `get_monthly_sales_trend(months: int = 12)`
Get monthly sales trend data.

**Parameters:**
- `months` (int): Number of months to analyze

**Returns:**
```python
{
    "success": bool,
    "data": {
        "labels": List[str],  # Period labels
        "sales": List[float],  # Sales amounts
        "voucher_counts": List[int]  # Number of vouchers
    }
}
```

#### `get_cash_flow_analysis(days: int = 30)`
Analyze cash flow for specified period.

**Parameters:**
- `days` (int): Number of days to analyze

**Returns:**
```python
{
    "success": bool,
    "data": {
        "dates": List[str],
        "cash_in": List[float],
        "cash_out": List[float], 
        "net_flow": List[float]
    },
    "summary": {
        "total_inflow": float,
        "total_outflow": float,
        "net_flow": float,
        "average_daily_flow": float
    }
}
```

#### `get_expense_analysis()`
Analyze expenses by category.

**Returns:**
```python
{
    "success": bool,
    "data": {
        "categories": List[str],
        "amounts": List[float],
        "percentages": List[float]
    },
    "details": Dict[str, Dict],
    "total": float
}
```

#### `execute_custom_query(query: str, params: Optional[tuple] = None)`
Execute custom SQL query with security validation.

**Parameters:**
- `query` (str): SQL query string
- `params` (tuple, optional): Query parameters

**Returns:** `TallyDataResponse`

**Example:**
```python
# Custom query with parameters
query = "SELECT $Name, $ClosingBalance FROM Ledger WHERE $Parent = ?"
response = service.execute_custom_query(query, ("Sundry Debtors",))
```

## AIService API

### Natural Language Processing

#### `process_natural_language_query(request: QueryRequest)`
Process natural language query and return structured response.

**Parameters:**
- `request` (QueryRequest): Query request object

**QueryRequest Model:**
```python
class QueryRequest(BaseModel):
    query_text: str
    context: Optional[Dict[str, Any]] = None
    filters: Optional[DashboardFilter] = None
```

**Returns:** `QueryResponse`

**Example:**
```python
from tallydash.services import AIService
from tallydash.models.app_models import QueryRequest

ai_service = AIService()

request = QueryRequest(
    query_text="Show me sales for this month",
    context={"company": "ABC Corp"},
    filters=None
)

response = ai_service.process_natural_language_query(request)
if response.success:
    print(response.message)
    print(response.data)
```

### Supported Query Types

The AI service can understand and process various types of queries:

#### Sales Queries
- "Show me sales for this month"
- "What are the total sales for Q1?"
- "Sales trend for last 6 months"

#### Customer Queries  
- "Top 5 customers by revenue"
- "Customer with highest outstanding balance"
- "New customers this month"

#### Expense Queries
- "Break down expenses by category"
- "Monthly expense comparison"
- "Highest expense categories"

#### Cash Flow Queries
- "Cash flow for last 30 days"
- "Daily cash position"
- "Receipts vs payments analysis"

#### Voucher Queries
- "Recent sales transactions"
- "Purchase vouchers for supplier X"
- "Journal entries this week"

## REST Endpoints

### Base URL
```
http://localhost:8000/api/v1
```

### Endpoints

#### GET `/companies`
Get list of companies.

**Response:**
```json
{
    "success": true,
    "data": [
        {
            "company_name": "ABC Corp",
            "currency": "INR",
            "start_date": "2024-04-01",
            "end_date": "2025-03-31"
        }
    ],
    "count": 1
}
```

#### GET `/ledgers`
Get ledgers with optional filtering.

**Query Parameters:**
- `group` (string, optional): Filter by group
- `limit` (integer, optional): Limit results

**Response:**
```json
{
    "success": true,
    "data": [
        {
            "ledger_name": "Cash",
            "parent": "Cash-in-Hand",
            "closing_balance": 50000.00
        }
    ]
}
```

#### GET `/vouchers`
Get vouchers with filtering.

**Query Parameters:**
- `type` (string, optional): Voucher type
- `date_from` (string, optional): Start date (YYYY-MM-DD)
- `date_to` (string, optional): End date (YYYY-MM-DD)
- `limit` (integer, optional): Limit results

#### POST `/ai-query`
Process natural language query.

**Request Body:**
```json
{
    "query_text": "Show me top customers",
    "context": {
        "company": "ABC Corp"
    },
    "filters": {
        "date_from": "2024-01-01",
        "date_to": "2024-01-31"
    }
}
```

**Response:**
```json
{
    "success": true,
    "message": "Retrieved top 5 customers",
    "data": [...],
    "chart_data": {
        "chart_type": "bar",
        "title": "Top Customers",
        "data": {...}
    }
}
```

#### GET `/financial-summary`
Get financial summary data.

**Response:**
```json
{
    "success": true,
    "data": {
        "total_sales": 500000.00,
        "total_expenses": 300000.00,
        "net_profit": 200000.00,
        "cash_balance": 150000.00
    }
}
```

## WebSocket Events

### Connection
```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8000/ws');
```

### Events

#### `data_updated`
Triggered when Tally data is updated.

**Payload:**
```json
{
    "event": "data_updated",
    "data": {
        "type": "voucher",
        "action": "created",
        "id": "SLS001"
    }
}
```

#### `ai_response`
AI query response via WebSocket.

**Payload:**
```json
{
    "event": "ai_response",
    "data": {
        "query_id": "12345",
        "response": {...}
    }
}
```

## Error Handling

### Error Response Format
```json
{
    "success": false,
    "message": "Error description",
    "error_code": "TALLY_CONNECTION_FAILED",
    "details": {
        "timestamp": "2024-01-15T10:30:00Z",
        "request_id": "req_12345"
    }
}
```

### Common Error Codes

| Code | Description | Solution |
|------|-------------|----------|
| `TALLY_CONNECTION_FAILED` | Cannot connect to Tally ODBC | Check Tally ODBC configuration |
| `INVALID_QUERY` | SQL query validation failed | Review query syntax |
| `PERMISSION_DENIED` | Insufficient permissions | Check user access rights |
| `RATE_LIMIT_EXCEEDED` | Too many requests | Reduce request frequency |
| `AI_SERVICE_UNAVAILABLE` | AI service not responding | Check API keys and connectivity |

### Error Handling Best Practices

```python
# Service layer error handling
try:
    response = service.get_companies()
    if response.success:
        # Process data
        pass
    else:
        # Handle business logic error
        logger.warning(f"Service error: {response.message}")
except Exception as e:
    # Handle unexpected errors
    logger.error(f"Unexpected error: {e}")
```

## Rate Limiting

### Default Limits
- **API Requests**: 100 per minute per IP
- **AI Queries**: 10 per minute per session
- **Database Queries**: 50 per minute per connection

### Custom Limits
Configure in environment:
```env
RATE_LIMIT_REQUESTS=200
RATE_LIMIT_AI_QUERIES=20
RATE_LIMIT_DB_QUERIES=100
```

## Caching

### Cache Configuration
```python
# Cache TTL settings
CACHE_TTL_COMPANIES = 3600  # 1 hour
CACHE_TTL_LEDGERS = 300     # 5 minutes  
CACHE_TTL_VOUCHERS = 60     # 1 minute
```

### Cache Keys Format
```
tallydash:companies:{hash}
tallydash:ledgers:{group}:{hash}
tallydash:vouchers:{type}:{date_range}:{hash}
```

## Pagination

### Request Parameters
```python
# Query parameters
{
    "page": 1,
    "page_size": 50,
    "sort_by": "voucher_date",
    "sort_order": "desc"
}
```

### Response Format
```json
{
    "success": true,
    "data": [...],
    "pagination": {
        "page": 1,
        "page_size": 50,
        "total_records": 1250,
        "total_pages": 25,
        "has_next": true,
        "has_previous": false
    }
}
```

## SDK Usage Examples

### Python SDK
```python
from tallydash import TallyDashClient

# Initialize client
client = TallyDashClient(
    host="localhost",
    port=8000,
    api_key="your-api-key"
)

# Get companies
companies = client.companies.list()

# Natural language query
result = client.ai.query("Show me monthly sales")

# Custom query
data = client.query.execute(
    "SELECT $Name, $ClosingBalance FROM Ledger"
)
```

### JavaScript SDK (Future)
```javascript
import TallyDash from 'tallydash-js';

const client = new TallyDash({
    baseURL: 'http://localhost:8000',
    apiKey: 'your-api-key'
});

// Get ledgers
const ledgers = await client.ledgers.list();

// AI query
const result = await client.ai.query('Top customers this month');
```

---

**For more examples and advanced usage, see the [User Guide](USER_GUIDE.md) and [Examples](../examples/) directory.**