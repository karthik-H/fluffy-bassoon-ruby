require 'minitest/autorun'
require 'rails-controller-testing'
require 'mocha/minitest'
Rails::Controller::Testing.install

require_relative '../../../app/controllers/events_controller'
require_relative '../../../app/models/event'
require_relative '../../../app/models/user'

class ControllerEventsUpdateTest < ActionController::TestCase
  tests EventsController

  def setup
    @event = Event.new(id: 1, title: 'Original', user_id: 1)
    Event.stubs(:find).with('1').returns(@event)
  end

  def test_update_event_successfully_with_valid_parameters
    @event.expects(:update).returns(true)
    put :update, params: { id: 1, event: { title: 'Updated' } }
    assert_redirected_to @event
    assert_equal 'Event was successfully updated.', flash[:notice]
  end

  def test_fail_to_update_event_with_invalid_parameters
    @event.expects(:update).returns(false)
    controller.expects(:fetch_users)
    put :update, params: { id: 1, event: { title: '' } }
    assert_response :unprocessable_entity
    assert_template :edit
  end

  def test_fail_to_update_event_with_empty_parameters
    @event.expects(:update).returns(false)
    controller.expects(:fetch_users)
    put :update, params: { id: 1, event: {} }
    assert_response :unprocessable_entity
    assert_template :edit
  end

  def test_update_event_with_valid_user_assignment
    @event.expects(:update).with({ 'user_id' => '2' }).returns(true)
    put :update, params: { id: 1, event: { user_id: 2 } }
    assert_redirected_to @event
    assert_equal 'Event was successfully updated.', flash[:notice]
  end

  def test_fail_to_update_event_with_invalid_user_assignment
    @event.expects(:update).returns(false)
    controller.expects(:fetch_users)
    put :update, params: { id: 1, event: { user_id: 9999 } }
    assert_response :unprocessable_entity
    assert_template :edit
  end

  def test_fail_to_update_event_with_excessively_long_title
    @event.expects(:update).returns(false)
    controller.expects(:fetch_users)
    long_title = 'a' * 5000
    put :update, params: { id: 1, event: { title: long_title } }
    assert_response :unprocessable_entity
    assert_template :edit
  end

  def test_attempt_to_update_a_non_existent_event
    Event.stubs(:find).with('999').raises(ActiveRecord::RecordNotFound)
    assert_raises ActiveRecord::RecordNotFound do
      put :update, params: { id: 999, event: { title: 'X' } }
    end
  end

  def test_fail_to_update_event_due_to_permission_denied
    controller.stubs(:authorize!).raises(StandardError.new('denied'))
    assert_raises StandardError do
      put :update, params: { id: 1, event: { title: 'Valid' } }
    end
  end

  def test_update_event_successfully_with_minimal_valid_parameters
    @event.expects(:update).returns(true)
    put :update, params: { id: 1, event: { title: 'Minimal' } }
    assert_redirected_to @event
    assert_equal 'Event was successfully updated.', flash[:notice]
  end

  def test_fail_to_update_event_due_to_duplicate_title
    @event.expects(:update).returns(false)
    controller.expects(:fetch_users)
    put :update, params: { id: 1, event: { title: 'Duplicate' } }
    assert_response :unprocessable_entity
    assert_template :edit
  end

  def test_update_event_with_no_changes_submitted
    @event.expects(:update).returns(true)
    put :update, params: { id: 1, event: { title: 'Original' } }
    assert_redirected_to @event
    assert_equal 'Event was successfully updated.', flash[:notice]
  end

  def test_fail_update_when_user_assignment_list_is_missing
    @event.expects(:update).returns(false)
    controller.expects(:fetch_users)
    put :update, params: { id: 1, event: { title: '' } }
    assert_response :unprocessable_entity
    assert_template :edit
  end

  def test_update_event_removing_all_assigned_users
    @event.expects(:update).with({ 'user_id' => [] }).returns(true)
    put :update, params: { id: 1, event: { user_id: [] } }
    assert_redirected_to @event
    assert_equal 'Event was successfully updated.', flash[:notice]
  end

  def test_fail_update_when_external_user_list_load_fails
    @event.expects(:update).returns(false)
    controller.expects(:fetch_users).raises(StandardError.new('fetch failed'))
    assert_raises StandardError do
      put :update, params: { id: 1, event: { title: '' } }
    end
  end

  def test_fail_update_due_to_invalid_data_type_in_parameters
    @event.expects(:update).returns(false)
    controller.expects(:fetch_users)
    put :update, params: { id: 1, event: { title: [1,2,3] } }
    assert_response :unprocessable_entity
    assert_template :edit
  end

  def test_update_fails_when_no_parameters_are_provided_at_all
    @event.expects(:update).returns(false)
    controller.expects(:fetch_users)
    put :update, params: { id: 1 }
    assert_response :unprocessable_entity
    assert_template :edit
  end

  def test_update_fails_when_external_user_list_service_times_out
    @event.expects(:update).returns(false)
    controller.expects(:fetch_users).raises(Timeout::Error)
    assert_raises Timeout::Error do
      put :update, params: { id: 1, event: { title: '' } }
    end
  end
end
