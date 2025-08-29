"""TallyDash - Main Reflex Application"""

import reflex as rx
from .components.dashboard import dashboard_page
from .components.chat import ai_chat_component
from .models.app_models import AppState
from .services import TallyService, AIService
from .config import settings

# Initialize services
tally_service = TallyService()
ai_service = AIService()


class TallyDashState(AppState):
    """Extended application state with business logic."""
    
    def __init__(self):
        super().__init__()
        
    async def on_load(self):
        """Called when the app loads."""
        await self.check_tally_connection()
        await self.load_companies()
        
    async def check_tally_connection(self):
        """Check Tally ODBC connection status."""
        try:
            result = tally_service.test_connection()
            self.update_connection_status(
                result["success"], 
                result.get("message", "")
            )
        except Exception as e:
            self.update_connection_status(False, f"Connection error: {str(e)}")
    
    async def load_companies(self):
        """Load available companies from Tally."""
        if not self.is_connected:
            return
            
        try:
            response = tally_service.get_companies()
            if response.success and response.data:
                self.available_companies = [comp["company_name"] for comp in response.data]
                if self.available_companies and not self.selected_company:
                    self.selected_company = self.available_companies[0]
        except Exception as e:
            self.connection_error = f"Failed to load companies: {str(e)}"
    
    async def refresh_dashboard(self):
        """Refresh dashboard data."""
        self.set_loading(True)
        
        try:
            dashboard_data = tally_service.get_dashboard_data(
                filters=self.filters.dict()
            )
            
            if dashboard_data["success"]:
                # Update dashboard data
                financial_summary = dashboard_data["data"].get("financial_summary", {})
                if financial_summary.get("success"):
                    self.dashboard_data.financial_summary = financial_summary["data"]
                
                # Update charts and tables
                self.dashboard_data.recent_vouchers = dashboard_data["data"].get("recent_vouchers", [])
                self.dashboard_data.last_updated = dashboard_data.get("last_updated")
                
        except Exception as e:
            self.add_ai_message("system", f"Error refreshing dashboard: {str(e)}")
        finally:
            self.set_loading(False)
    
    async def send_message(self):
        """Send AI message and get response."""
        if not self.current_message.strip() or self.is_ai_processing:
            return
        
        user_message = self.current_message.strip()
        self.add_ai_message("user", user_message)
        self.current_message = ""
        self.is_ai_processing = True
        
        try:
            # Create query request
            from .models.app_models import QueryRequest
            request = QueryRequest(
                query_text=user_message,
                filters=self.filters,
                context={"company": self.selected_company}
            )
            
            # Get AI response
            response = ai_service.process_natural_language_query(request)
            
            if response.success:
                # Add AI response
                self.add_ai_message("assistant", response.message)
                
                # Update dashboard if needed
                if response.data:
                    # Could update specific dashboard components based on response
                    pass
                    
            else:
                self.add_ai_message("error", f"Sorry, I couldn't process that: {response.message}")
                
        except Exception as e:
            self.add_ai_message("error", f"An error occurred: {str(e)}")
        finally:
            self.is_ai_processing = False
    
    def set_date_filter(self, date_from: str = "", date_to: str = ""):
        """Set date filter for dashboard."""
        if date_from:
            self.filters.date_from = date_from
        if date_to:
            self.filters.date_to = date_to
        
        # Trigger dashboard refresh
        return self.refresh_dashboard()
    
    def set_company_filter(self, company: str):
        """Set selected company."""
        self.selected_company = company
        return self.refresh_dashboard()


def index() -> rx.Component:
    """Main application page."""
    return rx.fragment(
        dashboard_page(),
        # Add global components
        rx.script("""
            // Initialize theme
            document.documentElement.setAttribute('data-theme', 'light');
            
            // Add keyboard shortcuts
            document.addEventListener('keydown', function(e) {
                // Ctrl/Cmd + K to focus search
                if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                    e.preventDefault();
                    // Focus AI chat input
                }
            });
        """)
    )


def about() -> rx.Component:
    """About page."""
    return rx.vstack(
        rx.heading("About TallyDash", size="8"),
        rx.text(
            "TallyDash is an AI-powered dashboard for Tally ERP data visualization and analysis.",
            size="4"
        ),
        rx.divider(),
        rx.vstack(
            rx.text("Features:", weight="bold", size="4"),
            rx.unordered_list(
                rx.list_item("Real-time Tally ODBC connectivity"),
                rx.list_item("AI-powered natural language queries"),
                rx.list_item("Interactive charts and visualizations"),
                rx.list_item("Financial reporting and analysis"),
                rx.list_item("Customer and supplier insights"),
                rx.list_item("Cash flow monitoring"),
            ),
            align_items="start"
        ),
        rx.divider(),
        rx.text(f"Version: {settings.app_description}", size="2", color="gray"),
        spacing="4",
        padding="8",
        max_width="800px",
        margin="0 auto"
    )


def settings_page() -> rx.Component:
    """Settings page."""
    return rx.vstack(
        rx.heading("Settings", size="6"),
        rx.card(
            rx.vstack(
                rx.heading("Tally Connection", size="4"),
                rx.hstack(
                    rx.text("Status:", weight="bold"),
                    rx.cond(
                        TallyDashState.is_connected,
                        rx.badge("Connected", color_scheme="green"),
                        rx.badge("Disconnected", color_scheme="red")
                    ),
                    align="center"
                ),
                rx.text(TallyDashState.connection_error, color="red"),
                rx.button(
                    "Test Connection",
                    on_click=TallyDashState.check_tally_connection,
                    loading=TallyDashState.is_loading
                ),
                spacing="3",
                width="100%"
            ),
            width="100%",
            padding="4"
        ),
        spacing="6",
        padding="6",
        max_width="600px",
        margin="0 auto"
    )


# Create the app
app = rx.App(
    state=TallyDashState,
    theme=rx.theme(
        appearance="light",
        has_background=True,
        radius="medium",
        accent_color="blue",
    ),
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
    ],
    head_components=[
        rx.script(src="https://cdn.plot.ly/plotly-latest.min.js"),
    ]
)

# Add pages
app.add_page(
    index,
    route="/",
    title="TallyDash - AI-Powered Tally Dashboard",
    description="Real-time Tally ERP data visualization with AI assistance"
)

app.add_page(
    about,
    route="/about", 
    title="About - TallyDash"
)

app.add_page(
    settings_page,
    route="/settings",
    title="Settings - TallyDash"
)

# Add custom CSS
app.add_custom_css("""
    .rx-Card {
        transition: all 0.2s ease;
    }
    
    .rx-Card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .chart-container {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .sidebar-nav-item:hover {
        transform: translateX(4px);
        transition: transform 0.2s ease;
    }
    
    .loading-spinner {
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--gray-3);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--gray-6);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--gray-8);
    }
""")