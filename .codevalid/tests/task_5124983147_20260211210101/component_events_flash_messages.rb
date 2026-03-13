require 'test_helper'
require 'action_view/testing/resolvers'

class ComponentEventsFlashMessagesTest < ActionView::TestCase
  tests ActionView::Base

  def setup
    @view = ActionView::Base.new(ActionView::LookupContext.new([]), {}, nil)
    @template = File.read('app/views/layouts/application.html.erb')
  end

  def render_with_flash(notice: nil, alert: nil)
    @view.assign(flash: { notice: notice, alert: alert })
    @view.render(inline: @template)
  end

  def test_render_notice_message_when_notice_is_present
    html = render_with_flash(notice: 'Event created successfully')
    assert_includes html, 'Event created successfully'
    assert_includes html, 'class="notice"'
  end

  def test_render_alert_message_when_alert_is_present
    html = render_with_flash(alert: 'Event could not be created')
    assert_includes html, 'Event could not be created'
    assert_includes html, 'class="alert"'
  end

  def test_render_both_notice_and_alert_messages_when_both_are_present
    html = render_with_flash(notice: 'Event updated', alert: 'Some fields missing')
    assert_includes html, 'Event updated'
    assert_includes html, 'Some fields missing'
  end

  def test_do_not_render_any_message_when_neither_notice_nor_alert_is_present
    html = render_with_flash
    refute_includes html, 'notice'
    refute_includes html, 'alert'
  end

  def test_do_not_render_notice_message_when_notice_is_empty_string
    html = render_with_flash(notice: '')
    refute_includes html, 'class="notice"'
  end

  def test_do_not_render_alert_message_when_alert_is_empty_string
    html = render_with_flash(alert: '')
    refute_includes html, 'class="alert"'
  end

  def test_render_notice_message_with_long_text
    long_text = 'T' * 255
    html = render_with_flash(notice: long_text)
    assert_includes html, long_text
  end

  def test_render_alert_message_with_special_characters
    msg = '<script>alert("xss")</script> & ©'
    html = render_with_flash(alert: msg)
    assert_includes html, CGI.escapeHTML(msg)
  end

  def test_render_nothing_when_notice_and_alert_are_whitespace_only
    html = render_with_flash(notice: '   ', alert: '   ')
    refute_includes html, 'class="notice"'
    refute_includes html, 'class="alert"'
  end

  def test_notice_styling_uses_correct_css_class
    html = render_with_flash(notice: 'Event saved')
    assert_includes html, 'class="notice"'
  end

  def test_alert_styling_uses_correct_css_class
    html = render_with_flash(alert: 'Failed to save')
    assert_includes html, 'class="alert"'
  end

  def test_order_of_messages_when_both_notice_and_alert_displayed
    html = render_with_flash(notice: 'A', alert: 'B')
    assert html.index('A') < html.index('B')
  end

  def test_notice_message_persists_across_redirect
    get root_path, params: {}, flash: { notice: 'Persisted' }
    follow_redirect! if response.redirect?
    assert_includes response.body, 'Persisted'
  end

  def test_alert_message_persists_across_redirect
    get root_path, params: {}, flash: { alert: 'Persisted alert' }
    follow_redirect! if response.redirect?
    assert_includes response.body, 'Persisted alert'
  end

  def test_flash_messages_do_not_expose_html_injection_via_interpolation
    html = render_with_flash(notice: 'Error <b>bold</b>')
    assert_includes html, 'Error &lt;b&gt;bold&lt;/b&gt;'
  end

  def test_render_flash_messages_at_top_of_main_content_area
    html = render_with_flash(notice: 'Saved')
    first_occurrence = html.index('Saved')
    assert first_occurrence < 200
  end

  def test_render_only_latest_flash_messages_on_redirect
    get root_path, params: {}, flash: { notice: 'Old message' }
    follow_redirect! if response.redirect?
    get root_path, params: {}, flash: { notice: 'New message' }
    follow_redirect! if response.redirect?
    assert_includes response.body, 'New message'
    refute_includes response.body, 'Old message'
  end

  def test_do_not_render_non_string_flash_values
    html = render_with_flash(notice: { a: 1 })
    refute_includes html, 'class="notice"'
  end
end
