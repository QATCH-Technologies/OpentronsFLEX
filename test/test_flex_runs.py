import unittest
from unittest.mock import patch, MagicMock
from src.flex_controls.flex_runs import FlexRuns
import json


class TestFlexRuns(unittest.TestCase):
    @patch("flex_runs.requests.post")
    def test_run_protocol(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": {"id": "test_run_id"}}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        result = FlexRuns.run_protocol(
            "http://test_url/runs", "test_protocol_id")
        self.assertEqual(result, "test_run_id")
        mock_post.assert_called_once_with(
            url="http://test_url/runs",
            headers=FlexRuns.HEADERS,
            data=json.dumps({"data": {"protocolId": "test_protocol_id"}}),
        )

    @patch("flex_runs.requests.delete")
    def test_delete_protocol(self, mock_delete):
        mock_response = MagicMock()
        mock_response.json.return_value = {"message": "Protocol deleted"}
        mock_response.raise_for_status = MagicMock()
        mock_delete.return_value = mock_response

        result = FlexRuns.delete_protocol(
            "http://test_url/protocols", "test_protocol_id")
        self.assertEqual(result, {"message": "Protocol deleted"})
        mock_delete.assert_called_once_with(
            url="http://test_url/protocols/test_protocol_id",
            headers=FlexRuns.HEADERS,
        )

    @patch("flex_runs.requests.post")
    def test_upload_protocol(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "id": "test_protocol_id",
                "metadata": {"protocolName": "test_protocol"},
            }
        }
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        with patch("builtins.open", unittest.mock.mock_open(read_data="test data")) as mock_file:
            result = FlexRuns.upload_protocol(
                "http://test_url/protocols", "test_path")
            self.assertEqual(
                result,
                {"protocol_id": "test_protocol_id",
                    "protocol_name": "test_protocol"},
            )
            mock_file.assert_called_once_with("test_path", "rb")
            mock_post.assert_called_once()

    @patch("flex_runs.requests.post")
    def test_upload_protocol_custom_labware(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "id": "test_protocol_id",
                "metadata": {"protocolName": "test_protocol"},
            }
        }
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        with patch("builtins.open", unittest.mock.mock_open(read_data="test data")) as mock_file:
            result = FlexRuns.upload_protocol_custom_labware(
                "http://test_url/protocols",
                "protocol_path",
                ["labware1_path", "labware2_path"],
            )
            self.assertEqual(
                result,
                {"protocol_id": "test_protocol_id",
                    "protocol_name": "test_protocol"},
            )
            self.assertEqual(mock_file.call_count, 3)
            mock_post.assert_called_once()

    @patch("flex_runs.requests.delete")
    def test_delete_run(self, mock_delete):
        mock_response = MagicMock()
        mock_response.json.return_value = {"message": "Run deleted"}
        mock_response.raise_for_status = MagicMock()
        mock_delete.return_value = mock_response

        result = FlexRuns.delete_run("http://test_url/runs", 123)
        self.assertEqual(result, {"message": "Run deleted"})
        mock_delete.assert_called_once_with(
            url="http://test_url/runs/123",
            headers=FlexRuns.HEADERS,
        )

    @patch("flex_runs.requests.get")
    def test_get_protocols_list(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [{"id": "1", "name": "protocol1"}, {"id": "2", "name": "protocol2"}]
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = FlexRuns.get_protocols_list("http://test_url/protocols")
        self.assertEqual(
            result, [{"id": "1", "name": "protocol1"},
                     {"id": "2", "name": "protocol2"}]
        )
        mock_get.assert_called_once_with(
            url="http://test_url/protocols", headers=FlexRuns.HEADERS
        )


if __name__ == "__main__":
    unittest.main()
