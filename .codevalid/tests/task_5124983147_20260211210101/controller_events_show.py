import os
import sys
import subprocess
import tempfile
import textwrap

import unittest

class TestEventsControllerShow(unittest.TestCase):
    """
    Integration tests for EventsController#show via Rails minitest.
    Each test will invoke the Rails test runner with a dynamically generated test file.
    """

    RAILS_TEST_TEMPLATE = textwrap.dedent("""
        require 'test_helper'

        class EventsControllerShowTest < ActionDispatch::IntegrationTest
          # Test Case 1: Show Event with Valid ID
          test "Show Event with Valid ID" do
            event = Event.create!(title: "Test Event 1")
            user1 = User.create!(name: "User One")
            user2 = User.create!(name: "User Two")
            event.assigned_user_ids = [user1.id, user2.id]
            event.save!

            get event_path(event.id)
            assert_response :success
            assert assigns(:event)
            assert_equal event, assigns(:event)
            assert_includes @response.body, "Test Event 1"
            assert_includes @response.body, "User One"
            assert_includes @response.body, "User Two"
          end

          # Test Case 2: Show Event with Nonexistent ID
          test "Show Event with Nonexistent ID" do
            get event_path(999)
            assert_response :not_found
            assert_nil assigns(:event)
          end

          # Test Case 3: Show Event with Missing ID
          test "Show Event with Missing ID" do
            assert_raises(ActionController::UrlGenerationError) do
              get event_path(nil)
            end
          end

          # Test Case 4: Show Event with Invalid ID Format
          test "Show Event with Invalid ID Format" do
            assert_raises(ActionController::UrlGenerationError) do
              get event_path('abc')
            end
          end

          # Test Case 5: Show Event with No Users Assigned
          test "Show Event with No Users Assigned" do
            event = Event.create!(title: "No Users Event")
            event.assigned_user_ids = []
            event.save!

            get event_path(event.id)
            assert_response :success
            assert assigns(:event)
            assert_equal event, assigns(:event)
            assert_includes @response.body, "No Users Event"
            # Should not include any user names
            assert_not_match(/User/, @response.body)
          end

          # Test Case 6: Show Event with Multiple Users Assigned
          test "Show Event with Multiple Users Assigned" do
            event = Event.create!(title: "Multi User Event")
            users = 3.times.map { |i| User.create!(name: "User#{i+1}") }
            event.assigned_user_ids = users.map(&:id)
            event.save!

            get event_path(event.id)
            assert_response :success
            assert assigns(:event)
            users.each do |user|
              assert_includes @response.body, user.name
            end
          end

          # Test Case 7: Show Event with Boundary ID
          test "Show Event with Boundary ID" do
            # ID = 0 (unlikely, but test)
            event0 = Event.create!(id: 0, title: "Boundary Event Zero")
            get event_path(0)
            assert_response :success
            assert assigns(:event)
            assert_equal event0, assigns(:event)
            assert_includes @response.body, "Boundary Event Zero"

            # ID = max integer
            max_id = 2**31 - 1
            event_max = Event.create!(id: max_id, title: "Boundary Event Max")
            get event_path(max_id)
            assert_response :success
            assert assigns(:event)
            assert_equal event_max, assigns(:event)
            assert_includes @response.body, "Boundary Event Max"
          end

          # Test Case 8: Show Event with Deleted Event
          test "Show Event with Deleted Event" do
            event = Event.create!(title: "To Be Deleted")
            id = event.id
            event.destroy

            get event_path(id)
            assert_response :not_found
            assert_nil assigns(:event)
          end

          # Test Case 9: Show Event with Large Number of Users Assigned
          test "Show Event with Large Number of Users Assigned" do
            event = Event.create!(title: "Large User Event")
            users = 1000.times.map { |i| User.create!(name: "User#{i+1}") }
            event.assigned_user_ids = users.map(&:id)
            event.save!

            get event_path(event.id)
            assert_response :success
            assert assigns(:event)
            users.each do |user|
              assert_includes @response.body, user.name
            end
          end
        end
    """)

    def run_rails_test(self, test_ruby_code):
        with tempfile.NamedTemporaryFile(suffix="_events_controller_show_test.rb", mode="w", delete=False) as f:
            f.write(test_ruby_code)
            test_file_path = f.name

        try:
            # Run the test using Rails test runner
            result = subprocess.run(
                ["bin/rails", "test", test_file_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            return result.returncode, result.stdout, result.stderr
        finally:
            os.remove(test_file_path)

    def test_all_cases(self):
        """Runs all controller show test cases via Rails minitest."""
        code = self.RAILS_TEST_TEMPLATE
        rc, out, err = self.run_rails_test(code)
        print("STDOUT:\n", out)
        print("STDERR:\n", err)
        self.assertEqual(rc, 0, f"Rails test failed:\n{out}\n{err}")

if __name__ == "__main__":
    unittest.main()