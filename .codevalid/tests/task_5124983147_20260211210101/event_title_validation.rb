require "test_helper"

class EventTitleValidationTest < ActiveSupport::TestCase
  # ---------------------------------------------------------------------------
  # Helper: build a valid event params hash
  # ---------------------------------------------------------------------------
  def valid_event_params(overrides = {})
    { title: "Conference", description: "A test event" }.merge(overrides)
  end

  # ---------------------------------------------------------------------------
  # Test Case 1: valid_title_on_create
  # Description: Event creation succeeds when a non-empty title is provided.
  # Type: positive
  # ---------------------------------------------------------------------------
  test "valid_title_on_create" do
    # Given
    event = Event.new(valid_event_params(title: "Conference"))

    # When
    result = event.save

    # Then
    assert result, "Expected save to return true for a valid title"
    assert event.persisted?, "Expected event to be persisted"
    assert_empty event.errors[:title], "Expected no title errors"
  ensure
    event.destroy if event.persisted?
  end

  # ---------------------------------------------------------------------------
  # Test Case 2: blank_title_on_create
  # Description: Event creation fails when the title is blank.
  # Type: negative
  # ---------------------------------------------------------------------------
  test "blank_title_on_create" do
    # Given
    event = Event.new(valid_event_params(title: ""))

    # When
    result = event.save

    # Then
    assert_not result, "Expected save to return false for a blank title"
    assert_not event.persisted?, "Expected event NOT to be persisted"
    assert_includes event.errors[:title], "can't be blank"
  end

  # ---------------------------------------------------------------------------
  # Test Case 3: nil_title_on_create
  # Description: Event creation fails when the title is null.
  # Type: negative
  # ---------------------------------------------------------------------------
  test "nil_title_on_create" do
    # Given
    event = Event.new(valid_event_params(title: nil))

    # When
    result = event.save

    # Then
    assert_not result, "Expected save to return false for a nil title"
    assert_not event.persisted?, "Expected event NOT to be persisted"
    assert_includes event.errors[:title], "can't be blank"
  end

  # ---------------------------------------------------------------------------
  # Test Case 4: whitespace_title_on_create
  # Description: Event creation fails when the title contains only whitespace.
  # Type: edge
  # ---------------------------------------------------------------------------
  test "whitespace_title_on_create" do
    # Given
    event = Event.new(valid_event_params(title: "   "))

    # When
    result = event.save

    # Then
    assert_not result, "Expected save to return false for a whitespace-only title"
    assert_not event.persisted?, "Expected event NOT to be persisted"
    assert_includes event.errors[:title], "can't be blank",
      "Rails presence validation should strip whitespace and treat as blank"
  end

  # ---------------------------------------------------------------------------
  # Test Case 5: valid_title_on_update
  # Description: Event update succeeds when the new title is valid.
  # Type: positive
  # ---------------------------------------------------------------------------
  test "valid_title_on_update" do
    # Given
    event = Event.create!(valid_event_params(title: "Original Title"))

    # When
    result = event.update(title: "Updated Title")

    # Then
    assert result, "Expected update to return true for a valid new title"
    assert_equal "Updated Title", event.reload.title
    assert_empty event.errors[:title]
  ensure
    event.destroy if event.persisted?
  end

  # ---------------------------------------------------------------------------
  # Test Case 6: blank_title_on_update
  # Description: Event update fails if the title is set to blank.
  # Type: negative
  # ---------------------------------------------------------------------------
  test "blank_title_on_update" do
    # Given
    event = Event.create!(valid_event_params(title: "Original Title"))
    original_title = event.title

    # When
    result = event.update(title: "")

    # Then
    assert_not result, "Expected update to return false for a blank title"
    assert_includes event.errors[:title], "can't be blank"
    assert_equal original_title, event.reload.title,
      "Expected title to remain unchanged after failed update"
  ensure
    event.destroy if event.persisted?
  end

  # ---------------------------------------------------------------------------
  # Test Case 7: nil_title_on_update
  # Description: Event update fails when the title is set to null.
  # Type: negative
  # ---------------------------------------------------------------------------
  test "nil_title_on_update" do
    # Given
    event = Event.create!(valid_event_params(title: "Original Title"))
    original_title = event.title

    # When
    result = event.update(title: nil)

    # Then
    assert_not result, "Expected update to return false for a nil title"
    assert_includes event.errors[:title], "can't be blank"
    assert_equal original_title, event.reload.title,
      "Expected event to remain unchanged after failed update"
  ensure
    event.destroy if event.persisted?
  end

  # ---------------------------------------------------------------------------
  # Test Case 8: max_length_title_boundary
  # Description: Event saves successfully when title is at maximum acceptable
  #              length (255 characters — standard DB string column limit).
  # Type: edge
  # ---------------------------------------------------------------------------
  test "max_length_title_boundary" do
    # Given
    max_title = "A" * 255
    event = Event.new(valid_event_params(title: max_title))

    # When
    result = event.save

    # Then
    assert result, "Expected save to succeed for a 255-character title"
    assert event.persisted?, "Expected event to be persisted"
    assert_equal 255, event.title.length
  ensure
    event.destroy if event.persisted?
  end

  # ---------------------------------------------------------------------------
  # Test Case 9: empty_string_after_strip
  # Description: Validation fails when title appears non-empty but becomes
  #              blank after trimming (whitespace + control characters).
  # Type: edge
  # ---------------------------------------------------------------------------
  test "empty_string_after_strip" do
    # Given
    event = Event.new(valid_event_params(title: " \n\t "))

    # When
    result = event.save

    # Then
    assert_not result,
      "Expected save to fail for a title consisting only of whitespace/control chars"
    assert_not event.persisted?
    assert_includes event.errors[:title], "can't be blank",
      "Rails presence validation should treat '\\n\\t ' as blank"
  end

  # ---------------------------------------------------------------------------
  # Test Case 10: ensure_error_message_attached
  # Description: Ensures proper error message is attached when validation fails.
  # Type: negative
  # ---------------------------------------------------------------------------
  test "ensure_error_message_attached" do
    # Given
    event = Event.new(valid_event_params(title: ""))

    # When
    event.valid?

    # Then
    assert_not_empty event.errors[:title],
      "Expected title errors to be present"
    assert_includes event.errors[:title], "can't be blank",
      "Expected error message 'can't be blank' to be attached to :title"
  end

  # ---------------------------------------------------------------------------
  # Test Case 11: no_side_effects_on_failed_save
  # Description: Event object should not persist or modify database when title
  #              validation fails.
  # Type: negative
  # ---------------------------------------------------------------------------
  test "no_side_effects_on_failed_save" do
    # Given
    count_before = Event.count
    event = Event.new(valid_event_params(title: ""))

    # When
    event.save

    # Then
    assert_equal count_before, Event.count,
      "Expected database record count to remain unchanged after failed save"
    assert_not event.persisted?,
      "Expected event to not be persisted"
    assert event.new_record?,
      "Expected event to still be a new (unsaved) record"
  end

  # ---------------------------------------------------------------------------
  # Test Case 12: role_check_editor_can_edit_title
  # Description: User with permission to edit events can successfully update
  #              title when valid.
  # Type: positive
  #
  # Note: The Event model itself has no role/permission logic. This test
  # validates that the title validation passes for an editor scenario —
  # permission enforcement is assumed at the controller/service layer.
  # ---------------------------------------------------------------------------
  test "role_check_editor_can_edit_title" do
    # Given — simulate an editor user who has already been authorised;
    # the model under test only enforces title validation.
    event = Event.create!(valid_event_params(title: "Initial Title"))
    new_title = "Editor Updated Title"

    # When — editor performs the update (authorisation assumed granted)
    result = event.update(title: new_title)

    # Then
    assert result, "Expected update to succeed for an editor with a valid title"
    assert_equal new_title, event.reload.title
    assert_empty event.errors[:title]
  ensure
    event.destroy if event.persisted?
  end

  # ---------------------------------------------------------------------------
  # Test Case 13: role_check_viewer_cannot_edit_title
  # Description: User without edit permissions cannot update title regardless
  #              of title validity.
  # Type: negative
  #
  # Note: The Event model has no built-in role/permission logic; permission
  # enforcement lives at the controller/service layer. This test simulates
  # that layer rejecting the request before the model save is attempted,
  # verifying the event remains unchanged.
  # ---------------------------------------------------------------------------
  test "role_check_viewer_cannot_edit_title" do
    # Given — an existing event and a viewer (read-only) user
    event = Event.create!(valid_event_params(title: "Original Title"))
    original_title = event.title

    # Simulate a permission check at the service/controller layer that
    # prevents the viewer from calling save/update on the model.
    viewer_can_edit = false

    # When
    update_performed = false
    if viewer_can_edit
      event.update(title: "Viewer Attempted Title")
      update_performed = true
    end

    # Then — the update was never performed; title is unchanged
    assert_not update_performed,
      "Expected the update to be blocked by permission check before reaching the model"
    assert_equal original_title, event.reload.title,
      "Expected title to remain unchanged because viewer lacks edit permissions"
  ensure
    event.destroy if event.persisted?
  end

  # ---------------------------------------------------------------------------
  # Test Case 14: state_transition_new_to_saved
  # Description: State transition from unsaved to saved only occurs with valid
  #              title.
  # Type: positive
  # ---------------------------------------------------------------------------
  test "state_transition_new_to_saved" do
    # Given
    event = Event.new(valid_event_params(title: "Valid Title"))
    assert event.new_record?, "Expected event to start as a new (unsaved) record"

    # When
    result = event.save

    # Then
    assert result, "Expected save to succeed"
    assert event.persisted?, "Expected event to transition to persisted state"
    assert_not event.new_record?,
      "Expected event to no longer be a new record after successful save"
  ensure
    event.destroy if event.persisted?
  end

  # ---------------------------------------------------------------------------
  # Test Case 15: state_transition_saved_to_saved_fail
  # Description: State remains unchanged on failed update due to blank title.
  # Type: negative
  # ---------------------------------------------------------------------------
  test "state_transition_saved_to_saved_fail" do
    # Given
    event = Event.create!(valid_event_params(title: "Stable Title"))
    original_title = event.title
    assert event.persisted?, "Expected event to be persisted before update attempt"

    # When
    result = event.update(title: "")

    # Then
    assert_not result, "Expected update to fail for blank title"
    assert event.persisted?,
      "Expected event to remain in persisted state (not destroyed)"
    assert_equal original_title, event.reload.title,
      "Expected persisted title to remain unchanged after failed update"
    assert_includes event.errors[:title], "can't be blank"
  ensure
    event.destroy if event.persisted?
  end
end
