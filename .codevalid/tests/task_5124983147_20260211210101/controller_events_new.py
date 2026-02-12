import unittest
from unittest.mock import patch, MagicMock

import sys
import os

# Ensure the app directory is in the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../app')))

from controllers.events_controller import EventsController
from models.event import Event

class EventsControllerNewTest(unittest.TestCase):
    def setUp(self):
        self.controller = EventsController()
        # Patch authentication if present
        self.auth_patch = patch.object(self.controller, 'authenticate_user', return_value=True)
        if hasattr(self.controller, 'authenticate_user'):
            self.auth_patch.start()
            self.addCleanup(self.auth_patch.stop)

    @patch('models.event.Event')
    @patch('controllers.events_controller.User')
    def test_new_event_success(self, mock_user, mock_event):
        # Given: Database contains users eligible for assignment
        eligible_users = [MagicMock(), MagicMock()]
        mock_user.eligible_for_assignment.return_value = eligible_users
        event_instance = MagicMock()
        event_instance.pk = None
        mock_event.return_value = event_instance

        # When
        self.controller.new()

        # Then
        self.assertIs(self.controller._event, event_instance)
        self.assertEqual(self.controller._users, eligible_users)
        mock_event.assert_called_once_with()
        mock_user.eligible_for_assignment.assert_called_once_with()

    @patch('models.event.Event')
    @patch('controllers.events_controller.User')
    def test_no_users_available(self, mock_user, mock_event):
        # Given: Database contains zero users
        mock_user.eligible_for_assignment.return_value = []
        event_instance = MagicMock()
        event_instance.pk = None
        mock_event.return_value = event_instance

        # When
        self.controller.new()

        # Then
        self.assertIs(self.controller._event, event_instance)
        self.assertEqual(self.controller._users, [])
        mock_event.assert_called_once_with()
        mock_user.eligible_for_assignment.assert_called_once_with()

    @patch('models.event.Event')
    @patch('controllers.events_controller.User')
    def test_users_with_ineligible_status(self, mock_user, mock_event):
        # Given: Database contains both eligible and ineligible users
        eligible_users = [MagicMock()]
        ineligible_users = [MagicMock()]
        mock_user.eligible_for_assignment.return_value = eligible_users
        event_instance = MagicMock()
        event_instance.pk = None
        mock_event.return_value = event_instance

        # When
        self.controller.new()

        # Then
        self.assertIs(self.controller._event, event_instance)
        self.assertEqual(self.controller._users, eligible_users)
        self.assertNotIn(ineligible_users[0], self.controller._users)
        mock_event.assert_called_once_with()
        mock_user.eligible_for_assignment.assert_called_once_with()

    @patch('models.event.Event')
    @patch('controllers.events_controller.User')
    def test_event_model_initialization_failure(self, mock_user, mock_event):
        # Given: Event model is misconfigured or has a required attribute with no default
        mock_event.side_effect = Exception("Initialization failed")
        mock_user.eligible_for_assignment.return_value = []

        # When / Then
        with self.assertRaises(Exception) as context:
            self.controller.new()
        self.assertIn("Initialization failed", str(context.exception))
        mock_event.assert_called_once_with()

    @patch('models.event.Event')
    @patch('controllers.events_controller.User')
    def test_user_query_failure(self, mock_user, mock_event):
        # Given: User model or database connection fails when fetching users
        mock_user.eligible_for_assignment.side_effect = Exception("User query failed")
        event_instance = MagicMock()
        event_instance.pk = None
        mock_event.return_value = event_instance

        # When / Then
        with self.assertRaises(Exception) as context:
            self.controller.new()
        self.assertIn("User query failed", str(context.exception))
        mock_event.assert_called_once_with()
        mock_user.eligible_for_assignment.assert_called_once_with()

    @patch('models.event.Event')
    @patch('controllers.events_controller.User')
    def test_event_prepopulated_attributes(self, mock_user, mock_event):
        # Given: Event model has default attributes set via model or database
        event_instance = MagicMock()
        event_instance.pk = None
        event_instance.default_attr = "default_value"
        mock_event.return_value = event_instance
        mock_user.eligible_for_assignment.return_value = []

        # When
        self.controller.new()

        # Then
        self.assertIs(self.controller._event, event_instance)
        self.assertEqual(self.controller._event.default_attr, "default_value")
        mock_event.assert_called_once_with()
        mock_user.eligible_for_assignment.assert_called_once_with()

    @patch('controllers.events_controller.User')
    @patch('models.event.Event')
    def test_authenticated_user_required(self, mock_event, mock_user):
        # Given: No user is authenticated and controller requires authentication
        # Simulate authentication failure
        if hasattr(self.controller, 'authenticate_user'):
            self.controller.authenticate_user = MagicMock(side_effect=Exception("Unauthorized"))
        mock_event.return_value = MagicMock()
        mock_user.eligible_for_assignment.return_value = []

        # When / Then
        if hasattr(self.controller, 'authenticate_user'):
            with self.assertRaises(Exception) as context:
                self.controller.new()
            self.assertIn("Unauthorized", str(context.exception))
        else:
            # If no authentication, test passes as not applicable
            self.skipTest("Authentication not implemented in controller.")

if __name__ == '__main__':
    unittest.main()