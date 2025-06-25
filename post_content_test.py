"""Test script for LinkedIn posting functionality."""

import os
import sys
import random
from pathlib import Path

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from linkedin.client import LinkedInClient, LinkedInPostRequest, validate_linkedin_config
from utils.logging import log_api_request, log_api_response


def get_random_test_content() -> str:
    """Generate random test content for LinkedIn posting."""
    test_contents = [
        "🚀 Testing LinkedIn API integration! Exciting times ahead for automated content generation. #AI #Tech #Innovation",
        "💡 Just implemented multi-agent content generation with image support. The future of content creation is here! #ContentGeneration #AI",
        "🎯 Exploring the intersection of AI and social media automation. What amazing possibilities lie ahead! #SocialMedia #Automation",
        "⚡ Building the next generation of intelligent content systems. Each step brings new insights! #MachineLearning #ContentAI",
        "🌟 From research to content to images - fully automated pipeline working seamlessly. Technology at its finest! #Pipeline #AI"
    ]
    return random.choice(test_contents)


def get_random_test_image() -> str:
    """Get a random test image from the data/images directory."""
    images_dir = Path("data/images")
    
    if not images_dir.exists():
        print(f"Images directory not found: {images_dir}")
        return None
    
    image_files = list(images_dir.glob("*.png")) + list(images_dir.glob("*.jpg")) + list(images_dir.glob("*.jpeg"))
    
    if not image_files:
        print("No image files found in data/images/")
        return None
    
    return str(random.choice(image_files))


def test_linkedin_config():
    """Test LinkedIn configuration validation."""
    print("=" * 60)
    print("TESTING LINKEDIN CONFIGURATION")
    print("=" * 60)
    
    config_status = validate_linkedin_config()
    print(f"Configuration Status: {config_status}")
    
    if config_status["linkedin_configured"]:
        print("✅ LinkedIn is properly configured!")
        return True
    else:
        print("❌ LinkedIn configuration issues:")
        print(f"   Error: {config_status['error']}")
        print("\nPlease set the following environment variables:")
        if not config_status["has_access_token"]:
            print("   - LINKEDIN_ACCESS_TOKEN")
        if not config_status["has_person_id"]:
            print("   - LINKEDIN_PERSON_ID")
        return False


def test_linkedin_posting_text_only():
    """Test posting text-only content to LinkedIn."""
    print("\n" + "=" * 60)
    print("TESTING TEXT-ONLY LINKEDIN POSTING")
    print("=" * 60)
    
    try:
        # Create LinkedIn client
        client = LinkedInClient()
        
        # Generate test content
        test_content = get_random_test_content()
        print(f"Test Content: {test_content}")
        
        # Create post request
        request = LinkedInPostRequest(
            content=test_content,
            visibility="PUBLIC"
        )
        
        # Post to LinkedIn
        print("\nPosting to LinkedIn...")
        result = client.post_content(request)
        
        if result.success:
            print("✅ Text-only post successful!")
            print(f"   Post ID: {result.linkedin_post_id}")
            print(f"   LinkedIn URL: {result.linkedin_url}")
            print(f"   Execution Time: {result.execution_time_seconds:.2f}s")
        else:
            print("❌ Text-only post failed!")
            print(f"   Error: {result.error}")
            
        return result.success
        
    except Exception as error:
        print(f"❌ Exception during text-only posting: {str(error)}")
        return False


def test_linkedin_posting_with_image():
    """Test posting content with image to LinkedIn."""
    print("\n" + "=" * 60)
    print("TESTING LINKEDIN POSTING WITH IMAGE")
    print("=" * 60)
    
    try:
        # Get random test image
        test_image = get_random_test_image()
        if not test_image:
            print("❌ No test images available. Skipping image test.")
            return False
        
        print(f"Test Image: {test_image}")
        
        # Create LinkedIn client
        client = LinkedInClient()
        
        # Generate test content
        test_content = get_random_test_content()
        print(f"Test Content: {test_content}")
        
        # Create post request with image
        request = LinkedInPostRequest(
            content=test_content,
            image_path=test_image,
            visibility="PUBLIC"
        )
        
        # Post to LinkedIn
        print("\nPosting to LinkedIn with image...")
        result = client.post_content(request)
        
        if result.success:
            print("✅ Post with image successful!")
            print(f"   Post ID: {result.linkedin_post_id}")
            print(f"   LinkedIn URL: {result.linkedin_url}")
            print(f"   Execution Time: {result.execution_time_seconds:.2f}s")
        else:
            print("❌ Post with image failed!")
            print(f"   Error: {result.error}")
            
        return result.success
        
    except Exception as error:
        print(f"❌ Exception during image posting: {str(error)}")
        return False


def test_api_endpoints():
    """Test the FastAPI endpoints (if server is running)."""
    print("\n" + "=" * 60)
    print("TESTING FASTAPI ENDPOINTS")
    print("=" * 60)
    
    try:
        import requests
        
        base_url = "http://localhost:8000"
        
        # Test LinkedIn status endpoint
        print("Testing /linkedin/status endpoint...")
        status_response = requests.get(f"{base_url}/linkedin/status")
        
        if status_response.status_code == 200:
            print("✅ LinkedIn status endpoint working!")
            status_data = status_response.json()
            print(f"   Service: {status_data['service']}")
            print(f"   Configured: {status_data['configured']}")
            print(f"   Status: {status_data['status']}")
        else:
            print(f"❌ LinkedIn status endpoint failed: {status_response.status_code}")
            
        # Test posting endpoint (only if configured)
        if status_response.status_code == 200 and status_response.json().get("configured"):
            print("\nTesting /linkedin/post endpoint...")
            
            test_content = get_random_test_content()
            test_image = get_random_test_image()
            
            post_data = {
                "content": test_content,
                "visibility": "PUBLIC"
            }
            
            if test_image:
                # Convert to relative path for API
                post_data["image_path"] = Path(test_image).name
            
            post_response = requests.post(f"{base_url}/linkedin/post", json=post_data)
            
            if post_response.status_code == 200:
                print("✅ LinkedIn post endpoint working!")
                post_result = post_response.json()
                print(f"   Success: {post_result['success']}")
                if post_result["success"]:
                    print(f"   Post ID: {post_result['linkedin_post_id']}")
                    print(f"   LinkedIn URL: {post_result['linkedin_url']}")
            else:
                print(f"❌ LinkedIn post endpoint failed: {post_response.status_code}")
                print(f"   Response: {post_response.text}")
        else:
            print("⚠️  Skipping post endpoint test (LinkedIn not configured or server not running)")
            
    except requests.ConnectionError:
        print("⚠️  FastAPI server not running. Start with: poetry run python run_api.py")
    except Exception as error:
        print(f"❌ Exception during API testing: {str(error)}")


def main():
    """Run all LinkedIn posting tests."""
    print("🧪 LinkedIn Posting Integration Tests")
    print("====================================")
    
    # Test 1: Configuration validation
    config_valid = test_linkedin_config()
    
    if not config_valid:
        print("\n❌ Cannot proceed with posting tests - configuration invalid")
        print("\nPlease configure LinkedIn environment variables in .env file:")
        print("   LINKEDIN_ACCESS_TOKEN=your_token_here")
        print("   LINKEDIN_PERSON_ID=your_person_id_here")
        return
    
    # Test 2: Text-only posting
    text_success = test_linkedin_posting_text_only()
    
    # Test 3: Posting with image
    image_success = test_linkedin_posting_with_image()
    
    # Test 4: API endpoints
    test_api_endpoints()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Configuration: {'✅ PASS' if config_valid else '❌ FAIL'}")
    print(f"Text Posting:  {'✅ PASS' if text_success else '❌ FAIL'}")
    print(f"Image Posting: {'✅ PASS' if image_success else '❌ FAIL'}")
    
    if config_valid and text_success and image_success:
        print("\n🎉 All tests passed! LinkedIn integration is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Please check the configuration and error messages above.")


if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    main()