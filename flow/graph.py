"""LangGraph workflow orchestration for multi-agent pipeline."""

import time
from typing import Any, Dict
from langgraph.graph import StateGraph
from models.schema import (
    WorkflowState, 
    ResearchRequest, 
    ContentRequest,
    ImageRequest
)
from agents.research import execute_research, validate_research_output
from agents.content import execute_content_generation, validate_content_output
from agents.image import execute_image_generation, validate_image_output
from utils.logging import (
    log_workflow_start, 
    log_workflow_success, 
    log_workflow_error
)


def research_node(state: WorkflowState) -> WorkflowState:
    """LangGraph node for research agent execution.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated workflow state with research results
    """
    try:
        # Create research request from state
        research_request = ResearchRequest(
            topic=state["topic"],
            context=f"Target platform: {state['platform']}, Tone: {state['tone']}"
        )
        
        # Store request in state
        state["research_request"] = research_request
        
        # Execute research agent
        research_response = execute_research(research_request)
        
        # Validate research output
        if not validate_research_output(research_response):
            raise ValueError("Research output validation failed")
        
        # Update state with results
        state["research_response"] = research_response
        
        return state
        
    except Exception as error:
        state["error"] = f"Research node failed: {str(error)}"
        return state


def content_node(state: WorkflowState) -> WorkflowState:
    """LangGraph node for content agent execution.
    
    Args:
        state: Current workflow state with research results
        
    Returns:
        Updated workflow state with content generation results
    """
    try:
        # Check if research was successful
        if state.get("error") or not state.get("research_response"):
            raise ValueError("Cannot proceed without valid research results")
        
        # Create content request from state
        content_request = ContentRequest(
            research_data=state["research_response"],
            platform=state["platform"],
            tone=state["tone"]
        )
        
        # Store request in state
        state["content_request"] = content_request
        
        # Execute content agent
        content_response = execute_content_generation(content_request)
        
        # Validate content output
        if not validate_content_output(content_response):
            raise ValueError("Content output validation failed")
        
        # Update state with results
        state["content_response"] = content_response
        
        return state
        
    except Exception as error:
        state["error"] = f"Content node failed: {str(error)}"
        return state


def image_node(state: WorkflowState) -> WorkflowState:
    """LangGraph node for image generation.
    
    Args:
        state: Current workflow state with content results
        
    Returns:
        Updated workflow state with image generation results
    """
    try:
        # Check if content generation was successful
        if state.get("error") or not state.get("content_response"):
            raise ValueError("Cannot proceed without valid content results")
        
        # Create image request from state
        image_request = ImageRequest(
            content_data=state["content_response"],
            topic=state["topic"],
            image_style="photorealistic",
            image_size="1024x1024"
        )
        
        # Store request in state
        state["image_request"] = image_request
        
        # Execute image generation agent
        image_response = execute_image_generation(image_request)
        
        # Validate image output
        if not validate_image_output(image_response):
            raise ValueError("Image output validation failed")
        
        # Update state with results
        state["image_response"] = image_response
        
        return state
        
    except Exception as error:
        # Log error but don't break workflow - content is still available
        state["error"] = f"Image generation failed: {str(error)}"
        return state


def should_continue_to_content(state: WorkflowState) -> str:
    """Conditional edge function to determine workflow continuation.
    
    Args:
        state: Current workflow state
        
    Returns:
        Next node to execute or "END" to terminate
    """
    if state.get("error"):
        return "END"
    
    if state.get("research_response"):
        return "content"
    
    return "END"


def should_continue_to_image(state: WorkflowState) -> str:
    """Conditional edge function for image generation.
    
    Args:
        state: Current workflow state
        
    Returns:
        Next node to execute or "END" to terminate
    """
    # Check if there was an error that prevents image generation
    if state.get("error") and "Content node failed" in state.get("error", ""):
        return "END"
    
    # Continue to image generation if content was successful
    if state.get("content_response"):
        return "image"
    
    return "END"


def create_workflow_graph() -> StateGraph:
    """Create and configure the LangGraph workflow.
    
    Returns:
        Configured StateGraph ready for execution
    """
    # Initialize the state graph
    workflow = StateGraph(WorkflowState)
    
    # Add nodes
    workflow.add_node("research", research_node)
    workflow.add_node("content", content_node)
    workflow.add_node("image", image_node)
    
    # Set entry point
    workflow.set_entry_point("research")
    
    # Add conditional edge from research to content
    workflow.add_conditional_edges(
        "research",
        should_continue_to_content,
        {
            "content": "content",
            "END": "__end__"
        }
    )
    
    # Add conditional edge from content to image
    workflow.add_conditional_edges(
        "content",
        should_continue_to_image,
        {
            "image": "image",
            "END": "__end__"
        }
    )
    
    # Add edge from image to end
    workflow.add_edge("image", "__end__")
    
    # Compile the graph
    return workflow.compile()


def execute_workflow(
    topic: str, 
    platform: str = "general", 
    tone: str = "informative"
) -> Dict[str, Any]:
    """Execute the complete multi-agent workflow.
    
    Args:
        topic: Research topic for content generation
        platform: Target platform for content optimization
        tone: Desired tone for the generated content
        
    Returns:
        Dictionary with workflow results and metadata
        
    Raises:
        Exception: If workflow execution fails
    """
    start_time = time.time()
    
    # Log workflow start
    log_workflow_start(topic, platform, tone)
    
    try:
        # Create workflow graph
        app = create_workflow_graph()
        
        # Initialize workflow state
        initial_state: WorkflowState = {
            "topic": topic,
            "platform": platform,
            "tone": tone,
            "research_request": None,
            "research_response": None,
            "content_request": None,
            "content_response": None,
            "image_request": None,
            "image_response": None,
            "error": None
        }
        
        # Execute workflow
        final_state = app.invoke(initial_state)
        
        # Check for workflow errors
        if final_state.get("error"):
            raise Exception(final_state["error"])
        
        # Check for successful completion
        if not final_state.get("content_response"):
            raise Exception("Workflow completed without generating content")
        
        # Calculate execution time
        execution_time = time.time() - start_time
        
        # Prepare results
        results = {
            "success": True,
            "topic": topic,
            "platform": platform,
            "tone": tone,
            "research_bullet_points": final_state["research_response"].bullet_points,
            "generated_content": final_state["content_response"].content,
            "word_count": final_state["content_response"].word_count,
            "generated_image_path": final_state["image_response"].image_path if final_state.get("image_response") else None,
            "execution_time_seconds": execution_time,
            "metadata": {
                "research_metadata": final_state["research_response"].metadata,
                "content_metadata": final_state["content_response"].metadata,
                "image_metadata": final_state["image_response"].metadata if final_state.get("image_response") else None
            }
        }
        
        # Log successful completion
        log_workflow_success(
            topic, 
            final_state["content_response"].content, 
            execution_time
        )
        
        return results
        
    except Exception as error:
        # Log workflow error
        log_workflow_error(topic, error)
        
        # Return error result
        return {
            "success": False,
            "topic": topic,
            "platform": platform,
            "tone": tone,
            "error": str(error),
            "execution_time_seconds": time.time() - start_time
        }


def get_workflow_status() -> Dict[str, Any]:
    """Get information about the workflow configuration.
    
    Returns:
        Dictionary with workflow metadata and capabilities
    """
    return {
        "workflow_version": "1.1",
        "agents": ["ResearchAgent", "ContentAgent", "ImageAgent"],
        "supported_platforms": ["twitter", "linkedin", "blog", "general"],
        "supported_tones": ["professional", "casual", "informative", "engaging"],
        "execution_flow": ["research", "content", "image"],
        "dependencies": {
            "pydantic_ai": "0.2.15",
            "langgraph": "0.4.8",
            "openai": "1.84.0",
            "logfire": "3.18.0"
        }
    }