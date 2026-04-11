import pytest
import httpx
from unittest.mock import AsyncMock, MagicMock, patch

from app.models.requests import AuthConfig, EndpointRequest
from app.services.endpoint_analyzer import analyze_endpoint, _build_auth_headers


class TestBuildAuthHeaders:
    def test_bearer_token(self):
        auth = AuthConfig(type="bearer", token="mytoken")
        headers = _build_auth_headers(auth)
        assert headers == {"Authorization": "Bearer mytoken"}

    def test_api_key_default_header(self):
        auth = AuthConfig(type="api_key", api_key="abc123")
        headers = _build_auth_headers(auth)
        assert headers == {"X-API-Key": "abc123"}

    def test_api_key_custom_header(self):
        auth = AuthConfig(type="api_key", api_key="abc123", header_name="X-Custom-Key")
        headers = _build_auth_headers(auth)
        assert headers == {"X-Custom-Key": "abc123"}

    def test_basic_auth(self):
        import base64
        auth = AuthConfig(type="basic", username="user", password="pass")
        headers = _build_auth_headers(auth)
        expected = base64.b64encode(b"user:pass").decode()
        assert headers == {"Authorization": f"Basic {expected}"}

    def test_unknown_type_returns_empty(self):
        auth = AuthConfig(type="unknown")
        headers = _build_auth_headers(auth)
        assert headers == {}


class TestAnalyzeEndpoint:
    @pytest.mark.asyncio
    async def test_get_request_success(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"id": 1, "name": "test"}

        with patch("app.services.endpoint_analyzer.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client.request = AsyncMock(return_value=mock_response)
            mock_client_cls.return_value = mock_client

            request = EndpointRequest(url="https://api.example.com/users", method="GET")
            result = await analyze_endpoint(request)

        assert result.status_code == 200
        assert result.method == "GET"
        assert result.response_body == {"id": 1, "name": "test"}

    @pytest.mark.asyncio
    async def test_auth_headers_are_redacted(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.json.return_value = {}

        with patch("app.services.endpoint_analyzer.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client.request = AsyncMock(return_value=mock_response)
            mock_client_cls.return_value = mock_client

            request = EndpointRequest(
                url="https://api.example.com/users",
                method="GET",
                auth=AuthConfig(type="bearer", token="secret-token"),
            )
            result = await analyze_endpoint(request)

        assert result.request_headers.get("Authorization") == "***"

    @pytest.mark.asyncio
    async def test_non_json_response_falls_back_to_text(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.json.side_effect = ValueError("not json")
        mock_response.text = "plain text response"

        with patch("app.services.endpoint_analyzer.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client.request = AsyncMock(return_value=mock_response)
            mock_client_cls.return_value = mock_client

            request = EndpointRequest(url="https://api.example.com/ping", method="GET")
            result = await analyze_endpoint(request)

        assert result.response_body == "plain text response"
