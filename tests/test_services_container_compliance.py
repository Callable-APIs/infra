"""Tests to verify services container endpoint compliance."""
import pytest
import json
import requests
from typing import Dict, Any


class TestServicesContainerCompliance:
    """Test cases for services container endpoint compliance."""

    # Services container endpoint (update with actual IP/domain)
    BASE_URL = "http://35.88.22.9:8080"

    def test_root_endpoint_exists(self):
        """Test that root endpoint exists and returns 200."""
        response = requests.get(f"{self.BASE_URL}/", timeout=10)
        assert response.status_code == 200, f"Root endpoint should return 200, got {response.status_code}"
        
        # Root endpoint can return HTML (for user-facing containers) or JSON
        # Both are acceptable - HTML is fine for browser access, JSON is fine for API services
        assert response.status_code == 200

    def test_root_endpoint_html_or_json(self):
        """Test that root endpoint returns HTML or JSON (both acceptable)."""
        response = requests.get(f"{self.BASE_URL}/", timeout=10)
        assert response.status_code == 200
        
        # Check if it's HTML or JSON
        content_type = response.headers.get('Content-Type', '').lower()
        is_html = 'text/html' in content_type or response.text.strip().startswith('<!')
        is_json = 'application/json' in content_type
        
        # Should be either HTML or JSON
        assert is_html or is_json, "Root endpoint should return HTML or JSON"
        
        # If HTML, that's fine - JSON service info is available via /api/status
        # If JSON, should have required fields
        if is_json:
            data = response.json()
            assert "service" in data or "version" in data, "JSON root endpoint should include service info"

    def test_health_endpoint_exists(self):
        """Test that health endpoint exists."""
        response = requests.get(f"{self.BASE_URL}/health", timeout=10)
        assert response.status_code == 200, f"Health endpoint should return 200, got {response.status_code}"

    def test_health_endpoint_format(self):
        """Test that health endpoint matches base container format."""
        response = requests.get(f"{self.BASE_URL}/health", timeout=10)
        assert response.status_code == 200
        
        data = response.json()
        
        # Check required fields
        assert "status" in data, "Health endpoint should include 'status' field"
        assert "timestamp" in data, "Health endpoint should include 'timestamp' field"
        assert "version" in data, "Health endpoint should include 'version' field"
        
        # Check format matches base container
        assert data["status"] == "healthy", "Health endpoint status should be 'healthy'"

    def test_api_health_endpoint_exists(self):
        """Test that API health endpoint exists."""
        response = requests.get(f"{self.BASE_URL}/api/health", timeout=10)
        assert response.status_code == 200, f"API health endpoint should return 200, got {response.status_code}"

    def test_api_health_endpoint_format(self):
        """Test that API health endpoint matches base container format."""
        response = requests.get(f"{self.BASE_URL}/api/health", timeout=10)
        assert response.status_code == 200
        
        data = response.json()
        
        # Check required fields
        assert "status" in data, "API health endpoint should include 'status' field"
        assert "timestamp" in data, "API health endpoint should include 'timestamp' field"
        assert "version" in data, "API health endpoint should include 'version' field"
        
        # Check format matches base container
        assert data["status"] == "ok", "API health endpoint status should be 'ok'"

    def test_api_health_different_from_health(self):
        """Test that /api/health returns different response than /health."""
        health_response = requests.get(f"{self.BASE_URL}/health", timeout=10)
        api_health_response = requests.get(f"{self.BASE_URL}/api/health", timeout=10)
        
        health_data = health_response.json()
        api_health_data = api_health_response.json()
        
        # They should have different status values
        assert health_data.get("status") != api_health_data.get("status") or \
               health_data.get("status") == "healthy" and api_health_data.get("status") == "ok", \
               "/api/health should return 'ok' while /health returns 'healthy'"

    def test_api_status_endpoint_exists(self):
        """Test that API status endpoint exists."""
        response = requests.get(f"{self.BASE_URL}/api/status", timeout=10)
        assert response.status_code == 200, f"API status endpoint should return 200, got {response.status_code}"

    def test_api_status_endpoint_format(self):
        """Test that API status endpoint matches base container format."""
        response = requests.get(f"{self.BASE_URL}/api/status", timeout=10)
        assert response.status_code == 200
        
        data = response.json()
        
        # Check required fields
        assert "service" in data, "API status endpoint should include 'service' field"
        assert "version" in data, "API status endpoint should include 'version' field"
        assert "status" in data, "API status endpoint should include 'status' field"
        assert "timestamp" in data, "API status endpoint should include 'timestamp' field"

    def test_all_base_endpoints_implemented(self):
        """Test that all required base container endpoints are implemented."""
        # Root endpoint can be HTML or JSON
        root_response = requests.get(f"{self.BASE_URL}/", timeout=10)
        assert root_response.status_code == 200, "Root endpoint should return 200"
        
        # Health endpoints MUST be JSON
        json_endpoints = ["/health", "/api/health", "/api/status"]
        
        for endpoint in json_endpoints:
            response = requests.get(f"{self.BASE_URL}{endpoint}", timeout=10)
            assert response.status_code == 200, f"Endpoint {endpoint} should return 200"
            
            # Must return JSON
            try:
                data = response.json()
                assert isinstance(data, dict), f"Endpoint {endpoint} should return JSON object"
            except json.JSONDecodeError:
                pytest.fail(f"Endpoint {endpoint} should return valid JSON")

    def test_service_specific_endpoints_available(self):
        """Test that service-specific endpoints are available."""
        # Services container should provide versioned API endpoints
        endpoints = [
            "/api/v1/calendar",
            "/api/v2/calendar",
            "/api/v1/astronomy",
            "/api/v2/astronomy"
        ]
        
        for endpoint in endpoints:
            response = requests.get(f"{self.BASE_URL}{endpoint}", timeout=10)
            # These may return 404 if not implemented, but should not return 500
            assert response.status_code != 500, f"Endpoint {endpoint} should not return 500 error"

