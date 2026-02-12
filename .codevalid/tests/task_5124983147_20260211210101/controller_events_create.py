import unittest
from unittest.mock import patch, MagicMock
from app import app

class EventsControllerCreateTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch("app.models.event.Event")
    def test_create_event_with_valid_parameters(self, MockEvent):
        """Test Case 1: Create event with valid parameters"""
        mock_event = MagicMock()
        mock_event.save.return_value = True
        MockEvent.new.return_value = mock_event

        valid_params = {
            "title": "Test Event",
            "date": "2026-02-12",
            "user_id": 1
        }

        response = self.app.post("/events", data={"event": valid_params}, follow_redirects=False)

        MockEvent.new.assert_called_once_with(valid_params)
        mock_event.save.assert_called_once()
        self.assertEqual(response.status_code, 302)
        self.assertIn("/events/", response.headers["Location"])
        # Notice message would be in flash, but not visible in redirect

    @patch("app.models.event.Event")
    @patch("app.models.user.User")
    def test_create_event_with_missing_title(self, MockUser, MockEvent):
        """Test Case 2: Create event with missing title"""
        mock_event = MagicMock()
        mock_event.save.return_value = False
        mock_event.errors = {"title": ["can't be blank"]}
        MockEvent.new.return_value = mock_event

        MockUser.all.return_value = [MagicMock(id=1, name="User1")]

        params = {
            "date": "2026-02-12",
            "user_id": 1
        }

        response = self.app.post("/events", data={"event": params})

        MockEvent.new.assert_called_once_with(params)
        mock_event.save.assert_called_once()
        MockUser.all.assert_called_once()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"can't be blank", response.data)
        self.assertIn(b"New Event", response.data)

    @patch("app.models.event.Event")
    @patch("app.models.user.User")
    def test_create_event_with_invalid_date_format(self, MockUser, MockEvent):
        """Test Case 3: Create event with invalid date format"""
        mock_event = MagicMock()
        mock_event.save.return_value = False
        mock_event.errors = {"date": ["is invalid"]}
        MockEvent.new.return_value = mock_event

        MockUser.all.return_value = [MagicMock(id=1, name="User1")]

        params = {
            "title": "Event",
            "date": "not-a-date",
            "user_id": 1
        }

        response = self.app.post("/events", data={"event": params})

        MockEvent.new.assert_called_once_with(params)
        mock_event.save.assert_called_once()
        MockUser.all.assert_called_once()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"is invalid", response.data)
        self.assertIn(b"New Event", response.data)

    @patch("app.models.event.Event")
    @patch("app.models.user.User")
    def test_create_event_with_non_existent_user(self, MockUser, MockEvent):
        """Test Case 4: Create event with non-existent user"""
        mock_event = MagicMock()
        mock_event.save.return_value = False
        mock_event.errors = {"user": ["must exist"]}
        MockEvent.new.return_value = mock_event

        MockUser.all.return_value = []

        params = {
            "title": "Event",
            "date": "2026-02-12",
            "user_id": 9999
        }

        response = self.app.post("/events", data={"event": params})

        MockEvent.new.assert_called_once_with(params)
        mock_event.save.assert_called_once()
        MockUser.all.assert_called_once()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"must exist", response.data)
        self.assertIn(b"New Event", response.data)

    @patch("app.models.event.Event")
    @patch("app.models.user.User")
    def test_create_event_with_empty_event_params(self, MockUser, MockEvent):
        """Test Case 5: Create event with empty event_params"""
        mock_event = MagicMock()
        mock_event.save.return_value = False
        mock_event.errors = {"title": ["can't be blank"], "date": ["can't be blank"], "user_id": ["can't be blank"]}
        MockEvent.new.return_value = mock_event

        MockUser.all.return_value = [MagicMock(id=1, name="User1")]

        params = {}

        response = self.app.post("/events", data={"event": params})

        MockEvent.new.assert_called_once_with(params)
        mock_event.save.assert_called_once()
        MockUser.all.assert_called_once()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"can't be blank", response.data)
        self.assertIn(b"New Event", response.data)

    @patch("app.models.event.Event")
    def test_create_event_with_boundary_title_length(self, MockEvent):
        """Test Case 6: Create event with boundary title length"""
        mock_event = MagicMock()
        mock_event.save.return_value = True
        MockEvent.new.return_value = mock_event

        max_length_title = "A" * 255
        params = {
            "title": max_length_title,
            "date": "2026-02-12",
            "user_id": 1
        }

        response = self.app.post("/events", data={"event": params}, follow_redirects=False)

        MockEvent.new.assert_called_once_with(params)
        mock_event.save.assert_called_once()
        self.assertEqual(response.status_code, 302)
        self.assertIn("/events/", response.headers["Location"])

    @patch("app.models.event.Event")
    @patch("app.models.user.User")
    def test_create_event_with_duplicate_title(self, MockUser, MockEvent):
        """Test Case 7: Create event with duplicate title"""
        mock_event = MagicMock()
        mock_event.save.return_value = False
        mock_event.errors = {"title": ["has already been taken"]}
        MockEvent.new.return_value = mock_event

        MockUser.all.return_value = [MagicMock(id=1, name="User1")]

        params = {
            "title": "Existing Event",
            "date": "2026-02-12",
            "user_id": 1
        }

        response = self.app.post("/events", data={"event": params})

        MockEvent.new.assert_called_once_with(params)
        mock_event.save.assert_called_once()
        MockUser.all.assert_called_once()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"has already been taken", response.data)
        self.assertIn(b"New Event", response.data)

    @patch("app.models.event.Event")
    def test_create_event_with_minimum_required_fields(self, MockEvent):
        """Test Case 8: Create event with minimum required fields"""
        mock_event = MagicMock()
        mock_event.save.return_value = True
        MockEvent.new.return_value = mock_event

        params = {
            "title": "Minimal Event",
            "date": "2026-02-12",
            "user_id": 1
        }

        response = self.app.post("/events", data={"event": params}, follow_redirects=False)

        MockEvent.new.assert_called_once_with(params)
        mock_event.save.assert_called_once()
        self.assertEqual(response.status_code, 302)
        self.assertIn("/events/", response.headers["Location"])

    @patch("app.models.event.Event")
    @patch("app.models.user.User")
    def test_create_event_with_invalid_field_type(self, MockUser, MockEvent):
        """Test Case 9: Create event with invalid field type"""
        mock_event = MagicMock()
        mock_event.save.return_value = False
        mock_event.errors = {"date": ["is not a valid date"]}
        MockEvent.new.return_value = mock_event

        MockUser.all.return_value = [MagicMock(id=1, name="User1")]

        params = {
            "title": "Event",
            "date": 123456,  # Invalid type
            "user_id": 1
        }

        response = self.app.post("/events", data={"event": params})

        MockEvent.new.assert_called_once_with(params)
        mock_event.save.assert_called_once()
        MockUser.all.assert_called_once()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"is not a valid date", response.data)
        self.assertIn(b"New Event", response.data)

    @patch("app.models.event.Event")
    def test_create_event_with_large_event_params_object(self, MockEvent):
        """Test Case 10: Create event with large event_params object"""
        mock_event = MagicMock()
        mock_event.save.return_value = True
        MockEvent.new.return_value = mock_event

        params = {
            "title": "Big Event",
            "date": "2026-02-12",
            "user_id": 1,
            "extra_field1": "foo",
            "extra_field2": "bar",
            "extra_field3": 123
        }

        response = self.app.post("/events", data={"event": params}, follow_redirects=False)

        # Only permitted fields should be passed to Event.new
        expected_params = {
            "title": "Big Event",
            "date": "2026-02-12",
            "user_id": 1
        }
        MockEvent.new.assert_called_once_with(expected_params)
        mock_event.save.assert_called_once()
        self.assertEqual(response.status_code, 302)
        self.assertIn("/events/", response.headers["Location"])

if __name__ == "__main__":
    unittest.main()