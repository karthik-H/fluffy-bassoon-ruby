require 'minitest/autorun'
require_relative '../../../app/models/event'

class EventAssignedUserCountTest < Minitest::Test
  def test_count_returns_number_of_assigned_users
    event = Event.new
    event.assigned_user_ids = [1, 2, 3, 4]
    assert_equal 4, event.assigned_user_count
  end

  def test_count_returns_one_for_single_user
    event = Event.new
    event.assigned_user_ids = [42]
    assert_equal 1, event.assigned_user_count
  end

  def test_count_returns_zero_when_no_users_assigned
    event = Event.new
    event.assigned_user_ids = []
    assert_equal 0, event.assigned_user_count
  end

  def test_count_returns_zero_when_assigned_user_ids_is_nil
    event = Event.new
    event.assigned_user_ids = nil
    assert_equal 0, event.assigned_user_count
  end

  def test_count_handles_non_array_assigned_user_ids
    event = Event.new
    event.assigned_user_ids = 5
    assert_equal 0, event.assigned_user_count
  end

  def test_count_includes_duplicates_in_assigned_user_ids
    event = Event.new
    event.assigned_user_ids = [1, 2, 2, 3]
    assert_equal 4, event.assigned_user_count
  end

  def test_count_handles_string_ids_in_assigned_user_ids
    event = Event.new
    event.assigned_user_ids = ["a", "b", 1]
    assert_equal 3, event.assigned_user_count
  end

  def test_count_handles_large_number_of_assigned_users
    event = Event.new
    event.assigned_user_ids = (1..10000).to_a
    assert_equal 10000, event.assigned_user_count
  end

  def test_count_handles_object_assigned_user_ids
    event = Event.new
    event.assigned_user_ids = { "user" => 1 }
    assert_equal 0, event.assigned_user_count
  end

  def test_count_handles_boolean_assigned_user_ids
    event = Event.new
    event.assigned_user_ids = true
    assert_equal 0, event.assigned_user_count
  end

  def test_count_handles_mixed_nested_arrays
    event = Event.new
    event.assigned_user_ids = [1, [2,3], 4]
    assert_equal 3, event.assigned_user_count
  end

  def test_count_handles_frozen_array
    event = Event.new
    event.assigned_user_ids = [1, 2].freeze
    assert_equal 2, event.assigned_user_count
  end
end
