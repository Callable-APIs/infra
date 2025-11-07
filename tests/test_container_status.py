"""Tests for status container application."""
import pytest
import json
from unittest.mock import Mock, patch, mock_open, MagicMock
from flask import Flask

from clint.container.status import app, load_nodes, load_container_version, main


class TestStatusContainer:
    """Test cases for status container."""

    def test_load_container_version_success(self):
        """Test loading container version from file."""
        with patch("builtins.open", mock_open(read_data="test-version-456\n")):
            version = load_container_version()
            assert version == "test-version-456"

    def test_load_container_version_file_not_found(self):
        """Test loading container version when file doesn't exist."""
        with patch("builtins.open", side_effect=FileNotFoundError()):
            version = load_container_version()
            assert version == "unknown"

    def test_load_nodes_from_hosts_json(self):
        """Test loading nodes from hosts.json file."""
        mock_hosts_data = {
            "groups": {
                "webapp_hosts": [
                    {
                        "name": "onode1",
                        "host": "192.9.154.97",
                        "provider": "oracle",
                        "role": "api_server"
                    },
                    {
                        "name": "gnode1",
                        "host": "35.233.161.8",
                        "provider": "google",
                        "role": "status"
                    }
                ],
                "status_container_hosts": [
                    {"name": "gnode1"}
                ]
            }
        }
        
        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", mock_open()):
                with patch("json.load", return_value=mock_hosts_data):
                    nodes = load_nodes()
                    assert len(nodes) == 2
                    assert nodes[0]["id"] == "onode1"
                    assert nodes[0]["provider"] == "Oracle Cloud"
                    assert nodes[1]["id"] == "gnode1"
                    assert nodes[1]["is_status_only"] is True

    def test_load_nodes_fallback(self):
        """Test loading nodes uses fallback when hosts.json not found."""
        with patch("os.path.exists", return_value=False):
            nodes = load_nodes()
            assert len(nodes) > 0
            assert isinstance(nodes, list)
            # Should have fallback nodes
            assert any(node["id"] == "onode1" for node in nodes)

    def test_root_endpoint_returns_html(self):
        """Test root endpoint returns HTML dashboard."""
        with app.test_client() as client:
            response = client.get("/")
            assert response.status_code == 200
            # Should return HTML, not JSON
            assert "text/html" in response.content_type or response.data.decode().startswith("<!DOCTYPE") or "<html" in response.data.decode().lower()

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
            with patch("clint.container.status.get_all_nodes_status") as mock_get_all:
                # Mock node status responses - match actual structure
                mock_get_all.return_value = [
                    {
                        "node_id": "onode1",
                        "display_name": "Oracle Cloud Node 1",
                        "health_status": "healthy",
                        "api_status": "running",
                        "ip": "192.9.154.97",
                        "provider": "Oracle Cloud",
                        "role": "Primary",
                        "response_time": 0.1,
                        "last_check": "2025-01-01T00:00:00"
                    }
                ]
                
                response = client.get("/api/status")
                assert response.status_code == 200
                data = json.loads(response.data)
                
                # Check required fields (based on actual response structure)
                assert "service" in data
                assert "overall_status" in data
                assert "total_nodes" in data
                assert "healthy_nodes" in data
                assert "last_updated" in data
                assert "nodes" in data
                
                # Check nodes structure
                assert isinstance(data["nodes"], list)

    def test_dashboard_endpoint(self):
        """Test dashboard endpoint returns HTML."""
        with app.test_client() as client:
            response = client.get("/dashboard")
            assert response.status_code == 200
            # Should return HTML
            assert "text/html" in response.content_type or "<html" in response.data.decode().lower()

    def test_all_base_endpoints_implemented(self):
        """Test that all required base container endpoints are implemented."""
        required_endpoints = ["/", "/health", "/api/health", "/api/status"]
        
        with app.test_client() as client:
            for endpoint in required_endpoints:
                response = client.get(endpoint)
                assert response.status_code == 200, f"Endpoint {endpoint} should return 200"

    def test_node_status_aggregation(self):
        """Test that node status is properly aggregated."""
        with app.test_client() as client:
            with patch("clint.container.status.get_all_nodes_status") as mock_get_all:
                # Mock node status responses - match actual structure
                mock_get_all.return_value = [
                    {
                        "node_id": "onode1",
                        "display_name": "Oracle Cloud Node 1",
                        "health_status": "healthy",
                        "api_status": "running",
                        "ip": "192.9.154.97",
                        "provider": "Oracle Cloud",
                        "role": "Primary",
                        "response_time": 0.1,
                        "last_check": "2025-01-01T00:00:00"
                    }
                ]
                
                response = client.get("/api/status")
                assert response.status_code == 200
                data = json.loads(response.data)
                
                # Should have nodes array
                assert "nodes" in data
                assert isinstance(data["nodes"], list)
                
                # Each node should have required fields
                if len(data["nodes"]) > 0:
                    node = data["nodes"][0]
                    assert "node_id" in node
                    assert "display_name" in node
                    assert "health_status" in node
                    assert "api_status" in node

    def test_status_only_node_detection(self):
        """Test that status-only nodes are detected correctly."""
        mock_hosts_data = {
            "groups": {
                "webapp_hosts": [
                    {
                        "name": "gnode1",
                        "host": "35.233.161.8",
                        "provider": "google",
                        "role": "status"
                    }
                ],
                "status_container_hosts": [
                    {"name": "gnode1"}
                ]
            }
        }
        
        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", mock_open()):
                with patch("json.load", return_value=mock_hosts_data):
                    nodes = load_nodes()
                    assert len(nodes) == 1
                    assert nodes[0]["is_status_only"] is True
                    assert nodes[0]["role"] == "Monitoring"

    def test_main_function(self):
        """Test main function sets up Flask app correctly."""
        with patch("clint.container.status.app.run") as mock_run:
            with patch("os.environ.get", return_value="8080"):
                main()
                mock_run.assert_called_once_with(
                    host="0.0.0.0", port=8080, debug=False
                )

    def test_main_function_custom_port(self):
        """Test main function uses PORT environment variable."""
        with patch("clint.container.status.app.run") as mock_run:
            with patch("os.environ.get", return_value="9000"):
                main()
                mock_run.assert_called_once_with(
                    host="0.0.0.0", port=9000, debug=False
                )

    def test_provider_name_mapping(self):
        """Test provider name mapping works correctly."""
        mock_hosts_data = {
            "groups": {
                "webapp_hosts": [
                    {"name": "onode1", "host": "1.2.3.4", "provider": "oracle", "role": "base"},
                    {"name": "gnode1", "host": "5.6.7.8", "provider": "google", "role": "base"},
                    {"name": "anode1", "host": "9.10.11.12", "provider": "aws", "role": "base"},
                    {"name": "inode1", "host": "13.14.15.16", "provider": "ibm", "role": "base"},
                ],
                "status_container_hosts": []
            }
        }
        
        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", mock_open()):
                with patch("json.load", return_value=mock_hosts_data):
                    nodes = load_nodes()
                    assert nodes[0]["provider"] == "Oracle Cloud"
                    assert nodes[1]["provider"] == "Google Cloud"
                    assert nodes[2]["provider"] == "AWS"
                    assert nodes[3]["provider"] == "IBM Cloud"

    def test_role_name_mapping(self):
        """Test role name mapping works correctly."""
        mock_hosts_data = {
            "groups": {
                "webapp_hosts": [
                    {"name": "onode1", "host": "1.2.3.4", "provider": "oracle", "role": "api_server"},
                    {"name": "gnode1", "host": "5.6.7.8", "provider": "google", "role": "base"},
                    {"name": "inode1", "host": "9.10.11.12", "provider": "ibm", "role": "services"},
                ],
                "status_container_hosts": []
            }
        }
        
        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", mock_open()):
                with patch("json.load", return_value=mock_hosts_data):
                    nodes = load_nodes()
                    assert nodes[0]["role"] == "Primary"
                    assert nodes[1]["role"] == "Secondary"
                    assert nodes[2]["role"] == "Services"

