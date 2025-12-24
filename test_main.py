import unittest
from unittest.mock import patch, MagicMock
from main import build_static_image_url, download_map

class Tests(unittest.TestCase):
    def test_build_static_image_url(self):
        # Test input parameters
        style_id = "mapbox/streets-v11"
        lon = -84.3895
        lat = 33.7490
        zoom = 13
        width = 128
        height = 128
        token = "test_token"

        # Expected URL
        expected_url = (
            "https://api.mapbox.com/styles/v1/mapbox/streets-v11/static/-84.389500,33.749000,13/128x128?access_token=test_token"
        )

        # Call the function
        result = build_static_image_url(style_id, lon, lat, zoom, width, height, token)

        # Assert the result matches the expected URL
        self.assertEqual(result, expected_url)

    @patch("main.requests.get")
    def test_download_map_invalid_url(self, mock_get):
        # Mock the response for an invalid URL
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.content = None
        mock_get.return_value = mock_response

        # Test parameters
        invalid_url = "http://invalid-url.com"
        filename = "test_map.png"
        # Call the function
        downloaded = download_map(invalid_url, filename)

        # Assertions
        mock_get.assert_called_once_with(invalid_url)
        self.assertFalse(downloaded)

if __name__ == "__main__":
    unittest.main()