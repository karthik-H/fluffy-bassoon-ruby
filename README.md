# Event Manager — Ruby on Rails Application

A simple event management application built with Ruby on Rails. It provides a user interface to **add**, **edit**, and **remove** events. Each event has a **title** and **description**.

---

## Prerequisites

Before running this application, ensure you have the following installed:

- **Ruby** 3.1 or newer (`ruby --version`)
- **Bundler** (`gem install bundler` if needed)
- **SQLite3** (used for the database)

---

## How to Run the Application

### 1. Install dependencies

From the project root:

```bash
bundle install
```

If you get permission errors, you can install gems in a user directory:

```bash
bundle install --path vendor/bundle
```

### 2. Create the database and run migrations

Create the SQLite database and apply the events table migration:

```bash
bundle exec rails db:create
bundle exec rails db:migrate
```

Or in one step:

```bash
bundle exec rails db:prepare
```

### 3. (Optional) Seed data

You can add sample events via the Rails console:

```bash
bundle exec rails console
```

Then in the console:

```ruby
Event.create!(title: "Team Meeting", description: "Weekly sync")
Event.create!(title: "Product Launch", description: "Release v2.0")
exit
```

### 4. Start the Rails server

Start the development server (default port 3000):

```bash
bundle exec rails server
```

Or:

```bash
bundle exec rails s
```

To use a different port (e.g. 4000):

```bash
bundle exec rails server -p 4000
```

### 5. Open the application in your browser

Visit:

- **http://localhost:3000**

You should see the Events list. From there you can:

- **Add** a new event: click “Add New Event”, fill in title and description, then submit.
- **Edit** an event: click “Edit” on an event, change the fields, and save.
- **Remove** an event: click “Remove” and confirm.

---

## Project structure (relevant parts)

| Path | Purpose |
|------|--------|
| `app/controllers/events_controller.rb` | CRUD actions for events |
| `app/models/event.rb` | Event model (title, description) |
| `app/views/events/` | Index, show, new, edit, and form partial |
| `config/routes.rb` | Routes (root + `resources :events`) |
| `db/migrate/` | Migration that creates the `events` table |
| `db/schema.rb` | Current database schema |

---

## Troubleshooting

- **“Rails is not installed”**  
  Run `bundle install` in the project root. If Rails still isn’t found, ensure your Ruby version is 3.1+ and run `bundle install` again.

- **Database errors**  
  Run `bundle exec rails db:drop db:create db:migrate` to reset the database (this deletes all data).

- **Port 3000 already in use**  
  Start the server on another port: `bundle exec rails server -p 4000`, then open http://localhost:4000.

- **SQLite3 missing**  
  Install SQLite3 for your OS (e.g. `brew install sqlite3` on macOS).

---

## Running the Playwright integration tests

See **[PLAYWRIGHT_TESTS.md](PLAYWRIGHT_TESTS.md)** for how to run the add-event Playwright integration tests (with server mocking and video recording) and how to view the results.
