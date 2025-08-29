#!/usr/bin/env python3
"""TallyDash application runner."""

import os
import sys
import logging
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from tallydash.app import app
from tallydash.config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format=settings.log_format,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("tallydash.log")
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Main application entry point."""
    logger.info(f"Starting TallyDash on {settings.host}:{settings.port}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Tally ODBC: {settings.tally_host}:{settings.tally_port}")
    
    try:
        # Run the Reflex app
        app.run(
            host=settings.host,
            port=settings.port,
            debug=settings.debug
        )
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()