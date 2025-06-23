"""Pydantic models for agent input/output and workflow state management."""

from typing import Any, Dict, List, Optional, TypedDict
from pydantic import BaseModel, Field


class ResearchRequest(BaseModel):
    """Request model for research agent."""
    
    topic: str = Field(
        description="The topic to research and generate bullet points for"
    )
    context: Optional[str] = Field(
        default=None,
        description="Additional context or constraints for the research"
    )


class ResearchResponse(BaseModel):
    """Response model for research agent output."""
    
    bullet_points: List[str] = Field(
        description="List of 5-7 factual bullet points about the topic",
        min_length=5,
        max_length=7
    )
    topic: str = Field(
        description="The original topic that was researched"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about the research process"
    )


class ContentRequest(BaseModel):
    """Request model for content agent."""
    
    research_data: ResearchResponse = Field(
        description="Research data from the research agent"
    )
    platform: str = Field(
        description="Target platform for content (e.g., 'twitter', 'linkedin', 'blog')"
    )
    tone: str = Field(
        description="Desired tone for the content (e.g., 'professional', 'casual', 'informative')"
    )


class ContentResponse(BaseModel):
    """Response model for content agent output."""
    
    content: str = Field(
        description="Generated platform-specific content"
    )
    platform: str = Field(
        description="Target platform the content was optimized for"
    )
    word_count: int = Field(
        description="Number of words in the generated content"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about the content generation process"
    )


class ImageRequest(BaseModel):
    """Request model for image generation agent."""
    
    content_data: ContentResponse = Field(
        description="Generated content to base image generation on"
    )
    topic: str = Field(
        description="The original research topic for filename generation"
    )
    image_style: str = Field(
        default="photorealistic",
        description="Style for image generation (photorealistic, artistic, etc.)"
    )
    image_size: str = Field(
        default="1024x1024",
        description="Image dimensions (1024x1024, 1792x1024, 1024x1792)"
    )


class ImageResponse(BaseModel):
    """Response model for image generation agent."""
    
    image_path: str = Field(
        description="Full file path where the generated image was saved"
    )
    image_prompt: str = Field(
        description="The prompt used to generate the image"
    )
    image_size: str = Field(
        description="Dimensions of the generated image"
    )
    file_size_bytes: int = Field(
        description="Size of the generated image file in bytes"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about image generation process"
    )


class WorkflowState(TypedDict):
    """TypedDict for LangGraph workflow state management."""
    
    topic: str
    platform: str
    tone: str
    research_request: Optional[ResearchRequest]
    research_response: Optional[ResearchResponse]
    content_request: Optional[ContentRequest]
    content_response: Optional[ContentResponse]
    image_request: Optional[ImageRequest]
    image_response: Optional[ImageResponse]
    error: Optional[str]