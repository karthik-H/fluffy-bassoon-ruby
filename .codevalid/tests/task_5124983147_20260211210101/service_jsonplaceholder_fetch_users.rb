require 'minitest/autorun'
require 'mocha/minitest'
require_relative '../../../app/services/jsonplaceholder_service'
require 'rails'

class ServiceJsonplaceholderFetchUsersTest < Minitest::Test
  def setup
    @cache = mock('cache')
    Rails.stubs(:cache).returns(@cache)
    @logger = mock('logger')
    Rails.stubs(:logger).returns(@logger)
    @logger.stubs(:error)
  end

  def mock_response(code, body)
    resp = mock('response')
    resp.stubs(:code).returns(code)
    resp.stubs(:body).returns(body)
    resp
  end

  # Test Case 1
  def test_fetch_users_cache_expired_success_200
    users = [{ 'id' => 1 }]
    @cache.expects(:fetch).with('jsonplaceholder_users', expires_in: JsonplaceholderService::CACHE_DURATION).yields
    Net::HTTP.expects(:get_response).returns(mock_response('200', users.to_json))
    result = JsonplaceholderService.fetch_users
    assert_equal users, result
  end

  # Test Case 2
  def test_fetch_users_cache_expired_api_error_404
    @cache.expects(:fetch).yields
    Net::HTTP.expects(:get_response).returns(mock_response('404', ''))
    result = JsonplaceholderService.fetch_users
    assert_equal [], result
  end

  # Test Case 3
  def test_fetch_users_cache_expired_api_error_500
    @cache.expects(:fetch).yields
    Net::HTTP.expects(:get_response).returns(mock_response('500', ''))
    result = JsonplaceholderService.fetch_users
    assert_equal [], result
  end

  # Test Case 4
  def test_fetch_users_cache_expired_api_empty_list
    @cache.expects(:fetch).yields
    Net::HTTP.expects(:get_response).returns(mock_response('200', [].to_json))
    result = JsonplaceholderService.fetch_users
    assert_equal [], result
  end

  # Test Case 5
  def test_fetch_users_cache_expired_api_invalid_json
    @cache.expects(:fetch).yields
    Net::HTTP.expects(:get_response).returns(mock_response('200', 'invalid'))
    result = JsonplaceholderService.fetch_users
    assert_equal [], result
  end

  # Test Case 6
  def test_fetch_users_cache_not_expired_return_cached_users
    users = [{ 'id' => 1 }]
    @cache.expects(:fetch).returns(users)
    result = JsonplaceholderService.fetch_users
    assert_equal users, result
  end

  # Test Case 7
  def test_fetch_users_cache_not_expired_cached_users_empty
    @cache.expects(:fetch).returns([])
    result = JsonplaceholderService.fetch_users
    assert_equal [], result
  end

  # Test Case 8
  def test_fetch_users_cache_expired_api_timeout
    @cache.expects(:fetch).yields
    Net::HTTP.expects(:get_response).raises(Timeout::Error)
    result = JsonplaceholderService.fetch_users
    assert_equal [], result
  end

  # Test Case 9
  def test_fetch_users_cache_expired_api_connection_error
    @cache.expects(:fetch).yields
    Net::HTTP.expects(:get_response).raises(SocketError)
    result = JsonplaceholderService.fetch_users
    assert_equal [], result
  end

  # Test Case 10
  def test_fetch_users_cache_expired_api_partial_user_list
    list = [{ 'id' => 1 }, { 'name' => 'Bob' }]
    @cache.expects(:fetch).yields
    Net::HTTP.expects(:get_response).returns(mock_response('200', list.to_json))
    result = JsonplaceholderService.fetch_users
    assert_equal list, result
  end

  # Test Case 11
  def test_fetch_users_api_204_no_content
    @cache.expects(:fetch).yields
    Net::HTTP.expects(:get_response).returns(mock_response('204', ''))
    result = JsonplaceholderService.fetch_users
    assert_equal [], result
  end

  # Test Case 12
  def test_fetch_users_cache_write_failure
    users = [{ 'id' => 1 }]
    @cache.expects(:fetch).raises(StandardError).then.yields
    Net::HTTP.expects(:get_response).returns(mock_response('200', users.to_json))
    result = JsonplaceholderService.fetch_users
    assert_equal users, result
  end

  # Test Case 13
  def test_fetch_users_api_returns_non_array_json
    @cache.expects(:fetch).yields
    Net::HTTP.expects(:get_response).returns(mock_response('200', { foo: 'bar' }.to_json))
    result = JsonplaceholderService.fetch_users
    assert_equal [], result
  end

  # Test Case 14
  def test_fetch_users_api_slow_but_not_timeout
    users = [{ 'id' => 1 }]
    @cache.expects(:fetch).yields
    Net::HTTP.expects(:get_response).returns(mock_response('200', users.to_json))
    result = JsonplaceholderService.fetch_users
    assert_equal users, result
  end

  # Test Case 15
  def test_fetch_users_cache_contains_invalid_data
    @cache.expects(:fetch).returns('invalid_data')
    result = JsonplaceholderService.fetch_users
    assert_equal 'invalid_data', result
  end

  # Test Case 16
  def test_fetch_users_cache_key_missing
    users = [{ 'id' => 2 }]
    @cache.expects(:fetch).yields
    Net::HTTP.expects(:get_response).returns(mock_response('200', users.to_json))
    result = JsonplaceholderService.fetch_users
    assert_equal users, result
  end

  # Test Case 17
  def test_fetch_users_api_returns_non_json_body
    @cache.expects(:fetch).yields
    Net::HTTP.expects(:get_response).returns(mock_response('200', 'plain text'))
    result = JsonplaceholderService.fetch_users
    assert_equal [], result
  end

  # Test Case 18
  def test_fetch_users_api_redirect_301
    @cache.expects(:fetch).yields
    Net::HTTP.expects(:get_response).returns(mock_response('301', ''))
    result = JsonplaceholderService.fetch_users
    assert_equal [], result
  end

  # Test Case 19
  def test_fetch_users_api_large_payload
    large_list = Array.new(1000) { |i| { 'id' => i } }
    @cache.expects(:fetch).yields
    Net::HTTP.expects(:get_response).returns(mock_response('200', large_list.to_json))
    result = JsonplaceholderService.fetch_users
    assert_equal large_list, result
  end

  # Test Case 20
  def test_fetch_users_api_ssl_error
    @cache.expects(:fetch).yields
    Net::HTTP.expects(:get_response).raises(OpenSSL::SSL::SSLError)
    result = JsonplaceholderService.fetch_users
    assert_equal [], result
  end
end
