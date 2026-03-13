require 'test_helper'

class EventsControllerIndexTest < ActionDispatch::IntegrationTest
  # Test Case 1
  def test_fetch_events_with_multiple_records
    e1 = Event.create!(created_at: Time.parse('2024-01-01'))
    e2 = Event.create!(created_at: Time.parse('2024-02-01'))
    e3 = Event.create!(created_at: Time.parse('2024-03-01'))
    get '/events'
    assert_response :success
    ids = JSON.parse(@response.body).map { |e| e['id'] }
    assert_equal [e3.id, e2.id, e1.id], ids
  end

  def test_fetch_events_with_single_record
    e = Event.create!(created_at: Time.parse('2024-05-01'))
    get '/events'
    assert_response :success
    body = JSON.parse(@response.body)
    assert_equal 1, body.length
    assert_equal e.id, body.first['id']
  end

  def test_fetch_events_with_no_records
    get '/events'
    assert_response :success
    assert_equal [], JSON.parse(@response.body)
  end

  def test_fetch_events_with_same_created_at
    t = Time.parse('2024-01-01 10:00:00')
    e1 = Event.create!(created_at: t)
    e2 = Event.create!(created_at: t)
    e3 = Event.create!(created_at: t)
    get '/events'
    assert_response :success
    ids = JSON.parse(@response.body).map { |e| e['id'] }
    assert_equal [e3.id, e2.id, e1.id].sort, ids.sort
  end

  def test_fetch_events_with_large_number_of_records
    base = Time.parse('2020-01-01')
    events = []
    10000.times do |i|
      events << Event.create!(created_at: base + i.days)
    end
    get '/events'
    assert_response :success
    body = JSON.parse(@response.body)
    assert_equal 10000, body.length
    assert_equal events.last.id, body.first['id']
  end

  def test_fetch_events_database_error
    Event.stub(:all, -> { raise ActiveRecord::ActiveRecordError }) do
      get '/events'
    end
    assert_response 500
  end

  def test_fetch_events_with_future_created_at
    e1 = Event.create!(created_at: Time.parse('2024-01-01'))
    e2 = Event.create!(created_at: Time.parse('2999-12-31'))
    get '/events'
    assert_response :success
    ids = JSON.parse(@response.body).map { |e| e['id'] }
    assert_equal [e2.id, e1.id], ids
  end

  def test_fetch_events_invalid_route
    get '/invalid_events_path'
    assert_response 404
  end

  def test_fetch_events_order_null_timestamp_handling
    e1 = Event.create!(created_at: Time.parse('2024-01-01'))
    e2 = Event.create!(created_at: Time.parse('2024-02-01'))
    e3 = Event.create!(created_at: nil)
    get '/events'
    assert_response :success
    ids = JSON.parse(@response.body).map { |e| e['id'] }
    assert_equal [e2.id, e1.id, e3.id], ids
  end

  def test_fetch_events_with_soft_deleted_records
    e1 = Event.create!(created_at: Time.parse('2024-01-01'), deleted: false)
    e2 = Event.create!(created_at: Time.parse('2024-02-01'), deleted: false)
    e3 = Event.create!(created_at: Time.parse('2024-03-01'), deleted: true)
    get '/events'
    assert_response :success
    ids = JSON.parse(@response.body).map { |e| e['id'] }
    assert_equal [e2.id, e1.id], ids
  end

  def test_fetch_events_invalid_query_parameters_ignored
    e1 = Event.create!(created_at: Time.parse('2024-01-01'))
    e2 = Event.create!(created_at: Time.parse('2024-02-01'))
    get '/events?sort=asc&foo=bar'
    assert_response :success
    ids = JSON.parse(@response.body).map { |e| e['id'] }
    assert_equal [e2.id, e1.id], ids
  end

  def test_fetch_events_with_timezone_variations
    e1 = Event.create!(created_at: Time.parse('2024-01-01 12:00:00 UTC'))
    e2 = Event.create!(created_at: Time.parse('2024-01-01 05:00:00 PST'))
    e3 = Event.create!(created_at: Time.parse('2024-01-01 09:00:00 EST'))
    get '/events'
    assert_response :success
    ids = JSON.parse(@response.body).map { |e| e['id'] }
    assert_equal [e3.id, e1.id, e2.id], ids
  end

  def test_fetch_events_with_millisecond_precision
    t = Time.parse('2024-01-01 10:00:00')
    e1 = Event.create!(created_at: t + 0.001)
    e2 = Event.create!(created_at: t + 0.002)
    e3 = Event.create!(created_at: t + 0.003)
    get '/events'
    assert_response :success
    ids = JSON.parse(@response.body).map { |e| e['id'] }
    assert_equal [e3.id, e2.id, e1.id], ids
  end

  def test_fetch_events_with_authorization_required
    user = users(:unauthorized_user)
    sign_in(user)
    get '/events'
    assert_response 403
  end
end
