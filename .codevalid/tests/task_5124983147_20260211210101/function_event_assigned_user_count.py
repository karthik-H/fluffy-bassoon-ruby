import unittest

import sys
import types

# Mocking the Event class as per Ruby's app/models/event.rb for Python test simulation
class Event:
    def __init__(self, assigned_user_ids=None):
        self.assigned_user_ids = assigned_user_ids

    def assigned_user_count(self):
        # Simulate the Ruby logic: return size of assigned_user_ids array or 0
        if isinstance(self.assigned_user_ids, list):
            return len(self.assigned_user_ids)
        return 0

class TestEventAssignedUserCount(unittest.TestCase):
    def test_count_returns_number_of_assigned_users(self):
        """Returns correct count when assigned_user_ids contains multiple user IDs."""
        event = Event(assigned_user_ids=[1, 2, 3, 4])
        self.assertEqual(event.assigned_user_count(), 4)

    def test_count_returns_one_for_single_user(self):
        """Returns 1 when assigned_user_ids contains a single user ID."""
        event = Event(assigned_user_ids=[42])
        self.assertEqual(event.assigned_user_count(), 1)

    def test_count_returns_zero_when_no_users_assigned(self):
        """Returns 0 when assigned_user_ids is an empty array."""
        event = Event(assigned_user_ids=[])
        self.assertEqual(event.assigned_user_count(), 0)

    def test_count_returns_zero_when_assigned_user_ids_is_nil(self):
        """Returns 0 when assigned_user_ids is nil."""
        event = Event(assigned_user_ids=None)
        self.assertEqual(event.assigned_user_count(), 0)

    def test_count_handles_non_array_assigned_user_ids(self):
        """Checks behavior when assigned_user_ids is not an array (e.g., is an integer). Should handle gracefully or return 0."""
        event = Event(assigned_user_ids=5)
        self.assertEqual(event.assigned_user_count(), 0)

    def test_count_includes_duplicates_in_assigned_user_ids(self):
        """Returns count including duplicate user IDs if present."""
        event = Event(assigned_user_ids=[1, 2, 2, 3])
        self.assertEqual(event.assigned_user_count(), 4)

    def test_count_handles_string_ids_in_assigned_user_ids(self):
        """Checks behavior when assigned_user_ids contains string IDs instead of integers."""
        event = Event(assigned_user_ids=["a", "b", 1])
        self.assertEqual(event.assigned_user_count(), 3)

    def test_count_handles_large_number_of_assigned_users(self):
        """Returns correct count when assigned_user_ids contains a large number of user IDs."""
        event = Event(assigned_user_ids=list(range(1, 10001)))
        self.assertEqual(event.assigned_user_count(), 10000)

    def test_count_handles_object_assigned_user_ids(self):
        """Checks behavior when assigned_user_ids is an object instead of an array. Should return 0 or handle safely."""
        event = Event(assigned_user_ids={"user": 1})
        self.assertEqual(event.assigned_user_count(), 0)

if __name__ == '__main__':
    unittest.main()