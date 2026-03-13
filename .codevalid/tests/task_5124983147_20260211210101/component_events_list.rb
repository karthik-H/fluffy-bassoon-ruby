require 'minitest/autorun'
require 'action_view'
require 'action_view/template'
require 'rails'
require_relative '../../../app/views/events/index.html.erb'

class ComponentEventsListTest < ActionView::TestCase
  tests EventsHelper if defined?(EventsHelper)

  def render_view(events: [], error: nil)
    @events = events
    @error = error
    render template: 'events/index'
  end

  def build_event(attrs)
    OpenStruct.new({ id: 1, title: 'Test', description: 'Desc', assigned_user_count: 1, created_at: Time.now }.merge(attrs))
  end

  def test_render_add_new_event_button
    events = [build_event({})]
    render_view(events: events)
    assert_select "a[href='#{Rails.application.routes.url_helpers.new_event_path}']", text: 'Add New Event'
  end

  def test_render_event_list_when_events_exist
    events = [build_event({ title: 'A', description: 'D', assigned_user_count: 3 }), build_event({ id: 2, title: 'B', description: 'E', assigned_user_count: 2 })]
    render_view(events: events)
    events.each do |e|
      assert_select 'div.event', text: /#{e.title}/
      assert_select 'div.event', text: /#{e.description}/
      assert_select 'div.event', text: /#{e.assigned_user_count}/
    end
  end

  def test_render_actions_for_each_event
    events = [build_event({ id: 1 }), build_event({ id: 2 })]
    render_view(events: events)
    events.each do |e|
      assert_select "a[href='#{Rails.application.routes.url_helpers.event_path(e.id)}']", text: 'View'
      assert_select "a[href='#{Rails.application.routes.url_helpers.edit_event_path(e.id)}']", text: 'Edit'
      assert_select "form[action='#{Rails.application.routes.url_helpers.event_path(e.id)}'][method='post']"
    end
  end

  def test_render_empty_state_when_no_events_exist
    render_view(events: [])
    assert_select 'p', text: 'No events yet'
    assert_select "a[href='#{Rails.application.routes.url_helpers.new_event_path}']"
  end

  def test_add_new_event_button_navigation
    render_view(events: [])
    assert_select "a[href='#{Rails.application.routes.url_helpers.new_event_path}']", text: 'Add New Event'
  end

  def test_view_event_action_navigation
    e = build_event({ id: 5 })
    render_view(events: [e])
    assert_select "a[href='#{Rails.application.routes.url_helpers.event_path(e.id)}']", text: 'View'
  end

  def test_edit_event_action_navigation
    e = build_event({ id: 6 })
    render_view(events: [e])
    assert_select "a[href='#{Rails.application.routes.url_helpers.edit_event_path(e.id)}']", text: 'Edit'
  end

  def test_remove_event_action_functionality
    events = [build_event({ id: 1 }), build_event({ id: 2 })]
    render_view(events: events)
    events.each do |e|
      assert_select "form[action='#{Rails.application.routes.url_helpers.event_path(e.id)}']"
    end
  end

  def test_remove_event_action_cancel_deletion
    e = build_event({ id: 3 })
    render_view(events: [e])
    assert_select "form[action='#{Rails.application.routes.url_helpers.event_path(e.id)}']"
  end

  def test_render_event_with_long_title
    long_title = 'x' * 260
    e = build_event({ title: long_title })
    render_view(events: [e])
    assert_select 'div.event', text: /#{long_title}/
  end

  def test_event_with_zero_assigned_users
    e = build_event({ assigned_user_count: 0 })
    render_view(events: [e])
    assert_select 'div.event', text: /0/
  end

  def test_event_with_missing_description
    e = build_event({ description: nil })
    render_view(events: [e])
    assert_select 'div.event', text: /No description/
  end

  def test_error_state_on_event_fetch_failure
    render_view(events: nil, error: 'Fetch failed')
    assert_select 'p.error', text: /Fetch failed/
  end

  def test_remove_event_api_failure_handling
    e = build_event({ id: 4 })
    render_view(events: [e], error: 'Deletion failed')
    assert_select 'p.error', text: /Deletion failed/
    assert_select 'div.event', text: /#{e.title}/
  end

  def test_event_list_with_incomplete_data
    e = build_event({ title: nil, description: nil, assigned_user_count: nil })
    render_view(events: [e])
    assert_select 'div.event'
  end

  def test_accessibility_of_event_actions
    e = build_event({})
    render_view(events: [e])
    assert_select "a[aria-label='Add New Event']"
    assert_select "a[aria-label='View Event']"
    assert_select "a[aria-label='Edit Event']"
    assert_select "button[aria-label='Remove Event']"
  end

  def test_sort_events_newest_first
    old = build_event({ id: 1, created_at: Time.now - 3600 })
    newe = build_event({ id: 2, created_at: Time.now })
    render_view(events: [old, newe])
    assert_select 'div.event:first-child', text: /#{newe.title}/
  end

  def test_conditional_user_count_badge
    e1 = build_event({ assigned_user_count: 0 })
    e2 = build_event({ assigned_user_count: 5, id: 77 })
    render_view(events: [e1, e2])
    assert_select 'div.event', text: /5 users/
    assert_no_match /0 users/, @rendered
  end

  def test_remove_event_confirmation_dialog
    e = build_event({ id: 9 })
    render_view(events: [e])
    assert_select "form[action='#{Rails.application.routes.url_helpers.event_path(e.id)}'][onsubmit]"
  end

  def test_missing_title_fallback
    e = build_event({ title: nil })
    render_view(events: [e])
    assert_select 'div.event', text: /Untitled Event/
  end

  def test_empty_state_correctness
    render_view(events: [])
    assert_select 'p', text: 'No events yet'
  end
end
