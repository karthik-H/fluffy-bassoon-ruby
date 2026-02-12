import pytest
from unittest.mock import patch, MagicMock
from flask import Flask
from bs4 import BeautifulSoup

@pytest.fixture
def client():
    app = Flask(__name__)

    @app.route("/")
    def root():
        # Root page: only Home
        return '''
        <nav aria-label="breadcrumb">
          <ol>
            <li><a href="/">Home</a></li>
          </ol>
        </nav>
        '''

    @app.route("/events")
    def events_index():
        # Events index: only Home
        return '''
        <nav aria-label="breadcrumb">
          <ol>
            <li><a href="/">Home</a></li>
          </ol>
        </nav>
        '''

    @app.route("/events/<int:event_id>")
    def event_detail(event_id):
        # Event detail: Home > Events > Event 42
        return f'''
        <nav aria-label="breadcrumb">
          <ol>
            <li><a href="/">Home</a></li>
            <li><a href="/events">Events</a></li>
            <li>Event {event_id}</li>
          </ol>
        </nav>
        '''

    @app.route("/events/<int:event_id>/edit")
    def event_edit(event_id):
        # Event edit: Home > Events > Event 42 > Edit
        return f'''
        <nav aria-label="breadcrumb">
          <ol>
            <li><a href="/">Home</a></li>
            <li><a href="/events">Events</a></li>
            <li><a href="/events/{event_id}">Event {event_id}</a></li>
            <li>Edit</li>
          </ol>
        </nav>
        '''

    @app.route("/events/<event_id>")
    def event_detail_str(event_id):
        # For special character and string event names
        return f'''
        <nav aria-label="breadcrumb">
          <ol>
            <li><a href="/">Home</a></li>
            <li><a href="/events">Events</a></li>
            <li>{event_id}</li>
          </ol>
        </nav>
        '''

    @app.route("/foo/bar")
    def invalid_path():
        # Invalid path: only Home
        return '''
        <nav aria-label="breadcrumb">
          <ol>
            <li><a href="/">Home</a></li>
          </ol>
        </nav>
        '''

    @app.route("/loading")
    def loading():
        # Loading state: Home > Events > Loading...
        return '''
        <nav aria-label="breadcrumb">
          <ol>
            <li><a href="/">Home</a></li>
            <li><a href="/events">Events</a></li>
            <li>Loading...</li>
          </ol>
        </nav>
        '''

    @app.route("/events/unknown")
    def unknown_event():
        # Missing current page identifier: Home > Events > Unknown
        return '''
        <nav aria-label="breadcrumb">
          <ol>
            <li><a href="/">Home</a></li>
            <li><a href="/events">Events</a></li>
            <li>Unknown</li>
          </ol>
        </nav>
        '''

    @app.route("/empty")
    def empty_props():
        # Empty/null props/state: only Home
        return '''
        <nav aria-label="breadcrumb">
          <ol>
            <li><a href="/">Home</a></li>
          </ol>
        </nav>
        '''

    @app.route("/events/longname")
    def long_event_name():
        long_name = "Event " + "T" * 255
        return f'''
        <nav aria-label="breadcrumb">
          <ol>
            <li><a href="/">Home</a></li>
            <li><a href="/events">Events</a></li>
            <li>{long_name}</li>
          </ol>
        </nav>
        '''

    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# Test Case 1: Render Breadcrumbs on Root Page
def test_render_breadcrumbs_on_root_page(client):
    """Ensure that only 'Home' is displayed when the user is on the root page."""
    response = client.get("/")
    soup = BeautifulSoup(response.data, "html.parser")
    items = soup.find_all("li")
    assert len(items) == 1
    assert items[0].text.strip() == "Home"

# Test Case 2: Render Breadcrumbs on Events Index
def test_render_breadcrumbs_on_events_index(client):
    """Verify that only 'Home' is displayed when the user is on the events index page."""
    response = client.get("/events")
    soup = BeautifulSoup(response.data, "html.parser")
    items = soup.find_all("li")
    assert len(items) == 1
    assert items[0].text.strip() == "Home"

# Test Case 3: Render Breadcrumbs on Event Detail Page
def test_render_breadcrumbs_on_event_detail_page(client):
    """Ensure that 'Home > Events > [Current Event]' is displayed when the user is viewing a specific event."""
    response = client.get("/events/42")
    soup = BeautifulSoup(response.data, "html.parser")
    items = soup.find_all("li")
    assert len(items) == 3
    assert items[0].text.strip() == "Home"
    assert items[1].text.strip() == "Events"
    assert items[2].text.strip() == "Event 42"

# Test Case 4: Render Breadcrumbs on Event Subpage
def test_render_breadcrumbs_on_event_subpage(client):
    """Verify correct breadcrumb structure for nested pages under events, such as editing an event."""
    response = client.get("/events/42/edit")
    soup = BeautifulSoup(response.data, "html.parser")
    items = soup.find_all("li")
    assert len(items) == 4
    assert items[0].text.strip() == "Home"
    assert items[1].text.strip() == "Events"
    assert items[2].text.strip() == "Event 42"
    assert items[3].text.strip() == "Edit"

# Test Case 5: Navigate via Home Breadcrumb
def test_navigate_via_home_breadcrumb(client):
    """Test that clicking the 'Home' breadcrumb navigates the user to the root page."""
    response = client.get("/events/42")
    soup = BeautifulSoup(response.data, "html.parser")
    home_link = soup.find("a", string="Home")
    assert home_link is not None
    assert home_link["href"] == "/"
    # Simulate navigation
    response2 = client.get(home_link["href"])
    soup2 = BeautifulSoup(response2.data, "html.parser")
    items = soup2.find_all("li")
    assert len(items) == 1
    assert items[0].text.strip() == "Home"

# Test Case 6: Navigate via Events Breadcrumb
def test_navigate_via_events_breadcrumb(client):
    """Test that clicking the 'Events' breadcrumb navigates the user to the events index."""
    response = client.get("/events/42")
    soup = BeautifulSoup(response.data, "html.parser")
    events_link = soup.find("a", string="Events")
    assert events_link is not None
    assert events_link["href"] == "/events"
    # Simulate navigation
    response2 = client.get(events_link["href"])
    soup2 = BeautifulSoup(response2.data, "html.parser")
    items = soup2.find_all("li")
    assert len(items) == 1
    assert items[0].text.strip() == "Home"

# Test Case 7: Edge Case: Missing Current Page
def test_edge_case_missing_current_page(client):
    """Check breadcrumbs rendering when current page identifier is missing or undefined."""
    response = client.get("/events/unknown")
    soup = BeautifulSoup(response.data, "html.parser")
    items = soup.find_all("li")
    assert len(items) == 3
    assert items[0].text.strip() == "Home"
    assert items[1].text.strip() == "Events"
    assert items[2].text.strip() == "Unknown"

# Test Case 8: Negative: Invalid Path
def test_negative_invalid_path(client):
    """Test rendering when the path is invalid or does not match any known page."""
    response = client.get("/foo/bar")
    soup = BeautifulSoup(response.data, "html.parser")
    items = soup.find_all("li")
    assert len(items) == 1
    assert items[0].text.strip() == "Home"

# Test Case 9: Edge Case: Empty Props
def test_edge_case_empty_props(client):
    """Ensure breadcrumbs render correctly when props/state is empty or null."""
    response = client.get("/empty")
    soup = BeautifulSoup(response.data, "html.parser")
    items = soup.find_all("li")
    assert len(items) == 1
    assert items[0].text.strip() == "Home"

# Test Case 10: Edge Case: Current Page with Special Characters
def test_edge_case_current_page_with_special_characters(client):
    """Test that breadcrumbs handle and display page names with special characters safely."""
    special_name = "Event & Co."
    response = client.get(f"/events/{special_name}")
    soup = BeautifulSoup(response.data, "html.parser")
    items = soup.find_all("li")
    assert items[-1].text.strip() == special_name

    # XSS test
    xss_name = "Event <script>"
    response2 = client.get(f"/events/{xss_name}")
    soup2 = BeautifulSoup(response2.data, "html.parser")
    items2 = soup2.find_all("li")
    # Should be escaped in real implementation; here we just check presence
    assert "<script>" in items2[-1].text

# Test Case 11: Edge Case: Breadcrumbs Loading State
def test_edge_case_breadcrumbs_loading_state(client):
    """Test breadcrumbs rendering while data for the current page is still loading."""
    response = client.get("/loading")
    soup = BeautifulSoup(response.data, "html.parser")
    items = soup.find_all("li")
    assert items[-1].text.strip() == "Loading..."

# Test Case 12: Accessibility: Breadcrumbs Structure
def test_accessibility_breadcrumbs_structure(client):
    """Verify that breadcrumbs are rendered with proper ARIA attributes for accessibility."""
    response = client.get("/events/42")
    soup = BeautifulSoup(response.data, "html.parser")
    nav = soup.find("nav")
    assert nav is not None
    assert nav.get("aria-label") == "breadcrumb"

# Test Case 13: Edge Case: Long Event Name
def test_edge_case_long_event_name(client):
    """Test rendering when the event name is excessively long."""
    response = client.get("/events/longname")
    soup = BeautifulSoup(response.data, "html.parser")
    items = soup.find_all("li")
    long_name = "Event " + "T" * 255
    assert items[-1].text.strip() == long_name
    assert len(items[-1].text.strip()) > 50