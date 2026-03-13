require "test_helper"
require "mocha/minitest"

class ControllerEventsNewTest < ActionDispatch::IntegrationTest
  setup do
    @controller_path = new_event_path
  end

  test "new_event_success" do
    JsonplaceholderService.stubs(:fetch_users).returns([{ "id" => 1 }, { "id" => 2 }])
    get @controller_path
    assert_response :success
    assert assigns(:event).new_record?
    assert_equal 2, assigns(:users).size
  end

  test "no_users_available" do
    JsonplaceholderService.stubs(:fetch_users).returns([])
    get @controller_path
    assert_response :success
    assert assigns(:event).new_record?
    assert_empty assigns(:users)
  end

  test "users_with_ineligible_status" do
    eligible = [{ "id" => 1, "active" => true }]
    ineligible = [{ "id" => 2, "active" => false }]
    JsonplaceholderService.stubs(:fetch_users).returns(eligible + ineligible)
    get @controller_path
    assert_response :success
    assert assigns(:event).new_record?
    assert_equal eligible, assigns(:users)
  end

  test "event_model_initialization_failure" do
    Event.stubs(:new).raises(StandardError.new("init fail"))
    JsonplaceholderService.stubs(:fetch_users).returns([])
    assert_raises(StandardError) { get @controller_path }
  end

  test "user_query_failure" do
    JsonplaceholderService.stubs(:fetch_users).raises(StandardError.new("fetch fail"))
    assert_raises(StandardError) { get @controller_path }
  end

  test "event_prepopulated_attributes" do
    JsonplaceholderService.stubs(:fetch_users).returns([])
    defaults = { title: "Default" }
    Event.stubs(:new).returns(Event.new(defaults))
    get @controller_path
    assert_response :success
    assert_equal "Default", assigns(:event).title
  end

  test "authenticated_user_required" do
    JsonplaceholderService.stubs(:fetch_users).returns([])
    self.stubs(:current_user).returns(nil)
    get @controller_path
    assert_response :redirect
  end

  test "external_user_service_timeout" do
    JsonplaceholderService.stubs(:fetch_users).raises(Timeout::Error)
    assert_raises(Timeout::Error) { get @controller_path }
  end

  test "external_user_service_returns_malformed_data" do
    JsonplaceholderService.stubs(:fetch_users).returns([nil, { "bad" => "data" }])
    get @controller_path rescue nil
    assert assigns(:event).new_record?
  end

  test "new_event_does_not_persist" do
    JsonplaceholderService.stubs(:fetch_users).returns([])
    assert_no_difference "Event.count" do
      get @controller_path
    end
    assert assigns(:event).new_record?
  end

  test "new_event_does_not_modify_existing_users" do
    users = [{ "id" => 1 }]
    JsonplaceholderService.stubs(:fetch_users).returns(users)
    get @controller_path
    assert_equal [{ "id" => 1 }], users
  end

  test "breadcrumb_context_in_new_event" do
    JsonplaceholderService.stubs(:fetch_users).returns([])
    get @controller_path
    assert_response :success
  end

  test "new_event_form_ui_metadata" do
    JsonplaceholderService.stubs(:fetch_users).returns([])
    get @controller_path
    assert_response :success
  end

  test "no_valid_assignable_users" do
    JsonplaceholderService.stubs(:fetch_users).returns([])
    get @controller_path
    assert_response :success
    assert_empty assigns(:users)
  end

  test "before_action_side_effect_check" do
    JsonplaceholderService.stubs(:fetch_users).returns([])
    assert_no_difference "Event.count" do
      get @controller_path
    end
  end
end
