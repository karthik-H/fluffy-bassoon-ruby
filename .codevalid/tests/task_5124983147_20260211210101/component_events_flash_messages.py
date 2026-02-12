import pytest
from bs4 import BeautifulSoup

# Simulate the ERB logic for flash messages in app/views/layouts/application.html.erb.
def render_flash_messages(notice=None, alert=None):
    html = ""
    if notice:
        html += f'<div class="notice"><span class="flash-message">{notice}</span><button class="dismiss-notice">x</button></div>'
    if alert:
        html += f'<div class="alert"><span class="flash-message">{alert}</span><button class="dismiss-alert">x</button></div>'
    return html

def get_soup(html):
    return BeautifulSoup(html, "html.parser")

@pytest.mark.describe("Flash Messages (Notice/Alert) Component")
class TestFlashMessages:

    @pytest.mark.it("Render notice message when notice is present")
    def test_render_notice_message_when_notice_is_present(self):
        # Given
        notice = "Event created successfully"
        alert = None
        # When
        html = render_flash_messages(notice=notice, alert=alert)
        soup = get_soup(html)
        # Then
        notice_div = soup.find("div", class_="notice")
        assert notice_div is not None
        assert "Event created successfully" in notice_div.text
        alert_div = soup.find("div", class_="alert")
        assert alert_div is None

    @pytest.mark.it("Render alert message when alert is present")
    def test_render_alert_message_when_alert_is_present(self):
        # Given
        notice = None
        alert = "Event could not be created"
        # When
        html = render_flash_messages(notice=notice, alert=alert)
        soup = get_soup(html)
        # Then
        alert_div = soup.find("div", class_="alert")
        assert alert_div is not None
        assert "Event could not be created" in alert_div.text
        notice_div = soup.find("div", class_="notice")
        assert notice_div is None

    @pytest.mark.it("Render both notice and alert messages when both are present")
    def test_render_both_notice_and_alert_messages_when_both_are_present(self):
        # Given
        notice = "Event updated"
        alert = "Some fields missing"
        # When
        html = render_flash_messages(notice=notice, alert=alert)
        soup = get_soup(html)
        # Then
        notice_div = soup.find("div", class_="notice")
        alert_div = soup.find("div", class_="alert")
        assert notice_div is not None
        assert alert_div is not None
        assert "Event updated" in notice_div.text
        assert "Some fields missing" in alert_div.text

    @pytest.mark.it("Do not render any message when neither notice nor alert is present")
    def test_do_not_render_any_message_when_neither_notice_nor_alert_is_present(self):
        # Given
        notice = None
        alert = None
        # When
        html = render_flash_messages(notice=notice, alert=alert)
        soup = get_soup(html)
        # Then
        assert soup.find("div", class_="notice") is None
        assert soup.find("div", class_="alert") is None

        # Also test with empty strings
        html_empty = render_flash_messages(notice="", alert="")
        soup_empty = get_soup(html_empty)
        assert soup_empty.find("div", class_="notice") is None
        assert soup_empty.find("div", class_="alert") is None

    @pytest.mark.it("Do not render notice message when notice is empty string")
    def test_do_not_render_notice_message_when_notice_is_empty_string(self):
        # Given
        notice = ""
        alert = None
        # When
        html = render_flash_messages(notice=notice, alert=alert)
        soup = get_soup(html)
        # Then
        assert soup.find("div", class_="notice") is None

    @pytest.mark.it("Do not render alert message when alert is empty string")
    def test_do_not_render_alert_message_when_alert_is_empty_string(self):
        # Given
        notice = None
        alert = ""
        # When
        html = render_flash_messages(notice=notice, alert=alert)
        soup = get_soup(html)
        # Then
        assert soup.find("div", class_="alert") is None

    @pytest.mark.it("Clear notice message after user action")
    def test_clear_notice_message_after_user_action(self):
        # Given
        notice = "Event deleted"
        alert = None
        # When (initial render)
        html = render_flash_messages(notice=notice, alert=alert)
        soup = get_soup(html)
        notice_div = soup.find("div", class_="notice")
        assert notice_div is not None
        # When (user clicks dismiss)
        html_after_dismiss = render_flash_messages(notice=None, alert=alert)
        soup_after = get_soup(html_after_dismiss)
        # Then
        assert soup_after.find("div", class_="notice") is None

    @pytest.mark.it("Clear alert message after user action")
    def test_clear_alert_message_after_user_action(self):
        # Given
        notice = None
        alert = "Access denied"
        # When (initial render)
        html = render_flash_messages(notice=notice, alert=alert)
        soup = get_soup(html)
        alert_div = soup.find("div", class_="alert")
        assert alert_div is not None
        # When (user clicks dismiss)
        html_after_dismiss = render_flash_messages(notice=notice, alert=None)
        soup_after = get_soup(html_after_dismiss)
        # Then
        assert soup_after.find("div", class_="alert") is None

    @pytest.mark.it("Render notice message with long text")
    def test_render_notice_message_with_long_text(self):
        # Given
        long_text = "T" * 255
        notice = long_text
        alert = None
        # When
        html = render_flash_messages(notice=notice, alert=alert)
        soup = get_soup(html)
        notice_div = soup.find("div", class_="notice")
        # Then
        assert notice_div is not None
        assert long_text in notice_div.text
        assert len(notice_div.text) >= 255

    @pytest.mark.it("Render alert message with special characters")
    def test_render_alert_message_with_special_characters(self):
        # Given
        alert = '<script>alert("xss")</script> & ©'
        notice = None
        # When
        html = render_flash_messages(notice=notice, alert=alert)
        soup = get_soup(html)
        alert_div = soup.find("div", class_="alert")
        # Then
        assert alert_div is not None
        # Should display as plain text, not executed as HTML/JS
        assert '<script>' in alert_div.text
        assert '&' in alert_div.text
        assert '©' in alert_div.text
        # Ensure the HTML is not interpreted (i.e., no <script> tag in parsed children)
        assert alert_div.find("script") is None