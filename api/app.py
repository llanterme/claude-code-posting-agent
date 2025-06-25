"""FastAPI application for multi-agent content generation system."""

import asyncio
import os
import time
from typing import Dict, Any, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from flow.graph import execute_workflow, get_workflow_status
from models.schema import ResearchRequest, ContentRequest, ImageRequest
from utils.logging import log_api_request, log_api_response, log_api_error, setup_logfire
from linkedin.client import LinkedInClient, LinkedInPostRequest, LinkedInPostResponse, validate_linkedin_config


class GenerateContentRequest(BaseModel):
    """Request model for content generation endpoint."""
    topic: str
    platform: str = "general"
    tone: str = "informative"


class GenerateContentResponse(BaseModel):
    """Response model for content generation endpoint."""
    success: bool
    topic: str
    platform: str
    tone: str
    research_bullet_points: List[str] = []
    generated_content: str = ""
    word_count: int = 0
    generated_image_path: str = None
    execution_time_seconds: float
    error: str = None
    metadata: Dict[str, Any] = {}


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str
    timestamp: str
    version: str


class StatusResponse(BaseModel):
    """Response model for status endpoint."""
    service: str
    workflow_status: Dict[str, Any]
    dependencies: Dict[str, str]
    health: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    print("🚀 FastAPI Multi-Agent Content Generation System starting up...")
    setup_logfire()
    yield
    # Shutdown
    print("🛑 FastAPI Multi-Agent Content Generation System shutting down...")


# Initialize FastAPI app
app = FastAPI(
    title="Multi-Agent Content Generation API",
    description="FastAPI wrapper for multi-agent LLM content generation system",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for images
app.mount("/static", StaticFiles(directory="data"), name="static")

# WebSocket connection manager
class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except:
            # Remove disconnected websocket
            self.disconnect(websocket)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove disconnected clients
                self.active_connections.remove(connection)


manager = ConnectionManager()


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint with basic health information."""
    return HealthResponse(
        status="healthy",
        timestamp=str(time.time()),
        version="1.0.0"
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=str(time.time()),
        version="1.0.0"
    )


@app.get("/status", response_model=StatusResponse)
async def get_status():
    """Get detailed system status and workflow information."""
    try:
        workflow_status = get_workflow_status()
        
        return StatusResponse(
            service="Multi-Agent Content Generation API",
            workflow_status=workflow_status,
            dependencies={
                "pydantic_ai": "0.2.15",
                "langgraph": "0.4.8", 
                "openai": "1.84.0",
                "fastapi": "0.104.0",
                "uvicorn": "0.24.0"
            },
            health="healthy"
        )
    except Exception as error:
        log_api_error("/status", error, {})
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(error)}")


@app.post("/generate", response_model=GenerateContentResponse)
async def generate_content(request: GenerateContentRequest):
    """Generate content using the multi-agent workflow."""
    start_time = time.time()
    
    # Log incoming request
    log_api_request("/generate", request.model_dump())
    
    try:
        # Validate request parameters
        if not request.topic.strip():
            raise HTTPException(status_code=400, detail="Topic cannot be empty")
        
        supported_platforms = ["twitter", "linkedin", "blog", "general"]
        if request.platform.lower() not in supported_platforms:
            raise HTTPException(
                status_code=400, 
                detail=f"Platform must be one of: {', '.join(supported_platforms)}"
            )
        
        supported_tones = ["professional", "casual", "informative", "engaging"]
        if request.tone.lower() not in supported_tones:
            raise HTTPException(
                status_code=400,
                detail=f"Tone must be one of: {', '.join(supported_tones)}"
            )
        
        # Execute workflow
        result = execute_workflow(
            topic=request.topic,
            platform=request.platform,
            tone=request.tone
        )
        
        # Prepare response
        response = GenerateContentResponse(
            success=result["success"],
            topic=result["topic"],
            platform=result["platform"],
            tone=result["tone"],
            research_bullet_points=result.get("research_bullet_points", []),
            generated_content=result.get("generated_content", ""),
            word_count=result.get("word_count", 0),
            generated_image_path=result.get("generated_image_path"),
            execution_time_seconds=result["execution_time_seconds"],
            error=result.get("error"),
            metadata=result.get("metadata", {})
        )
        
        # Log successful response
        log_api_response("/generate", response.model_dump(), time.time() - start_time)
        
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as error:
        # Log error and return 500
        log_api_error("/generate", error, request.model_dump())
        raise HTTPException(status_code=500, detail=f"Content generation failed: {str(error)}")


@app.websocket("/ws/generate")
async def websocket_generate_content(websocket: WebSocket):
    """WebSocket endpoint for real-time content generation with progress updates."""
    await manager.connect(websocket)
    
    try:
        # Send initial connection confirmation
        await manager.send_personal_message(
            '{"status": "connected", "message": "WebSocket connected successfully"}',
            websocket
        )
        
        while True:
            # Receive generation request with proper error handling
            try:
                data = await websocket.receive_json()
            except WebSocketDisconnect:
                # Client disconnected, break the loop
                print("WebSocket client disconnected")
                break
            except Exception as e:
                # Only send error if WebSocket is still connected
                try:
                    await manager.send_personal_message(
                        f'{{"status": "error", "message": "Failed to receive data", "error": "{str(e)}"}}',
                        websocket
                    )
                except:
                    # WebSocket already closed, break the loop
                    break
                continue
            
            try:
                # Validate request
                request = GenerateContentRequest(**data)
                
                # Send progress updates
                await manager.send_personal_message(
                    f'{{"status": "started", "message": "Starting content generation for topic: {request.topic}"}}',
                    websocket
                )
                
                await manager.send_personal_message(
                    f'{{"status": "research", "message": "Executing research agent..."}}',
                    websocket
                )
                
                # Execute workflow (in production, you'd want to make this async)
                result = await asyncio.get_event_loop().run_in_executor(
                    None,
                    execute_workflow,
                    request.topic,
                    request.platform,
                    request.tone
                )
                
                if result["success"]:
                    await manager.send_personal_message(
                        f'{{"status": "content", "message": "Content generation completed successfully"}}',
                        websocket
                    )
                    
                    # Send final result
                    response = GenerateContentResponse(**result)
                    await manager.send_personal_message(
                        f'{{"status": "completed", "data": {response.model_dump_json()}}}',
                        websocket
                    )
                else:
                    await manager.send_personal_message(
                        f'{{"status": "error", "message": "Content generation failed", "error": "{result.get("error", "Unknown error")}"}}',
                        websocket
                    )
                    
            except Exception as error:
                try:
                    await manager.send_personal_message(
                        f'{{"status": "error", "message": "Request processing failed", "error": "{str(error)}"}}',
                        websocket
                    )
                except:
                    # WebSocket already closed
                    break
                
    except WebSocketDisconnect:
        print("WebSocket client disconnected")
    finally:
        # Always clean up the connection
        manager.disconnect(websocket)


@app.get("/platforms")
async def get_supported_platforms():
    """Get list of supported platforms."""
    return {
        "platforms": [
            {
                "name": "twitter",
                "display_name": "Twitter/X",
                "max_length": 280,
                "description": "Short-form social media content"
            },
            {
                "name": "linkedin", 
                "display_name": "LinkedIn",
                "max_length": 3000,
                "description": "Professional networking content"
            },
            {
                "name": "blog",
                "display_name": "Blog Post",
                "max_length": None,
                "description": "Long-form blog content"
            },
            {
                "name": "general",
                "display_name": "General",
                "max_length": None,
                "description": "General purpose content"
            }
        ]
    }


@app.get("/tones")
async def get_supported_tones():
    """Get list of supported content tones."""
    return {
        "tones": [
            {
                "name": "professional",
                "display_name": "Professional",
                "description": "Formal, authoritative, business-focused"
            },
            {
                "name": "casual",
                "display_name": "Casual", 
                "description": "Conversational, relatable, friendly"
            },
            {
                "name": "informative",
                "display_name": "Informative",
                "description": "Educational, fact-focused, clear explanations"
            },
            {
                "name": "engaging",
                "display_name": "Engaging",
                "description": "Enthusiastic, interactive, call-to-action oriented"
            }
        ]
    }


@app.post("/linkedin/post", response_model=LinkedInPostResponse)
async def post_to_linkedin(request: LinkedInPostRequest):
    """Post content to LinkedIn with optional image."""
    start_time = time.time()
    
    # Log incoming request
    log_api_request("/linkedin/post", request.model_dump())
    
    try:
        # Validate LinkedIn configuration
        config_status = validate_linkedin_config()
        if not config_status["linkedin_configured"]:
            raise HTTPException(
                status_code=500, 
                detail=f"LinkedIn not configured: {config_status['error']}"
            )
        
        # Validate request parameters
        if not request.content.strip():
            raise HTTPException(status_code=400, detail="Content cannot be empty")
        
        # Validate image file if provided
        if request.image_path:
            if not request.image_path.startswith(("/", "data/")):
                # Convert relative path to absolute path
                request.image_path = f"data/images/{request.image_path}"
            
            if not os.path.exists(request.image_path):
                raise HTTPException(
                    status_code=400, 
                    detail=f"Image file not found: {request.image_path}"
                )
        
        # Initialize LinkedIn client and post content
        linkedin_client = LinkedInClient()
        result = linkedin_client.post_content(request)
        
        # Log successful response
        log_api_response("/linkedin/post", result.model_dump(), time.time() - start_time)
        
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as error:
        # Log error and return 500
        log_api_error("/linkedin/post", error, request.model_dump())
        raise HTTPException(status_code=500, detail=f"LinkedIn posting failed: {str(error)}")


@app.get("/linkedin/status")
async def get_linkedin_status():
    """Get LinkedIn integration status and configuration."""
    try:
        config_status = validate_linkedin_config()
        return {
            "service": "LinkedIn Integration",
            "configured": config_status["linkedin_configured"],
            "status": "ready" if config_status["linkedin_configured"] else "not_configured",
            "details": config_status,
            "supported_image_formats": ["png", "jpg", "jpeg", "gif"],
            "max_image_size_mb": 20
        }
    except Exception as error:
        log_api_error("/linkedin/status", error, {})
        raise HTTPException(status_code=500, detail=f"LinkedIn status check failed: {str(error)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )