"""Content Agent implementation using PydanticAI."""

import time
from typing import Any, Dict
from pydantic_ai import Agent
from models.schema import ContentRequest, ContentResponse
from utils.logging import log_agent_start, log_agent_success, log_agent_error


# Content Agent with PydanticAI
content_agent = Agent(
    model="openai:gpt-4o",
    result_type=ContentResponse,
    system_prompt="""You are an expert content creator specializing in 
    platform-optimized content generation.

    Your responsibilities:
    1. Transform research bullet points into engaging, platform-specific content
    2. Adapt tone and style based on the specified tone requirement
    3. Optimize content format and length for the target platform
    4. Maintain factual accuracy from the research while making it engaging
    5. Include appropriate calls-to-action or engagement elements

    Platform-specific guidelines:
    - Twitter: CRITICAL - Must be under 280 characters total. Concise, engaging, hashtag-friendly
    - LinkedIn: Professional, thought-leadership focused (1300 chars ideal)
    - Blog: Comprehensive, structured, SEO-friendly (500-1000 words)
    - General: Balanced approach, moderate length (200-400 words)

    Tone guidelines:
    - Professional: Formal, authoritative, business-focused
    - Casual: Conversational, relatable, friendly
    - Informative: Educational, fact-focused, clear explanations
    - Engaging: Enthusiastic, interactive, call-to-action oriented

    Format your response as a ContentResponse with:
    - content: The generated platform-optimized content
    - platform: The target platform
    - word_count: Accurate word count of the content
    - metadata: Content strategy insights and optimization notes
    """
)


def execute_content_generation(request: ContentRequest) -> ContentResponse:
    """Execute content agent with proper logging and error handling.
    
    Args:
        request: ContentRequest with research data, platform, and tone
        
    Returns:
        ContentResponse with generated content and metadata
        
    Raises:
        Exception: If content agent execution fails
    """
    start_time = time.time()
    
    # Log agent start
    log_agent_start("ContentAgent", request.model_dump())
    
    try:
        # Prepare detailed prompt with research data
        research_bullets = "\n".join([
            f"• {bullet}" for bullet in request.research_data.bullet_points
        ])
        
        user_prompt = f"""Create content for {request.platform} platform with {request.tone} tone.

Research Topic: {request.research_data.topic}

Research Findings:
{research_bullets}

Requirements:
- Platform: {request.platform}
- Tone: {request.tone}
- Use the research findings as the factual foundation
- Optimize for the specified platform's format and audience
- Maintain the requested tone throughout
"""
        
        # Execute the content agent
        result = content_agent.run_sync(user_prompt)
        response = result.output
        
        # Ensure response includes request parameters
        response.platform = request.platform
        
        # Calculate accurate word count
        response.word_count = len(response.content.split())
        
        # Add execution metadata
        execution_time = time.time() - start_time
        response.metadata.update({
            "execution_time_seconds": execution_time,
            "agent_version": "1.0",
            "model_used": "openai:gpt-4o",
            "source_topic": request.research_data.topic,
            "requested_tone": request.tone,
            "bullet_points_used": len(request.research_data.bullet_points)
        })
        
        # Log successful completion
        log_agent_success(
            "ContentAgent", 
            response.model_dump(), 
            execution_time
        )
        
        return response
        
    except Exception as error:
        # Log error with request context
        log_agent_error("ContentAgent", error, request.model_dump())
        raise error


def validate_content_output(response: ContentResponse) -> bool:
    """Validate that content response meets platform requirements.
    
    Args:
        response: ContentResponse to validate
        
    Returns:
        True if response is valid, False otherwise
    """
    # Check that content is non-empty
    if not response.content or not response.content.strip():
        return False
    
    # Check platform-specific length requirements
    content_length = len(response.content)
    
    if response.platform.lower() == "twitter" and content_length > 280:
        return False
    elif response.platform.lower() == "linkedin" and content_length > 3000:
        return False
    
    # Check that word count is accurate (within reasonable margin)
    actual_word_count = len(response.content.split())
    if abs(response.word_count - actual_word_count) > 2:
        return False
    
    # Check that platform is specified
    if not response.platform or not response.platform.strip():
        return False
    
    return True


def get_platform_recommendations() -> Dict[str, Dict[str, Any]]:
    """Get platform-specific content recommendations.
    
    Returns:
        Dictionary of platform guidelines and best practices
    """
    return {
        "twitter": {
            "max_length": 280,
            "ideal_length": 240,
            "features": ["hashtags", "mentions", "emojis"],
            "style": "concise and engaging"
        },
        "linkedin": {
            "max_length": 3000,
            "ideal_length": 1300,
            "features": ["professional tone", "thought leadership", "industry insights"],
            "style": "professional and authoritative"
        },
        "blog": {
            "min_length": 500,
            "ideal_length": 1000,
            "features": ["SEO optimization", "structured headings", "detailed explanations"],
            "style": "comprehensive and informative"
        },
        "general": {
            "min_length": 200,
            "ideal_length": 400,
            "features": ["balanced approach", "moderate detail", "versatile format"],
            "style": "adaptable and clear"
        }
    }