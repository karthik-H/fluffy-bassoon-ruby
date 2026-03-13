require 'test_helper'

class ComponentEventsBreadcrumbsTest < ActionDispatch::IntegrationTest
  def render_path(path, event: nil)
    get path
    @event = event
    @response.body
  end

  test "Render Breadcrumbs on Root Page" do
    body = render_path("/")
    assert_includes body, "Home"
    refute_includes body, "Events"
  end

  test "Render Breadcrumbs on Events Index" do
    body = render_path("/events")
    assert_includes body, "Home"
    refute_includes body, "Events</a>"
  end

  test "Render Breadcrumbs on Event Detail Page" do
    event = Event.create!(title: "Event 42")
    body = render_path("/events/#{event.id}", event: event)
    assert_includes body, "Home"
    assert_includes body, "Events"
    assert_includes body, event.title
  end

  test "Render Breadcrumbs on Event Subpage" do
    event = Event.create!(title: "Event 42")
    body = render_path("/events/#{event.id}/edit", event: event)
    assert_includes body, "Edit"
    assert_includes body, event.title
  end

  test "Navigate via Home Breadcrumb" do
    get "/events/1"
    follow_redirect! while redirect?
    assert_response :success
  end

  test "Navigate via Events Breadcrumb" do
    event = Event.create!(title: "Event 42")
    get "/events/#{event.id}"
    follow_redirect! while redirect?
    assert_response :success
  end

  test "Edge Case: Missing Current Page" do
    body = render_path("/events/999")
    assert_includes body, "Home"
  end

  test "Negative: Invalid Path" do
    get "/foo/bar"
    assert_response :not_found
  end

  test "Edge Case: Empty Props" do
    body = render_path("/")
    assert_includes body, "Home"
  end

  test "Edge Case: Current Page with Special Characters" do
    event = Event.create!(title: "Event & Co.")
    body = render_path("/events/#{event.id}", event: event)
    assert_includes body, "Event &amp; Co."
  end

  test "Edge Case: Breadcrumbs Loading State" do
    body = render_path("/events/1")
    assert_includes body, "Home"
  end

  test "Accessibility: Breadcrumbs Structure" do
    body = render_path("/")
    assert_includes body, "breadcrumb"
  end

  test "Edge Case: Long Event Name" do
    title = "E" * 255
    event = Event.create!(title: title)
    body = render_path("/events/#{event.id}", event: event)
    assert_includes body, title
  end

  test "Render Breadcrumbs on New Event Page" do
    body = render_path("/events/new")
    assert_includes body, "New Event"
  end

  test "Negative: Event Not Found When Rendering Breadcrumbs" do
    body = render_path("/events/999/edit")
    assert_includes body, "Event"
  end
end
