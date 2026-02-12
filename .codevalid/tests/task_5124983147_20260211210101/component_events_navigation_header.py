import unittest
from unittest.mock import patch, MagicMock

# Assumptions:
# - The header component is rendered via a function `render_header(path='/', navigation_data=True)`
# - The returned DOM mock provides methods for querying elements and simulating events.
# - Navigation is handled via `app.views.layouts.application.navigate`
# - The logo is found via dom.find_element('logo')
# - Navigation links are found via dom.find_nav_link('All Events') etc.

def render_header(path='/', navigation_data=True):
    """
    Renders the header component at the given path.
    navigation_data: If False, simulates missing navigation data.
    Returns a mock DOM object with query and event simulation methods.
    """
    dom = MagicMock()
    dom.path = path
    dom.navigation_data = navigation_data
    return dom

class TestHeaderNavigation(unittest.TestCase):
    def setUp(self):
        self.patcher = patch('app.views.layouts.application.render_header', side_effect=render_header)
        self.mock_render = self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def test_render_logo_as_link_to_root(self):
        """Test Case 1: Render Logo as Link to Root"""
        dom = render_header(path='/events')
        logo = dom.find_element('logo')
        self.assertIsNotNone(logo, "Logo element should be present")
        self.assertTrue(logo.is_link(), "Logo should be a link")
        self.assertEqual(logo.href, '/', "Logo link should point to root path '/'")

    def test_all_events_link_is_active_on_root_path(self):
        """Test Case 2: All Events Link is Active on Root Path"""
        dom = render_header(path='/')
        all_events_link = dom.find_nav_link('All Events')
        self.assertIsNotNone(all_events_link, "'All Events' link should be present")
        self.assertTrue(all_events_link.is_active(), "'All Events' link should be active on root path")

    def test_all_events_link_is_active_on_events_path(self):
        """Test Case 3: All Events Link is Active on /events Path"""
        dom = render_header(path='/events')
        all_events_link = dom.find_nav_link('All Events')
        self.assertIsNotNone(all_events_link, "'All Events' link should be present")
        self.assertTrue(all_events_link.is_active(), "'All Events' link should be active on /events path")

    def test_new_event_link_is_active_on_events_new_path(self):
        """Test Case 4: New Event Link is Active on /events/new Path"""
        dom = render_header(path='/events/new')
        new_event_link = dom.find_nav_link('New Event')
        self.assertIsNotNone(new_event_link, "'New Event' link should be present")
        self.assertTrue(new_event_link.is_active(), "'New Event' link should be active on /events/new path")

    def test_all_events_link_navigates_correctly(self):
        """Test Case 5: All Events Link Navigates Correctly"""
        dom = render_header(path='/about')
        all_events_link = dom.find_nav_link('All Events')
        self.assertIsNotNone(all_events_link, "'All Events' link should be present")
        with patch('app.views.layouts.application.navigate') as mock_nav:
            all_events_link.click()
            mock_nav.assert_called_with('/events')

    def test_new_event_link_navigates_correctly(self):
        """Test Case 6: New Event Link Navigates Correctly"""
        dom = render_header(path='/')
        new_event_link = dom.find_nav_link('New Event')
        self.assertIsNotNone(new_event_link, "'New Event' link should be present")
        with patch('app.views.layouts.application.navigate') as mock_nav:
            new_event_link.click()
            mock_nav.assert_called_with('/events/new')

    def test_logo_link_navigates_to_root(self):
        """Test Case 7: Logo Link Navigates to Root"""
        dom = render_header(path='/events')
        logo = dom.find_element('logo')
        self.assertIsNotNone(logo, "Logo element should be present")
        with patch('app.views.layouts.application.navigate') as mock_nav:
            logo.click()
            mock_nav.assert_called_with('/')

    def test_no_navigation_link_is_active_on_unrelated_path(self):
        """Test Case 8: No Navigation Link is Active on Unrelated Path"""
        dom = render_header(path='/about')
        all_events_link = dom.find_nav_link('All Events')
        new_event_link = dom.find_nav_link('New Event')
        if all_events_link:
            self.assertFalse(all_events_link.is_active(), "'All Events' link should not be active on unrelated path")
        if new_event_link:
            self.assertFalse(new_event_link.is_active(), "'New Event' link should not be active on unrelated path")

    def test_navigation_links_not_rendered_when_navigation_data_missing(self):
        """Test Case 9: Navigation Links Not Rendered When Navigation Data Missing"""
        dom = render_header(path='/', navigation_data=False)
        all_events_link = dom.find_nav_link('All Events')
        new_event_link = dom.find_nav_link('New Event')
        self.assertIsNone(all_events_link, "'All Events' link should not be rendered when navigation data is missing")
        self.assertIsNone(new_event_link, "'New Event' link should not be rendered when navigation data is missing")

    def test_header_renders_on_invalid_path(self):
        """Test Case 10: Header Renders on Invalid Path"""
        dom = render_header(path='/random')
        logo = dom.find_element('logo')
        self.assertIsNotNone(logo, "Logo should be present on invalid path")
        all_events_link = dom.find_nav_link('All Events')
        new_event_link = dom.find_nav_link('New Event')
        if all_events_link:
            self.assertFalse(all_events_link.is_active(), "'All Events' link should not be active on invalid path")
        if new_event_link:
            self.assertFalse(new_event_link.is_active(), "'New Event' link should not be active on invalid path")

    def test_rapid_path_changes_reflect_active_link_correctly(self):
        """Test Case 11: Rapid Path Changes Reflect Active Link Correctly"""
        for path, active_link in [
            ('/', 'All Events'),
            ('/events', 'All Events'),
            ('/events/new', 'New Event')
        ]:
            dom = render_header(path=path)
            all_events_link = dom.find_nav_link('All Events')
            new_event_link = dom.find_nav_link('New Event')
            if active_link == 'All Events':
                self.assertTrue(all_events_link.is_active(), f"'All Events' should be active on {path}")
                if new_event_link:
                    self.assertFalse(new_event_link.is_active(), f"'New Event' should not be active on {path}")
            elif active_link == 'New Event':
                self.assertTrue(new_event_link.is_active(), f"'New Event' should be active on {path}")
                if all_events_link:
                    self.assertFalse(all_events_link.is_active(), f"'All Events' should not be active on {path}")

    def test_navigation_links_are_accessible_via_keyboard(self):
        """Test Case 12: Navigation Links are Accessible via Keyboard"""
        dom = render_header(path='/')
        all_events_link = dom.find_nav_link('All Events')
        new_event_link = dom.find_nav_link('New Event')
        for link, target in [(all_events_link, '/events'), (new_event_link, '/events/new')]:
            if link:
                with patch('app.views.layouts.application.navigate') as mock_nav:
                    link.focus()
                    link.key_press('Enter')
                    mock_nav.assert_called_with(target)
                    link.key_press(' ')
                    mock_nav.assert_called_with(target)

    def test_no_duplicate_navigation_links_rendered(self):
        """Test Case 13: No Duplicate Navigation Links Rendered"""
        dom = render_header(path='/')
        all_events_links = dom.find_all_nav_links('All Events')
        new_event_links = dom.find_all_nav_links('New Event')
        self.assertEqual(len(all_events_links), 1, "There should be only one 'All Events' link")
        self.assertEqual(len(new_event_links), 1, "There should be only one 'New Event' link")

if __name__ == '__main__':
    unittest.main()