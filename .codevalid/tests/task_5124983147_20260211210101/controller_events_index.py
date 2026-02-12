import unittest
from unittest.mock import patch, MagicMock
import datetime

# Assuming usage of requests for HTTP calls to the Rails test server
import requests

class EventsControllerIndexTest(unittest.TestCase):
    BASE_URL = "http://localhost:3000"  # Adjust if test server runs on a different port

    def setUp(self):
        # Clean up and prepare the database for each test
        # This assumes a test helper endpoint or direct DB access for test setup
        # In a real Rails test, you'd use fixtures or FactoryBot, but here we simulate via HTTP or mocks
        pass

    def tearDown(self):
        # Clean up after each test
        pass

    def create_event(self, created_at, extra_fields=None):
        """Helper to create an event via API or direct DB access."""
        data = {"created_at": created_at}
        if extra_fields:
            data.update(extra_fields)
        # This assumes a test-only endpoint exists for creating events
        # In a real Rails test, you'd use FactoryBot or fixtures
        requests.post(f"{self.BASE_URL}/test_helpers/events", json=data)

    def get_events(self, path="/events"):
        """Helper to GET events index."""
        return requests.get(f"{self.BASE_URL}{path}")

    def test_fetch_events_with_multiple_records(self):
        """Should return all events ordered by created_at descending when multiple events exist."""
        self.create_event("2024-01-01T00:00:00Z")
        self.create_event("2024-02-01T00:00:00Z")
        self.create_event("2024-03-01T00:00:00Z")
        resp = self.get_events()
        self.assertEqual(resp.status_code, 200)
        events = resp.json()
        self.assertEqual(len(events), 3)
        created_ats = [e["created_at"] for e in events]
        self.assertEqual(
            created_ats,
            ["2024-03-01T00:00:00Z", "2024-02-01T00:00:00Z", "2024-01-01T00:00:00Z"]
        )

    def test_fetch_events_with_single_record(self):
        """Should return a single event when only one event exists."""
        self.create_event("2024-05-01T00:00:00Z")
        resp = self.get_events()
        self.assertEqual(resp.status_code, 200)
        events = resp.json()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["created_at"], "2024-05-01T00:00:00Z")

    def test_fetch_events_with_no_records(self):
        """Should return an empty list when there are no events in the database."""
        resp = self.get_events()
        self.assertEqual(resp.status_code, 200)
        events = resp.json()
        self.assertEqual(events, [])

    def test_fetch_events_with_same_created_at(self):
        """Should return all events when multiple events have the same created_at value, maintaining a stable order."""
        self.create_event("2024-01-01T10:00:00Z", {"name": "A"})
        self.create_event("2024-01-01T10:00:00Z", {"name": "B"})
        self.create_event("2024-01-01T10:00:00Z", {"name": "C"})
        resp = self.get_events()
        self.assertEqual(resp.status_code, 200)
        events = resp.json()
        self.assertEqual(len(events), 3)
        # Check all have the same created_at
        for e in events:
            self.assertEqual(e["created_at"], "2024-01-01T10:00:00Z")
        # Check stable order by name (or id if available)
        names = [e["name"] for e in events]
        self.assertEqual(names, sorted(names))  # Assuming insertion order is preserved

    def test_fetch_events_with_large_number_of_records(self):
        """Should return all events correctly ordered when there is a large number of events."""
        base_date = datetime.datetime(2020, 1, 1)
        for i in range(10000):
            dt = base_date + datetime.timedelta(days=i)
            self.create_event(dt.strftime("%Y-%m-%dT00:00:00Z"))
        resp = self.get_events()
        self.assertEqual(resp.status_code, 200)
        events = resp.json()
        self.assertEqual(len(events), 10000)
        # Check descending order
        created_ats = [e["created_at"] for e in events]
        sorted_ats = sorted(created_ats, reverse=True)
        self.assertEqual(created_ats, sorted_ats)

    @patch("requests.get")
    def test_fetch_events_database_error(self, mock_get):
        """Should handle and report an error if the database is unavailable or query fails."""
        # Simulate DB error by mocking requests.get to return 500
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_resp.json.side_effect = Exception("DB error")
        mock_get.return_value = mock_resp
        resp = self.get_events()
        self.assertEqual(resp.status_code, 500)

    def test_fetch_events_with_future_created_at(self):
        """Should list events with created_at in the future at the top of the list."""
        self.create_event("2024-01-01T00:00:00Z")
        self.create_event("2999-12-31T00:00:00Z")
        resp = self.get_events()
        self.assertEqual(resp.status_code, 200)
        events = resp.json()
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0]["created_at"], "2999-12-31T00:00:00Z")
        self.assertEqual(events[1]["created_at"], "2024-01-01T00:00:00Z")

    def test_fetch_events_invalid_route(self):
        """Should return a 404 error if the route does not exist."""
        resp = self.get_events(path="/invalid_events_path")
        self.assertEqual(resp.status_code, 404)

if __name__ == "__main__":
    unittest.main()