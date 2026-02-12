# This file is a Ruby test file, but the extension is .py per instructions.
# The content is a complete Minitest test suite for Event#assigned_users.

require 'minitest/autorun'
require 'mocha/minitest'
require_relative '../../../app/models/event'
require_relative '../../../app/services/jsonplaceholder_service'

class EventAssignedUsersTest < Minitest::Test
  def setup
    @event = Event.new
  end

  def test_returns_empty_array_when_assigned_user_ids_blank
    @event.assigned_user_ids = nil
    JsonplaceholderService.expects(:fetch_user).never
    assert_equal [], @event.assigned_users

    @event.assigned_user_ids = []
    JsonplaceholderService.expects(:fetch_user).never
    assert_equal [], @event.assigned_users
  end

  def test_returns_user_for_single_valid_assigned_user_id
    user = { 'id' => 1, 'name' => 'User One' }
    @event.assigned_user_ids = [1]
    JsonplaceholderService.expects(:fetch_user).with(1).returns(user)
    assert_equal [user], @event.assigned_users
  end

  def test_returns_users_for_multiple_valid_assigned_user_ids
    users = [
      { 'id' => 1, 'name' => 'User One' },
      { 'id' => 2, 'name' => 'User Two' },
      { 'id' => 3, 'name' => 'User Three' }
    ]
    @event.assigned_user_ids = [1, 2, 3]
    JsonplaceholderService.expects(:fetch_user).with(1).returns(users[0])
    JsonplaceholderService.expects(:fetch_user).with(2).returns(users[1])
    JsonplaceholderService.expects(:fetch_user).with(3).returns(users[2])
    assert_equal users, @event.assigned_users
  end

  def test_returns_non_nil_users_when_some_ids_invalid
    user1 = { 'id' => 1, 'name' => 'User One' }
    user2 = { 'id' => 2, 'name' => 'User Two' }
    @event.assigned_user_ids = [1, 99, 2]
    JsonplaceholderService.expects(:fetch_user).with(1).returns(user1)
    JsonplaceholderService.expects(:fetch_user).with(99).returns(nil)
    JsonplaceholderService.expects(:fetch_user).with(2).returns(user2)
    assert_equal [user1, user2], @event.assigned_users
  end

  def test_returns_empty_array_when_all_ids_invalid
    @event.assigned_user_ids = [999, 1000]
    JsonplaceholderService.expects(:fetch_user).with(999).returns(nil)
    JsonplaceholderService.expects(:fetch_user).with(1000).returns(nil)
    assert_equal [], @event.assigned_users
  end

  def test_returns_users_for_duplicate_assigned_user_ids
    user1 = { 'id' => 1, 'name' => 'User One' }
    user2 = { 'id' => 2, 'name' => 'User Two' }
    @event.assigned_user_ids = [1, 2, 1]
    JsonplaceholderService.expects(:fetch_user).with(1).twice.returns(user1)
    JsonplaceholderService.expects(:fetch_user).with(2).returns(user2)
    assert_equal [user1, user2, user1], @event.assigned_users
  end

  def test_handles_external_service_error_gracefully
    user1 = { 'id' => 1, 'name' => 'User One' }
    @event.assigned_user_ids = [1, 2]
    JsonplaceholderService.expects(:fetch_user).with(1).returns(user1)
    JsonplaceholderService.expects(:fetch_user).with(2).raises(StandardError)
    # The implementation rescues and returns nil for errored IDs
    assert_equal [user1], @event.assigned_users
  end

  def test_returns_users_for_large_list_of_ids
    ids = (1..1000).to_a
    users = ids.map { |i| { 'id' => i, 'name' => "User #{i}" } }
    @event.assigned_user_ids = ids
    ids.each_with_index do |id, idx|
      JsonplaceholderService.expects(:fetch_user).with(id).returns(users[idx])
    end
    assert_equal users, @event.assigned_users
  end

  def test_ignores_non_integer_user_ids
    user1 = { 'id' => 1, 'name' => 'User One' }
    @event.assigned_user_ids = [1, 'abc', nil]
    JsonplaceholderService.expects(:fetch_user).with(1).returns(user1)
    JsonplaceholderService.expects(:fetch_user).with('abc').returns(nil)
    JsonplaceholderService.expects(:fetch_user).with(nil).returns(nil)
    assert_equal [user1], @event.assigned_users
  end
end