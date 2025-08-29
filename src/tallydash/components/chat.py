import reflex as rx
from typing import List, Dict, Any
from ..models.app_models import AppState, AIMessage, MessageType


def message_bubble(message: AIMessage) -> rx.Component:
    """Create a message bubble component."""
    is_user = message.type == MessageType.USER
    
    return rx.hstack(
        rx.spacer() if is_user else rx.box(),
        rx.card(
            rx.vstack(
                rx.text(
                    message.content,
                    size="3",
                    line_height="1.5",
                    white_space="pre-wrap"
                ),
                rx.text(
                    message.timestamp.strftime("%H:%M") if hasattr(message.timestamp, 'strftime') 
                    else str(message.timestamp)[:5],
                    size="1",
                    color="gray",
                    align="right" if is_user else "left"
                ),
                align_items="stretch",
                spacing="2"
            ),
            background_color="var(--accent-3)" if is_user else "var(--gray-3)",
            color="var(--accent-12)" if is_user else "var(--gray-12)",
            max_width="70%",
            width="auto",
            padding="3"
        ),
        rx.spacer() if not is_user else rx.box(),
        width="100%",
        margin="2"
    )


def typing_indicator() -> rx.Component:
    """Create a typing indicator component."""
    return rx.hstack(
        rx.card(
            rx.hstack(
                rx.text("AI is thinking", size="2", color="gray"),
                rx.spinner(size="1"),
                align="center",
                spacing="2"
            ),
            background_color="var(--gray-3)",
            padding="3",
            max_width="150px"
        ),
        rx.spacer(),
        width="100%",
        margin="2"
    )


def quick_suggestions() -> rx.Component:
    """Create quick suggestion buttons."""
    suggestions = [
        "Show me sales for this month",
        "Top 5 customers by revenue", 
        "Cash flow analysis",
        "Expense breakdown",
        "Outstanding receivables"
    ]
    
    return rx.vstack(
        rx.text("Quick suggestions:", size="2", color="gray", weight="bold"),
        rx.wrap(
            *[
                rx.button(
                    suggestion,
                    variant="outline",
                    size="1",
                    on_click=AppState.set_current_message(suggestion),
                    style={"font-size": "12px", "padding": "6px 12px"}
                )
                for suggestion in suggestions
            ],
            spacing="2"
        ),
        width="100%",
        spacing="2",
        padding="3",
        background_color="var(--gray-2)",
        border_radius="8px"
    )


def chat_input() -> rx.Component:
    """Create chat input component."""
    return rx.hstack(
        rx.input(
            placeholder="Ask me about your Tally data...",
            value=AppState.current_message,
            on_change=AppState.set_current_message,
            on_key_down=lambda key: AppState.send_message() if key == "Enter" else None,
            width="100%",
            size="3"
        ),
        rx.button(
            rx.icon("send", size=18),
            on_click=AppState.send_message,
            disabled=AppState.is_ai_processing,
            size="3",
            color_scheme="blue"
        ),
        width="100%",
        spacing="2"
    )


def chat_header() -> rx.Component:
    """Create chat header with controls."""
    return rx.hstack(
        rx.hstack(
            rx.icon("bot", size=20, color="blue"),
            rx.heading("AI Assistant", size="4"),
            align="center",
            spacing="2"
        ),
        rx.spacer(),
        rx.hstack(
            rx.button(
                rx.icon("trash-2", size=16),
                variant="ghost",
                size="2",
                on_click=AppState.clear_ai_chat,
                title="Clear chat"
            ),
            rx.button(
                rx.icon("minimize-2", size=16),
                variant="ghost", 
                size="2",
                title="Minimize chat"
            ),
            spacing="1"
        ),
        width="100%",
        align="center",
        padding="3",
        border_bottom="1px solid var(--gray-6)"
    )


def chat_messages_area() -> rx.Component:
    """Create scrollable messages area."""
    return rx.scroll_area(
        rx.vstack(
            rx.cond(
                AppState.ai_messages.length() == 0,
                rx.vstack(
                    rx.icon("message-circle", size=48, color="gray"),
                    rx.text("Start a conversation!", size="4", color="gray", weight="bold"),
                    rx.text(
                        "Ask me anything about your Tally data. I can help with sales analysis, expense tracking, customer insights, and more.",
                        size="2",
                        color="gray",
                        text_align="center",
                        max_width="300px"
                    ),
                    align="center",
                    spacing="3",
                    padding="6"
                ),
                rx.vstack(
                    rx.foreach(
                        AppState.ai_messages,
                        message_bubble
                    ),
                    rx.cond(
                        AppState.is_ai_processing,
                        typing_indicator(),
                        rx.box()
                    ),
                    width="100%",
                    spacing="1"
                )
            ),
            width="100%",
            min_height="400px"
        ),
        width="100%",
        height="400px",
        padding="2"
    )


def ai_chat_component() -> rx.Component:
    """Create the main AI chat component."""
    return rx.card(
        rx.vstack(
            chat_header(),
            chat_messages_area(),
            rx.divider(),
            rx.cond(
                AppState.ai_messages.length() == 0,
                quick_suggestions(),
                rx.box()
            ),
            chat_input(),
            width="100%",
            spacing="0"
        ),
        width="100%",
        max_width="500px",
        height="600px",
        background_color="white",
        shadow="lg"
    )


def floating_chat_button() -> rx.Component:
    """Create a floating chat button."""
    return rx.button(
        rx.icon("message-circle", size=24),
        position="fixed",
        bottom="20px",
        right="20px",
        z_index="1000",
        size="4",
        border_radius="50%",
        background_color="var(--accent-9)",
        color="white",
        shadow="lg",
        _hover={
            "background_color": "var(--accent-10)",
            "transform": "scale(1.1)"
        },
        transition="all 0.2s ease"
    )


def chat_sidebar() -> rx.Component:
    """Create a chat sidebar component."""
    return rx.vstack(
        rx.hstack(
            rx.icon("bot", size=20, color="blue"),
            rx.heading("AI Assistant", size="4"),
            rx.spacer(),
            rx.button(
                rx.icon("x", size=16),
                variant="ghost",
                size="2"
            ),
            width="100%",
            align="center",
            padding="4",
            border_bottom="1px solid var(--gray-6)"
        ),
        chat_messages_area(),
        rx.divider(),
        rx.cond(
            AppState.ai_messages.length() == 0,
            quick_suggestions(),
            rx.box()
        ),
        chat_input(),
        width="400px",
        height="100vh",
        background_color="white",
        border_left="1px solid var(--gray-6)",
        position="fixed",
        right="0",
        top="0",
        z_index="100",
        shadow="lg"
    )


def embedded_chat_panel() -> rx.Component:
    """Create an embedded chat panel for dashboard."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.icon("bot", size=18, color="blue"),
                rx.text("AI Assistant", size="3", weight="bold"),
                rx.spacer(),
                rx.badge("Online", color_scheme="green", size="1"),
                width="100%",
                align="center"
            ),
            rx.scroll_area(
                rx.vstack(
                    rx.cond(
                        AppState.ai_messages.length() == 0,
                        rx.text(
                            "Ask me about your data!",
                            size="2",
                            color="gray",
                            text_align="center",
                            padding="4"
                        ),
                        rx.foreach(
                            AppState.ai_messages.slice(-3),  # Show last 3 messages
                            lambda msg: rx.hstack(
                                rx.text(
                                    msg.content,
                                    size="2",
                                    max_width="200px",
                                    overflow="hidden",
                                    text_overflow="ellipsis"
                                ),
                                width="100%"
                            )
                        )
                    ),
                    width="100%",
                    spacing="2"
                ),
                height="120px",
                width="100%"
            ),
            rx.input(
                placeholder="Quick question...",
                size="2",
                on_key_down=lambda key: AppState.send_message() if key == "Enter" else None
            ),
            width="100%",
            spacing="3"
        ),
        width="300px",
        height="200px",
        padding="3"
    )