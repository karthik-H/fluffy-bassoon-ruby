# frozen_string_literal: true

require "minitest/autorun"
require "net/http"
require "json"
require "uri"

BASE_URL = "http://localhost:3000"

class EndpointEventsResourceTest < Minitest::Test
  # Utility methods for setup/teardown
  def self.cleanup_events
    (1..20).each do |id|
      Net::HTTP.start("localhost", 3000) do |http|
        req = Net::HTTP::Delete.new("/events/#{id}")
        http.request(req)
      end
    end
  end

  def setup
    self.class.cleanup_events
    # Seed a sample event for tests that require it
    @sample_event = {
      "title" => "Sample Event",
      "date" => "2024-08-01",
      "location" => "New York"
    }
    uri = URI("#{BASE_URL}/events")
    resp = Net::HTTP.post(uri, @sample_event.to_json, "Content-Type" => "application/json")
    if resp.code.to_i == 201
      @sample_event_id = JSON.parse(resp.body)["id"] || 1
    else
      @sample_event_id = 1
    end
  end

  def teardown
    self.class.cleanup_events
  end

  # Test Case 1: List all events - positive
  def test_list_all_events_positive
    uri = URI("#{BASE_URL}/events")
    resp = Net::HTTP.get_response(uri)
    assert_equal 200, resp.code.to_i
    data = JSON.parse(resp.body)
    assert_equal(
      {"events" => [
        {"date" => "2024-08-01", "id" => @sample_event_id, "location" => "New York", "title" => "Sample Event"}
      ]},
      data
    )
  end

  # Test Case 2: List events - no events present
  def test_list_events_no_events_present
    self.class.cleanup_events
    uri = URI("#{BASE_URL}/events")
    resp = Net::HTTP.get_response(uri)
    assert_equal 200, resp.code.to_i
    data = JSON.parse(resp.body)
    assert_equal({"events" => []}, data)
  end

  # Test Case 3: Get event details - valid ID
  def test_get_event_details_valid_id
    uri = URI("#{BASE_URL}/events/#{@sample_event_id}")
    resp = Net::HTTP.get_response(uri)
    assert_equal 200, resp.code.to_i
    data = JSON.parse(resp.body)
    assert_equal(
      {"date" => "2024-08-01", "id" => @sample_event_id, "location" => "New York", "title" => "Sample Event"},
      data
    )
  end

  # Test Case 4: Get event details - invalid ID
  def test_get_event_details_invalid_id
    uri = URI("#{BASE_URL}/events/9999")
    resp = Net::HTTP.get_response(uri)
    assert_equal 404, resp.code.to_i
    data = JSON.parse(resp.body)
    assert_equal({"error" => "Event not found"}, data)
  end

  # Test Case 5: Access new event form
  def test_access_new_event_form
    uri = URI("#{BASE_URL}/events/new")
    resp = Net::HTTP.get_response(uri)
    assert_equal 200, resp.code.to_i
    data = JSON.parse(resp.body)
    assert_equal({"form" => {"fields" => ["title", "date", "location"]}}, data)
  end

  # Test Case 6: Create event - valid data
  def test_create_event_valid_data
    payload = {"date" => "2024-09-01", "location" => "San Francisco", "title" => "New Event"}
    uri = URI("#{BASE_URL}/events")
    resp = Net::HTTP.post(uri, payload.to_json, "Content-Type" => "application/json")
    assert_equal 201, resp.code.to_i
    data = JSON.parse(resp.body)
    assert_equal(
      {"date" => "2024-09-01", "id" => data["id"], "location" => "San Francisco", "title" => "New Event"},
      data
    )
  end

  # Test Case 7: Create event - missing required fields
  def test_create_event_missing_required_fields
    payload = {"date" => "2024-09-01", "title" => ""}
    uri = URI("#{BASE_URL}/events")
    resp = Net::HTTP.post(uri, payload.to_json, "Content-Type" => "application/json")
    assert_equal 422, resp.code.to_i
    data = JSON.parse(resp.body)
    assert_equal(
      {"errors" => {"location" => ["can't be blank"], "title" => ["can't be blank"]}},
      data
    )
  end

  # Test Case 8: Create event - title at maximum length
  def test_create_event_title_at_maximum_length
    max_title = "T" * 255
    payload = {"date" => "2024-09-01", "location" => "Los Angeles", "title" => max_title}
    uri = URI("#{BASE_URL}/events")
    resp = Net::HTTP.post(uri, payload.to_json, "Content-Type" => "application/json")
    assert_equal 201, resp.code.to_i
    data = JSON.parse(resp.body)
    assert_equal(
      {"date" => "2024-09-01", "id" => data["id"], "location" => "Los Angeles", "title" => max_title},
      data
    )
  end

  # Test Case 9: Create event - invalid date format
  def test_create_event_invalid_date_format
    payload = {"date" => "not-a-date", "location" => "Chicago", "title" => "Invalid Date Event"}
    uri = URI("#{BASE_URL}/events")
    resp = Net::HTTP.post(uri, payload.to_json, "Content-Type" => "application/json")
    assert_equal 422, resp.code.to_i
    data = JSON.parse(resp.body)
    assert_equal(
      {"errors" => {"date" => ["is not a valid date"]}},
      data
    )
  end

  # Test Case 10: Access edit event form - valid ID
  def test_access_edit_event_form_valid_id
    uri = URI("#{BASE_URL}/events/#{@sample_event_id}/edit")
    resp = Net::HTTP.get_response(uri)
    assert_equal 200, resp.code.to_i
    data = JSON.parse(resp.body)
    assert_equal(
      {"form" => {
        "fields" => ["title", "date", "location"],
        "values" => {"date" => "2024-08-01", "location" => "New York", "title" => "Sample Event"}
      }},
      data
    )
  end

  # Test Case 11: Access edit event form - invalid ID
  def test_access_edit_event_form_invalid_id
    uri = URI("#{BASE_URL}/events/9999/edit")
    resp = Net::HTTP.get_response(uri)
    assert_equal 404, resp.code.to_i
    data = JSON.parse(resp.body)
    assert_equal({"error" => "Event not found"}, data)
  end

  # Test Case 12: Update event - PATCH with valid data
  def test_update_event_patch_valid_data
    payload = {"title" => "Updated Event Name"}
    uri = URI("#{BASE_URL}/events/#{@sample_event_id}")
    http = Net::HTTP.new(uri.host, uri.port)
    req = Net::HTTP::Patch.new(uri.path, "Content-Type" => "application/json")
    req.body = payload.to_json
    resp = http.request(req)
    assert_equal 200, resp.code.to_i
    data = JSON.parse(resp.body)
    assert_equal(
      {"date" => "2024-08-01", "id" => @sample_event_id, "location" => "New York", "title" => "Updated Event Name"},
      data
    )
  end

  # Test Case 13: Update event - PUT with all fields
  def test_update_event_put_all_fields
    payload = {"date" => "2024-10-10", "location" => "Boston", "title" => "Completely Updated Event"}
    uri = URI("#{BASE_URL}/events/#{@sample_event_id}")
    http = Net::HTTP.new(uri.host, uri.port)
    req = Net::HTTP::Put.new(uri.path, "Content-Type" => "application/json")
    req.body = payload.to_json
    resp = http.request(req)
    assert_equal 200, resp.code.to_i
    data = JSON.parse(resp.body)
    assert_equal(
      {"date" => "2024-10-10", "id" => @sample_event_id, "location" => "Boston", "title" => "Completely Updated Event"},
      data
    )
  end

  # Test Case 14: Update event - invalid ID
  def test_update_event_invalid_id
    payload = {"title" => "Updated"}
    uri = URI("#{BASE_URL}/events/9999")
    http = Net::HTTP.new(uri.host, uri.port)
    req = Net::HTTP::Patch.new(uri.path, "Content-Type" => "application/json")
    req.body = payload.to_json
    resp = http.request(req)
    assert_equal 404, resp.code.to_i
    data = JSON.parse(resp.body)
    assert_equal({"error" => "Event not found"}, data)
  end

  # Test Case 15: Update event - invalid data
  def test_update_event_invalid_data
    payload = {"date" => "invalid-date"}
    uri = URI("#{BASE_URL}/events/#{@sample_event_id}")
    http = Net::HTTP.new(uri.host, uri.port)
    req = Net::HTTP::Patch.new(uri.path, "Content-Type" => "application/json")
    req.body = payload.to_json
    resp = http.request(req)
    assert_equal 422, resp.code.to_i
    data = JSON.parse(resp.body)
    assert_equal(
      {"errors" => {"date" => ["is not a valid date"]}},
      data
    )
  end

  # Test Case 16: Delete event - valid ID
  def test_delete_event_valid_id
    # Create a new event to delete
    payload = {"date" => "2024-12-01", "location" => "Austin", "title" => "Delete Me"}
    uri = URI("#{BASE_URL}/events")
    resp = Net::HTTP.post(uri, payload.to_json, "Content-Type" => "application/json")
    event_id = JSON.parse(resp.body)["id"]
    del_uri = URI("#{BASE_URL}/events/#{event_id}")
    http = Net::HTTP.new(del_uri.host, del_uri.port)
    req = Net::HTTP::Delete.new(del_uri.path)
    del_resp = http.request(req)
    assert_equal 204, del_resp.code.to_i
    assert_equal "", del_resp.body.strip
  end

  # Test Case 17: Delete event - invalid ID
  def test_delete_event_invalid_id
    uri = URI("#{BASE_URL}/events/9999")
    http = Net::HTTP.new(uri.host, uri.port)
    req = Net::HTTP::Delete.new(uri.path)
    resp = http.request(req)
    assert_equal 404, resp.code.to_i
    data = JSON.parse(resp.body)
    assert_equal({"error" => "Event not found"}, data)
  end

  # Test Case 18: Create event - extra fields in request
  def test_create_event_extra_fields_in_request
    payload = {
      "date" => "2024-11-01",
      "location" => "Miami",
      "title" => "Event With Extra",
      "unexpected" => "field"
    }
    uri = URI("#{BASE_URL}/events")
    resp = Net::HTTP.post(uri, payload.to_json, "Content-Type" => "application/json")
    assert_equal 201, resp.code.to_i
    data = JSON.parse(resp.body)
    assert_equal(
      {"date" => "2024-11-01", "id" => data["id"], "location" => "Miami", "title" => "Event With Extra"},
      data
    )
    refute_includes data.keys, "unexpected"
  end

  # Test Case 19: Create event - empty request body
  def test_create_event_empty_request_body
    uri = URI("#{BASE_URL}/events")
    resp = Net::HTTP.post(uri, {}.to_json, "Content-Type" => "application/json")
    assert_equal 422, resp.code.to_i
    data = JSON.parse(resp.body)
    assert_equal(
      {"errors" => {"date" => ["can't be blank"], "location" => ["can't be blank"], "title" => ["can't be blank"]}},
      data
    )
  end
end