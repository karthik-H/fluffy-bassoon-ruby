import unittest
from unittest.mock import patch, MagicMock

import sys
import os

# Ensure app is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from app.controllers.events_controller import EventsController
from app.models.event import Event

class EventsControllerEditTest(unittest.TestCase):
    def setUp(self):
        self.controller = EventsController()
        self.controller.params = {}
        self.controller.instance_variable_set = MagicMock()
        self.controller.set_event = MagicMock()
        self.controller.fetch_users_for_assignment = MagicMock()
        self.controller.users = []
        self.controller.event = None

    @patch('app.controllers.events_controller.Event')
    @patch('app.controllers.events_controller.User')
    def test_edit_existing_event_with_valid_id(self, MockUser, MockEvent):
        # Given
        event = MagicMock()
        event.id = 10
        MockEvent.find.return_value = event
        users = [MagicMock(), MagicMock()]
        MockUser.all.return_value = users

        self.controller.params = {'id': 10}
        self.controller.set_event = MagicMock(side_effect=lambda: setattr(self.controller, 'event', event))
        self.controller.fetch_users_for_assignment = MagicMock(side_effect=lambda: setattr(self.controller, 'users', users))

        # When
        self.controller.edit()

        # Then
        self.assertEqual(self.controller.event.id, 10)
        self.assertEqual(self.controller.users, users)

    @patch('app.controllers.events_controller.Event')
    def test_edit_with_non_existent_event_id(self, MockEvent):
        # Given
        MockEvent.find.side_effect = Exception('ActiveRecord::RecordNotFound')
        self.controller.params = {'id': 9999}
        self.controller.set_event = MagicMock(side_effect=Exception('ActiveRecord::RecordNotFound'))

        # When / Then
        with self.assertRaises(Exception) as context:
            self.controller.edit()
        self.assertIn('ActiveRecord::RecordNotFound', str(context.exception))

    @patch('app.controllers.events_controller.Event')
    @patch('app.controllers.events_controller.User')
    def test_edit_event_when_no_users_exist(self, MockUser, MockEvent):
        # Given
        event = MagicMock()
        event.id = 20
        MockEvent.find.return_value = event
        MockUser.all.return_value = []

        self.controller.params = {'id': 20}
        self.controller.set_event = MagicMock(side_effect=lambda: setattr(self.controller, 'event', event))
        self.controller.fetch_users_for_assignment = MagicMock(side_effect=lambda: setattr(self.controller, 'users', []))

        # When
        self.controller.edit()

        # Then
        self.assertEqual(self.controller.event.id, 20)
        self.assertEqual(self.controller.users, [])

    @patch('app.controllers.events_controller.Event')
    @patch('app.controllers.events_controller.User')
    def test_edit_event_with_no_current_user_assignments(self, MockUser, MockEvent):
        # Given
        event = MagicMock()
        event.id = 30
        event.assigned_user_ids = []
        MockEvent.find.return_value = event
        users = [MagicMock(), MagicMock()]
        MockUser.all.return_value = users

        self.controller.params = {'id': 30}
        self.controller.set_event = MagicMock(side_effect=lambda: setattr(self.controller, 'event', event))
        self.controller.fetch_users_for_assignment = MagicMock(side_effect=lambda: setattr(self.controller, 'users', users))

        # When
        self.controller.edit()

        # Then
        self.assertEqual(self.controller.event.id, 30)
        self.assertEqual(self.controller.users, users)
        self.assertEqual(getattr(self.controller.event, 'assigned_user_ids', []), [])

    @patch('app.controllers.events_controller.Event')
    @patch('app.controllers.events_controller.User')
    def test_edit_event_with_large_number_of_users(self, MockUser, MockEvent):
        # Given
        event = MagicMock()
        event.id = 40
        MockEvent.find.return_value = event
        users = [MagicMock() for _ in range(1000)]
        MockUser.all.return_value = users

        self.controller.params = {'id': 40}
        self.controller.set_event = MagicMock(side_effect=lambda: setattr(self.controller, 'event', event))
        self.controller.fetch_users_for_assignment = MagicMock(side_effect=lambda: setattr(self.controller, 'users', users))

        # When
        self.controller.edit()

        # Then
        self.assertEqual(self.controller.event.id, 40)
        self.assertEqual(len(self.controller.users), 1000)

    def test_edit_event_with_invalid_event_id_type(self):
        # Given
        self.controller.params = {'id': 'abc'}
        self.controller.set_event = MagicMock(side_effect=Exception('Invalid ID'))

        # When / Then
        with self.assertRaises(Exception) as context:
            self.controller.edit()
        self.assertIn('Invalid ID', str(context.exception))

    @patch('app.controllers.events_controller.Event')
    def test_edit_event_deleted_just_before_editing(self, MockEvent):
        # Given
        MockEvent.find.side_effect = Exception('ActiveRecord::RecordNotFound')
        self.controller.params = {'id': 50}
        self.controller.set_event = MagicMock(side_effect=Exception('ActiveRecord::RecordNotFound'))

        # When / Then
        with self.assertRaises(Exception) as context:
            self.controller.edit()
        self.assertIn('ActiveRecord::RecordNotFound', str(context.exception))

    @patch('app.controllers.events_controller.Event')
    @patch('app.controllers.events_controller.User')
    def test_edit_event_with_special_characters_in_attributes(self, MockUser, MockEvent):
        # Given
        event = MagicMock()
        event.id = 60
        event.name = "Party 🎉 & Co."
        event.description = "Let's celebrate! Special chars: <>&\"'/%"
        MockEvent.find.return_value = event
        users = [MagicMock()]
        MockUser.all.return_value = users

        self.controller.params = {'id': 60}
        self.controller.set_event = MagicMock(side_effect=lambda: setattr(self.controller, 'event', event))
        self.controller.fetch_users_for_assignment = MagicMock(side_effect=lambda: setattr(self.controller, 'users', users))

        # When
        self.controller.edit()

        # Then
        self.assertEqual(self.controller.event.id, 60)
        self.assertEqual(self.controller.event.name, "Party 🎉 & Co.")
        self.assertEqual(self.controller.event.description, "Let's celebrate! Special chars: <>&\"'/%")
        self.assertEqual(self.controller.users, users)

if __name__ == '__main__':
    unittest.main()