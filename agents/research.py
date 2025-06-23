"""Research Agent implementation using PydanticAI."""

import time
from typing import Any, Dict
from pydantic_ai import Agent
from models.schema import ResearchRequest, ResearchResponse
from utils.logging import log_agent_start, log_agent_success, log_agent_error


# Research Agent with PydanticAI
research_agent = Agent(
    model="openai:gpt-4o",
    result_type=ResearchResponse,
    system_prompt="""You are a expert researcher tasked with generating factual, 
    well-researched bullet points on any given topic.

    Your responsibilities:
    1. Generate exactly 5-7 factual bullet points about the topic
    2. Ensure each bullet point is informative and accurate
    3. Focus on the most important and relevant aspects of the topic
    4. Use clear, concise language suitable for content creation
    5. Include diverse perspectives and key facts about the topic

    Format your response as a ResearchResponse with:
    - bullet_points: List of 5-7 factual statements
    - topic: The original topic researched
    - metadata: Any relevant research context or sources considered
    """
)


def execute_research(request: ResearchRequest) -> ResearchResponse:
    """Execute research agent with proper logging and error handling.
    
    Args:
        request: ResearchRequest with topic and optional context
        
    Returns:
        ResearchResponse with bullet points and metadata
        
    Raises:
        Exception: If research agent execution fails
    """
    start_time = time.time()
    
    # Log agent start
    log_agent_start("ResearchAgent", request.model_dump())
    
    try:
        # Prepare the prompt with context if provided
        user_prompt = f"Research topic: {request.topic}"
        if request.context:
            user_prompt += f"\nAdditional context: {request.context}"
        
        # Execute the research agent
        result = research_agent.run_sync(user_prompt)
        response = result.output
        
        # Ensure the response includes the original topic
        if response.topic != request.topic:
            response.topic = request.topic
        
        # Add execution metadata
        execution_time = time.time() - start_time
        response.metadata.update({
            "execution_time_seconds": execution_time,
            "agent_version": "1.0",
            "model_used": "openai:gpt-4o"
        })
        
        # Log successful completion
        log_agent_success(
            "ResearchAgent", 
            response.model_dump(), 
            execution_time
        )
        
        return response
        
    except Exception as error:
        # Log error with request context
        log_agent_error("ResearchAgent", error, request.model_dump())
        raise error


def validate_research_output(response: ResearchResponse) -> bool:
    """Validate that research response meets requirements.
    
    Args:
        response: ResearchResponse to validate
        
    Returns:
        True if response is valid, False otherwise
    """
    # Check bullet points count (5-7 required)
    if not (5 <= len(response.bullet_points) <= 7):
        return False
    
    # Check that all bullet points are non-empty strings
    if not all(isinstance(bp, str) and bp.strip() for bp in response.bullet_points):
        return False
    
    # Check that topic is provided
    if not response.topic or not response.topic.strip():
        return False
    
    return True