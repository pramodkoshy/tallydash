"""Reflex configuration file."""

import reflex as rx

config = rx.Config(
    app_name="tallydash",
    db_url="sqlite:///reflex.db",
    env=rx.Env.DEV,
    frontend_port=3000,
    backend_port=8000,
    api_url="http://localhost:8000",
    deploy_url=None,
    timeout=120,
    cors_allowed_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    # Enable bun for faster builds (optional)
    bun_path="$HOME/.bun/bin/bun",
    # Tailwind config (optional)
    tailwind={
        "theme": {
            "extend": {
                "colors": {
                    "primary": {
                        "50": "#eff6ff",
                        "500": "#3b82f6", 
                        "900": "#1e3a8a",
                    }
                }
            }
        }
    }
)