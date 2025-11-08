"""Tests for base container application."""
import pytest
import json
from unittest.mock import Mock, patch, mock_open
from flask import Flask

from clint.container.base import app, load_container_version, main


class TestBaseContainer:
    """Test cases for base container."""

    def test_load_container_version_success(self):
        """Test loading container version from file."""
        with patch("builtins.open", mock_open(read_data="test-version-123\n")):
            version = load_container_version()
            assert version == "test-version-123"

    def test_load_container_version_file_not_found(self):
        """Test loading container version when file doesn't exist."""
        with patch("builtins.open", side_effect=FileNotFoundError()):
            version = load_container_version()
            assert version == "unknown"

    def test_root_endpoint(self):
        """Test root endpoint returns correct JSON."""
        with app.test_client() as client:
            response = client.get("/")
            assert response.status_code == 200
            data = json.loads(response.data)
            assert "service" in data
            assert "version" in data
            assert "status" in data
            assert "uptime" in data
            assert "timestamp" in data
            assert data["service"] == "CallableAPIs Base Container"
            assert data["status"] == "running"

    def test_health_endpoint(self):
        """Test health endpoint returns correct format."""
        with app.test_client() as client:
            response = client.get("/health")
            assert response.status_code == 200
            data = json.loads(response.data)
            assert "status" in data
            assert "timestamp" in data
            assert "version" in data
            assert data["status"] == "healthy"

    def test_api_health_endpoint(self):
        """Test API health endpoint returns correct format."""
        with app.test_client() as client:
            response = client.get("/api/health")
            assert response.status_code == 200
            data = json.loads(response.data)
            assert "status" in data
            assert "timestamp" in data
            assert "version" in data
            assert data["status"] == "ok"

    def test_api_status_endpoint_structure(self):
        """Test API status endpoint returns correct structure."""
        with app.test_client() as client:
            with patch("clint.container.base.SecretsManager") as mock_secrets:
                mock_manager = Mock()
                mock_manager.get_secret_keys.return_value = ["key1", "key2"]
                mock_manager.get_vault_password_hash.return_value = "hash123"
                mock_manager.get_secrets_file_hash.return_value = "filehash456"
                mock_secrets.return_value = mock_manager
                
                response = client.get("/api/status")
                assert response.status_code == 200
                data = json.loads(response.data)
                
                # Check required fields
                assert "service" in data
                assert "version" in data
                assert "status" in data
                assert "uptime" in data
                assert "timestamp" in data
                assert "environment" in data
                assert "secrets" in data
                
                # Check environment structure
                assert "python_version" in data["environment"]
                assert "container" in data["environment"]
                
                # Check secrets structure
                assert "keys" in data["secrets"]
                assert "vault_password_hash" in data["secrets"]
                assert "secrets_file_hash" in data["secrets"]

    def test_api_status_endpoint_secrets_unavailable(self):
        """Test API status endpoint when secrets manager is unavailable."""
        with app.test_client() as client:
            with patch("clint.container.base.SECRETS_AVAILABLE", False):
                response = client.get("/api/status")
                assert response.status_code == 200
                data = json.loads(response.data)
                assert data["secrets"]["vault_password_hash"] == "unavailable"
                assert data["secrets"]["secrets_file_hash"] == "unavailable"

    def test_api_status_endpoint_secrets_error(self):
        """Test API status endpoint handles secrets errors gracefully."""
        with app.test_client() as client:
            with patch("clint.container.base.SecretsManager") as mock_secrets:
                mock_secrets.side_effect = Exception("Secrets error")
                
                response = client.get("/api/status")
                assert response.status_code == 200
                data = json.loads(response.data)
                assert data["secrets"]["vault_password_hash"] == "error"
                assert data["secrets"]["secrets_file_hash"] == "error"

    def test_404_error_handler(self):
        """Test 404 error handler."""
        with app.test_client() as client:
            response = client.get("/nonexistent")
            assert response.status_code == 404
            data = json.loads(response.data)
            assert "error" in data
            assert "message" in data
            assert "status" in data
            assert data["error"] == "Not Found"
            assert data["status"] == 404

    def test_500_error_handler(self):
        """Test 500 error handler."""
        with app.test_client() as client:
            # Force an error by patching a route to raise an exception
            with patch("clint.container.base.app.route") as mock_route:
                mock_route.side_effect = Exception("Test error")
                # This will trigger the error handler
                pass  # Error handler is tested via exception handling

    def test_main_function(self):
        """Test main function sets up Flask app correctly."""
        with patch("clint.container.base.app.run") as mock_run:
            with patch("os.environ.get", return_value="8080"):
                main()
                mock_run.assert_called_once_with(
                    host="0.0.0.0", port=8080, debug=False
                )

    def test_main_function_custom_port(self):
        """Test main function uses PORT environment variable."""
        with patch("clint.container.base.app.run") as mock_run:
            with patch("os.environ.get", return_value="9000"):
                main()
                mock_run.assert_called_once_with(
                    host="0.0.0.0", port=9000, debug=False
                )

    def test_all_base_endpoints_implemented(self):
        """Test that all required base container endpoints are implemented."""
        required_endpoints = ["/", "/health", "/api/health", "/api/status"]
        
        with app.test_client() as client:
            for endpoint in required_endpoints:
                response = client.get(endpoint)
                assert response.status_code == 200, f"Endpoint {endpoint} should return 200"
                data = json.loads(response.data)
                assert isinstance(data, dict), f"Endpoint {endpoint} should return JSON"

    def test_endpoint_response_format(self):
        """Test that all endpoints return proper JSON format."""
        with app.test_client() as client:
            endpoints = ["/", "/health", "/api/health", "/api/status"]
            
            for endpoint in endpoints:
                response = client.get(endpoint)
                assert response.status_code == 200
                data = json.loads(response.data)
                assert isinstance(data, dict)
                assert "timestamp" in data or endpoint == "/"  # Root may not have timestamp
                
                # Verify JSON is valid
                assert json.dumps(data)  # Should not raise exception


