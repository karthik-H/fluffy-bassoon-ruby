import os
import subprocess
import tempfile
import textwrap

import pytest

RAILS_ENV = os.environ.get("RAILS_ENV", "test")

def run_rails_command(command, input_data=None):
    """Helper to run a rails command and return output, error, and exit code."""
    proc = subprocess.Popen(
        command,
        shell=True,
        stdin=subprocess.PIPE if input_data else None,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={**os.environ, "RAILS_ENV": RAILS_ENV},
        universal_newlines=True,
    )
    out, err = proc.communicate(input_data)
    return out, err, proc.returncode

@pytest.fixture(autouse=True)
def setup_and_teardown_db():
    # Ensure test db is migrated and clean before each test
    run_rails_command("bin/rails db:test:prepare")
    yield
    run_rails_command("bin/rails db:test:prepare")

def create_event(id=None, attrs=None):
    """Create an event in the test database and return its id."""
    attrs = attrs or {}
    attr_str = ", ".join(f"{k}: '{v}'" for k, v in attrs.items())
    id_str = f"id: {id}, " if id else ""
    code = f"Event.create!({id_str}{attr_str})"
    run_rails_command(f'bin/rails runner "{code}"')
    # Fetch the event id
    out, _, _ = run_rails_command(
        'bin/rails runner "puts Event.last.id"'
    )
    return int(out.strip())

def destroy_event(id, session={}):
    """Simulate a destroy request to EventsController."""
    # Use Rails integration test runner to simulate HTTP DELETE
    session_str = (
        ", ".join(f"{k}: '{v}'" for k, v in session.items()) if session else ""
    )
    code = textwrap.dedent(f"""
        require_relative '../../app/controllers/events_controller'
        require 'rails/test_help'
        class DestroyTest < ActionDispatch::IntegrationTest
          def destroy_event
            delete event_url({id}), session: {{{session_str}}}
            [response.status, response.redirect_url, flash[:notice], flash[:alert]]
          rescue => e
            puts "EXCEPTION:{{{{#{'{'}e.class.name{'}'}}}}}:{{{{#{'{'}e.message{'}'}}}}}"
            raise
          end
        end
        t = DestroyTest.new('destroy_event')
        begin
          result = t.destroy_event
          puts "RESULT:{{{{#{'{'}result.inspect{'}'}}}}}"
        rescue => e
        end
    """)
    with tempfile.NamedTemporaryFile("w", suffix=".rb", delete=False) as f:
        f.write(code)
        fname = f.name
    out, err, code = run_rails_command(f"bin/rails runner {fname}")
    os.unlink(fname)
    return out, err, code

def login_as(user_id):
    """Stub: In a real app, set session or cookies for authentication."""
    # For this test, we assume session[:user_id] is used
    return {"user_id": user_id}

def test_destroy_event_successfully():
    """Test Case 1: Destroy Event Successfully
    Verifies that an existing event is destroyed and the user is redirected with a success notice."""
    event_id = create_event(id=1)
    session = login_as(1)
    out, err, code = destroy_event(event_id, session)
    # Check event is gone
    out2, _, _ = run_rails_command(f'bin/rails runner "puts Event.where(id: {event_id}).count"')
    assert "RESULT:" in out
    assert "redirect" in out or "302" in out
    assert "notice" in out or "success" in out
    assert out2.strip() == "0"

def test_destroy_non_existent_event():
    """Test Case 2: Destroy Non-existent Event
    Checks the behavior when attempting to destroy an event that does not exist."""
    session = login_as(1)
    out, err, code = destroy_event(9999, session)
    assert "RecordNotFound" in out or "404" in out or "EXCEPTION" in out

def test_destroy_event_without_authorization():
    """Test Case 3: Destroy Event Without Authorization
    Verifies that an unauthorized user cannot destroy an event."""
    event_id = create_event(id=2)
    # User 99 is not authorized
    session = login_as(99)
    out, err, code = destroy_event(event_id, session)
    # Event should still exist
    out2, _, _ = run_rails_command(f'bin/rails runner "puts Event.where(id: {event_id}).count"')
    assert out2.strip() == "1"
    assert "403" in out or "forbidden" in out.lower() or "alert" in out.lower()

def test_destroy_event_without_authentication():
    """Test Case 4: Destroy Event Without Authentication
    Checks the behavior when a non-authenticated user attempts to destroy an event."""
    event_id = create_event(id=3)
    # No session
    out, err, code = destroy_event(event_id, session={})
    out2, _, _ = run_rails_command(f'bin/rails runner "puts Event.where(id: {event_id}).count"')
    assert out2.strip() == "1"
    assert "login" in out.lower() or "redirect" in out.lower() or "401" in out or "authentication" in out.lower()

def test_destroy_event_with_invalid_id_format():
    """Test Case 5: Destroy Event With Invalid ID Format
    Ensures the controller handles invalid ID formats gracefully."""
    session = login_as(1)
    out, err, code = destroy_event("'abc'", session)
    assert "404" in out or "400" in out or "parameter" in out.lower() or "EXCEPTION" in out

def test_destroy_event_that_was_already_deleted():
    """Test Case 6: Destroy Event That Was Already Deleted
    Checks the behavior when attempting to destroy an event that has just been deleted in a concurrent request."""
    event_id = create_event(id=4)
    # Delete event directly
    run_rails_command(f'bin/rails runner "Event.find({event_id}).destroy"')
    session = login_as(1)
    out, err, code = destroy_event(event_id, session)
    assert "RecordNotFound" in out or "404" in out or "EXCEPTION" in out

def test_destroy_event_redirects_to_events_list():
    """Test Case 7: Destroy Event Redirects to Events List
    Verifies that after successful deletion, the response redirects the user to the events index page."""
    event_id = create_event(id=5)
    session = login_as(1)
    out, err, code = destroy_event(event_id, session)
    assert "redirect" in out or "302" in out

def test_destroy_event_shows_notice_message():
    """Test Case 8: Destroy Event Shows Notice Message
    Ensures that a notice message is set and displayed to the user after successful deletion."""
    event_id = create_event(id=6)
    session = login_as(1)
    out, err, code = destroy_event(event_id, session)
    assert "notice" in out or "success" in out
