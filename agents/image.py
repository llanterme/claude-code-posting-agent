"""Image Agent implementation using PydanticAI and OpenAI image generation."""

import os
import time
import re
import base64
from datetime import datetime
from typing import Any, Dict
from io import BytesIO
from pydantic_ai import Agent
from openai import OpenAI
import requests
from PIL import Image
from models.schema import ImageRequest, ImageResponse, ContentResponse
from utils.logging import (
    log_image_generation_start,
    log_image_generation_success,
    log_image_generation_error
)


# Image Agent with PydanticAI
image_agent = Agent(
    model="openai:gpt-4o",  # Using GPT-4o for prompt analysis
    output_type=str,  # Returns the image generation prompt
    system_prompt="""You are an expert visual content creator specializing in 
    generating descriptive prompts for image generation based on written content.

    Your responsibilities:
    1. Analyze the provided content to understand its core message and themes
    2. Create a detailed, descriptive prompt for image generation
    3. Focus on visual elements that would complement and enhance the content
    4. Consider the platform and tone to ensure appropriate visual style
    5. Generate prompts that are clear, specific, and actionable for image AI

    Guidelines for image prompts:
    - Be specific about visual elements, colors, composition, and style
    - Consider the content's mood and tone
    - Include relevant contextual details that enhance the message
    - Avoid text or words in the image description
    - Focus on scenes, objects, people, or abstract concepts that represent the content
    - Keep prompts concise but descriptive (2-3 sentences max)

    Platform considerations:
    - Twitter: Clean, engaging, eye-catching visuals
    - LinkedIn: Professional, business-oriented imagery
    - Blog: Comprehensive, illustrative visuals
    - General: Balanced, versatile imagery

    Return only the image generation prompt, nothing else.
    """
)


def create_image_prompt(content_response: ContentResponse) -> str:
    """Generate image prompt based on content data.
    
    Args:
        content_response: ContentResponse with generated content
        
    Returns:
        String prompt for image generation
        
    Raises:
        Exception: If prompt generation fails
    """
    try:
        # Prepare detailed prompt for image prompt generation
        user_prompt = f"""Create an image generation prompt based on this content:

Platform: {content_response.platform}
Content: {content_response.content}

The image should visually represent the key themes and message of this content.
Focus on creating a prompt that will generate a relevant, engaging image that complements the written content.
"""
        
        # Execute the agent to get image prompt
        result = image_agent.run_sync(user_prompt)
        image_prompt = result.output.strip()
        
        if not image_prompt:
            raise ValueError("Generated image prompt is empty")
            
        return image_prompt
        
    except Exception as error:
        raise Exception(f"Failed to create image prompt: {str(error)}")


def ensure_images_directory() -> str:
    """Ensure data/images directory exists and return path.
    
    Returns:
        String path to images directory
        
    Raises:
        Exception: If directory cannot be created
    """
    try:
        images_dir = "data/images"
        os.makedirs(images_dir, exist_ok=True)
        return images_dir
    except PermissionError:
        raise Exception("Cannot create data/images directory: Permission denied")
    except OSError as e:
        raise Exception(f"Cannot create data/images directory: {e}")


def generate_image_filename(topic: str, platform: str) -> str:
    """Generate unique filename for image.
    
    Args:
        topic: The research topic
        platform: Target platform
        
    Returns:
        String filename with timestamp and sanitized topic
    """
    # Create timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Sanitize topic for filename (remove special characters)
    topic_slug = re.sub(r'[^\w\s-]', '', topic)
    topic_slug = re.sub(r'\s+', '_', topic_slug)
    topic_slug = topic_slug.lower()[:30]  # Limit length
    
    # Sanitize platform
    platform_safe = re.sub(r'[^\w]', '', platform).lower()
    
    return f"{timestamp}_{topic_slug}_{platform_safe}.png"




def execute_image_generation(request: ImageRequest) -> ImageResponse:
    """Execute image agent with proper logging and error handling.
    
    Args:
        request: ImageRequest with content data and parameters
        
    Returns:
        ImageResponse with generated image path and metadata
        
    Raises:
        Exception: If image generation fails
    """
    start_time = time.time()
    
    # Log agent start
    log_image_generation_start(request.model_dump())
    
    try:
        # Ensure images directory exists
        images_dir = ensure_images_directory()
        
        # Generate image prompt based on content
        image_prompt = create_image_prompt(request.content_data)
        
        # Generate unique filename
        filename = generate_image_filename(
            request.topic, 
            request.content_data.platform
        )
        file_path = os.path.join(images_dir, filename)
        
        # Initialize OpenAI client
        client = OpenAI()
        
        # Generate image using OpenAI gpt-image-1
        try:
            # Generate image with gpt-image-1 (returns base64)
            response = client.images.generate(
                model="gpt-image-1",
                prompt=image_prompt,
                size=request.image_size,
                quality="medium",  # Options: "low", "medium", "high", "auto"
                output_format="png"  # Options: "png", "jpeg", "webp"
              
            )
            
            # Extract base64 image data from response
            if response.data and len(response.data) > 0:
                image_base64 = response.data[0].b64_json
                
                # Decode the base64 image
                image_bytes = base64.b64decode(image_base64)
                
                # Create an image from the bytes
                image = Image.open(BytesIO(image_bytes))
                
                # Save the image to file
                image.save(file_path, "PNG")
                
                # Get file size
                file_size = os.path.getsize(file_path)
                
            else:
                raise Exception("No image data in response")
                
        except Exception as e:
            raise Exception(f"Image generation failed: {str(e)}")
        
        # Calculate execution time
        execution_time = time.time() - start_time
        
        # Create response with metadata
        # Convert absolute path to relative URL path for web serving
        relative_path = os.path.relpath(file_path, "data")
        web_path = f"static/{relative_path}".replace("\\", "/")  # Ensure forward slashes for URLs
        
        image_response = ImageResponse(
            image_path=web_path,
            image_prompt=image_prompt,
            image_size=request.image_size,
            file_size_bytes=file_size,
            metadata={
                "execution_time_seconds": execution_time,
                "agent_version": "1.0",
                "model_used": "gpt-image-1",
                "source_content_platform": request.content_data.platform,
                "source_content_topic": request.topic,
                "image_style": request.image_style,
                "generation_timestamp": datetime.now().isoformat()
            }
        )
        
        # Log successful completion
        log_image_generation_success(
            image_response.model_dump(), 
            execution_time
        )
        
        return image_response
        
    except Exception as error:
        # Log error with request context
        log_image_generation_error(error, request.model_dump())
        raise error


def validate_image_output(response: ImageResponse) -> bool:
    """Validate that image response meets requirements.
    
    Args:
        response: ImageResponse to validate
        
    Returns:
        True if response is valid, False otherwise
    """
    # Check that file exists and is readable
    # Handle both web paths and absolute paths
    actual_file_path = response.image_path
    if response.image_path.startswith("static/"):
        actual_file_path = response.image_path.replace("static/", "data/")
    
    if not os.path.exists(actual_file_path):
        return False
    
    try:
        with open(actual_file_path, 'rb') as f:
            f.read(1)  # Try to read first byte
    except IOError:
        return False
    
    # Check file size is reasonable (between 1KB and 10MB)
    if response.file_size_bytes < 1000 or response.file_size_bytes > 10_000_000:
        return False
    
    # Check that required fields are present and non-empty
    if not response.image_prompt or not response.image_prompt.strip():
        return False
    
    if not response.image_size or not response.image_size.strip():
        return False
    
    # Check that file path exists (handle both absolute and relative web paths)
    if response.image_path.startswith("static/"):
        # Web path - convert back to actual file path for validation
        actual_file_path = response.image_path.replace("static/", "data/")
        if not os.path.exists(actual_file_path):
            return False
    else:
        # Absolute path - check directly
        if not os.path.isabs(response.image_path):
            return False
    
    return True


def get_supported_image_sizes() -> list[str]:
    """Get list of supported image sizes.
    
    Returns:
        List of supported image dimension strings
    """
    return ["1024x1024", "1792x1024", "1024x1792"]


def get_supported_image_styles() -> list[str]:
    """Get list of supported image styles.
    
    Returns:
        List of supported image style strings
    """
    return ["photorealistic", "artistic", "abstract", "minimalist", "professional"]