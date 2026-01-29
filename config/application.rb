require_relative "boot"

require "rails/all"

Bundler.require(*Rails.groups)

module EventManager
  class Application < Rails::Application
    config.load_defaults 7.1
    config.generators.system_tests = nil
  end
end
