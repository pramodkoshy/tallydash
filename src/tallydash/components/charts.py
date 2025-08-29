import reflex as rx
from typing import Dict, Any, List, Optional


def create_chart_component(
    chart_type: str = "bar",
    title: str = "Chart",
    data: Optional[Dict[str, Any]] = None,
    height: str = "400px",
    width: str = "100%"
) -> rx.Component:
    """
    Create a chart component using Plotly.
    
    Args:
        chart_type: Type of chart (bar, line, pie, doughnut, area, scatter)
        title: Chart title
        data: Chart data in Chart.js format
        height: Chart height
        width: Chart width
    """
    if data is None:
        data = {"labels": [], "datasets": []}
    
    # Convert data to Plotly format
    plotly_data = _convert_to_plotly_format(data, chart_type)
    
    # Create layout configuration
    layout = {
        "title": {
            "text": title,
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 18, "color": "var(--gray-12)"}
        },
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {"color": "var(--gray-11)"},
        "margin": {"t": 60, "r": 20, "b": 40, "l": 60},
        "showlegend": len(data.get("datasets", [])) > 1,
        "legend": {
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "right",
            "x": 1
        }
    }
    
    # Add chart-specific layout options
    if chart_type in ["bar", "line", "area", "scatter"]:
        layout.update({
            "xaxis": {
                "gridcolor": "var(--gray-6)",
                "showgrid": True,
                "zeroline": False
            },
            "yaxis": {
                "gridcolor": "var(--gray-6)",
                "showgrid": True,
                "zeroline": False
            }
        })
    
    config = {
        "displayModeBar": True,
        "modeBarButtonsToRemove": [
            "pan2d", "select2d", "lasso2d", "resetScale2d", 
            "zoomIn2d", "zoomOut2d", "autoScale2d"
        ],
        "displaylogo": False,
        "responsive": True
    }
    
    return rx.card(
        rx.plotly(
            data=plotly_data,
            layout=layout,
            config=config,
            width=width,
            height=height
        ),
        width="100%",
        height="auto"
    )


def _convert_to_plotly_format(data: Dict[str, Any], chart_type: str) -> List[Dict[str, Any]]:
    """Convert Chart.js format data to Plotly format."""
    labels = data.get("labels", [])
    datasets = data.get("datasets", [])
    
    plotly_data = []
    
    for i, dataset in enumerate(datasets):
        dataset_data = dataset.get("data", [])
        
        if chart_type == "bar":
            trace = {
                "type": "bar",
                "x": labels,
                "y": dataset_data,
                "name": dataset.get("label", f"Dataset {i+1}"),
                "marker": {
                    "color": dataset.get("backgroundColor", f"hsl({i * 137.5 % 360}, 70%, 60%)")
                }
            }
        
        elif chart_type == "line":
            trace = {
                "type": "scatter",
                "mode": "lines+markers",
                "x": labels,
                "y": dataset_data,
                "name": dataset.get("label", f"Dataset {i+1}"),
                "line": {
                    "color": dataset.get("borderColor", f"hsl({i * 137.5 % 360}, 70%, 60%)")
                },
                "marker": {
                    "size": 6
                }
            }
        
        elif chart_type == "area":
            trace = {
                "type": "scatter",
                "mode": "lines",
                "fill": "tozeroy" if i == 0 else "tonexty",
                "x": labels,
                "y": dataset_data,
                "name": dataset.get("label", f"Dataset {i+1}"),
                "line": {
                    "color": dataset.get("borderColor", f"hsl({i * 137.5 % 360}, 70%, 60%)")
                },
                "fillcolor": dataset.get("backgroundColor", f"hsla({i * 137.5 % 360}, 70%, 60%, 0.3)")
            }
        
        elif chart_type in ["pie", "doughnut"]:
            trace = {
                "type": "pie",
                "labels": labels,
                "values": dataset_data,
                "name": dataset.get("label", ""),
                "hole": 0.4 if chart_type == "doughnut" else 0,
                "marker": {
                    "colors": dataset.get("backgroundColor", [
                        f"hsl({j * 137.5 % 360}, 70%, 60%)" for j in range(len(labels))
                    ])
                },
                "textinfo": "label+percent",
                "textposition": "auto"
            }
        
        elif chart_type == "scatter":
            trace = {
                "type": "scatter",
                "mode": "markers",
                "x": labels,
                "y": dataset_data,
                "name": dataset.get("label", f"Dataset {i+1}"),
                "marker": {
                    "color": dataset.get("backgroundColor", f"hsl({i * 137.5 % 360}, 70%, 60%)"),
                    "size": 8
                }
            }
        
        else:
            # Default to bar chart
            trace = {
                "type": "bar",
                "x": labels,
                "y": dataset_data,
                "name": dataset.get("label", f"Dataset {i+1}")
            }
        
        plotly_data.append(trace)
    
    return plotly_data


def sales_trend_chart(data: Optional[Dict[str, Any]] = None) -> rx.Component:
    """Create a sales trend line chart."""
    if data is None:
        # Sample data
        data = {
            "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
            "datasets": [{
                "label": "Sales",
                "data": [45000, 52000, 48000, 61000, 55000, 67000],
                "borderColor": "#3B82F6",
                "backgroundColor": "rgba(59, 130, 246, 0.1)"
            }]
        }
    
    return create_chart_component(
        chart_type="line",
        title="Sales Trend",
        data=data,
        height="350px"
    )


def expense_breakdown_chart(data: Optional[Dict[str, Any]] = None) -> rx.Component:
    """Create an expense breakdown pie chart."""
    if data is None:
        # Sample data
        data = {
            "labels": ["Rent", "Utilities", "Supplies", "Marketing", "Travel", "Others"],
            "datasets": [{
                "data": [30, 15, 20, 25, 5, 5],
                "backgroundColor": [
                    "#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF", "#FF9F40"
                ]
            }]
        }
    
    return create_chart_component(
        chart_type="doughnut",
        title="Expense Breakdown",
        data=data,
        height="350px"
    )


def cash_flow_chart(data: Optional[Dict[str, Any]] = None) -> rx.Component:
    """Create a cash flow area chart."""
    if data is None:
        # Sample data
        data = {
            "labels": ["Week 1", "Week 2", "Week 3", "Week 4"],
            "datasets": [
                {
                    "label": "Cash In",
                    "data": [25000, 30000, 28000, 35000],
                    "borderColor": "#10B981",
                    "backgroundColor": "rgba(16, 185, 129, 0.3)"
                },
                {
                    "label": "Cash Out",
                    "data": [20000, 25000, 22000, 30000],
                    "borderColor": "#EF4444",
                    "backgroundColor": "rgba(239, 68, 68, 0.3)"
                }
            ]
        }
    
    return create_chart_component(
        chart_type="area",
        title="Cash Flow",
        data=data,
        height="350px"
    )


def top_customers_chart(data: Optional[Dict[str, Any]] = None) -> rx.Component:
    """Create a top customers bar chart."""
    if data is None:
        # Sample data
        data = {
            "labels": ["ABC Corp", "XYZ Ltd", "PQR Inc", "LMN Co", "RST Pvt"],
            "datasets": [{
                "label": "Sales Amount",
                "data": [125000, 98000, 87000, 76000, 65000],
                "backgroundColor": "#8B5CF6"
            }]
        }
    
    return create_chart_component(
        chart_type="bar",
        title="Top 5 Customers",
        data=data,
        height="350px"
    )


def monthly_comparison_chart(data: Optional[Dict[str, Any]] = None) -> rx.Component:
    """Create a monthly comparison bar chart."""
    if data is None:
        # Sample data
        data = {
            "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
            "datasets": [
                {
                    "label": "This Year",
                    "data": [45000, 52000, 48000, 61000, 55000, 67000],
                    "backgroundColor": "#3B82F6"
                },
                {
                    "label": "Last Year",
                    "data": [38000, 45000, 42000, 55000, 48000, 58000],
                    "backgroundColor": "#94A3B8"
                }
            ]
        }
    
    return create_chart_component(
        chart_type="bar",
        title="Monthly Sales Comparison",
        data=data,
        height="350px"
    )


def profit_loss_chart(data: Optional[Dict[str, Any]] = None) -> rx.Component:
    """Create a profit/loss waterfall-style chart."""
    if data is None:
        # Sample data showing revenue, expenses, and profit
        data = {
            "labels": ["Revenue", "COGS", "Operating Exp", "Other Exp", "Net Profit"],
            "datasets": [{
                "label": "Amount",
                "data": [500000, -200000, -150000, -50000, 100000],
                "backgroundColor": [
                    "#10B981",  # Green for revenue
                    "#EF4444",  # Red for expenses
                    "#EF4444",  # Red for expenses
                    "#EF4444",  # Red for expenses
                    "#3B82F6"   # Blue for profit
                ]
            }]
        }
    
    return create_chart_component(
        chart_type="bar",
        title="Profit & Loss Summary",
        data=data,
        height="350px"
    )


def interactive_dashboard_charts() -> rx.Component:
    """Create a grid of interactive dashboard charts."""
    return rx.grid(
        sales_trend_chart(),
        expense_breakdown_chart(),
        cash_flow_chart(),
        top_customers_chart(),
        columns="2",
        spacing="6",
        width="100%"
    )