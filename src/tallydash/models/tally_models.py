from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, date
from decimal import Decimal
from enum import Enum


class VoucherType(str, Enum):
    """Enumeration of voucher types in Tally."""
    SALES = "Sales"
    PURCHASE = "Purchase"
    PAYMENT = "Payment"
    RECEIPT = "Receipt"
    JOURNAL = "Journal"
    CONTRA = "Contra"
    CREDIT_NOTE = "Credit Note"
    DEBIT_NOTE = "Debit Note"


class Company(BaseModel):
    """Model for Tally company data."""
    company_name: str = Field(..., description="Name of the company")
    start_date: Optional[date] = Field(None, description="Books start date")
    end_date: Optional[date] = Field(None, description="Books end date")
    currency: Optional[str] = Field(None, description="Company currency")
    
    class Config:
        json_encoders = {
            date: lambda v: v.isoformat() if v else None
        }


class Ledger(BaseModel):
    """Model for Tally ledger data."""
    ledger_name: str = Field(..., description="Name of the ledger")
    parent: Optional[str] = Field(None, description="Parent group name")
    opening_balance: Optional[Decimal] = Field(None, description="Opening balance")
    closing_balance: Optional[Decimal] = Field(None, description="Closing balance")
    is_revenue: Optional[bool] = Field(None, description="Is revenue account")
    is_expense: Optional[bool] = Field(None, description="Is expense account")
    is_asset: Optional[bool] = Field(None, description="Is asset account")
    is_liability: Optional[bool] = Field(None, description="Is liability account")
    is_debit: Optional[bool] = Field(None, description="Has debit balance")
    
    @validator('opening_balance', 'closing_balance', pre=True)
    def parse_decimal(cls, v):
        """Parse decimal values from various formats."""
        if v is None:
            return None
        if isinstance(v, (int, float)):
            return Decimal(str(v))
        if isinstance(v, str):
            try:
                # Remove common formatting characters
                cleaned = v.replace(',', '').replace(' ', '').strip()
                return Decimal(cleaned) if cleaned else None
            except:
                return None
        return v
    
    @property
    def balance_type(self) -> str:
        """Get the balance type (Dr/Cr)."""
        if self.closing_balance is None:
            return "N/A"
        return "Dr" if (self.closing_balance >= 0 and self.is_debit) else "Cr"
    
    @property
    def absolute_balance(self) -> Optional[Decimal]:
        """Get absolute value of closing balance."""
        return abs(self.closing_balance) if self.closing_balance is not None else None


class VoucherEntry(BaseModel):
    """Model for individual voucher entry (ledger posting)."""
    ledger_name: str = Field(..., description="Ledger name")
    amount: Decimal = Field(..., description="Amount")
    is_debit: bool = Field(..., description="Is debit entry")
    
    @validator('amount', pre=True)
    def parse_amount(cls, v):
        """Parse amount from various formats."""
        if isinstance(v, (int, float)):
            return Decimal(str(v))
        if isinstance(v, str):
            try:
                cleaned = v.replace(',', '').replace(' ', '').strip()
                return Decimal(cleaned)
            except:
                return Decimal('0')
        return v


class Voucher(BaseModel):
    """Model for Tally voucher data."""
    voucher_date: date = Field(..., description="Voucher date")
    voucher_number: str = Field(..., description="Voucher number")
    voucher_type: VoucherType = Field(..., description="Type of voucher")
    amount: Optional[Decimal] = Field(None, description="Total voucher amount")
    reference: Optional[str] = Field(None, description="Reference number")
    narration: Optional[str] = Field(None, description="Voucher narration")
    party_name: Optional[str] = Field(None, description="Party name")
    entries: Optional[List[VoucherEntry]] = Field(None, description="Voucher entries")
    
    @validator('voucher_date', pre=True)
    def parse_date(cls, v):
        """Parse date from various formats."""
        if isinstance(v, date):
            return v
        if isinstance(v, datetime):
            return v.date()
        if isinstance(v, str):
            try:
                # Try common date formats
                for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y']:
                    try:
                        return datetime.strptime(v, fmt).date()
                    except ValueError:
                        continue
                raise ValueError(f"Unable to parse date: {v}")
            except ValueError:
                raise ValueError(f"Invalid date format: {v}")
        return v
    
    @validator('amount', pre=True)
    def parse_amount(cls, v):
        """Parse amount from various formats."""
        if v is None:
            return None
        if isinstance(v, (int, float)):
            return Decimal(str(v))
        if isinstance(v, str):
            try:
                cleaned = v.replace(',', '').replace(' ', '').strip()
                return Decimal(cleaned) if cleaned else None
            except:
                return None
        return v
    
    class Config:
        json_encoders = {
            date: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        }


class StockItem(BaseModel):
    """Model for Tally stock item data."""
    item_name: str = Field(..., description="Stock item name")
    group_name: Optional[str] = Field(None, description="Stock group")
    closing_stock: Optional[Decimal] = Field(None, description="Closing stock quantity")
    closing_value: Optional[Decimal] = Field(None, description="Closing stock value")
    unit: Optional[str] = Field(None, description="Unit of measurement")
    opening_stock: Optional[Decimal] = Field(None, description="Opening stock quantity")
    opening_value: Optional[Decimal] = Field(None, description="Opening stock value")
    
    @validator('closing_stock', 'closing_value', 'opening_stock', 'opening_value', pre=True)
    def parse_decimal_fields(cls, v):
        """Parse decimal values from various formats."""
        if v is None:
            return None
        if isinstance(v, (int, float)):
            return Decimal(str(v))
        if isinstance(v, str):
            try:
                cleaned = v.replace(',', '').replace(' ', '').strip()
                return Decimal(cleaned) if cleaned else None
            except:
                return None
        return v


class FinancialSummary(BaseModel):
    """Model for financial summary data."""
    total_sales: Optional[Decimal] = Field(None, description="Total sales amount")
    total_purchases: Optional[Decimal] = Field(None, description="Total purchase amount")
    total_receipts: Optional[Decimal] = Field(None, description="Total receipts")
    total_payments: Optional[Decimal] = Field(None, description="Total payments")
    net_profit: Optional[Decimal] = Field(None, description="Net profit/loss")
    total_debtors: Optional[Decimal] = Field(None, description="Total sundry debtors")
    total_creditors: Optional[Decimal] = Field(None, description="Total sundry creditors")
    cash_balance: Optional[Decimal] = Field(None, description="Cash/bank balance")
    
    @validator('*', pre=True)
    def parse_all_decimals(cls, v):
        """Parse all decimal fields."""
        if v is None:
            return None
        if isinstance(v, (int, float)):
            return Decimal(str(v))
        if isinstance(v, str):
            try:
                cleaned = v.replace(',', '').replace(' ', '').strip()
                return Decimal(cleaned) if cleaned else None
            except:
                return None
        return v
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v) if v is not None else None
        }


class PeriodSummary(BaseModel):
    """Model for period-based summary data."""
    period_name: str = Field(..., description="Period identifier (e.g., '2024-01')")
    start_date: date = Field(..., description="Period start date")
    end_date: date = Field(..., description="Period end date")
    sales_amount: Optional[Decimal] = Field(None, description="Sales in period")
    purchase_amount: Optional[Decimal] = Field(None, description="Purchases in period")
    voucher_count: Optional[int] = Field(None, description="Number of vouchers")
    
    class Config:
        json_encoders = {
            date: lambda v: v.isoformat(),
            Decimal: lambda v: float(v) if v is not None else None
        }


class TallyDataResponse(BaseModel):
    """Generic response model for Tally data."""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field("", description="Response message")
    data: Union[List[Dict[str, Any]], Dict[str, Any], None] = Field(None, description="Response data")
    count: Optional[int] = Field(None, description="Number of records")
    query_time: Optional[float] = Field(None, description="Query execution time in seconds")
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v) if v is not None else None,
            date: lambda v: v.isoformat() if v is not None else None,
            datetime: lambda v: v.isoformat() if v is not None else None
        }