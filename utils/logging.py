"""Logfire integration for structured logging and tracing."""

import os
from typing import Any, Dict, Optional
import logfire
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def setup_logfire() -> None:
    """Initialize Logfire for structured logging and tracing.
    
    Configures Logfire with project settings and authentication.
    Should be called once at application startup.
    """
    # Configure Logfire with project token from environment
    logfire_token = os.getenv("LOGFIRE_TOKEN")
    if logfire_token:
        logfire.configure(token=logfire_token)
    else:
        # Configure for local development without token
        logfire.configure(send_to_logfire=False)


def log_agent_start(agent_name: str, request_data: Dict[str, Any]) -> None:
    """Log the start of an agent execution.
    
    Args:
        agent_name: Name of the agent being executed
        request_data: Input data for the agent
    """
    logfire.info(
        "Agent execution started",
        agent=agent_name,
        request=request_data
    )


def log_agent_success(
    agent_name: str, 
    response_data: Dict[str, Any],
    execution_time: Optional[float] = None
) -> None:
    """Log successful completion of an agent execution.
    
    Args:
        agent_name: Name of the agent that completed
        response_data: Output data from the agent
        execution_time: Optional execution time in seconds
    """
    log_data = {
        "agent": agent_name,
        "response": response_data,
        "status": "success"
    }
    
    if execution_time is not None:
        log_data["execution_time_seconds"] = execution_time
    
    logfire.info("Agent execution completed", **log_data)


def log_agent_error(
    agent_name: str, 
    error: Exception,
    request_data: Optional[Dict[str, Any]] = None
) -> None:
    """Log an error during agent execution.
    
    Args:
        agent_name: Name of the agent that failed
        error: Exception that occurred
        request_data: Optional input data that caused the error
    """
    log_data = {
        "agent": agent_name,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "status": "error"
    }
    
    if request_data is not None:
        log_data["request"] = request_data
    
    logfire.error("Agent execution failed", **log_data)


def log_workflow_start(topic: str, platform: str, tone: str) -> None:
    """Log the start of a complete workflow execution.
    
    Args:
        topic: Research topic
        platform: Target platform
        tone: Content tone
    """
    logfire.info(
        "Workflow execution started",
        topic=topic,
        platform=platform,
        tone=tone
    )


def log_workflow_success(
    topic: str,
    final_content: str,
    execution_time: Optional[float] = None
) -> None:
    """Log successful completion of a workflow.
    
    Args:
        topic: Research topic
        final_content: Generated content
        execution_time: Optional total execution time in seconds
    """
    log_data = {
        "topic": topic,
        "content_length": len(final_content),
        "status": "success"
    }
    
    if execution_time is not None:
        log_data["total_execution_time_seconds"] = execution_time
    
    logfire.info("Workflow completed successfully", **log_data)


def log_workflow_error(topic: str, error: Exception) -> None:
    """Log an error during workflow execution.
    
    Args:
        topic: Research topic
        error: Exception that occurred
    """
    logfire.error(
        "Workflow execution failed",
        topic=topic,
        error_type=type(error).__name__,
        error_message=str(error),
        status="error"
    )


def log_image_generation_start(request_data: Dict[str, Any]) -> None:
    """Log the start of image generation process.
    
    Args:
        request_data: Input data for image generation
    """
    logfire.info(
        "Image generation started",
        agent="ImageAgent",
        request=request_data
    )


def log_image_generation_success(
    response_data: Dict[str, Any], 
    execution_time: Optional[float] = None
) -> None:
    """Log successful image generation.
    
    Args:
        response_data: Output data from image generation
        execution_time: Optional execution time in seconds
    """
    log_data = {
        "agent": "ImageAgent",
        "response": response_data,
        "status": "success"
    }
    
    if execution_time is not None:
        log_data["execution_time_seconds"] = execution_time
    
    logfire.info("Image generation completed", **log_data)


def log_image_generation_error(
    error: Exception, 
    request_data: Optional[Dict[str, Any]] = None
) -> None:
    """Log image generation errors.
    
    Args:
        error: Exception that occurred
        request_data: Optional input data that caused the error
    """
    log_data = {
        "agent": "ImageAgent",
        "error_type": type(error).__name__,
        "error_message": str(error),
        "status": "error"
    }
    
    if request_data is not None:
        log_data["request"] = request_data
    
    logfire.error("Image generation failed", **log_data)