import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tallydash.services.tally_service import TallyService
from tallydash.models.tally_models import TallyDataResponse
from unittest.mock import Mock, patch


class TestTallyService:
    """Test cases for TallyService."""
    
    @pytest.fixture
    def tally_service(self):
        """Create TallyService instance for testing."""
        with patch('tallydash.services.tally_service.TallyDatabase'):
            return TallyService()
    
    def test_service_initialization(self, tally_service):
        """Test TallyService initialization."""
        assert tally_service is not None
        assert hasattr(tally_service, 'db')
        assert hasattr(tally_service, 'queries')
    
    @patch('tallydash.services.tally_service.TallyDatabase')
    def test_test_connection_success(self, mock_db):
        """Test successful connection test."""
        # Mock successful connection
        mock_db.return_value.test_connection.return_value = True
        
        service = TallyService()
        result = service.test_connection()
        
        assert result["success"] is True
        assert "successful" in result["message"].lower()
        assert "response_time" in result
    
    @patch('tallydash.services.tally_service.TallyDatabase')
    def test_test_connection_failure(self, mock_db):
        """Test failed connection test."""
        # Mock failed connection
        mock_db.return_value.test_connection.return_value = False
        
        service = TallyService()
        result = service.test_connection()
        
        assert result["success"] is False
        assert "failed" in result["message"].lower()
    
    @patch('tallydash.services.tally_service.TallyDatabase')
    def test_get_companies_success(self, mock_db):
        """Test successful company retrieval."""
        # Mock company data
        mock_data = [
            {"company_name": "Test Company 1", "currency": "INR"},
            {"company_name": "Test Company 2", "currency": "USD"}
        ]
        mock_db.return_value.execute_query.return_value = mock_data
        
        service = TallyService()
        result = service.get_companies()
        
        assert isinstance(result, TallyDataResponse)
        assert result.success is True
        assert len(result.data) == 2
        assert result.count == 2
    
    @patch('tallydash.services.tally_service.TallyDatabase')
    def test_get_ledgers_with_filter(self, mock_db):
        """Test ledger retrieval with group filter."""
        # Mock ledger data
        mock_data = [
            {"ledger_name": "Cash", "parent": "Cash-in-Hand", "closing_balance": 10000},
            {"ledger_name": "Bank", "parent": "Bank Accounts", "closing_balance": 50000}
        ]
        mock_db.return_value.execute_query.return_value = mock_data
        
        service = TallyService()
        result = service.get_ledgers(group_filter="Cash-in-Hand")
        
        assert result.success is True
        assert len(result.data) == 2
    
    @patch('tallydash.services.tally_service.TallyDatabase')
    def test_financial_summary_calculation(self, mock_db):
        """Test financial summary calculation."""
        # Mock various data for summary calculation
        mock_db.return_value.execute_query.side_effect = [
            [{"amount": 100000, "is_revenue": True}, {"amount": 60000, "is_expense": True}],  # P&L
            [{"amount": 25000}],  # Receipts
            [{"amount": 15000}],  # Payments
            [{"outstanding_amount": 30000}],  # Debtors
            [{"outstanding_amount": 20000}]   # Creditors
        ]
        
        service = TallyService()
        result = service.get_financial_summary()
        
        assert result["success"] is True
        assert "data" in result
        summary = result["data"]
        assert summary["total_sales"] == 100000
        assert summary["total_receipts"] == 25000
        assert summary["total_payments"] == 15000
        assert summary["net_profit"] == 40000  # 100000 - 60000
    
    @patch('tallydash.services.tally_service.TallyDatabase')
    def test_get_vouchers_with_filters(self, mock_db):
        """Test voucher retrieval with filters."""
        from datetime import date
        
        mock_data = [
            {
                "voucher_date": "2024-01-15",
                "voucher_number": "SLS001",
                "voucher_type": "Sales",
                "amount": 25000
            }
        ]
        mock_db.return_value.get_vouchers.return_value = mock_data
        
        service = TallyService()
        result = service.get_vouchers(
            voucher_type="Sales",
            date_from=date(2024, 1, 1),
            date_to=date(2024, 1, 31),
            limit=10
        )
        
        assert result.success is True
        assert len(result.data) == 1
        assert result.data[0]["voucher_type"] == "Sales"
    
    @patch('tallydash.services.tally_service.TallyDatabase')
    def test_error_handling(self, mock_db):
        """Test error handling in service methods."""
        # Mock database exception
        mock_db.return_value.execute_query.side_effect = Exception("Database error")
        
        service = TallyService()
        result = service.get_companies()
        
        assert result.success is False
        assert "error" in result.message.lower()
    
    @patch('tallydash.services.tally_service.pd.DataFrame')
    @patch('tallydash.services.tally_service.TallyDatabase')
    def test_monthly_sales_trend(self, mock_db, mock_df):
        """Test monthly sales trend calculation."""
        mock_data = [
            {"year": 2024, "month": 1, "total_sales": 50000, "voucher_count": 10},
            {"year": 2024, "month": 2, "total_sales": 60000, "voucher_count": 12}
        ]
        mock_db.return_value.execute_query.return_value = mock_data
        
        # Mock pandas DataFrame
        mock_df_instance = Mock()
        mock_df_instance.empty = False
        mock_df_instance.sort_values.return_value.tail.return_value = mock_df_instance
        mock_df_instance.__getitem__.side_effect = lambda x: {
            'period': ['2024-01', '2024-02'],
            'total_sales': [50000, 60000],
            'voucher_count': [10, 12]
        }[x]
        mock_df_instance.tolist.return_value = ['2024-01', '2024-02']
        mock_df.return_value = mock_df_instance
        
        service = TallyService()
        result = service.get_monthly_sales_trend(months=6)
        
        assert result["success"] is True
        assert "data" in result