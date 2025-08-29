from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, date
from enum import Enum
import reflex as rx


class MessageType(str, Enum):
    """Types of AI messages."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    ERROR = "error"


class ChartType(str, Enum):
    """Types of charts supported."""
    BAR = "bar"
    LINE = "line"
    PIE = "pie"
    AREA = "area"
    SCATTER = "scatter"
    DONUT = "donut"


class AIMessage(BaseModel):
    """Model for AI chat messages."""
    id: str = Field(..., description="Unique message ID")
    type: MessageType = Field(..., description="Type of message")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.now, description="Message timestamp")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ChartData(BaseModel):
    """Model for chart data."""
    chart_type: ChartType = Field(..., description="Type of chart")
    title: str = Field(..., description="Chart title")
    data: Dict[str, Any] = Field(..., description="Chart data")
    options: Optional[Dict[str, Any]] = Field(None, description="Chart options")
    
    class Config:
        arbitrary_types_allowed = True


class DashboardFilter(BaseModel):
    """Model for dashboard filters."""
    company: Optional[str] = Field(None, description="Selected company")
    date_from: Optional[date] = Field(None, description="Start date filter")
    date_to: Optional[date] = Field(None, description="End date filter")
    voucher_type: Optional[str] = Field(None, description="Voucher type filter")
    ledger_group: Optional[str] = Field(None, description="Ledger group filter")
    
    class Config:
        json_encoders = {
            date: lambda v: v.isoformat() if v else None
        }


class DashboardData(BaseModel):
    """Model for dashboard data."""
    financial_summary: Optional[Dict[str, Any]] = Field(None, description="Financial summary")
    charts: List[ChartData] = Field(default_factory=list, description="Chart data")
    recent_vouchers: List[Dict[str, Any]] = Field(default_factory=list, description="Recent vouchers")
    top_ledgers: List[Dict[str, Any]] = Field(default_factory=list, description="Top ledgers by balance")
    last_updated: datetime = Field(default_factory=datetime.now, description="Last update time")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AppState(rx.State):
    """Main application state for Reflex."""
    
    # Connection status
    is_connected: bool = False
    connection_error: str = ""
    
    # Company and filters
    selected_company: str = ""
    available_companies: List[str] = []
    filters: DashboardFilter = DashboardFilter()
    
    # Dashboard data
    dashboard_data: DashboardData = DashboardData()
    is_loading: bool = False
    
    # AI Chat
    ai_messages: List[AIMessage] = []
    current_message: str = ""
    is_ai_processing: bool = False
    
    # UI State
    sidebar_open: bool = True
    active_tab: str = "dashboard"
    theme: str = "light"
    
    # Data cache
    ledgers_cache: List[Dict[str, Any]] = []
    vouchers_cache: List[Dict[str, Any]] = []
    cache_timestamp: Optional[datetime] = None
    
    def toggle_sidebar(self):
        """Toggle sidebar visibility."""
        self.sidebar_open = not self.sidebar_open
    
    def set_active_tab(self, tab: str):
        """Set the active tab."""
        self.active_tab = tab
    
    def toggle_theme(self):
        """Toggle between light and dark theme."""
        self.theme = "dark" if self.theme == "light" else "light"
    
    def set_loading(self, loading: bool):
        """Set loading state."""
        self.is_loading = loading
    
    def add_ai_message(self, message_type: MessageType, content: str):
        """Add a message to AI chat."""
        message = AIMessage(
            id=f"msg_{len(self.ai_messages)}_{datetime.now().timestamp()}",
            type=message_type,
            content=content
        )
        self.ai_messages.append(message)
    
    def clear_ai_chat(self):
        """Clear AI chat history."""
        self.ai_messages = []
    
    def set_filters(self, **filters):
        """Update dashboard filters."""
        for key, value in filters.items():
            if hasattr(self.filters, key):
                setattr(self.filters, key, value)
    
    def update_connection_status(self, connected: bool, error: str = ""):
        """Update connection status."""
        self.is_connected = connected
        self.connection_error = error
    
    def update_dashboard_data(self, data: DashboardData):
        """Update dashboard data."""
        self.dashboard_data = data
    
    def cache_data(self, ledgers: List[Dict], vouchers: List[Dict]):
        """Cache data for performance."""
        self.ledgers_cache = ledgers
        self.vouchers_cache = vouchers
        self.cache_timestamp = datetime.now()
    
    @property
    def is_cache_valid(self) -> bool:
        """Check if cache is still valid (within 5 minutes)."""
        if not self.cache_timestamp:
            return False
        return (datetime.now() - self.cache_timestamp).seconds < 300


class QueryRequest(BaseModel):
    """Model for query requests."""
    query_text: str = Field(..., description="Natural language query")
    context: Optional[Dict[str, Any]] = Field(None, description="Query context")
    filters: Optional[DashboardFilter] = Field(None, description="Applied filters")
    
    
class QueryResponse(BaseModel):
    """Model for query responses."""
    success: bool = Field(..., description="Query success status")
    message: str = Field("", description="Response message")
    data: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = Field(None, description="Query results")
    chart_data: Optional[ChartData] = Field(None, description="Chart data if applicable")
    sql_query: Optional[str] = Field(None, description="Generated SQL query")
    execution_time: Optional[float] = Field(None, description="Query execution time")
    
    
class NotificationLevel(str, Enum):
    """Notification levels."""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


class Notification(BaseModel):
    """Model for notifications."""
    id: str = Field(..., description="Notification ID")
    level: NotificationLevel = Field(..., description="Notification level")
    title: str = Field(..., description="Notification title")
    message: str = Field(..., description="Notification message")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp")
    auto_dismiss: bool = Field(True, description="Auto dismiss notification")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UserPreferences(BaseModel):
    """Model for user preferences."""
    theme: str = Field("light", description="UI theme")
    date_format: str = Field("%Y-%m-%d", description="Date format preference")
    currency_format: str = Field("₹{:,.2f}", description="Currency format")
    default_company: Optional[str] = Field(None, description="Default company")
    auto_refresh: bool = Field(True, description="Auto refresh data")
    refresh_interval: int = Field(300, description="Refresh interval in seconds")
    show_animations: bool = Field(True, description="Show UI animations")
    dashboard_layout: List[str] = Field(
        default_factory=lambda: ["summary", "charts", "recent_vouchers"],
        description="Dashboard widget order"
    )


class SystemStatus(BaseModel):
    """Model for system status."""
    tally_connected: bool = Field(False, description="Tally connection status")
    database_status: str = Field("unknown", description="Database status")
    ai_service_status: str = Field("unknown", description="AI service status")
    cache_status: str = Field("unknown", description="Cache status")
    last_check: datetime = Field(default_factory=datetime.now, description="Last status check")
    uptime: Optional[int] = Field(None, description="Uptime in seconds")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }