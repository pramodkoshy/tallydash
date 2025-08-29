import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date, timedelta
from decimal import Decimal
import time
import pandas as pd

from ..database import TallyDatabase, TallyQueries
from ..models.tally_models import *
from ..config import settings
from ..utils.helpers import cache_result, format_currency


logger = logging.getLogger(__name__)


class TallyService:
    """Service layer for Tally operations."""
    
    def __init__(self):
        self.db = TallyDatabase()
        self.queries = TallyQueries()
    
    def test_connection(self) -> Dict[str, Any]:
        """Test connection to Tally ODBC."""
        try:
            start_time = time.time()
            result = self.db.test_connection()
            response_time = time.time() - start_time
            
            return {
                "success": result,
                "message": "Connection successful" if result else "Connection failed",
                "response_time": response_time
            }
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return {
                "success": False,
                "message": f"Connection error: {str(e)}",
                "response_time": 0
            }
    
    @cache_result(ttl=settings.cache_ttl)
    def get_companies(self) -> TallyDataResponse:
        """Get list of companies from Tally."""
        try:
            start_time = time.time()
            data = self.db.execute_query(self.queries.GET_COMPANIES)
            
            companies = [Company(**row) for row in data]
            query_time = time.time() - start_time
            
            return TallyDataResponse(
                success=True,
                message=f"Retrieved {len(companies)} companies",
                data=[company.dict() for company in companies],
                count=len(companies),
                query_time=query_time
            )
        except Exception as e:
            logger.error(f"Error fetching companies: {e}")
            return TallyDataResponse(
                success=False,
                message=f"Error fetching companies: {str(e)}"
            )
    
    @cache_result(ttl=settings.cache_ttl)
    def get_ledgers(self, group_filter: Optional[str] = None) -> TallyDataResponse:
        """Get ledgers from Tally with optional group filter."""
        try:
            start_time = time.time()
            
            if group_filter:
                data = self.db.execute_query(self.queries.GET_LEDGERS_BY_GROUP, (group_filter,))
            else:
                data = self.db.execute_query(self.queries.GET_ALL_LEDGERS)
            
            ledgers = [Ledger(**row) for row in data]
            query_time = time.time() - start_time
            
            return TallyDataResponse(
                success=True,
                message=f"Retrieved {len(ledgers)} ledgers",
                data=[ledger.dict() for ledger in ledgers],
                count=len(ledgers),
                query_time=query_time
            )
        except Exception as e:
            logger.error(f"Error fetching ledgers: {e}")
            return TallyDataResponse(
                success=False,
                message=f"Error fetching ledgers: {str(e)}"
            )
    
    def get_vouchers(
        self,
        voucher_type: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        limit: Optional[int] = None
    ) -> TallyDataResponse:
        """Get vouchers with optional filters."""
        try:
            start_time = time.time()
            
            # Use database method for filtered vouchers
            data = self.db.get_vouchers(voucher_type, 
                                       date_from.isoformat() if date_from else None,
                                       date_to.isoformat() if date_to else None,
                                       limit)
            
            vouchers = [Voucher(**row) for row in data]
            query_time = time.time() - start_time
            
            return TallyDataResponse(
                success=True,
                message=f"Retrieved {len(vouchers)} vouchers",
                data=[voucher.dict() for voucher in vouchers],
                count=len(vouchers),
                query_time=query_time
            )
        except Exception as e:
            logger.error(f"Error fetching vouchers: {e}")
            return TallyDataResponse(
                success=False,
                message=f"Error fetching vouchers: {str(e)}"
            )
    
    @cache_result(ttl=settings.cache_ttl)
    def get_financial_summary(self) -> Dict[str, Any]:
        """Get financial summary data."""
        try:
            # Get profit & loss data
            pl_data = self.db.execute_query(self.queries.GET_PROFIT_LOSS_DATA)
            
            # Get cash flow data
            receipts = self.db.execute_query(self.queries.GET_CASH_RECEIPTS)
            payments = self.db.execute_query(self.queries.GET_CASH_PAYMENTS)
            
            # Get debtors and creditors
            debtors = self.db.execute_query(self.queries.GET_SUNDRY_DEBTORS)
            creditors = self.db.execute_query(self.queries.GET_SUNDRY_CREDITORS)
            
            # Calculate summary
            summary = FinancialSummary()
            
            # Calculate totals
            summary.total_receipts = sum(Decimal(str(r.get('amount', 0))) for r in receipts)
            summary.total_payments = sum(Decimal(str(p.get('amount', 0))) for p in payments)
            summary.total_debtors = sum(Decimal(str(d.get('outstanding_amount', 0))) for d in debtors)
            summary.total_creditors = sum(Decimal(str(c.get('outstanding_amount', 0))) for c in creditors)
            
            # Calculate revenue and expenses from P&L data
            revenue = sum(Decimal(str(row.get('amount', 0))) for row in pl_data if row.get('is_revenue'))
            expenses = sum(Decimal(str(row.get('amount', 0))) for row in pl_data if row.get('is_expense'))
            
            summary.total_sales = revenue
            summary.net_profit = revenue - expenses
            summary.cash_balance = summary.total_receipts - summary.total_payments
            
            return {
                "success": True,
                "data": summary.dict(),
                "message": "Financial summary calculated successfully"
            }
            
        except Exception as e:
            logger.error(f"Error calculating financial summary: {e}")
            return {
                "success": False,
                "message": f"Error calculating financial summary: {str(e)}"
            }
    
    def get_top_customers(self, limit: int = 10) -> TallyDataResponse:
        """Get top customers by sales amount."""
        try:
            start_time = time.time()
            query = self.queries.get_top_customers_query(limit)
            data = self.db.execute_query(query)
            query_time = time.time() - start_time
            
            return TallyDataResponse(
                success=True,
                message=f"Retrieved top {len(data)} customers",
                data=data,
                count=len(data),
                query_time=query_time
            )
        except Exception as e:
            logger.error(f"Error fetching top customers: {e}")
            return TallyDataResponse(
                success=False,
                message=f"Error fetching top customers: {str(e)}"
            )
    
    def get_monthly_sales_trend(self, months: int = 12) -> Dict[str, Any]:
        """Get monthly sales trend data."""
        try:
            data = self.db.execute_query(self.queries.GET_MONTHLY_SALES_SUMMARY)
            
            # Convert to pandas for easier manipulation
            df = pd.DataFrame(data)
            if df.empty:
                return {"success": False, "message": "No sales data found"}
            
            # Sort by year and month
            df = df.sort_values(['year', 'month']).tail(months)
            
            # Create period labels
            df['period'] = df['year'].astype(str) + '-' + df['month'].astype(str).str.zfill(2)
            
            chart_data = {
                "labels": df['period'].tolist(),
                "sales": df['total_sales'].tolist(),
                "voucher_counts": df['voucher_count'].tolist()
            }
            
            return {
                "success": True,
                "data": chart_data,
                "message": f"Retrieved {len(df)} months of sales data"
            }
            
        except Exception as e:
            logger.error(f"Error fetching sales trend: {e}")
            return {
                "success": False,
                "message": f"Error fetching sales trend: {str(e)}"
            }
    
    def get_cash_flow_analysis(self, days: int = 30) -> Dict[str, Any]:
        """Get cash flow analysis for specified days."""
        try:
            data = self.db.execute_query(self.queries.GET_DAILY_CASH_FLOW)
            
            # Convert to pandas
            df = pd.DataFrame(data)
            if df.empty:
                return {"success": False, "message": "No cash flow data found"}
            
            # Convert date column and sort
            df['voucher_date'] = pd.to_datetime(df['voucher_date'])
            df = df.sort_values('voucher_date').tail(days)
            
            chart_data = {
                "dates": df['voucher_date'].dt.strftime('%Y-%m-%d').tolist(),
                "cash_in": df['cash_in'].tolist(),
                "cash_out": df['cash_out'].tolist(),
                "net_flow": df['net_cash_flow'].tolist()
            }
            
            # Calculate summary
            summary = {
                "total_inflow": float(df['cash_in'].sum()),
                "total_outflow": float(df['cash_out'].sum()),
                "net_flow": float(df['net_cash_flow'].sum()),
                "average_daily_flow": float(df['net_cash_flow'].mean())
            }
            
            return {
                "success": True,
                "data": chart_data,
                "summary": summary,
                "message": f"Retrieved {days} days of cash flow data"
            }
            
        except Exception as e:
            logger.error(f"Error fetching cash flow analysis: {e}")
            return {
                "success": False,
                "message": f"Error fetching cash flow analysis: {str(e)}"
            }
    
    def get_expense_analysis(self) -> Dict[str, Any]:
        """Get expense analysis by category."""
        try:
            query = self.queries.get_expense_analysis_query()
            data = self.db.execute_query(query)
            
            # Group by expense category
            expenses_by_category = {}
            total_expenses = Decimal('0')
            
            for row in data:
                category = row.get('expense_category', 'Other')
                amount = Decimal(str(row.get('amount', 0)))
                
                if category not in expenses_by_category:
                    expenses_by_category[category] = {
                        "total": Decimal('0'),
                        "accounts": []
                    }
                
                expenses_by_category[category]["total"] += amount
                expenses_by_category[category]["accounts"].append({
                    "name": row.get('account_name'),
                    "amount": float(amount)
                })
                total_expenses += amount
            
            # Convert to chart-friendly format
            chart_data = {
                "categories": list(expenses_by_category.keys()),
                "amounts": [float(cat_data["total"]) for cat_data in expenses_by_category.values()],
                "percentages": [float(cat_data["total"] / total_expenses * 100) 
                             for cat_data in expenses_by_category.values()]
            }
            
            return {
                "success": True,
                "data": chart_data,
                "details": {k: {"total": float(v["total"]), "accounts": v["accounts"]} 
                          for k, v in expenses_by_category.items()},
                "total": float(total_expenses),
                "message": f"Analyzed {len(expenses_by_category)} expense categories"
            }
            
        except Exception as e:
            logger.error(f"Error in expense analysis: {e}")
            return {
                "success": False,
                "message": f"Error in expense analysis: {str(e)}"
            }
    
    def execute_custom_query(self, query: str, params: Optional[tuple] = None) -> TallyDataResponse:
        """Execute a custom SQL query (with security validation)."""
        try:
            start_time = time.time()
            data = self.db.execute_query(query, params)
            query_time = time.time() - start_time
            
            return TallyDataResponse(
                success=True,
                message=f"Query executed successfully, returned {len(data)} rows",
                data=data,
                count=len(data),
                query_time=query_time
            )
        except Exception as e:
            logger.error(f"Error executing custom query: {e}")
            return TallyDataResponse(
                success=False,
                message=f"Query execution failed: {str(e)}"
            )
    
    def get_dashboard_data(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get comprehensive dashboard data."""
        try:
            dashboard_data = {}
            
            # Get financial summary
            financial_summary = self.get_financial_summary()
            dashboard_data["financial_summary"] = financial_summary
            
            # Get recent vouchers (last 10)
            recent_vouchers = self.get_vouchers(limit=10)
            dashboard_data["recent_vouchers"] = recent_vouchers.data if recent_vouchers.success else []
            
            # Get top customers
            top_customers = self.get_top_customers(limit=5)
            dashboard_data["top_customers"] = top_customers.data if top_customers.success else []
            
            # Get sales trend
            sales_trend = self.get_monthly_sales_trend(months=6)
            dashboard_data["sales_trend"] = sales_trend.get("data", {})
            
            # Get cash flow
            cash_flow = self.get_cash_flow_analysis(days=30)
            dashboard_data["cash_flow"] = cash_flow.get("data", {})
            
            # Get expense analysis
            expense_analysis = self.get_expense_analysis()
            dashboard_data["expense_analysis"] = expense_analysis.get("data", {})
            
            return {
                "success": True,
                "data": dashboard_data,
                "last_updated": datetime.now().isoformat(),
                "message": "Dashboard data retrieved successfully"
            }
            
        except Exception as e:
            logger.error(f"Error fetching dashboard data: {e}")
            return {
                "success": False,
                "message": f"Error fetching dashboard data: {str(e)}"
            }