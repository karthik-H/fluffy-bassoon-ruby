# This file is auto-generated from the current state of the database. Instead
# of editing this file, please use the migrations feature of Active Record to
# incrementally modify your database, and then regenerate this schema definition.
#
# This file is the source Rails uses to define your schema when running `bin/rails
# db:schema:load`. When creating a new database, `bin/rails db:schema:load` tends to
# be faster and is potentially less error prone than running all of your
# migrations from scratch. Old migrations may fail to apply correctly if those
# migrations use external dependencies or application code.
#
# It's strongly recommended that you check this file into your version control system.

ActiveRecord::Schema[7.2].define(version: 2025_01_29_000001) do
  # These are extensions that must be enabled in order to support this database
  enable_extension "plpgsql"
  enable_extension "vector"

# Could not dump table "breakdown_chunks_v2" because of following StandardError
#   Unknown type 'vector(3072)' for column 'embedding'


  create_table "events", force: :cascade do |t|
    t.string "title", null: false
    t.text "description"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.text "assigned_user_ids"
  end

  create_table "git_files", id: :serial, force: :cascade do |t|
    t.integer "workspace_id", null: false
    t.string "file_path", limit: 1000, null: false
    t.string "file_name", limit: 500, null: false
    t.string "branch", limit: 255, null: false
    t.integer "file_size"
    t.string "file_type", limit: 100
    t.boolean "breakdown_created", null: false
    t.datetime "created_at", precision: nil, default: -> { "now()" }
    t.datetime "updated_at", precision: nil, default: -> { "now()" }
  end

  create_table "jira_configurations", id: :serial, force: :cascade do |t|
    t.integer "workspace_id", null: false
    t.string "jira_url", limit: 500, null: false
    t.string "jira_email", limit: 255, null: false
    t.string "jira_api_token", limit: 500, null: false
    t.string "jira_project_key", limit: 100, null: false
    t.datetime "created_at", precision: nil, default: -> { "now()" }
    t.datetime "updated_at", precision: nil, default: -> { "now()" }
  end

  create_table "jira_issues", id: :serial, force: :cascade do |t|
    t.integer "workspace_id", null: false
    t.string "issue_key", limit: 100, null: false
    t.string "issue_id", limit: 100, null: false
    t.string "issue_type", limit: 100, null: false
    t.string "summary", limit: 500, null: false
    t.text "description"
    t.string "status", limit: 100
    t.string "priority", limit: 50
    t.string "assignee", limit: 255
    t.string "reporter", limit: 255
    t.datetime "created_date", precision: nil
    t.datetime "updated_date", precision: nil
    t.string "resolution", limit: 100
    t.text "labels"
    t.text "components"
    t.text "raw_data"
    t.boolean "breakdown_created", null: false
    t.datetime "created_at", precision: nil, default: -> { "now()" }
    t.datetime "updated_at", precision: nil, default: -> { "now()" }
  end

  create_table "project_files", id: :serial, force: :cascade do |t|
    t.integer "workspace_id", null: false
    t.string "file_name", limit: 500, null: false
    t.string "file_key", limit: 1000, null: false
    t.integer "file_size"
    t.string "file_type", limit: 100
    t.string "s3_url", limit: 1000
    t.boolean "breakdown_created", null: false
    t.datetime "created_at", precision: nil, default: -> { "now()" }
    t.datetime "updated_at", precision: nil, default: -> { "now()" }
  end

  create_table "repo_branch_status", primary_key: ["repo", "branch"], force: :cascade do |t|
    t.string "repo", limit: 500, null: false
    t.string "branch", limit: 255, null: false
    t.string "spec_generation_status", limit: 50
    t.string "test_generation_status", limit: 50
    t.datetime "created_at", precision: nil, default: -> { "now()" }
    t.datetime "updated_at", precision: nil, default: -> { "now()" }
  end

  create_table "user_workspace_mapping", primary_key: ["user_id", "workspace_id"], force: :cascade do |t|
    t.string "user_id", null: false
    t.integer "workspace_id", null: false
  end

  create_table "users", id: :string, force: :cascade do |t|
    t.string "email"
    t.string "first_name"
    t.string "last_name"
    t.string "profile_image_url"
    t.datetime "created_at", precision: nil, default: -> { "now()" }
    t.datetime "updated_at", precision: nil, default: -> { "now()" }

    t.unique_constraint ["email"], name: "users_email_key"
  end

  create_table "workspace_settings", primary_key: "workspace_id", id: :serial, force: :cascade do |t|
    t.boolean "should_trigger_functional_mapping", null: false
    t.datetime "created_at", precision: nil, default: -> { "now()" }
    t.datetime "updated_at", precision: nil, default: -> { "now()" }
    t.boolean "enable_pull_request_review", default: false
  end

  create_table "workspaces", id: :serial, force: :cascade do |t|
    t.string "user_id", null: false
    t.string "installation_id", null: false
    t.string "code"
    t.string "setup_action", null: false
    t.string "name", limit: 255, null: false
    t.text "description"
    t.string "git_url", limit: 500
    t.string "status", limit: 50
    t.datetime "created_at", precision: nil, default: -> { "now()" }
    t.datetime "updated_at", precision: nil, default: -> { "now()" }
    t.string "default_branch", limit: 255, default: "main"
  end
end
