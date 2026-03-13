class Event < ApplicationRecord
  validates :title, presence: true
  
  def assigned_user_ids
    value = read_attribute(:assigned_user_ids)
    JSON.parse(value) rescue []
  end
  
  def assigned_user_ids=(value)
    write_attribute(:assigned_user_ids, value.is_a?(Array) ? value.to_json : value)
  end
  
  def assigned_users
    return [] if assigned_user_ids.blank?
    assigned_user_ids.map { |id| JsonplaceholderService.fetch_user(id) }.compact
  end
  
  def assigned_user_count
    assigned_user_ids&.size || 0
  end
end
