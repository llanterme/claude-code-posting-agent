"""LinkedIn API client for posting content and images."""

import os
import time
import mimetypes
from typing import Optional, Dict, Any
from pathlib import Path

import requests
from pydantic import BaseModel

from utils.logging import log_api_request, log_api_response, log_api_error


class LinkedInPostRequest(BaseModel):
    """Request model for LinkedIn posting."""
    content: str
    image_path: Optional[str] = None
    visibility: str = "PUBLIC"  # PUBLIC, CONNECTIONS, LOGGED_IN_MEMBERS


class LinkedInPostResponse(BaseModel):
    """Response model for LinkedIn posting."""
    success: bool
    linkedin_post_id: Optional[str] = None
    linkedin_url: Optional[str] = None
    error: Optional[str] = None
    execution_time_seconds: float


class LinkedInClient:
    """LinkedIn API client for posting content with images."""
    
    def __init__(self, access_token: Optional[str] = None):
        """Initialize LinkedIn client with access token.
        
        Args:
            access_token: LinkedIn access token. If None, loads from environment.
        """
        self.access_token = access_token or os.getenv("LINKEDIN_ACCESS_TOKEN")
        if not self.access_token:
            raise ValueError("LinkedIn access token not provided. Set LINKEDIN_ACCESS_TOKEN environment variable.")
        
        self.base_url = "https://api.linkedin.com/v2"
        self.person_id = os.getenv("LINKEDIN_PERSON_ID")
        if not self.person_id:
            raise ValueError("LinkedIn person ID not provided. Set LINKEDIN_PERSON_ID environment variable.")
        
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
    
    def _make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Make HTTP request with proper error handling and logging.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            **kwargs: Additional arguments for requests
            
        Returns:
            Response object
            
        Raises:
            Exception: If request fails
        """
        try:
            log_api_request(url, kwargs.get("json", {}))
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
            log_api_response(url, response.json() if response.content else {}, 0)
            return response
        except requests.RequestException as e:
            log_api_error(url, e, kwargs.get("json", {}))
            raise Exception(f"LinkedIn API request failed: {str(e)}")
    
    def _upload_image(self, image_path: str) -> str:
        """Upload image to LinkedIn and return the asset URN.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Asset URN for the uploaded image
            
        Raises:
            Exception: If image upload fails
        """
        # Step 1: Register upload
        register_url = f"{self.base_url}/assets?action=registerUpload"
        
        # Determine file type
        mime_type, _ = mimetypes.guess_type(image_path)
        if not mime_type or not mime_type.startswith('image/'):
            raise Exception(f"Invalid image file type: {mime_type}")
        
        register_payload = {
            "registerUploadRequest": {
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                "owner": f"urn:li:person:{self.person_id}",
                "serviceRelationships": [
                    {
                        "relationshipType": "OWNER",
                        "identifier": "urn:li:userGeneratedContent"
                    }
                ]
            }
        }
        
        register_response = self._make_request("POST", register_url, headers=self.headers, json=register_payload)
        register_data = register_response.json()
        
        # Extract upload URL and asset URN
        upload_mechanism = register_data["value"]["uploadMechanism"]
        upload_url = upload_mechanism["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
        asset_urn = register_data["value"]["asset"]
        
        # Step 2: Upload the image binary
        with open(image_path, 'rb') as image_file:
            image_data = image_file.read()
        
        upload_headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": mime_type
        }
        
        upload_response = requests.post(upload_url, headers=upload_headers, data=image_data)
        upload_response.raise_for_status()
        
        return asset_urn
    
    def post_content(self, request: LinkedInPostRequest) -> LinkedInPostResponse:
        """Post content to LinkedIn with optional image.
        
        Args:
            request: LinkedIn post request with content and optional image
            
        Returns:
            LinkedIn post response with success status and post details
        """
        start_time = time.time()
        
        try:
            # Prepare the base post payload
            post_payload = {
                "author": f"urn:li:person:{self.person_id}",
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": request.content
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": request.visibility
                }
            }
            
            # Handle image upload if provided
            if request.image_path:
                # Validate image file exists
                if not os.path.exists(request.image_path):
                    raise Exception(f"Image file not found: {request.image_path}")
                
                # Upload image and get asset URN
                asset_urn = self._upload_image(request.image_path)
                
                # Update payload to include image
                post_payload["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "IMAGE"
                post_payload["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [
                    {
                        "status": "READY",
                        "description": {
                            "text": "Generated content image"
                        },
                        "media": asset_urn,
                        "title": {
                            "text": "AI Generated Image"
                        }
                    }
                ]
            
            # Post to LinkedIn
            post_url = f"{self.base_url}/ugcPosts"
            post_response = self._make_request("POST", post_url, headers=self.headers, json=post_payload)
            post_data = post_response.json()
            
            # Extract post ID and construct URL
            post_id = post_data.get("id", "")
            linkedin_url = f"https://www.linkedin.com/feed/update/{post_id}" if post_id else None
            
            execution_time = time.time() - start_time
            
            return LinkedInPostResponse(
                success=True,
                linkedin_post_id=post_id,
                linkedin_url=linkedin_url,
                execution_time_seconds=execution_time
            )
            
        except Exception as error:
            execution_time = time.time() - start_time
            return LinkedInPostResponse(
                success=False,
                error=str(error),
                execution_time_seconds=execution_time
            )


def validate_linkedin_config() -> Dict[str, Any]:
    """Validate LinkedIn configuration and return status.
    
    Returns:
        Dictionary with validation status and details
    """
    config_status = {
        "linkedin_configured": False,
        "has_access_token": False,
        "has_person_id": False,
        "error": None
    }
    
    try:
        access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
        person_id = os.getenv("LINKEDIN_PERSON_ID")
        
        config_status["has_access_token"] = bool(access_token)
        config_status["has_person_id"] = bool(person_id)
        config_status["linkedin_configured"] = bool(access_token and person_id)
        
        if not config_status["linkedin_configured"]:
            missing = []
            if not access_token:
                missing.append("LINKEDIN_ACCESS_TOKEN")
            if not person_id:
                missing.append("LINKEDIN_PERSON_ID")
            config_status["error"] = f"Missing environment variables: {', '.join(missing)}"
        
    except Exception as error:
        config_status["error"] = str(error)
    
    return config_status


def get_supported_image_formats() -> list[str]:
    """Get list of supported image formats for LinkedIn.
    
    Returns:
        List of supported image file extensions
    """
    return ["png", "jpg", "jpeg", "gif"]


def validate_image_file(image_path: str) -> bool:
    """Validate if image file is suitable for LinkedIn posting.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        True if image is valid, False otherwise
    """
    if not os.path.exists(image_path):
        return False
    
    # Check file extension
    file_ext = Path(image_path).suffix.lower().lstrip('.')
    if file_ext not in get_supported_image_formats():
        return False
    
    # Check file size (LinkedIn limit is 20MB)
    file_size = os.path.getsize(image_path)
    max_size = 20 * 1024 * 1024  # 20MB in bytes
    if file_size > max_size:
        return False
    
    return True