require 'net/http'
require 'json'
require 'uri'

class JsonplaceholderService
  BASE_URL = 'https://jsonplaceholder.typicode.com'
  
  CACHE_DURATION = 5.minutes
  
  class << self
    def fetch_users
      Rails.cache.fetch('jsonplaceholder_users', expires_in: CACHE_DURATION) do
        uri = URI("#{BASE_URL}/users")
        response = Net::HTTP.get_response(uri)
        if response.code == '200'
          JSON.parse(response.body)
        else
          []
        end
      rescue => e
        Rails.logger.error("Error fetching users from JSONPlaceholder: #{e.message}")
        []
      end
    end
    
    def fetch_user(user_id)
      Rails.cache.fetch("jsonplaceholder_user_#{user_id}", expires_in: CACHE_DURATION) do
        uri = URI("#{BASE_URL}/users/#{user_id}")
        response = Net::HTTP.get_response(uri)
        if response.code == '200'
          JSON.parse(response.body)
        else
          nil
        end
      rescue => e
        Rails.logger.error("Error fetching user #{user_id} from JSONPlaceholder: #{e.message}")
        nil
      end
    end
  end
end
