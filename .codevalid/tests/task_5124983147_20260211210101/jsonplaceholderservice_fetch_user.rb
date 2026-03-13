require 'minitest/autorun'
require 'mocha/minitest'
require 'rails'
require_relative '../../../app/services/jsonplaceholder_service'

class JsonplaceholderServiceFetchUserTest < Minitest::Test
  def setup
    Rails.cache.clear
  end

  def mock_response(code, body)
    resp = mock
    resp.stubs(:code).returns(code)
    resp.stubs(:body).returns(body)
    resp
  end

  def test_fetch_user_happy_path_cache_miss_successful_request
    user_json = { 'id' => 1, 'name' => 'User One' }.to_json
    HTTParty.stubs(:get).with('https://jsonplaceholder.typicode.com/users/1').returns(mock_response('200', user_json))
    result = JsonplaceholderService.fetch_user(1)
    assert_equal({'id'=>1,'name'=>'User One'}, result)
    assert_equal({'id'=>1,'name'=>'User One'}, Rails.cache.read('jsonplaceholder_user_1'))
  end

  def test_fetch_user_happy_path_cache_hit
    Rails.cache.write('jsonplaceholder_user_1', {'id'=>1,'name'=>'Cached User'})
    HTTParty.expects(:get).never
    result = JsonplaceholderService.fetch_user(1)
    assert_equal({'id'=>1,'name'=>'Cached User'}, result)
  end

  def test_fetch_user_api_returns_404
    HTTParty.stubs(:get).with('https://jsonplaceholder.typicode.com/users/999').returns(mock_response('404', '{}'))
    result = JsonplaceholderService.fetch_user(999)
    assert_nil result
    assert_nil Rails.cache.read('jsonplaceholder_user_999')
  end

  def test_fetch_user_api_returns_500
    HTTParty.stubs(:get).with('https://jsonplaceholder.typicode.com/users/1').returns(mock_response('500', { error: 'server error' }.to_json))
    JsonplaceholderService.expects(:log).at_least_once
    result = JsonplaceholderService.fetch_user(1)
    assert_nil result
    assert_nil Rails.cache.read('jsonplaceholder_user_1')
  end

  def test_fetch_user_api_timeout_exception
    HTTParty.stubs(:get).raises(Net::OpenTimeout)
    JsonplaceholderService.expects(:log).at_least_once
    result = JsonplaceholderService.fetch_user(3)
    assert_nil result
    assert_nil Rails.cache.read('jsonplaceholder_user_3')
  end

  def test_fetch_user_api_network_error_exception
    HTTParty.stubs(:get).raises(Errno::ECONNREFUSED)
    JsonplaceholderService.expects(:log).at_least_once
    result = JsonplaceholderService.fetch_user(2)
    assert_nil result
    assert_nil Rails.cache.read('jsonplaceholder_user_2')
  end

  def test_fetch_user_invalid_user_id_zero
    HTTParty.stubs(:get).with('https://jsonplaceholder.typicode.com/users/0').returns(mock_response('404', '{}'))
    result = JsonplaceholderService.fetch_user(0)
    assert_nil result
  end

  def test_fetch_user_invalid_user_id_negative
    HTTParty.stubs(:get).with('https://jsonplaceholder.typicode.com/users/-1').returns(mock_response('404', '{}'))
    result = JsonplaceholderService.fetch_user(-1)
    assert_nil result
  end

  def test_fetch_user_invalid_user_id_non_integer
    HTTParty.stubs(:get).with('https://jsonplaceholder.typicode.com/users/abc').returns(mock_response('404', '{}'))
    result = JsonplaceholderService.fetch_user('abc')
    assert_nil result
  end

  def test_fetch_user_cache_expired_calls_api_again
    Rails.cache.write('jsonplaceholder_user_4', {'old'=>'data'}, expires_in: -1)
    user_json = { 'id' => 4, 'name' => 'Fresh User' }.to_json
    HTTParty.stubs(:get).with('https://jsonplaceholder.typicode.com/users/4').returns(mock_response('200', user_json))
    result = JsonplaceholderService.fetch_user(4)
    assert_equal({'id'=>4,'name'=>'Fresh User'}, result)
    assert_equal({'id'=>4,'name'=>'Fresh User'}, Rails.cache.read('jsonplaceholder_user_4'))
  end

  def test_fetch_user_cache_corrupted_value
    Rails.cache.write('jsonplaceholder_user_5', 'corrupted')
    user_json = { 'id' => 5, 'name' => 'User Five' }.to_json
    HTTParty.stubs(:get).with('https://jsonplaceholder.typicode.com/users/5').returns(mock_response('200', user_json))
    result = JsonplaceholderService.fetch_user(5)
    assert_equal({'id'=>5,'name'=>'User Five'}, result)
    assert_equal({'id'=>5,'name'=>'User Five'}, Rails.cache.read('jsonplaceholder_user_5'))
  end

  def test_fetch_user_external_api_returns_invalid_json
    HTTParty.stubs(:get).with('https://jsonplaceholder.typicode.com/users/6').returns(mock_response('200', 'invalid json'))
    JsonplaceholderService.expects(:log).at_least_once
    result = JsonplaceholderService.fetch_user(6)
    assert_nil result
    assert_nil Rails.cache.read('jsonplaceholder_user_6')
  end

  def test_fetch_user_used_in_event_detail_user_assignment
    # Mock Event and interaction
    event = mock
    event.stubs(:assigned_users).returns([1,2])
    HTTParty.stubs(:get).with('https://jsonplaceholder.typicode.com/users/1').returns(mock_response('200', {id:1,name:"U1"}.to_json))
    HTTParty.stubs(:get).with('https://jsonplaceholder.typicode.com/users/2').returns(mock_response('200', {id:2,name:"U2"}.to_json))
    users = event.assigned_users.map{ |id| JsonplaceholderService.fetch_user(id) }
    assert_equal [ {'id'=>1,'name'=>'U1'}, {'id'=>2,'name'=>'U2'} ], users
  end

  def test_fetch_user_missing_user_in_event_detail
    event = mock
    event.stubs(:assigned_users).returns([1,999])
    HTTParty.stubs(:get).with('https://jsonplaceholder.typicode.com/users/1').returns(mock_response('200', {id:1,name:"U1"}.to_json))
    HTTParty.stubs(:get).with('https://jsonplaceholder.typicode.com/users/999').returns(mock_response('404', '{}'))
    users = event.assigned_users.map{ |id| JsonplaceholderService.fetch_user(id) }
    assert_equal [ {'id'=>1,'name'=>'U1'}, nil ], users
  end

  def test_fetch_user_does_not_modify_external_user_list
    HTTParty.expects(:post).never
    HTTParty.expects(:put).never
    HTTParty.expects(:patch).never
    HTTParty.expects(:delete).never
    HTTParty.stubs(:get).with('https://jsonplaceholder.typicode.com/users/1').returns(mock_response('404','{}'))
    JsonplaceholderService.fetch_user(1)
  end

  def test_fetch_user_null_response_body
    HTTParty.stubs(:get).with('https://jsonplaceholder.typicode.com/users/7').returns(mock_response('200', nil))
    result = JsonplaceholderService.fetch_user(7)
    assert_nil result
    assert_nil Rails.cache.read('jsonplaceholder_user_7')
  end

  def test_fetch_user_large_user_id_boundary
    HTTParty.stubs(:get).with('https://jsonplaceholder.typicode.com/users/999999').returns(mock_response('404', '{}'))
    result = JsonplaceholderService.fetch_user(999999)
    assert_nil result
  end

  def test_fetch_user_cache_entry_explicit_nil
    Rails.cache.write('jsonplaceholder_user_8', nil)
    user_json = { 'id' => 8, 'name' => 'User Eight' }.to_json
    HTTParty.stubs(:get).with('https://jsonplaceholder.typicode.com/users/8').returns(mock_response('200', user_json))
    result = JsonplaceholderService.fetch_user(8)
    assert_equal({'id'=>8,'name'=>'User Eight'}, result)
    assert_equal({'id'=>8,'name'=>'User Eight'}, Rails.cache.read('jsonplaceholder_user_8'))
  end
end
