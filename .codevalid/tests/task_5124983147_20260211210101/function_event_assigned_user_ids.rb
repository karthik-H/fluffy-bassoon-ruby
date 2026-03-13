require 'minitest/autorun'
require_relative '../../../../app/models/event'
require 'json'

class FunctionEventAssignedUserIdsTest < Minitest::Test
  def setup
    @event = Event.new
  end

  def test_returns_empty_array_when_assigned_user_ids_is_nil
    # Given
    @event.assigned_user_ids = nil
    # When
    result = @event.assigned_user_ids
    # Then
    assert_equal [], result
  end

  def test_returns_empty_array_when_assigned_user_ids_is_empty_string
    @event.assigned_user_ids = ""
    result = @event.assigned_user_ids
    assert_equal [], result
  end

  def test_returns_array_when_assigned_user_ids_is_valid_json_array
    @event.assigned_user_ids = "[1,2,3]"
    result = @event.assigned_user_ids
    assert_equal [1,2,3], result
  end

  def test_returns_empty_array_when_assigned_user_ids_is_valid_json_empty_array
    @event.assigned_user_ids = "[]"
    result = @event.assigned_user_ids
    assert_equal [], result
  end

  def test_returns_empty_array_on_malformed_json_in_assigned_user_ids
    @event.assigned_user_ids = "[1, 2, 3"
    result = @event.assigned_user_ids
    assert_equal [], result
  end

  def test_returns_non_array_when_assigned_user_ids_is_valid_json_not_array
    @event.assigned_user_ids = '{"user":1}'
    result = @event.assigned_user_ids
    assert_equal({"user" => 1}, result)
  end

  def test_returns_nil_when_assigned_user_ids_is_json_null
    @event.assigned_user_ids = 'null'
    result = @event.assigned_user_ids
    assert_nil result
  end

  def test_returns_string_when_assigned_user_ids_is_json_string
    @event.assigned_user_ids = '"123"'
    result = @event.assigned_user_ids
    assert_equal "123", result
  end

  def test_returns_number_when_assigned_user_ids_is_json_number
    @event.assigned_user_ids = '42'
    result = @event.assigned_user_ids
    assert_equal 42, result
  end

  def test_returns_empty_array_when_assigned_user_ids_is_whitespace_string
    @event.assigned_user_ids = '   '
    result = @event.assigned_user_ids
    assert_equal [], result
  end

  def test_returns_empty_array_when_assigned_user_ids_is_non_json_text
    @event.assigned_user_ids = 'not json'
    result = @event.assigned_user_ids
    assert_equal [], result
  end

  def test_handles_large_json_array_for_assigned_user_ids
    large = (0...1000).to_a
    @event.assigned_user_ids = large.to_json
    result = @event.assigned_user_ids
    assert_equal large, result
  end

  def test_handles_whitespace_wrapped_json
    @event.assigned_user_ids = "   [1,2]   "
    result = @event.assigned_user_ids
    assert_equal [1,2], result
  end

  def test_handles_non_string_preparsed_array
    @event.write_attribute(:assigned_user_ids, [5,6])
    result = @event.assigned_user_ids
    assert_equal [5,6], result
  end
end
