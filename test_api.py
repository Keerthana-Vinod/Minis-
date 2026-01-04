"""
Test script for the Food Product Assistant API
"""

import requests
import json
from pathlib import Path

# API base URL
BASE_URL = "http://localhost:8000"

def test_root():
    """Test root endpoint"""
    print("\n=== Testing Root Endpoint ===")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_health():
    """Test health check endpoint"""
    print("\n=== Testing Health Endpoint ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_stats():
    """Test stats endpoint"""
    print("\n=== Testing Stats Endpoint ===")
    response = requests.get(f"{BASE_URL}/stats")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_info():
    """Test info endpoint"""
    print("\n=== Testing Info Endpoint ===")
    response = requests.get(f"{BASE_URL}/info")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_chat(image_path: str = None, query: str = "What are the ingredients?"):
    """Test chat endpoint with image upload"""
    print("\n=== Testing Chat Endpoint ===")
    
    if image_path and Path(image_path).exists():
        files = {"image": open(image_path, "rb")}
        data = {"query": query}
        
        response = requests.post(f"{BASE_URL}/chat", files=files, data=data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\nQuery: {query}")
            print(f"Response: {result['response']}")
            print(f"Processing Time: {result['processing_time']:.2f}s")
        else:
            print(f"Error: {response.text}")
    else:
        print("⚠️  No image provided or file not found.")
        print("To test chat endpoint, provide an image path:")
        print("python test_api.py --image /path/to/image.jpg")

def main():
    """Run all tests"""
    import sys
    
    print("=" * 60)
    print("Food Product Assistant API - Test Suite")
    print("=" * 60)
    
    # Check if server is running
    try:
        requests.get(f"{BASE_URL}/health", timeout=2)
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Server not running at {BASE_URL}")
        print("Please start the server first: python main.py")
        return
    
    # Run tests
    test_root()
    test_health()
    test_info()
    test_stats()
    
    # Check for image argument
    image_path = None
    query = "What are the ingredients in this product?"
    
    if len(sys.argv) > 1:
        for i, arg in enumerate(sys.argv):
            if arg == "--image" and i + 1 < len(sys.argv):
                image_path = sys.argv[i + 1]
            elif arg == "--query" and i + 1 < len(sys.argv):
                query = sys.argv[i + 1]
    
    test_chat(image_path, query)
    
    print("\n" + "=" * 60)
    print("Tests completed!")
    print("=" * 60)
    print("\nFor interactive testing, visit: http://localhost:8000/docs")

if __name__ == "__main__":
    main()
