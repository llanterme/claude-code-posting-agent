#!/usr/bin/env python3
"""Development server runner for FastAPI application."""

import uvicorn
from utils.logging import setup_logfire

if __name__ == "__main__":
    # Initialize logging before starting server
    setup_logfire()
    
    # Run the FastAPI application
    uvicorn.run(
        "api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    )