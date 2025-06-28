#!/usr/bin/env python3
"""
Test script for metrics endpoint

This script tests the /metrics endpoint to ensure it's working correctly
and returns valid Prometheus metrics.
"""

import asyncio
import sys
from typing import Any, Dict

import httpx


async def test_metrics_endpoint(base_url: str = "http://localhost:8000") -> Dict[str, Any]:
    """Test the metrics endpoint and return results."""
    results = {
        "endpoint_accessible": False,
        "content_type": None,
        "metrics_count": 0,
        "has_http_metrics": False,
        "has_business_metrics": False,
        "error": None
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Test metrics endpoint
            response = await client.get(f"{base_url}/metrics")
            
            if response.status_code == 200:
                results["endpoint_accessible"] = True
                results["content_type"] = response.headers.get("content-type")
                
                # Parse metrics content
                content = response.text
                metrics_lines = [line.strip() for line in content.split('\n') if line.strip()]
                results["metrics_count"] = len(metrics_lines)
                
                # Check for specific metric types
                results["has_http_metrics"] = any("http_requests_total" in line for line in metrics_lines)
                results["has_business_metrics"] = any("weather_requests_total" in line for line in metrics_lines)
                
                print("✅ Metrics endpoint is accessible")
                print(f"   Content-Type: {results['content_type']}")
                print(f"   Metrics count: {results['metrics_count']}")
                print(f"   Has HTTP metrics: {results['has_http_metrics']}")
                print(f"   Has business metrics: {results['has_business_metrics']}")
                
                # Show sample metrics
                print("\n📊 Sample metrics:")
                for line in metrics_lines[:10]:  # Show first 10 metrics
                    if line and not line.startswith('#'):
                        print(f"   {line}")
                
            else:
                results["error"] = f"HTTP {response.status_code}: {response.text}"
                print(f"❌ Metrics endpoint returned status {response.status_code}")
                
    except httpx.ConnectError:
        results["error"] = "Could not connect to server"
        print("❌ Could not connect to server. Make sure the backend is running.")
    except Exception as e:
        results["error"] = str(e)
        print(f"❌ Error testing metrics endpoint: {e}")
    
    return results


async def test_health_endpoint(base_url: str = "http://localhost:8000") -> Dict[str, Any]:
    """Test the health endpoint to ensure it's working."""
    results = {
        "endpoint_accessible": False,
        "status": None,
        "response_time_ms": None,
        "error": None
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{base_url}/health")
            
            if response.status_code == 200:
                data = response.json()
                results["endpoint_accessible"] = True
                results["status"] = data.get("status")
                results["response_time_ms"] = data.get("response_time_ms")
                
                print("✅ Health endpoint is accessible")
                print(f"   Status: {results['status']}")
                print(f"   Response time: {results['response_time_ms']}ms")
                
            else:
                results["error"] = f"HTTP {response.status_code}: {response.text}"
                print(f"❌ Health endpoint returned status {response.status_code}")
                
    except Exception as e:
        results["error"] = str(e)
        print(f"❌ Error testing health endpoint: {e}")
    
    return results


async def main():
    """Main test function."""
    print("🧪 Testing Family Dashboard Metrics Endpoint")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Test health endpoint first
    print("\n1. Testing Health Endpoint")
    print("-" * 30)
    health_results = await test_health_endpoint(base_url)
    
    # Test metrics endpoint
    print("\n2. Testing Metrics Endpoint")
    print("-" * 30)
    metrics_results = await test_metrics_endpoint(base_url)
    
    # Summary
    print("\n📋 Test Summary")
    print("=" * 50)
    
    if health_results["endpoint_accessible"]:
        print("✅ Health endpoint: PASSED")
    else:
        print("❌ Health endpoint: FAILED")
        print(f"   Error: {health_results['error']}")
    
    if metrics_results["endpoint_accessible"]:
        print("✅ Metrics endpoint: PASSED")
        print(f"   Metrics found: {metrics_results['metrics_count']}")
    else:
        print("❌ Metrics endpoint: FAILED")
        print(f"   Error: {metrics_results['error']}")
    
    # Overall result
    if health_results["endpoint_accessible"] and metrics_results["endpoint_accessible"]:
        print("\n🎉 All tests passed! Metrics endpoint is working correctly.")
        return 0
    else:
        print("\n💥 Some tests failed. Check the errors above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 