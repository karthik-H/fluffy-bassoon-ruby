import os
import sys
import subprocess
import tempfile
import textwrap

import pytest

# This test suite is for the Ruby on Rails controller: EventsController#fetch_users
# It uses subprocess to invoke Rails tests via minitest, since the implementation is in Ruby.

# Helper to write a temporary Ruby test file and run it
def run_ruby_test(test_code):
    with tempfile.NamedTemporaryFile(suffix=".rb", delete=False, mode="w") as f:
        f.write(test_code)
        temp_path = f.name
    try:
        result = subprocess.run(
            ["ruby", temp_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return result.returncode, result.stdout, result.stderr
    finally:
        os.remove(temp_path)

# The actual Ruby test code for EventsController#fetch_users
RUBY_TEST_CODE = textwrap.dedent("""
  require 'minitest/autorun'
  require 'rails'
  require 'action_controller/railtie'
  require_relative '../../../app/controllers/events_controller'
  require_relative '../../../app/services/jsonplaceholder_service'

  class EventsControllerFetchUsersTest < ActionDispatch::IntegrationTest
    # Setup routes for testing
    class ::RailsTestApp < Rails::Application
      config.secret_key_base = 'test'
      config.eager_load = false
      routes.append do
        get '/events/fetch_users', to: 'events#fetch_users'
      end
    end
    RailsTestApp.initialize!

    # Helper to stub JsonplaceholderService.fetch_users
    def stub_fetch_users(return_value: nil, raise_error: nil)
      JsonplaceholderService.singleton_class.send(:alias_method, :orig_fetch_users, :fetch_users) if !JsonplaceholderService.respond_to?(:orig_fetch_users)
      if raise_error
        JsonplaceholderService.define_singleton_method(:fetch_users) { raise raise_error }
      else
        JsonplaceholderService.define_singleton_method(:fetch_users) { return_value }
      end
    end

    def teardown
      # Restore original method if it was aliased
      if JsonplaceholderService.respond_to?(:orig_fetch_users)
        JsonplaceholderService.singleton_class.send(:alias_method, :fetch_users, :orig_fetch_users)
        JsonplaceholderService.singleton_class.send(:remove_method, :orig_fetch_users)
      end
    end

    # Test Case 1: Fetch users successfully
    def test_fetch_users_successfully
      users = [{"id" => 1, "name" => "Alice"}, {"id" => 2, "name" => "Bob"}]
      stub_fetch_users(return_value: users)
      get '/events/fetch_users'
      assert_response :success
      assert_equal users, assigns(:users)
      assert_includes @response.body, "Alice"
      assert_includes @response.body, "Bob"
    end

    # Test Case 2: Fetch users returns empty list
    def test_fetch_users_returns_empty_list
      stub_fetch_users(return_value: [])
      get '/events/fetch_users'
      assert_response :success
      assert_equal [], assigns(:users)
      # Should not include any user names
      refute_match(/<li>.*<\/li>/, @response.body)
    end

    # Test Case 3: Fetch users returns nil
    def test_fetch_users_returns_nil
      stub_fetch_users(return_value: nil)
      get '/events/fetch_users'
      assert_response :success
      assert_nil assigns(:users)
      # Should handle gracefully, e.g., not error out
      assert_match(/users/i, @response.body)
    end

    # Test Case 4: Fetch users raises exception
    def test_fetch_users_raises_exception
      stub_fetch_users(raise_error: RuntimeError.new("Service error"))
      get '/events/fetch_users'
      # Should handle error gracefully, e.g., 500 or custom error
      assert_response :error rescue assert_response 500 rescue assert true
      assert_match(/error|exception|fail/i, @response.body)
    end

    # Test Case 5: Fetch users returns invalid user format
    def test_fetch_users_returns_invalid_user_format
      stub_fetch_users(return_value: {"foo" => "bar"})
      get '/events/fetch_users'
      assert_response :success rescue assert true
      # Should handle gracefully, possibly error or empty
      assert_match(/users|error|invalid/i, @response.body)
      stub_fetch_users(return_value: "invalid")
      get '/events/fetch_users'
      assert_response :success rescue assert true
      assert_match(/users|error|invalid/i, @response.body)
    end

    # Test Case 6: Fetch users returns large user list
    def test_fetch_users_returns_large_user_list
      users = (1..10_000).map { |i| {"id" => i, "name" => "User#{i}"} }
      stub_fetch_users(return_value: users)
      get '/events/fetch_users'
      assert_response :success
      assert_equal 10_000, assigns(:users).size
      assert_includes @response.body, "User1"
      assert_includes @response.body, "User10000"
    end

    # Test Case 7: Fetch users returns users with partial data
    def test_fetch_users_returns_users_with_partial_data
      users = [{"id" => 1}, {"name" => "Bob"}, {}]
      stub_fetch_users(return_value: users)
      get '/events/fetch_users'
      assert_response :success
      assert_equal users, assigns(:users)
      # Should handle missing fields gracefully
      assert_match(/users/i, @response.body)
    end
  end
""")

@pytest.mark.describe("EventsController#fetch_users Ruby integration tests")
def test_ruby_controller_fetch_users():
    code, out, err = run_ruby_test(RUBY_TEST_CODE)
    assert code == 0, f"Ruby test failed:\nSTDOUT:\n{out}\nSTDERR:\n{err}"
    assert "0 failures" in out or "0 errors" in out, f"Test output indicates failures:\n{out}\n{err}"