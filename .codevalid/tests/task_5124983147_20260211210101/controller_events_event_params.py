import unittest
from unittest.mock import MagicMock

import sys
import os

# Ensure app is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

from app.controllers.events_controller import EventsController

class TestEventsControllerEventParams(unittest.TestCase):
    def setUp(self):
        # Simulate a controller instance with params attribute
        class DummyController(EventsController):
            def __init__(self, params):
                self.params = params

        self.DummyController = DummyController

    def call_event_params(self, params):
        controller = self.DummyController(params)
        return controller.event_params()

    def test_valid_event_parameters_with_assigned_user_ids_present_and_all_values_valid(self):
        # Test Case 1
        params = {
            'event': {
                'assigned_user_ids': ['1', '2', '3'],
                'description': 'Discuss project updates',
                'title': 'Team Meeting'
            }
        }
        expected = {
            'assigned_user_ids': [1, 2, 3],
            'description': 'Discuss project updates',
            'title': 'Team Meeting'
        }
        result = self.call_event_params({'params': params})
        self.assertEqual(result, expected)

    def test_assigned_user_ids_contains_blank_values(self):
        # Test Case 2
        params = {
            'event': {
                'assigned_user_ids': ['', '4', ' ', '5'],
                'description': 'Plan next sprint',
                'title': 'Sprint Planning'
            }
        }
        expected = {
            'assigned_user_ids': [4, 5],
            'description': 'Plan next sprint',
            'title': 'Sprint Planning'
        }
        result = self.call_event_params({'params': params})
        self.assertEqual(result, expected)

    def test_assigned_user_ids_array_contains_only_blank_values(self):
        # Test Case 3
        params = {
            'event': {
                'assigned_user_ids': ['', ' ', ''],
                'description': 'Showcase features',
                'title': 'Demo Day'
            }
        }
        expected = {
            'assigned_user_ids': [],
            'description': 'Showcase features',
            'title': 'Demo Day'
        }
        result = self.call_event_params({'params': params})
        self.assertEqual(result, expected)

    def test_assigned_user_ids_is_missing(self):
        # Test Case 4
        params = {
            'event': {
                'description': 'Release new version',
                'title': 'Release'
            }
        }
        expected = {
            'assigned_user_ids': [],
            'description': 'Release new version',
            'title': 'Release'
        }
        result = self.call_event_params({'params': params})
        self.assertEqual(result, expected)

    def test_assigned_user_ids_is_an_empty_array(self):
        # Test Case 5
        params = {
            'event': {
                'assigned_user_ids': [],
                'description': 'Review bugs',
                'title': 'Bug Triage'
            }
        }
        expected = {
            'assigned_user_ids': [],
            'description': 'Review bugs',
            'title': 'Bug Triage'
        }
        result = self.call_event_params({'params': params})
        self.assertEqual(result, expected)

    def test_assigned_user_ids_contains_non_numeric_values(self):
        # Test Case 6
        params = {
            'event': {
                'assigned_user_ids': ['abc', '6', '', 'xyz'],
                'description': 'Daily sync',
                'title': 'Standup'
            }
        }
        expected = {
            'assigned_user_ids': [6],
            'description': 'Daily sync',
            'title': 'Standup'
        }
        result = self.call_event_params({'params': params})
        self.assertEqual(result, expected)

    def test_unpermitted_params_included(self):
        # Test Case 7
        params = {
            'event': {
                'assigned_user_ids': ['7'],
                'description': 'Review the sprint',
                'title': 'Retrospective',
                'unpermitted': 'should not be included'
            }
        }
        expected = {
            'assigned_user_ids': [7],
            'description': 'Review the sprint',
            'title': 'Retrospective'
        }
        result = self.call_event_params({'params': params})
        self.assertEqual(result, expected)

    def test_title_is_missing(self):
        # Test Case 8
        params = {
            'event': {
                'assigned_user_ids': ['8', '9'],
                'description': 'No title event'
            }
        }
        expected = {
            'assigned_user_ids': [8, 9],
            'description': 'No title event'
        }
        result = self.call_event_params({'params': params})
        self.assertEqual(result, expected)

    def test_description_is_missing(self):
        # Test Case 9
        params = {
            'event': {
                'assigned_user_ids': ['10'],
                'title': 'No Description'
            }
        }
        expected = {
            'assigned_user_ids': [10],
            'title': 'No Description'
        }
        result = self.call_event_params({'params': params})
        self.assertEqual(result, expected)

    def test_no_event_key_in_params(self):
        # Test Case 10
        params = {}
        expected = {}
        result = self.call_event_params({'params': params})
        self.assertEqual(result, expected)

    def test_assigned_user_ids_contains_nested_array(self):
        # Test Case 11
        params = {
            'event': {
                'assigned_user_ids': ['11', ['12', '']],
                'description': 'Training session',
                'title': 'Workshop'
            }
        }
        expected = {
            'assigned_user_ids': [11, 12],
            'description': 'Training session',
            'title': 'Workshop'
        }
        result = self.call_event_params({'params': params})
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()