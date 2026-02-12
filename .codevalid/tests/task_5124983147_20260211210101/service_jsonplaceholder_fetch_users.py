import unittest
from unittest.mock import patch, MagicMock

import sys
import os

# Ensure the app directory is in the path for import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../app/services')))
from app.services import jsonplaceholder_service

class TestJsonplaceholderServiceFetchUsers(unittest.TestCase):
    def setUp(self):
        self.service = jsonplaceholder_service.JsonplaceholderService

    @patch('app.services.jsonplaceholder_service.JsonplaceholderService._cache_expired', return_value=True)
    @patch('app.services.jsonplaceholder_service.requests.get')
    @patch('app.services.jsonplaceholder_service.JsonplaceholderService._set_cached_users')
    def test_fetch_users_cache_expired_success_200(self, mock_set_cache, mock_get, mock_cache_expired):
        # Given
        users = [{"id": 1, "name": "User1"}, {"id": 2, "name": "User2"}]
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = users
        mock_get.return_value = mock_response

        # When
        result = self.service.fetch_users()

        # Then
        mock_get.assert_called_once_with("https://jsonplaceholder.typicode.com/users", timeout=5)
        mock_set_cache.assert_called_once_with(users)
        self.assertEqual(result, users)

    @patch('app.services.jsonplaceholder_service.JsonplaceholderService._cache_expired', return_value=True)
    @patch('app.services.jsonplaceholder_service.requests.get')
    def test_fetch_users_cache_expired_api_error_404(self, mock_get, mock_cache_expired):
        # Given
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        # When
        result = self.service.fetch_users()

        # Then
        mock_get.assert_called_once_with("https://jsonplaceholder.typicode.com/users", timeout=5)
        self.assertEqual(result, [])

    @patch('app.services.jsonplaceholder_service.JsonplaceholderService._cache_expired', return_value=True)
    @patch('app.services.jsonplaceholder_service.requests.get')
    def test_fetch_users_cache_expired_api_error_500(self, mock_get, mock_cache_expired):
        # Given
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        # When
        result = self.service.fetch_users()

        # Then
        mock_get.assert_called_once_with("https://jsonplaceholder.typicode.com/users", timeout=5)
        self.assertEqual(result, [])

    @patch('app.services.jsonplaceholder_service.JsonplaceholderService._cache_expired', return_value=True)
    @patch('app.services.jsonplaceholder_service.requests.get')
    @patch('app.services.jsonplaceholder_service.JsonplaceholderService._set_cached_users')
    def test_fetch_users_cache_expired_api_empty_list(self, mock_set_cache, mock_get, mock_cache_expired):
        # Given
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        # When
        result = self.service.fetch_users()

        # Then
        mock_get.assert_called_once_with("https://jsonplaceholder.typicode.com/users", timeout=5)
        mock_set_cache.assert_called_once_with([])
        self.assertEqual(result, [])

    @patch('app.services.jsonplaceholder_service.JsonplaceholderService._cache_expired', return_value=True)
    @patch('app.services.jsonplaceholder_service.requests.get')
    def test_fetch_users_cache_expired_api_invalid_json(self, mock_get, mock_cache_expired):
        # Given
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response

        # When
        result = self.service.fetch_users()

        # Then
        mock_get.assert_called_once_with("https://jsonplaceholder.typicode.com/users", timeout=5)
        self.assertEqual(result, [])

    @patch('app.services.jsonplaceholder_service.JsonplaceholderService._cache_expired', return_value=False)
    @patch('app.services.jsonplaceholder_service.JsonplaceholderService._get_cached_users')
    def test_fetch_users_cache_not_expired_return_cached_users(self, mock_get_cache, mock_cache_expired):
        # Given
        cached_users = [{"id": 1, "name": "CachedUser"}]
        mock_get_cache.return_value = cached_users

        # When
        result = self.service.fetch_users()

        # Then
        mock_get_cache.assert_called_once()
        self.assertEqual(result, cached_users)

    @patch('app.services.jsonplaceholder_service.JsonplaceholderService._cache_expired', return_value=False)
    @patch('app.services.jsonplaceholder_service.JsonplaceholderService._get_cached_users')
    def test_fetch_users_cache_not_expired_cached_users_empty(self, mock_get_cache, mock_cache_expired):
        # Given
        mock_get_cache.return_value = []

        # When
        result = self.service.fetch_users()

        # Then
        mock_get_cache.assert_called_once()
        self.assertEqual(result, [])

    @patch('app.services.jsonplaceholder_service.JsonplaceholderService._cache_expired', return_value=True)
    @patch('app.services.jsonplaceholder_service.requests.get', side_effect=Exception("Timeout"))
    def test_fetch_users_cache_expired_api_timeout(self, mock_get, mock_cache_expired):
        # Given: requests.get will raise an Exception (simulate timeout)

        # When
        result = self.service.fetch_users()

        # Then
        mock_get.assert_called_once_with("https://jsonplaceholder.typicode.com/users", timeout=5)
        self.assertEqual(result, [])

    @patch('app.services.jsonplaceholder_service.JsonplaceholderService._cache_expired', return_value=True)
    @patch('app.services.jsonplaceholder_service.requests.get', side_effect=Exception("Connection error"))
    def test_fetch_users_cache_expired_api_connection_error(self, mock_get, mock_cache_expired):
        # Given: requests.get will raise an Exception (simulate connection error)

        # When
        result = self.service.fetch_users()

        # Then
        mock_get.assert_called_once_with("https://jsonplaceholder.typicode.com/users", timeout=5)
        self.assertEqual(result, [])

    @patch('app.services.jsonplaceholder_service.JsonplaceholderService._cache_expired', return_value=True)
    @patch('app.services.jsonplaceholder_service.requests.get')
    @patch('app.services.jsonplaceholder_service.JsonplaceholderService._set_cached_users')
    def test_fetch_users_cache_expired_api_partial_user_list(self, mock_set_cache, mock_get, mock_cache_expired):
        # Given
        partial_users = [{"id": 1}, {"name": "User2"}]  # missing fields
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = partial_users
        mock_get.return_value = mock_response

        # When
        result = self.service.fetch_users()

        # Then
        mock_get.assert_called_once_with("https://jsonplaceholder.typicode.com/users", timeout=5)
        mock_set_cache.assert_called_once_with(partial_users)
        self.assertEqual(result, partial_users)

if __name__ == '__main__':
    unittest.main()