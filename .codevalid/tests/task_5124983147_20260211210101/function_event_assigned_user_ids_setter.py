import unittest
import json

import sys
import os

# Ensure app/models is in the path for import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../app/models")))

from event import Event

class TestEventAssignedUserIdsSetter(unittest.TestCase):
    def setUp(self):
        # Create a new Event instance for each test
        self.event = Event()

    def test_assign_array_of_integers(self):
        # Given
        value = [1, 2, 3]
        # When
        self.event.assigned_user_ids = value
        # Then
        self.assertEqual(self.event.assigned_user_ids, json.dumps([1, 2, 3]))

    def test_assign_array_of_strings(self):
        # Given
        value = ['u1', 'u2']
        # When
        self.event.assigned_user_ids = value
        # Then
        self.assertEqual(self.event.assigned_user_ids, json.dumps(['u1', 'u2']))

    def test_assign_empty_array(self):
        # Given
        value = []
        # When
        self.event.assigned_user_ids = value
        # Then
        self.assertEqual(self.event.assigned_user_ids, json.dumps([]))

    def test_assign_array_with_nil(self):
        # Given
        value = [1, None, 3]
        # When
        self.event.assigned_user_ids = value
        # Then
        # Ruby nil -> JSON null, Python None -> JSON null
        self.assertEqual(self.event.assigned_user_ids, json.dumps([1, None, 3]))

    def test_assign_array_with_mixed_types(self):
        # Given
        value = [1, '2', 3.0, None]
        # When
        self.event.assigned_user_ids = value
        # Then
        self.assertEqual(self.event.assigned_user_ids, json.dumps([1, '2', 3.0, None]))

    def test_assign_string_input(self):
        # Given
        value = 'string_user_id'
        # When
        self.event.assigned_user_ids = value
        # Then
        self.assertEqual(self.event.assigned_user_ids, 'string_user_id')

    def test_assign_integer_input(self):
        # Given
        value = 42
        # When
        self.event.assigned_user_ids = value
        # Then
        self.assertEqual(self.event.assigned_user_ids, 42)

    def test_assign_nil_input(self):
        # Given
        value = None
        # When
        self.event.assigned_user_ids = value
        # Then
        self.assertIsNone(self.event.assigned_user_ids)

    def test_assign_array_with_duplicate_ids(self):
        # Given
        value = [1, 2, 2, 3]
        # When
        self.event.assigned_user_ids = value
        # Then
        self.assertEqual(self.event.assigned_user_ids, json.dumps([1, 2, 2, 3]))

    def test_assign_large_array(self):
        # Given
        value = list(range(1, 1001))
        # When
        self.event.assigned_user_ids = value
        # Then
        self.assertEqual(self.event.assigned_user_ids, json.dumps(value))

if __name__ == '__main__':
    unittest.main()