class AddAssignedUserIdsToEvents < ActiveRecord::Migration[7.1]
  def change
    add_column :events, :assigned_user_ids, :text
  end
end
