require 'minitest/autorun'
require_relative '../../../app/models/event'
require 'set'

class EventAssignedUserIdsSetterTest < Minitest::Test
  def setup
    @event = Event.new
  end

  def test_assign_array_of_integers
    @event.assigned_user_ids = [1,2,3]
    assert_equal '[1,2,3]', @event.read_attribute(:assigned_user_ids)
  end

  def test_assign_array_of_strings
    @event.assigned_user_ids = ['u1','u2']
    assert_equal '["u1","u2"]', @event.read_attribute(:assigned_user_ids)
  end

  def test_assign_empty_array
    @event.assigned_user_ids = []
    assert_equal '[]', @event.read_attribute(:assigned_user_ids)
  end

  def test_assign_array_with_nil
    @event.assigned_user_ids = [1,nil,3]
    assert_equal '[1,null,3]', @event.read_attribute(:assigned_user_ids)
  end

  def test_assign_array_with_mixed_types
    @event.assigned_user_ids = [1,'2',3.0,nil]
    assert_equal '[1,"2",3.0,null]', @event.read_attribute(:assigned_user_ids)
  end

  def test_assign_string_input
    @event.assigned_user_ids = 'string_user_id'
    assert_equal 'string_user_id', @event.read_attribute(:assigned_user_ids)
  end

  def test_assign_integer_input
    @event.assigned_user_ids = 42
    assert_equal 42, @event.read_attribute(:assigned_user_ids)
  end

  def test_assign_nil_input
    @event.assigned_user_ids = nil
    assert_nil @event.read_attribute(:assigned_user_ids)
  end

  def test_assign_array_with_duplicate_ids
    @event.assigned_user_ids = [1,2,2,3]
    assert_equal '[1,2,2,3]', @event.read_attribute(:assigned_user_ids)
  end

  def test_assign_large_array
    arr = (1..1000).to_a
    @event.assigned_user_ids = arr
    assert_equal arr.to_json, @event.read_attribute(:assigned_user_ids)
  end

  def test_assign_non_array_iterable
    val = Set.new([1,2])
    @event.assigned_user_ids = val
    assert_equal val, @event.read_attribute(:assigned_user_ids)
  end

  def test_assign_hash_value
    val = { id: 1 }
    @event.assigned_user_ids = val
    assert_equal val, @event.read_attribute(:assigned_user_ids)
  end

  def test_assign_boolean_true
    @event.assigned_user_ids = true
    assert_equal true, @event.read_attribute(:assigned_user_ids)
  end

  def test_assign_boolean_false
    @event.assigned_user_ids = false
    assert_equal false, @event.read_attribute(:assigned_user_ids)
  end

  def test_assign_array_with_nested_array
    @event.assigned_user_ids = [1,[2,3]]
    assert_equal '[1,[2,3]]', @event.read_attribute(:assigned_user_ids)
  end

  def test_assign_array_with_hash
    val = [{id:1},{id:2}]
    @event.assigned_user_ids = val
    assert_equal val.to_json, @event.read_attribute(:assigned_user_ids)
  end

  def test_assign_array_with_symbols
    @event.assigned_user_ids = [:a,:b]
    assert_equal '["a","b"]', @event.read_attribute(:assigned_user_ids)
  end

  def test_assign_array_with_boolean_values
    @event.assigned_user_ids = [true,false]
    assert_equal '[true,false]', @event.read_attribute(:assigned_user_ids)
  end

  def test_assign_array_with_empty_strings
    @event.assigned_user_ids = ['']
    assert_equal '[""]', @event.read_attribute(:assigned_user_ids)
  end

  def test_assign_array_with_large_nested_structure
    @event.assigned_user_ids = [1,[2,[3,[4]]]]
    assert_equal '[1,[2,[3,[4]]]]', @event.read_attribute(:assigned_user_ids)
  end

  def test_assign_float_value
    @event.assigned_user_ids = 3.14
    assert_equal 3.14, @event.read_attribute(:assigned_user_ids)
  end

  def test_assign_object_value
    obj = Object.new
    @event.assigned_user_ids = obj
    assert_equal obj, @event.read_attribute(:assigned_user_ids)
  end

  def test_assign_array_with_unsupported_types
    proc_val = ->{}
    assert_raises(JSON::GeneratorError) do
      @event.assigned_user_ids = [proc_val]
    end
  end
end
