require 'test_helper'

class EventsControllerDestroyTest < ActionDispatch::IntegrationTest
  def setup
    @event = Event.create!(id: 1, title: 'Test', description: 'Desc')
    @event2 = Event.create!(id: 2, title: 'Test2', description: 'Desc2')
    @event3 = Event.create!(id: 3, title: 'Test3', description: 'Desc3')
    @event4 = Event.create!(id: 4, title: 'Test4', description: 'Desc4')
    @event5 = Event.create!(id: 5, title: 'Test5', description: 'Desc5')
    @event6 = Event.create!(id: 6, title: 'Test6', description: 'Desc6')
  end

  test 'Destroy Event Successfully' do
    sign_in users(:authorized)
    assert_difference('Event.count', -1) do
      delete event_url(@event)
    end
    assert_redirected_to events_url
    assert_equal 'Event was successfully removed.', flash[:notice]
  end

  test 'Destroy Non-existent Event' do
    assert_raises(ActiveRecord::RecordNotFound) do
      delete event_url(9999)
    end
  end

  test 'Destroy Event Without Authorization' do
    sign_in users(:unauthorized)
    assert_no_difference('Event.count') do
      delete event_url(@event2)
    end
    assert_response :forbidden
  end

  test 'Destroy Event Without Authentication' do
    assert_no_difference('Event.count') do
      delete event_url(@event3)
    end
    assert_redirected_to new_user_session_url
  end

  test 'Destroy Event With Invalid ID Format' do
    assert_raises(ActionController::BadRequest, ActiveRecord::RecordNotFound) do
      delete event_url('abc')
    end
  end

  test 'Destroy Event That Was Already Deleted' do
    @event4.destroy
    assert_raises(ActiveRecord::RecordNotFound) do
      delete event_url(4)
    end
  end

  test 'Destroy Event Redirects to Events List' do
    sign_in users(:authorized)
    assert_difference('Event.count', -1) do
      delete event_url(@event5)
    end
    assert_redirected_to events_url
  end

  test 'Destroy Event Shows Notice Message' do
    sign_in users(:authorized)
    delete event_url(@event6)
    assert_equal 'Event was successfully removed.', flash[:notice]
  end

  test 'Destroy Event Failure Due to Database Error' do
    sign_in users(:authorized)
    Event.any_instance.stubs(:destroy).raises(StandardError.new('DB fail'))
    assert_no_difference('Event.count') do
      assert_raises(StandardError) do
        delete event_url(@event)
      end
    end
  end

  test 'Destroy Event With Dependent Records' do
    sign_in users(:authorized)
    Event.any_instance.stubs(:destroy).returns(false)
    assert_no_difference('Event.count') do
      delete event_url(@event2)
    end
    assert_response :unprocessable_entity
  end

  test 'Destroy Event Confirmation Required' do
    sign_in users(:authorized)
    assert_no_difference('Event.count') do
      delete event_url(@event3), params: { confirm: 'no' }
    end
    assert_response :ok
  end

  test 'Destroy Event While Logged In But Session Expired Mid-Request' do
    sign_in users(:authorized)
    expire_session!
    assert_no_difference('Event.count') do
      delete event_url(@event4)
    end
    assert_redirected_to new_user_session_url
  end

  test 'Destroy Event With Very Large ID' do
    assert_raises(ActiveRecord::RecordNotFound) do
      delete event_url(999999999999)
    end
  end

  test 'Destroy Event When Flash Already Contains Messages' do
    sign_in users(:authorized)
    flash[:notice] = 'Old message'
    delete event_url(@event5)
    assert_equal 'Event was successfully removed.', flash[:notice]
  end
end
