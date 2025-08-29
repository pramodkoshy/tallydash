import logging
import json
import re
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, date
import openai
from anthropic import Anthropic

from ..config import settings
from ..models.app_models import QueryRequest, QueryResponse, ChartData, ChartType
from ..models.tally_models import TallyDataResponse
from .tally_service import TallyService
from ..utils.helpers import extract_date_range, parse_natural_language_query


logger = logging.getLogger(__name__)


class AIService:
    """Service for AI-powered natural language interactions with Tally data."""
    
    def __init__(self):
        self.tally_service = TallyService()
        
        # Initialize AI clients
        if settings.openai_api_key:
            openai.api_key = settings.openai_api_key
            self.openai_client = openai
        else:
            self.openai_client = None
            
        if settings.anthropic_api_key:
            self.anthropic_client = Anthropic(api_key=settings.anthropic_api_key)
        else:
            self.anthropic_client = None
            
        # Query patterns for natural language understanding
        self.query_patterns = {
            "sales": ["sales", "revenue", "income", "turnover"],
            "expenses": ["expenses", "costs", "expenditure", "spending"],
            "profit": ["profit", "loss", "earnings", "net income"],
            "cash_flow": ["cash flow", "receipts", "payments", "cash"],
            "customers": ["customers", "debtors", "parties", "clients"],
            "suppliers": ["suppliers", "creditors", "vendors"],
            "vouchers": ["vouchers", "transactions", "entries"],
            "ledgers": ["ledgers", "accounts", "balances"],
            "reports": ["report", "statement", "summary", "analysis"]
        }
    
    def process_natural_language_query(self, request: QueryRequest) -> QueryResponse:
        """Process a natural language query and return structured response."""
        try:
            query_text = request.query_text.lower().strip()
            logger.info(f"Processing NL query: {query_text}")
            
            # First, try to understand the intent using pattern matching
            intent, entities = self._extract_intent_and_entities(query_text)
            
            if not intent:
                # Fall back to AI-powered understanding if available
                if self.openai_client or self.anthropic_client:
                    return self._ai_powered_query(request)
                else:
                    return QueryResponse(
                        success=False,
                        message="Could not understand the query. Please be more specific."
                    )
            
            # Execute the query based on intent
            return self._execute_intent_based_query(intent, entities, request)
            
        except Exception as e:
            logger.error(f"Error processing natural language query: {e}")
            return QueryResponse(
                success=False,
                message=f"Error processing query: {str(e)}"
            )
    
    def _extract_intent_and_entities(self, query_text: str) -> Tuple[Optional[str], Dict[str, Any]]:
        """Extract intent and entities from natural language query."""
        entities = {}
        intent = None
        
        # Extract date ranges
        date_range = extract_date_range(query_text)
        if date_range:
            entities["date_from"], entities["date_to"] = date_range
        
        # Extract numbers (amounts, limits)
        numbers = re.findall(r'\d+(?:,\d{3})*(?:\.\d{2})?', query_text)
        if numbers:
            entities["numbers"] = [float(num.replace(',', '')) for num in numbers]
        
        # Detect intent based on patterns
        for pattern_intent, keywords in self.query_patterns.items():
            if any(keyword in query_text for keyword in keywords):
                intent = pattern_intent
                break
        
        # Extract specific entities based on intent
        if intent == "customers":
            entities["limit"] = self._extract_limit(query_text)
            entities["sort_by"] = "sales" if "sales" in query_text else "balance"
        elif intent == "vouchers":
            entities["voucher_type"] = self._extract_voucher_type(query_text)
            entities["limit"] = self._extract_limit(query_text)
        elif intent == "ledgers":
            entities["group"] = self._extract_ledger_group(query_text)
            entities["balance_filter"] = self._extract_balance_filter(query_text)
        
        return intent, entities
    
    def _extract_limit(self, query_text: str) -> Optional[int]:
        """Extract limit/top N from query."""
        patterns = [
            r"top\s+(\d+)",
            r"first\s+(\d+)",
            r"limit\s+(\d+)",
            r"(\d+)\s+(?:customers|suppliers|ledgers|vouchers)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query_text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        return None
    
    def _extract_voucher_type(self, query_text: str) -> Optional[str]:
        """Extract voucher type from query."""
        voucher_types = {
            "sales": "Sales",
            "purchase": "Purchase",
            "payment": "Payment",
            "receipt": "Receipt",
            "journal": "Journal",
            "contra": "Contra"
        }
        
        for keyword, voucher_type in voucher_types.items():
            if keyword in query_text:
                return voucher_type
        return None
    
    def _extract_ledger_group(self, query_text: str) -> Optional[str]:
        """Extract ledger group from query."""
        groups = [
            "sundry debtors", "sundry creditors", "bank accounts", 
            "cash-in-hand", "sales accounts", "purchase accounts",
            "expenses", "assets", "liabilities"
        ]
        
        for group in groups:
            if group in query_text:
                return group.title()
        return None
    
    def _extract_balance_filter(self, query_text: str) -> Optional[Dict[str, Any]]:
        """Extract balance filter conditions."""
        filter_conditions = {}
        
        # Extract balance comparisons
        patterns = [
            (r"above\s+(\d+(?:,\d{3})*(?:\.\d{2})?)", ">"),
            (r"below\s+(\d+(?:,\d{3})*(?:\.\d{2})?)", "<"),
            (r"greater\s+than\s+(\d+(?:,\d{3})*(?:\.\d{2})?)", ">"),
            (r"less\s+than\s+(\d+(?:,\d{3})*(?:\.\d{2})?)", "<"),
        ]
        
        for pattern, operator in patterns:
            match = re.search(pattern, query_text, re.IGNORECASE)
            if match:
                amount = float(match.group(1).replace(',', ''))
                filter_conditions = {"operator": operator, "amount": amount}
                break
        
        return filter_conditions if filter_conditions else None
    
    def _execute_intent_based_query(
        self, 
        intent: str, 
        entities: Dict[str, Any], 
        request: QueryRequest
    ) -> QueryResponse:
        """Execute query based on extracted intent and entities."""
        try:
            if intent == "sales":
                return self._handle_sales_query(entities, request)
            elif intent == "expenses":
                return self._handle_expenses_query(entities, request)
            elif intent == "profit":
                return self._handle_profit_query(entities, request)
            elif intent == "cash_flow":
                return self._handle_cash_flow_query(entities, request)
            elif intent == "customers":
                return self._handle_customers_query(entities, request)
            elif intent == "vouchers":
                return self._handle_vouchers_query(entities, request)
            elif intent == "ledgers":
                return self._handle_ledgers_query(entities, request)
            elif intent == "reports":
                return self._handle_reports_query(entities, request)
            else:
                return QueryResponse(
                    success=False,
                    message=f"Intent '{intent}' not yet implemented"
                )
                
        except Exception as e:
            logger.error(f"Error executing intent-based query: {e}")
            return QueryResponse(
                success=False,
                message=f"Error executing query: {str(e)}"
            )
    
    def _handle_sales_query(self, entities: Dict[str, Any], request: QueryRequest) -> QueryResponse:
        """Handle sales-related queries."""
        date_from = entities.get("date_from")
        date_to = entities.get("date_to")
        
        # Get sales vouchers
        response = self.tally_service.get_vouchers(
            voucher_type="Sales",
            date_from=date_from,
            date_to=date_to,
            limit=entities.get("limit", 100)
        )
        
        if not response.success:
            return QueryResponse(success=False, message=response.message)
        
        # Calculate totals
        total_sales = sum(float(v.get('amount', 0)) for v in response.data)
        voucher_count = len(response.data)
        
        # Create chart data
        chart_data = self._create_sales_chart(response.data)
        
        return QueryResponse(
            success=True,
            message=f"Found {voucher_count} sales transactions totaling ₹{total_sales:,.2f}",
            data={
                "vouchers": response.data,
                "summary": {
                    "total_sales": total_sales,
                    "voucher_count": voucher_count,
                    "average_sale": total_sales / voucher_count if voucher_count > 0 else 0
                }
            },
            chart_data=chart_data,
            execution_time=response.query_time
        )
    
    def _handle_customers_query(self, entities: Dict[str, Any], request: QueryRequest) -> QueryResponse:
        """Handle customer-related queries."""
        limit = entities.get("limit", 10)
        
        response = self.tally_service.get_top_customers(limit=limit)
        
        if not response.success:
            return QueryResponse(success=False, message=response.message)
        
        # Create chart data for top customers
        chart_data = ChartData(
            chart_type=ChartType.BAR,
            title=f"Top {limit} Customers by Sales",
            data={
                "labels": [c["customer_name"] for c in response.data],
                "datasets": [{
                    "label": "Sales Amount",
                    "data": [float(c["total_sales"]) for c in response.data]
                }]
            }
        )
        
        return QueryResponse(
            success=True,
            message=f"Retrieved top {len(response.data)} customers",
            data=response.data,
            chart_data=chart_data,
            execution_time=response.query_time
        )
    
    def _handle_cash_flow_query(self, entities: Dict[str, Any], request: QueryRequest) -> QueryResponse:
        """Handle cash flow queries."""
        days = entities.get("numbers", [30])[0] if entities.get("numbers") else 30
        
        response = self.tally_service.get_cash_flow_analysis(days=int(days))
        
        if not response["success"]:
            return QueryResponse(success=False, message=response["message"])
        
        # Create cash flow chart
        chart_data = ChartData(
            chart_type=ChartType.LINE,
            title=f"Cash Flow - Last {days} Days",
            data={
                "labels": response["data"]["dates"],
                "datasets": [
                    {
                        "label": "Cash In",
                        "data": response["data"]["cash_in"],
                        "borderColor": "green"
                    },
                    {
                        "label": "Cash Out", 
                        "data": response["data"]["cash_out"],
                        "borderColor": "red"
                    },
                    {
                        "label": "Net Flow",
                        "data": response["data"]["net_flow"],
                        "borderColor": "blue"
                    }
                ]
            }
        )
        
        return QueryResponse(
            success=True,
            message=f"Cash flow analysis for {days} days",
            data=response["data"],
            chart_data=chart_data
        )
    
    def _handle_expenses_query(self, entities: Dict[str, Any], request: QueryRequest) -> QueryResponse:
        """Handle expense-related queries."""
        response = self.tally_service.get_expense_analysis()
        
        if not response["success"]:
            return QueryResponse(success=False, message=response["message"])
        
        # Create expense pie chart
        chart_data = ChartData(
            chart_type=ChartType.PIE,
            title="Expenses by Category",
            data={
                "labels": response["data"]["categories"],
                "datasets": [{
                    "data": response["data"]["amounts"],
                    "backgroundColor": [
                        "#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0",
                        "#9966FF", "#FF9F40", "#FF6384", "#C9CBCF"
                    ]
                }]
            }
        )
        
        return QueryResponse(
            success=True,
            message=f"Expense analysis across {len(response['data']['categories'])} categories",
            data=response["data"],
            chart_data=chart_data
        )
    
    def _handle_vouchers_query(self, entities: Dict[str, Any], request: QueryRequest) -> QueryResponse:
        """Handle voucher-related queries."""
        response = self.tally_service.get_vouchers(
            voucher_type=entities.get("voucher_type"),
            date_from=entities.get("date_from"),
            date_to=entities.get("date_to"),
            limit=entities.get("limit", 50)
        )
        
        return QueryResponse(
            success=response.success,
            message=response.message,
            data=response.data,
            execution_time=response.query_time
        )
    
    def _handle_ledgers_query(self, entities: Dict[str, Any], request: QueryRequest) -> QueryResponse:
        """Handle ledger-related queries."""
        response = self.tally_service.get_ledgers(group_filter=entities.get("group"))
        
        # Apply balance filter if specified
        if entities.get("balance_filter") and response.success:
            balance_filter = entities["balance_filter"]
            filtered_data = []
            
            for ledger in response.data:
                balance = float(ledger.get("closing_balance", 0))
                if balance_filter["operator"] == ">" and balance > balance_filter["amount"]:
                    filtered_data.append(ledger)
                elif balance_filter["operator"] == "<" and balance < balance_filter["amount"]:
                    filtered_data.append(ledger)
            
            response.data = filtered_data
            response.count = len(filtered_data)
        
        return QueryResponse(
            success=response.success,
            message=f"Retrieved {response.count} ledgers",
            data=response.data,
            execution_time=response.query_time
        )
    
    def _handle_profit_query(self, entities: Dict[str, Any], request: QueryRequest) -> QueryResponse:
        """Handle profit/loss queries."""
        financial_summary = self.tally_service.get_financial_summary()
        
        if not financial_summary["success"]:
            return QueryResponse(success=False, message=financial_summary["message"])
        
        data = financial_summary["data"]
        
        return QueryResponse(
            success=True,
            message="Financial summary retrieved",
            data=data
        )
    
    def _handle_reports_query(self, entities: Dict[str, Any], request: QueryRequest) -> QueryResponse:
        """Handle report generation queries."""
        dashboard_data = self.tally_service.get_dashboard_data()
        
        return QueryResponse(
            success=dashboard_data["success"],
            message="Comprehensive report generated",
            data=dashboard_data.get("data", {})
        )
    
    def _create_sales_chart(self, sales_data: List[Dict[str, Any]]) -> ChartData:
        """Create chart data for sales visualization."""
        # Group by date for daily sales chart
        daily_sales = {}
        for voucher in sales_data:
            date_key = voucher.get("voucher_date", "Unknown")
            amount = float(voucher.get("amount", 0))
            
            if date_key in daily_sales:
                daily_sales[date_key] += amount
            else:
                daily_sales[date_key] = amount
        
        # Sort by date
        sorted_dates = sorted(daily_sales.keys())
        
        return ChartData(
            chart_type=ChartType.BAR,
            title="Daily Sales",
            data={
                "labels": sorted_dates,
                "datasets": [{
                    "label": "Sales Amount",
                    "data": [daily_sales[date] for date in sorted_dates],
                    "backgroundColor": "#36A2EB"
                }]
            }
        )
    
    def _ai_powered_query(self, request: QueryRequest) -> QueryResponse:
        """Use AI models for complex query understanding."""
        try:
            # Create context about available data
            context = self._build_context()
            
            # Create prompt for AI
            prompt = self._build_ai_prompt(request.query_text, context)
            
            # Try OpenAI first, then Anthropic
            if self.openai_client:
                response = self._query_openai(prompt)
            elif self.anthropic_client:
                response = self._query_anthropic(prompt)
            else:
                return QueryResponse(
                    success=False,
                    message="No AI service configured"
                )
            
            # Parse AI response and execute query
            return self._parse_ai_response(response, request)
            
        except Exception as e:
            logger.error(f"Error in AI-powered query: {e}")
            return QueryResponse(
                success=False,
                message=f"AI query failed: {str(e)}"
            )
    
    def _build_context(self) -> str:
        """Build context about available Tally data for AI."""
        return """
        Available Tally data includes:
        - Companies: Name, financial year, currency
        - Ledgers: Name, parent group, opening/closing balance, type (asset/liability/income/expense)
        - Vouchers: Date, number, type (Sales/Purchase/Payment/Receipt/Journal), amount, party name
        - Stock Items: Name, group, quantity, value, unit
        
        Common operations:
        - Get financial summary (sales, expenses, profit/loss, cash flow)
        - Analyze top customers/suppliers
        - Generate reports and charts
        - Filter by date ranges, amounts, types
        """
    
    def _build_ai_prompt(self, query: str, context: str) -> str:
        """Build prompt for AI query understanding."""
        return f"""
        {context}
        
        User Query: "{query}"
        
        Based on the user's query, determine:
        1. Intent (sales, expenses, customers, vouchers, reports, etc.)
        2. Entities (dates, amounts, filters, limits)
        3. Required data sources
        4. Appropriate chart type if visualization is needed
        
        Respond with JSON format:
        {{
            "intent": "intent_name",
            "entities": {{"key": "value"}},
            "data_sources": ["source1", "source2"],
            "chart_type": "bar/line/pie/none",
            "sql_hints": "any specific query requirements"
        }}
        """
    
    def _query_openai(self, prompt: str) -> str:
        """Query OpenAI API."""
        response = self.openai_client.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.1
        )
        return response.choices[0].message.content
    
    def _query_anthropic(self, prompt: str) -> str:
        """Query Anthropic API."""
        response = self.anthropic_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    
    def _parse_ai_response(self, ai_response: str, request: QueryRequest) -> QueryResponse:
        """Parse AI response and execute appropriate query."""
        try:
            # Try to parse JSON response
            parsed = json.loads(ai_response)
            
            intent = parsed.get("intent")
            entities = parsed.get("entities", {})
            
            # Convert string dates to date objects if present
            for key in ["date_from", "date_to"]:
                if key in entities and isinstance(entities[key], str):
                    try:
                        entities[key] = datetime.strptime(entities[key], "%Y-%m-%d").date()
                    except ValueError:
                        pass  # Keep as string if parsing fails
            
            # Execute based on parsed intent
            return self._execute_intent_based_query(intent, entities, request)
            
        except json.JSONDecodeError:
            logger.error("Failed to parse AI response as JSON")
            return QueryResponse(
                success=False,
                message="Could not understand the query. Please try rephrasing."
            )
        except Exception as e:
            logger.error(f"Error parsing AI response: {e}")
            return QueryResponse(
                success=False,
                message=f"Error processing AI response: {str(e)}"
            )