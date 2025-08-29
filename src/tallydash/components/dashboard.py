import reflex as rx
from typing import List, Dict, Any
from ..models.app_models import AppState
from .charts import create_chart_component
from .chat import ai_chat_component


def metric_card(title: str, value: str, change: str = "", change_positive: bool = True) -> rx.Component:
    """Create a metric card component."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.text(title, size="2", color="gray"),
                rx.spacer(),
                rx.icon("trending_up" if change_positive else "trending_down", 
                        size=16, color="green" if change_positive else "red"),
                width="100%",
                align="center"
            ),
            rx.hstack(
                rx.text(value, size="6", weight="bold"),
                rx.spacer(),
                rx.text(change, size="2", 
                        color="green" if change_positive else "red") if change else rx.text(""),
                width="100%",
                align="center"
            ),
            width="100%",
            spacing="2"
        ),
        width="100%",
        height="120px",
        padding="4"
    )


def financial_summary_section() -> rx.Component:
    """Create financial summary section with metric cards."""
    return rx.vstack(
        rx.heading("Financial Overview", size="6", margin_bottom="4"),
        rx.grid(
            metric_card(
                "Total Sales", 
                "₹12,45,678", 
                "+12.5%", 
                True
            ),
            metric_card(
                "Total Expenses", 
                "₹8,65,432", 
                "+5.2%", 
                False
            ),
            metric_card(
                "Net Profit", 
                "₹3,80,246", 
                "+18.3%", 
                True
            ),
            metric_card(
                "Cash Balance", 
                "₹5,67,890", 
                "-2.1%", 
                False
            ),
            columns="4",
            spacing="4",
            width="100%"
        ),
        width="100%",
        spacing="4"
    )


def recent_transactions_table() -> rx.Component:
    """Create recent transactions table."""
    # Sample data - in real implementation, this would come from state
    sample_data = [
        {"date": "2024-01-15", "voucher": "SLS001", "type": "Sales", "party": "ABC Corp", "amount": "₹25,000"},
        {"date": "2024-01-14", "voucher": "PUR001", "type": "Purchase", "party": "XYZ Ltd", "amount": "₹15,000"},
        {"date": "2024-01-13", "voucher": "RCT001", "type": "Receipt", "party": "ABC Corp", "amount": "₹20,000"},
        {"date": "2024-01-12", "voucher": "PMT001", "type": "Payment", "party": "Supplier 1", "amount": "₹10,000"},
        {"date": "2024-01-11", "voucher": "JRN001", "type": "Journal", "party": "Internal", "amount": "₹5,000"},
    ]
    
    return rx.vstack(
        rx.hstack(
            rx.heading("Recent Transactions", size="5"),
            rx.spacer(),
            rx.button("View All", variant="outline", size="2"),
            width="100%",
            align="center"
        ),
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell("Date"),
                    rx.table.column_header_cell("Voucher"),
                    rx.table.column_header_cell("Type"),
                    rx.table.column_header_cell("Party"),
                    rx.table.column_header_cell("Amount"),
                )
            ),
            rx.table.body(
                *[
                    rx.table.row(
                        rx.table.row_header_cell(row["date"]),
                        rx.table.cell(row["voucher"]),
                        rx.table.cell(
                            rx.badge(row["type"], 
                                   color_scheme="blue" if row["type"] == "Sales" 
                                   else "green" if row["type"] == "Receipt"
                                   else "red" if row["type"] == "Payment"
                                   else "orange")
                        ),
                        rx.table.cell(row["party"]),
                        rx.table.cell(row["amount"], style={"text-align": "right"}),
                    )
                    for row in sample_data
                ]
            ),
            width="100%"
        ),
        width="100%",
        spacing="4"
    )


def top_customers_section() -> rx.Component:
    """Create top customers section."""
    # Sample data
    sample_customers = [
        {"name": "ABC Corporation", "sales": "₹2,50,000", "transactions": 15},
        {"name": "XYZ Limited", "sales": "₹1,80,000", "transactions": 12},
        {"name": "PQR Industries", "sales": "₹1,45,000", "transactions": 8},
        {"name": "LMN Enterprises", "sales": "₹1,20,000", "transactions": 10},
        {"name": "RST Solutions", "sales": "₹95,000", "transactions": 6},
    ]
    
    return rx.vstack(
        rx.heading("Top Customers", size="5", margin_bottom="3"),
        rx.vstack(
            *[
                rx.hstack(
                    rx.vstack(
                        rx.text(customer["name"], weight="bold", size="3"),
                        rx.text(f"{customer['transactions']} transactions", 
                               size="2", color="gray"),
                        align_items="start",
                        spacing="1"
                    ),
                    rx.spacer(),
                    rx.text(customer["sales"], size="3", weight="bold"),
                    width="100%",
                    align="center",
                    padding="3",
                    border="1px solid var(--gray-6)",
                    border_radius="8px"
                )
                for customer in sample_customers
            ],
            width="100%",
            spacing="2"
        ),
        width="100%",
        spacing="3"
    )


def sidebar_navigation() -> rx.Component:
    """Create sidebar navigation."""
    nav_items = [
        {"icon": "layout-dashboard", "label": "Dashboard", "active": True},
        {"icon": "receipt", "label": "Vouchers", "active": False},
        {"icon": "users", "label": "Parties", "active": False},
        {"icon": "trending-up", "label": "Reports", "active": False},
        {"icon": "bar-chart-3", "label": "Analytics", "active": False},
        {"icon": "settings", "label": "Settings", "active": False},
    ]
    
    return rx.vstack(
        rx.hstack(
            rx.icon("building-2", size=24),
            rx.heading("TallyDash", size="5"),
            width="100%",
            align="center",
            padding="4"
        ),
        rx.divider(),
        rx.vstack(
            *[
                rx.hstack(
                    rx.icon(item["icon"], size=18),
                    rx.text(item["label"]),
                    width="100%",
                    align="center",
                    padding="3",
                    border_radius="8px",
                    background_color="var(--accent-3)" if item["active"] else "transparent",
                    color="var(--accent-11)" if item["active"] else "var(--gray-11)",
                    _hover={"background_color": "var(--gray-3)", "cursor": "pointer"}
                )
                for item in nav_items
            ],
            width="100%",
            padding="2",
            spacing="1"
        ),
        rx.spacer(),
        rx.vstack(
            rx.divider(),
            rx.hstack(
                rx.icon("database", size=16, color="green"),
                rx.text("Tally Connected", size="2"),
                width="100%",
                align="center",
                padding="3"
            ),
            width="100%"
        ),
        width="250px",
        height="100vh",
        background_color="var(--gray-2)",
        border_right="1px solid var(--gray-6)"
    )


def header_bar() -> rx.Component:
    """Create top header bar."""
    return rx.hstack(
        rx.hstack(
            rx.button(
                rx.icon("menu", size=18),
                variant="ghost",
                size="2"
            ),
            rx.text("Dashboard", size="5", weight="bold"),
            align="center",
            spacing="3"
        ),
        rx.spacer(),
        rx.hstack(
            rx.button(
                rx.icon("refresh-cw", size=16),
                variant="outline",
                size="2"
            ),
            rx.select(
                ["Last 7 days", "Last 30 days", "Last 3 months", "Last year"],
                default_value="Last 30 days",
                size="2"
            ),
            rx.button(
                rx.icon("user", size=16),
                variant="ghost",
                size="2"
            ),
            align="center",
            spacing="2"
        ),
        width="100%",
        padding="4",
        border_bottom="1px solid var(--gray-6)",
        background_color="white"
    )


def dashboard_content() -> rx.Component:
    """Create main dashboard content area."""
    return rx.vstack(
        financial_summary_section(),
        rx.grid(
            rx.vstack(
                create_chart_component(
                    chart_type="line",
                    title="Sales Trend - Last 6 Months",
                    data={
                        "labels": ["Aug", "Sep", "Oct", "Nov", "Dec", "Jan"],
                        "datasets": [{
                            "label": "Sales",
                            "data": [45000, 52000, 48000, 61000, 55000, 67000],
                            "borderColor": "#3B82F6",
                            "backgroundColor": "rgba(59, 130, 246, 0.1)"
                        }]
                    }
                ),
                create_chart_component(
                    chart_type="doughnut",
                    title="Expense Breakdown",
                    data={
                        "labels": ["Rent", "Utilities", "Supplies", "Marketing", "Others"],
                        "datasets": [{
                            "data": [30, 15, 20, 25, 10],
                            "backgroundColor": [
                                "#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF"
                            ]
                        }]
                    }
                ),
                width="100%",
                spacing="6"
            ),
            rx.vstack(
                recent_transactions_table(),
                top_customers_section(),
                width="100%",
                spacing="6"
            ),
            columns="2",
            spacing="6",
            width="100%"
        ),
        width="100%",
        spacing="6",
        padding="6"
    )


def dashboard_page() -> rx.Component:
    """Create the main dashboard page."""
    return rx.hstack(
        sidebar_navigation(),
        rx.vstack(
            header_bar(),
            rx.scroll_area(
                dashboard_content(),
                width="100%",
                height="calc(100vh - 80px)"
            ),
            width="100%"
        ),
        width="100%",
        height="100vh",
        spacing="0"
    )