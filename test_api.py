#!/usr/bin/env python3
"""Test script for the FastAPI endpoints."""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health_endpoint():
    """Test the health check endpoint."""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health endpoint working")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
    except requests.ConnectionError:
        print("❌ Could not connect to API server. Make sure it's running.")
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")

def test_status_endpoint():
    """Test the status endpoint."""
    try:
        response = requests.get(f"{BASE_URL}/status")
        if response.status_code == 200:
            print("✅ Status endpoint working")
            status_data = response.json()
            print(f"   Service: {status_data.get('service')}")
            print(f"   Health: {status_data.get('health')}")
        else:
            print(f"❌ Status endpoint failed: {response.status_code}")
    except requests.ConnectionError:
        print("❌ Could not connect to API server")
    except Exception as e:
        print(f"❌ Status endpoint error: {e}")

def test_platforms_endpoint():
    """Test the platforms endpoint."""
    try:
        response = requests.get(f"{BASE_URL}/platforms")
        if response.status_code == 200:
            print("✅ Platforms endpoint working")
            platforms = response.json().get('platforms', [])
            print(f"   Available platforms: {[p['name'] for p in platforms]}")
        else:
            print(f"❌ Platforms endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Platforms endpoint error: {e}")

def test_tones_endpoint():
    """Test the tones endpoint."""
    try:
        response = requests.get(f"{BASE_URL}/tones")
        if response.status_code == 200:
            print("✅ Tones endpoint working")
            tones = response.json().get('tones', [])
            print(f"   Available tones: {[t['name'] for t in tones]}")
        else:
            print(f"❌ Tones endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Tones endpoint error: {e}")

def test_generate_endpoint():
    """Test the content generation endpoint."""
    try:
        payload = {
            "topic": "artificial intelligence in healthcare",
            "platform": "twitter",
            "tone": "informative"
        }
        
        print("🔄 Testing content generation (this may take a moment)...")
        start_time = time.time()
        
        response = requests.post(
            f"{BASE_URL}/generate",
            json=payload,
            timeout=60
        )
        
        execution_time = time.time() - start_time
        
        if response.status_code == 200:
            print("✅ Generate endpoint working")
            result = response.json()
            print(f"   Success: {result.get('success')}")
            print(f"   Content length: {len(result.get('generated_content', ''))}")
            print(f"   Execution time: {execution_time:.2f}s")
            if result.get('generated_content'):
                print(f"   Sample content: {result['generated_content'][:100]}...")
        else:
            print(f"❌ Generate endpoint failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except requests.Timeout:
        print("❌ Generate endpoint timed out")
    except Exception as e:
        print(f"❌ Generate endpoint error: {e}")

if __name__ == "__main__":
    print("🧪 Testing FastAPI Multi-Agent Content Generation API")
    print("=" * 60)
    
    test_health_endpoint()
    test_status_endpoint()
    test_platforms_endpoint()
    test_tones_endpoint()
    
    # Only test generation if other endpoints work
    print("\n" + "=" * 60)
    print("⚠️  The generate endpoint test requires OpenAI API key")
    print("   Make sure you have OPENAI_API_KEY in your environment")
    
    user_input = input("Run content generation test? (y/N): ")
    if user_input.lower() == 'y':
        test_generate_endpoint()
    
    print("\n✅ API testing complete!")