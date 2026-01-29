class EventsController < ApplicationController
  before_action :set_event, only: [:show, :edit, :update, :destroy]
  before_action :fetch_users, only: [:new, :edit, :show]

  def index
    @events = Event.all.order(created_at: :desc)
  end

  def show
  end

  def new
    @event = Event.new
  end

  def edit
  end

  def create
    @event = Event.new(event_params)
    if @event.save
      redirect_to @event, notice: "Event was successfully created."
    else
      fetch_users
      render :new, status: :unprocessable_entity
    end
  end

  def update
    if @event.update(event_params)
      redirect_to @event, notice: "Event was successfully updated."
    else
      fetch_users
      render :edit, status: :unprocessable_entity
    end
  end

  def destroy
    @event.destroy
    redirect_to events_url, notice: "Event was successfully removed."
  end

  private

  def set_event
    @event = Event.find(params[:id])
  end

  def event_params
    permitted = params.require(:event).permit(:title, :description, assigned_user_ids: [])
    # Remove empty strings from assigned_user_ids array and convert to integers
    if permitted[:assigned_user_ids].present?
      permitted[:assigned_user_ids] = permitted[:assigned_user_ids].reject(&:blank?).map(&:to_i)
    else
      permitted[:assigned_user_ids] = []
    end
    permitted
  end
  
  def fetch_users
    @users = JsonplaceholderService.fetch_users
  end
end
