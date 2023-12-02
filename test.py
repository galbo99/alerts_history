import unittest
from main import fetch_alerts_history
from unittest.mock import patch


class TestFetchAlertsHistory(unittest.TestCase):
    @patch('main.log_operation')
    @patch('requests.get')
    def test_fetch_alerts_history_success(self, mock_requests_get, mock_log_operation):
        # Mocking the response
        mock_response = mock_requests_get.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = [{'alertDate': '2023-01-01', 'title': 'Test Alert', 'data': 'Test Data', 'category': 'Test Category'}]

        result = fetch_alerts_history('https://www.oref.org.il/WarningMessages/History/AlertsHistory.json')
        # Assertions
        self.assertEqual(result, [{'alertDate': '2023-01-01', 'title': 'Test Alert', 'data': 'Test Data', 'category': 'Test Category'}])
        mock_log_operation.assert_called_with("Fetching alerts history succeeded - there are 1 alerts in last 24 hours")

    @patch('main.log_operation')
    @patch('sys.exit')
    @patch('requests.get')
    def test_fetch_alerts_history_failure(self, mock_requests_get, mock_exit, mock_log_operation):
        # Mocking the response
        mock_response = mock_requests_get.return_value
        mock_response.status_code = 404
        mock_response.text = 'Not Found'

        fetch_alerts_history('https://www.oref.org.il/WarningMessages/History/AlertsHistory.json')

        # Assertions
        mock_log_operation.assert_called_with("API call failed with status code: 404  ... and reponse text: Not Found... exit script")
        mock_exit.assert_called_with(1)

if __name__ == '__main__':
    unittest.main()



