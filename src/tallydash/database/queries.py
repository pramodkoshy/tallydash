from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta


class TallyQueries:
    """Pre-built SQL queries for Tally ODBC operations."""
    
    # Company Queries
    GET_COMPANIES = """
        SELECT 
            $Name as company_name,
            $StartOfBooks as start_date,
            $EndOfBooks as end_date,
            $Currency as currency
        FROM Company
        ORDER BY $Name
    """
    
    # Ledger Queries
    GET_ALL_LEDGERS = """
        SELECT 
            $Name as ledger_name,
            $Parent as parent,
            $OpeningBalance as opening_balance,
            $ClosingBalance as closing_balance,
            $IsRevenue as is_revenue,
            $IsDebitBalance as is_debit
        FROM Ledger
        ORDER BY $Name
    """
    
    GET_LEDGERS_BY_GROUP = """
        SELECT 
            $Name as ledger_name,
            $Parent as parent,
            $OpeningBalance as opening_balance,
            $ClosingBalance as closing_balance
        FROM Ledger
        WHERE $Parent = ?
        ORDER BY $Name
    """
    
    GET_LEDGER_BALANCE = """
        SELECT 
            $Name as ledger_name,
            $ClosingBalance as closing_balance
        FROM Ledger
        WHERE $Name = ?
    """
    
    # Voucher Queries
    GET_ALL_VOUCHERS = """
        SELECT 
            $Date as voucher_date,
            $VoucherNumber as voucher_number,
            $VoucherType as voucher_type,
            $Amount as amount,
            $Reference as reference,
            $Narration as narration
        FROM Voucher
        ORDER BY $Date DESC, $VoucherNumber DESC
    """
    
    GET_VOUCHERS_BY_TYPE = """
        SELECT 
            $Date as voucher_date,
            $VoucherNumber as voucher_number,
            $VoucherType as voucher_type,
            $Amount as amount,
            $Reference as reference,
            $Narration as narration
        FROM Voucher
        WHERE $VoucherType = ?
        ORDER BY $Date DESC
    """
    
    GET_VOUCHERS_BY_DATE_RANGE = """
        SELECT 
            $Date as voucher_date,
            $VoucherNumber as voucher_number,
            $VoucherType as voucher_type,
            $Amount as amount,
            $Reference as reference,
            $Narration as narration
        FROM Voucher
        WHERE $Date >= ? AND $Date <= ?
        ORDER BY $Date DESC
    """
    
    GET_SALES_VOUCHERS = """
        SELECT 
            $Date as voucher_date,
            $VoucherNumber as voucher_number,
            $Amount as amount,
            $Reference as reference,
            $PartyName as party_name
        FROM Voucher
        WHERE $VoucherType = 'Sales'
        ORDER BY $Date DESC
    """
    
    GET_PURCHASE_VOUCHERS = """
        SELECT 
            $Date as voucher_date,
            $VoucherNumber as voucher_number,
            $Amount as amount,
            $Reference as reference,
            $PartyName as party_name
        FROM Voucher
        WHERE $VoucherType = 'Purchase'
        ORDER BY $Date DESC
    """
    
    # Financial Reports Queries
    GET_PROFIT_LOSS_DATA = """
        SELECT 
            $Name as account_name,
            $Parent as group_name,
            $ClosingBalance as amount,
            $IsRevenue as is_revenue,
            $IsExpense as is_expense
        FROM Ledger
        WHERE $IsRevenue = 'Yes' OR $IsExpense = 'Yes'
        ORDER BY $Parent, $Name
    """
    
    GET_BALANCE_SHEET_DATA = """
        SELECT 
            $Name as account_name,
            $Parent as group_name,
            $ClosingBalance as amount,
            $IsAsset as is_asset,
            $IsLiability as is_liability
        FROM Ledger
        WHERE $IsAsset = 'Yes' OR $IsLiability = 'Yes'
        ORDER BY $Parent, $Name
    """
    
    # Cash Flow Queries
    GET_CASH_RECEIPTS = """
        SELECT 
            $Date as voucher_date,
            $Amount as amount,
            $PartyName as party_name,
            $Narration as narration
        FROM Voucher
        WHERE $VoucherType = 'Receipt'
        ORDER BY $Date DESC
    """
    
    GET_CASH_PAYMENTS = """
        SELECT 
            $Date as voucher_date,
            $Amount as amount,
            $PartyName as party_name,
            $Narration as narration
        FROM Voucher
        WHERE $VoucherType = 'Payment'
        ORDER BY $Date DESC
    """
    
    # Inventory Queries (if available)
    GET_STOCK_ITEMS = """
        SELECT 
            $Name as item_name,
            $StockGroup as group_name,
            $ClosingStock as closing_stock,
            $ClosingValue as closing_value,
            $Unit as unit
        FROM StockItem
        ORDER BY $Name
    """
    
    GET_STOCK_SUMMARY = """
        SELECT 
            $StockGroup as group_name,
            SUM($ClosingValue) as total_value,
            COUNT(*) as item_count
        FROM StockItem
        GROUP BY $StockGroup
        ORDER BY total_value DESC
    """
    
    # Party/Customer Queries
    GET_SUNDRY_DEBTORS = """
        SELECT 
            $Name as party_name,
            $ClosingBalance as outstanding_amount,
            $Parent as group_name
        FROM Ledger
        WHERE $Parent = 'Sundry Debtors'
        ORDER BY $ClosingBalance DESC
    """
    
    GET_SUNDRY_CREDITORS = """
        SELECT 
            $Name as party_name,
            $ClosingBalance as outstanding_amount,
            $Parent as group_name
        FROM Ledger
        WHERE $Parent = 'Sundry Creditors'
        ORDER BY $ClosingBalance DESC
    """
    
    # Summary Queries
    GET_MONTHLY_SALES_SUMMARY = """
        SELECT 
            YEAR($Date) as year,
            MONTH($Date) as month,
            SUM($Amount) as total_sales,
            COUNT(*) as voucher_count
        FROM Voucher
        WHERE $VoucherType = 'Sales'
        GROUP BY YEAR($Date), MONTH($Date)
        ORDER BY year DESC, month DESC
    """
    
    GET_DAILY_CASH_FLOW = """
        SELECT 
            $Date as voucher_date,
            SUM(CASE WHEN $VoucherType = 'Receipt' THEN $Amount ELSE 0 END) as cash_in,
            SUM(CASE WHEN $VoucherType = 'Payment' THEN $Amount ELSE 0 END) as cash_out,
            (SUM(CASE WHEN $VoucherType = 'Receipt' THEN $Amount ELSE 0 END) - 
             SUM(CASE WHEN $VoucherType = 'Payment' THEN $Amount ELSE 0 END)) as net_cash_flow
        FROM Voucher
        WHERE $VoucherType IN ('Receipt', 'Payment')
        GROUP BY $Date
        ORDER BY $Date DESC
    """
    
    @staticmethod
    def get_vouchers_by_period(period: str) -> str:
        """Generate query for vouchers in a specific period."""
        base_query = """
            SELECT 
                $Date as voucher_date,
                $VoucherNumber as voucher_number,
                $VoucherType as voucher_type,
                $Amount as amount,
                $PartyName as party_name
            FROM Voucher
            WHERE $Date >= ? AND $Date <= ?
            ORDER BY $Date DESC
        """
        return base_query
    
    @staticmethod
    def get_top_customers_query(limit: int = 10) -> str:
        """Generate query for top customers by sales."""
        return f"""
            SELECT TOP {limit}
                $PartyName as customer_name,
                SUM($Amount) as total_sales,
                COUNT(*) as transaction_count
            FROM Voucher
            WHERE $VoucherType = 'Sales' AND $PartyName IS NOT NULL
            GROUP BY $PartyName
            ORDER BY total_sales DESC
        """
    
    @staticmethod
    def get_expense_analysis_query() -> str:
        """Generate query for expense analysis."""
        return """
            SELECT 
                $Parent as expense_category,
                $Name as account_name,
                $ClosingBalance as amount
            FROM Ledger
            WHERE $IsExpense = 'Yes' AND $ClosingBalance <> 0
            ORDER BY $Parent, $ClosingBalance DESC
        """
    
    @staticmethod
    def build_dynamic_query(
        table: str,
        fields: List[str],
        conditions: Dict[str, Any],
        order_by: Optional[str] = None,
        limit: Optional[int] = None
    ) -> tuple[str, tuple]:
        """Build a dynamic query with parameters."""
        # Build SELECT clause
        select_fields = ", ".join([f"${field}" for field in fields])
        query = f"SELECT {select_fields} FROM {table}"
        
        # Build WHERE clause
        params = []
        if conditions:
            where_conditions = []
            for field, value in conditions.items():
                if value is not None:
                    where_conditions.append(f"${field} = ?")
                    params.append(value)
            
            if where_conditions:
                query += " WHERE " + " AND ".join(where_conditions)
        
        # Add ORDER BY
        if order_by:
            query += f" ORDER BY ${order_by}"
        
        # Add LIMIT
        if limit:
            query += f" LIMIT {limit}"
        
        return query, tuple(params)