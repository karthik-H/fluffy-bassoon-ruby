require "test_helper"
require "minitest/autorun"
require_relative "../../../app/controllers/events_controller"

class ControllerEventsFetchUsersTest < ActionDispatch::IntegrationTest
  tests EventsController

  def setup
    @routes = Rails.application.routes
  end

  test "Test Case 1: Fetch users successfully" do
    returned = [{"id"=>1, "name"=>"Alice"}, {"id"=>2, "name"=>"Bob"}]
    JsonplaceholderService.stub :fetch_users, returned do
      get new_event_path
      assert_equal returned, assigns(:users)
    end
  end

  test "Test Case 2: Fetch users returns empty list" do
    JsonplaceholderService.stub :fetch_users, [] do
      get new_event_path
      assert_equal [], assigns(:users)
    end
  end

  test "Test Case 3: Fetch users returns nil" do
    JsonplaceholderService.stub :fetch_users, nil do
      get new_event_path
      assert_nil assigns(:users)
    end
  end

  test "Test Case 4: Fetch users raises exception" do
    JsonplaceholderService.stub :fetch_users, proc { raise RuntimeError } do
      assert_raises(RuntimeError) { get new_event_path }
    end
  end

  test "Test Case 5: Fetch users returns invalid user format" do
    invalid = "invalid"
    JsonplaceholderService.stub :fetch_users, invalid do
      get new_event_path
      assert_equal invalid, assigns(:users)
    end
    invalid2 = {"foo"=>"bar"}
    JsonplaceholderService.stub :fetch_users, invalid2 do
      get new_event_path
      assert_equal invalid2, assigns(:users)
    end
  end

  test "Test Case 6: Fetch users returns large user list" do
    large = Array.new(10000) { |i| {"id"=>i} }
    JsonplaceholderService.stub :fetch_users, large do
      get new_event_path
      assert_equal large, assigns(:users)
    end
  end

  test "Test Case 7: Fetch users returns users with partial data" do
    list = [{"id"=>1}, {"name"=>"Bob"}, {}]
    JsonplaceholderService.stub :fetch_users, list do
      get new_event_path
      assert_equal list, assigns(:users)
    end
  end

  test "Test Case 8: Fetch users is only triggered on new, edit, and show" do
    JsonplaceholderService.stub :fetch_users, [{"id"=>1}] do
      get new_event_path
      assert assigns(:users)
      event = Event.create!(title:"T", description:"D")
      get edit_event_path(event)
      assert assigns(:users)
      get event_path(event)
      assert assigns(:users)
      get events_path
      assert_nil assigns(:users)
      delete event_path(event)
      assert_nil assigns(:users)
    end
  end

  test "Test Case 9: Fetch users does not modify external data" do
    source = [{"id"=>1, "name"=>"Z"}]
    JsonplaceholderService.stub :fetch_users, source do
      get new_event_path
      assert_equal source, assigns(:users)
      assert_equal [{"id"=>1, "name"=>"Z"}], source
    end
  end

  test "Test Case 10: Fetch users preserved state for event form rendering" do
    list = [{"id"=>1}]
    JsonplaceholderService.stub :fetch_users, list do
      get new_event_path
      assert_equal list, assigns(:users)
    end
  end

  test "Test Case 11: Fetch users does not run on create or update" do
    called = false
    JsonplaceholderService.stub :fetch_users, proc { called = true; [] } do
      post events_path, params:{event:{title:"A", description:"B"}}
      assert_equal false, called
      event = Event.create!(title:"X", description:"Y")
      patch event_path(event), params:{event:{title:"New"}}
      assert_equal false, called
    end
  end

  test "Test Case 12: Fetch users populates list for show view" do
    list = [{"id"=>5}]
    JsonplaceholderService.stub :fetch_users, list do
      event = Event.create!(title:"A", description:"B")
      get event_path(event)
      assert_equal list, assigns(:users)
    end
  end
end
