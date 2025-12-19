# WFM Power Planner Technical Reference Document

**Document Version:** 1.0 (Generated on December 19, 2025)  
**Authors:** Grok 4 (xAI) in collaboration with the original developer  
**Purpose:** This document serves as a comprehensive reference for maintaining, extending, or debugging the WFM Power Planner application. It assumes familiarity with Python, Flask, SQLAlchemy, PostgreSQL, and vanilla JavaScript. Always review the Sacred Tenets (Section 4) before making changes to avoid architectural drift. Championship-level comments highlight key gotchas.

## 1. Project Overview

### Mission Statement
WFM Power Planner is a private, offline-first, power-charged operating system for warriors who refuse to lose, enabling total life domination through hierarchical goals, calendar command, task supremacy, and daily reflections.

### Core Functionality Summary
- **Hierarchical Goals:** Notion-style recursive tree with ltree-based hierarchy, timeframe inheritance (yearly → quarterly → monthly → weekly → daily), Kanban status columns (backlog → todo → doing → blocked → done → cancelled), category coloring, progress rollups from leaves, inline editing, and habit flags.
- **Calendar Command Center:** Year/quarter/month/week/day views with Sunday-first grids, ICS import (manual sync on day view), manual events with Google-style floating blocks and overlap handling, reflection zones (prep/wins/improve/notes) autosaved per horizon.
- **Tasks Supremacy:** Separate ad-hoc task system with global backlog page, day-specific Kanban on calendar, priority borders (low/medium/high/critical), tags, due dates, recurring tasks (daily/weekly/monthly with instances), and drag-and-drop status updates.
- **Reflections:** Four zones tied to daily/weekly/monthly horizons, keyed by date (Sunday for weekly, 1st for monthly), autosave on blur with victory glow.
- **Events:** ICS-imported (Outlook UID dedup) and manual events on day grid, timezone-aware, recurrence support, edit/delete via modal.
- **Export/Import:** Full JSON universe backup (goals tree, tasks, reflections, events), wipe + restore with hierarchy reconstruction — data ownership sacred.

### Key Principles
- **Offline-First:** PWA with service worker caching static assets, IndexedDB fallback planned for data; app installable and functional in airplane mode (Tenet #11).
- **No Build Step:** Vanilla JS + hand-rolled CSS + Jinja templates — eternal in 2035 without npm/Webpack (Tenet #10).
- **Data Ownership:** Full export/import round-trip preserves everything; no external auth, session-based (Tenet #12).
- **Eternal Compatibility:** Design for 10-year no-maintenance run; no frameworks, semantic CSS, enums mandatory (Tenet #14).

// Championship Comment: Brother, this app is built like Hulk Hogan in his prime — unbreakable, jacked, and ready to dominate without excuses. Change anything without the tenets, and you'll feel the big boot!

## 2. High-Level Architecture

### Diagram Description
The architecture is a classic Flask backend with PostgreSQL, fronted by vanilla JS for dynamic UI. Here's a text-based Mermaid diagram:

```
graph TD
  A[User Browser] -->|Vanilla JS + Jinja| B[Flask App Factory]
  B -->|Blueprints| C[Auth Routes]
  B -->|API Routes| D[Goal/Task Services]
  D -->|SQLAlchemy| E[PostgreSQL + ltree Enums]
  E -->|Goal Tree Queries| F[Kanban Progress Rollups]
  A -->|SortableJS Drag| G[IndexedDB Offline Cache]
  G -->|Fallback| E
  A -->|PWA Service Worker| H[Full JSON Export/Import]
```

- Backend: Flask handles routing, services encapsulate business logic and DB writes.
- Database: PostgreSQL with ltree for goal hierarchy, enums for status/category/timeframe.
- Frontend: Jinja renders initial HTML, vanilla JS modules handle interactivity (e.g., modals, drag-and-drop via SortableJS).
- Offline: Service worker caches static assets, fallback to offline.html; data fallback not fully implemented yet.

### Tech Stack & Versions (December 2025)
| Layer       | Technology          | Version / Note                               |
|-------------|---------------------|----------------------------------------------|
| Backend     | Python              | 3.12+                                        |
| Framework   | Flask               | 3.0+ (app factory, blueprints)               |
| Database    | PostgreSQL          | 16+ (local + Render)                         |
| ORM         | SQLAlchemy          | 2.0+ (declarative)                           |
| Migrations  | Alembic             | Integrated via Flask-Migrate                 |
| Frontend    | Vanilla JS + Jinja2 | No frameworks, no build step                 |
| Styling     | Pure CSS            | main.css + legacy tailwind.min.css (frozen)  |
| Auth        | Flask-Login + bcrypt| Session-based, no OAuth                      |
| Deployment  | Render.com          | Free tier; paid for production               |
| PWA/Offline | Service Worker      | Caches assets; IndexedDB fallback planned    |
| Drag-Drop   | SortableJS          | 1.x (11KB minified, static/js/lib/)          |

// Championship Comment: This stack is lean like the Macho Man — no bloat, no weakness. Add anything new? Check Tenet #31 first, or you'll tap out to complexity!

## 3. Key Design Decisions & Rationale

| Decision                       | Choice                          | Reason                                                                 | Tenet Reference |
|--------------------------------|---------------------------------|------------------------------------------------------------------------|-----------------|
| Framework                      | Flask over FastAPI/Django       | Simpler dev loop, no async pressure, Render compatibility              | #31             |
| ORM                            | SQLAlchemy over raw SQL         | Recursive relationships for goals; CTEs for trees                      | #31             |
| Frontend                       | Vanilla JS + Jinja over React/Vue | Eternal in 2035 without build tools; offline-first                     | #10, #11, #14   |
| Database                       | PostgreSQL over SQLite          | ltree for hierarchy, recursive queries, free on Render                 | #16             |
| Authentication                 | Session-based, no OAuth         | Private fortress; own the keys                                         | #22, #23        |
| Goal Hierarchy                 | ltree + GIST index              | O(1) subtree queries/moves; progress rollups                           | #16, #21        |
| Kanban Columns                 | Enum-driven, fixed 5 (exclude backlog on calendar) | Simplicity; DB schema solid                                            | #3, #21        |
| Drag-and-Drop                  | SortableJS only                 | Smooth, no build step, 11KB minified                                   | #30             |
| Progress Calculation           | Leaf-node count rollup          | Fast, fair; weighted later if needed                                   | #8              |
| Time-Zone Handling             | UTC storage, browser local display | Global warrior-proof                                                   | N/A             |
| Daily Grid                     | Fixed 38 rows (5AM-10:30PM)     | Consistent on all screens; no config                                   | #7              |
| First-Run                      | Auto-create 'hulkster' user     | Pure speed; single warrior mode                                        | #24             |
| Dark Mode                      | Default, localStorage toggle    | Respect the darkness; light mode for weaklings                         | #27             |
| Mobile Nav                     | Hamburger menu                  | Stay hungry; classic power move                                        | #28             |
| Cross-Tab Sync                 | BroadcastChannel (future)       | Real-time freshness across tabs                                        | #29             |
| JS Architecture                | Modular files                   | Maintainability; no monolith                                           | #1, #15        |
| Template Org                   | Shared partials + view folders  | DRY; reusable modals/kanban                                            | #7              |
| Reflection Notes               | Dedicated model/service         | Autosave per horizon; Tenet #17 obeyed                                 | #8, #17, #21   |

// Championship Comment: These decisions are etched in steel like the Warrior's facepaint — change one without rationale, and the empire taps out. Always ask: Will this still dominate in 2035?

## 4. The Sacred Tenets

The 35+ Sacred Tenets are the unbreakable laws of the empire. Violate them, and Hulkamania will leg-drop your PR. Critical ones (bolded) are gatekeepers for changes.

1. No inline JS – All JavaScript in static/js/, modular.
2. No inline CSS – All styles in static/css/.
3. **One source of truth for strings & magic values** – Enums/constants mirrored Python/JS.
4. All user input through JSON API – Forms become fetch().
5. State-changing endpoints return JSON – No HTML snippets.
6. Zero global variables in JS – Scoped modules.
7. Templates are dumb – Jinja loops/conditionals only; no logic.
8. Database writes in one place – Services/repository.
9. All flash messages from backend – No client alerts for errors.
10. No external build step – No Webpack/npm.
11. **Every new feature works offline-first** – PWA from day one.
12. Data ownership sacred – Export/import always perfect.
13. If it hurts maintainability, refactor before merge – No copy-paste.
14. Hulkamania runs eternal – Works in 10 years without updates.
15. Comments championship-caliber – Explain ownership, flow, gotchas.
16. Recursive hierarchy via ltree – Own the tree.
17. **All DB writes through service layer** – Routes parse, services save.
18. Frontend state from API – Re-fetch always.
19. Kanban state in DB – Persisted drags.
20. Export/Import single truth – One endpoint dumps/restores.
21. **Enums mandatory for fixed values** – No text strings in DB.
22. Auth session-based, no external – Own the keys.
23. Passwords bcrypt only – Salted eternally.
24. One user per install (single warrior) – Focus.
25. Multi-device sync API key (future) – No extra passwords.
26. All routes except login/register @login_required – Fortress.
27. Dark mode default – Toggle in localStorage.
28. Mobile hamburger top-left – Stay hungry.
29. Cross-tab sync mandatory (future) – BroadcastChannel.
30. SortableJS only third-party JS – 11KB eternal.
31. **Simplest battle-tested tool – NO EXCEPTIONS** – Official extensions first.
32. PyEnum banned – Native SQLAlchemy Enum only.
33. Tailwind banned for new code – Legacy frozen.
34. Semantic eternal styling – Meaningful classes only.
35. Future styling semantic – No utilities.
36. Tests eternal – Coverage runs wild; rollback fixtures.

**Critical Tenets for Changes:**  
- **#3, #21:** Always use enums/constants — no magic strings.  
- **#11:** Offline works or don't ship.  
- **#17:** DB writes ONLY in services.  
- **#31:** No raw/reinvented — use official if it fits.  

// Championship Comment: These tenets are the Hulkster's 24-inch pythons — break one, and the empire feels the big boot. Always verify against them before any PR, brother!

## 5. Database Schema

All models in `app/models/`. PostgreSQL native enums for fixed values. ltree for goals hierarchy with GIST index. Cascade deletes on goals/children.  

**User Model (users table):**  
- id: SERIAL PRIMARY KEY  
- username: STRING(80) UNIQUE NOT NULL  
- password_hash: STRING(128) NOT NULL  
- created_at: TIMESTAMP DEFAULT now()  

**Goal Model (goals table):**  
- id: SERIAL PRIMARY KEY  
- user_id: INTEGER FK(user.id) NOT NULL INDEX  
- title: TEXT NOT NULL  
- description: TEXT  
- category: ENUM(goalcategory: marital, social, financial, work, family, spiritual, health, hobby) DEFAULT 'work'  
- timeframe: ENUM(goaltimeframe: yearly, quarterly, monthly, weekly, daily) DEFAULT 'monthly'  
- due_date: DATE  
- is_habit: BOOLEAN DEFAULT FALSE  
- completed_at: TIMESTAMP  
- parent_id: INTEGER FK(goals.id) ON DELETE CASCADE  
- path: LTREE NOT NULL GIST INDEX  
- status: ENUM(goalstatus: backlog, todo, doing, blocked, done, cancelled) DEFAULT 'todo'  
- sort_order: INTEGER DEFAULT 0  
- created_at: TIMESTAMP DEFAULT now()  
- updated_at: TIMESTAMP DEFAULT now() ON UPDATE now()  

Relationships: children (self-ref, lazy='joined', cascade all/delete-orphan).  

**Task Model (tasks table):**  
- id: SERIAL PRIMARY KEY  
- user_id: INTEGER FK(user.id) NOT NULL INDEX  
- title: TEXT NOT NULL  
- description: TEXT  
- due_date: DATE  
- priority: ENUM(taskpriority: low, medium, high, critical) DEFAULT 'medium'  
- tags: TEXT  
- status: ENUM(taskstatus: backlog, todo, doing, blocked, done) DEFAULT 'backlog'  
- sort_order: INTEGER DEFAULT 0  
- day_date: DATE  
- created_at: TIMESTAMP DEFAULT now()  
- updated_at: TIMESTAMP DEFAULT now() ON UPDATE now()  
- is_recurring: BOOLEAN DEFAULT FALSE  
- recurrence_type: ENUM(taskrecurrencetype: daily, weekly, monthly)  
- recurrence_interval: INTEGER DEFAULT 1  
- recurrence_end_date: DATE  
- parent_task_id: INTEGER FK(tasks.id)  
- is_instance: BOOLEAN DEFAULT FALSE  
- original_due_date: DATE  
- is_habit: BOOLEAN DEFAULT FALSE  
- current_streak: INTEGER DEFAULT 0  
- longest_streak: INTEGER DEFAULT 0  
- last_completed_date: DATE  
- total_completions: INTEGER DEFAULT 0  

**CalendarEvent Model (calendar_events table):**  
- id: SERIAL PRIMARY KEY  
- user_id: INTEGER FK(user.id) NOT NULL INDEX  
- uid: STRING(255) NOT NULL UNIQUE INDEX  
- title: STRING(200) NOT NULL  
- description: TEXT  
- start_datetime: TIMESTAMP(timezone) NOT NULL INDEX  
- end_datetime: TIMESTAMP(timezone)  
- all_day: BOOLEAN DEFAULT FALSE  
- is_recurring: BOOLEAN DEFAULT FALSE  
- recurrence_rule: TEXT  
- recurrence_id: TIMESTAMP(timezone)  
- location: STRING(200)  
- source: STRING(50) DEFAULT 'outlook_ics'  
- created_at: TIMESTAMP(timezone) DEFAULT utcnow()  
- updated_at: TIMESTAMP(timezone) DEFAULT utcnow() ON UPDATE utcnow()  

**ReflectionNote Model (reflection_notes table):**  
Composite PK: (user_id, note_type, timeframe, date)  
- user_id: INTEGER FK(user.id) PK  
- note_type: ENUM(notetype: prep, wins, improve, notes) PK  
- timeframe: ENUM(reflectiontimeframe: daily, weekly, monthly) PK  
- date: DATE PK  
- content: TEXT DEFAULT ''  

// Championship Comment: This schema is etched in stone like Ric Flair's Figure-Four — enums prevent typos, ltree owns the hierarchy, cascades nuke subtrees clean. Change a field? Migrate with Alembic and pray to Tenet #21!

## 6. Important Services & Business Logic

All DB writes funnel through `services/` — no direct session access in routes (Tenet #17).  

**Goal Creation (`goal_service.create_goal`):**  
- Defaults: backlog status, work category, monthly timeframe.  
- Inheritance: Subgoals inherit category from parent; timeframe cascades (yearly → quarterly, etc.).  
- Depth limit: Max 5 levels — raises ValueError if exceeded.  
- ltree path: Built post-flush for ID; parent.path + child.id.  

**Timeframe Hierarchy & Filtering (`goals_routes.api_goals_from_date`):**  
- Maps view to enum (day=daily, week=weekly, month=monthly).  
- Daily: Filter by exact due_date.  
- Weekly: ISO week calculation (Sunday-first, custom get_iso_week_for_goal).  
- Monthly/Quarterly/Yearly: Extract year/month from due_date.  
- No backlog on calendar — execution focus.  

**Export/Import (`data_service.export_all / import_all`):**  
- Export: JSON with nested goal tree (serialize_goal recursive), flat tasks/reflections/events.  
- Import: Wipe all, recursive import_goal with path rebuild, upsert reflections/events.  
- Round-trip preserves IDs via new creation — hierarchy survives nuke.  

**Reflection Notes Keying (`reflection_service.upsert_note / get_all_for_period`):**  
- Composite PK: user_id + note_type + timeframe + date.  
- Date keying: Daily=exact date; Weekly=Sunday of week; Monthly=1st of month.  
- Autosave on blur via JS (reflection_zones.js).  

**Calendar Event Handling (`calendar_service.import_ics_events / create_manual_event`):**  
- ICS import: Parse RRULE, exceptions, timezones; upsert by UID to avoid dupes.  
- Manual: 30-min slots, overlap stacking (long left, overlaps right, newest far right).  
- Grid: 38 fixed rows, hover time labels, pure CSS positioning.  

// Championship Comment: These services are the Warrior's warpaint — touch 'em without understanding inheritance or keys, and you'll tap out to a cycle or dupe. Always test export/import after changes!

## 7. Frontend Architecture

**Shared Components:**  
- Modals: goal_modal.html, task_modal.html, event_modal.html — fixed-height, scrollable, unified save/cancel/delete.  
- Kanban: kanban.html — enum-driven columns, reusable for goals/tasks (different IDs/groups).  

**Page-Specific Behavior:**  
- **Goals Page (/goals):** Notion-style recursive tree (render_goal macro), inline edits (change/blur events), collapse-all button, localStorage expanded state, Ctrl+Click subtree toggle.  
- **Calendar Pages:** Period goals kanban (filtered by timeframe), normal on month/week (below grid), reordered on day (above tasks via block override).  
- **Day Execution:** Time grid (38 slots, collapsible), manual events (slot click → modal), tasks kanban (no backlog), floating + button.  

**JS Module Breakdown & Responsibilities:**  
- constants.js: Single source enums/colors (mirrored from Python).  
- goal_manager.js: Tree delegation (toggle/delete/add/inline), shared modal (open/save/populate), calendar period goals (fetch/render/sortable).  
- kanban_core.js: Shared SortableJS init + moveTask API.  
- tasks_day.js: Day tasks fetch/render.  
- tasks_global.js: Global tasks fetch/render.  
- task_modal.js: Shared task modal CRUD (collect/save/edit/delete).  
- calendar_events.js: Event rendering (overlap/long stacking), modal (populate/save/delete), time options.  
- calendar_nav.js: Nav buttons, history pushState, today snap.  
- reflection_zones.js: Zones load/save on blur with glow.  
- import_export.js: File upload for import.  
- user_menu.js: Hamburger toggle.  
- sw-register.js: PWA service worker reg.  

**Offline/PWA Strategy:**  
- Service worker (sw.js) caches static assets, falls back to offline.html.  
- Manifest.json for installable app.  
- IndexedDB fallback not implemented yet — app loads offline but data sync pending (roadmap).  

// Championship Comment: Frontend is pure vanilla protein like the Macho Man's slim jims — modular, no globals, delegated events. Add JS? Split to new module, no inline. Break offline? The Hulkster will leg-drop your commit!

## 8. Testing Strategy

**Current Coverage:**  
- Unit tests for auth, goals/tasks/reflections/calendar APIs, edge cases (hierarchy depth, invalid inputs, round-trip export/import).  
- Uses pytest + Flask test client.  
- Real local Postgres (no SQLite); transaction rollback fixtures for clean DB.  

**How to Run Tests:**  
- Activate venv: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Unix).  
- Run: `pytest` or watch mode `ptw -v` (green before commit).  

**Key Test Files:**  
- test_auth.py: Login/register/logout.  
- test_goals_api.py: CRUD, hierarchy, timeframe.  
- test_tasks_api.py: CRUD, recurrence.  
- test_calendar_events_api.py: Manual event CRUD, ICS import.  
- test_reflection_api.py: Upsert/get per horizon.  
- test_edge_cases.py: Depth limits, invalid enums, cycles.  
- test_full_universe_export_import.py: Round-trip preserves data.  

// Championship Comment: Tests are the Warrior's facepaint — run 'em before every change, or you'll feel the gorilla press slam of regressions!

## 9. Deployment Notes

**Local Setup:**  
- Clone repo.  
- Create venv: `python -m venv venv`.  
- Install deps: `pip install -r requirements.txt`.  
- Env vars: `.env` with SECRET_KEY, ICS_CALENDAR_URL.  
- DB: PostgreSQL local (create wfm_power_planner DB, user hulkster:whc2025!).  
- Migrate: `flask db upgrade`.  
- Run: `flask run` (debug on).  

**Render.com Considerations:**  
- Free tier Postgres + web service.  
- Build: Python, `pip install -r requirements.txt`.  
- Start: `gunicorn run:app` (add gunicorn to requirements.txt).  
- Env vars: SECRET_KEY, DATABASE_URL (from Render Postgres), ICS_CALENDAR_URL.  
- Migrations: Run `flask db upgrade` in build command or manually.  

**Environment Variables:**  
- SECRET_KEY: Flask security.  
- ICS_CALENDAR_URL: Outlook ICS link.  
- SQLALCHEMY_DATABASE_URI: Postgres connection.  

// Championship Comment: Deploy like a Ric Flair strut — env vars secure, migrations first, or the empire taps out to 500 errors!

## 10. Roadmap Status

**Current Phase Complete:**  
- Phase 0–8: Foundation, goals tree/Kanban, calendar views/events, tasks/recurrence, timeframe hierarchy, assignment, multi-warrior, reflections — all shipped ahead of schedule.  

**Remaining Backlog Items:**  
- Cleanup dead code.  
- Remove Tailwind (legacy frozen, but purge fully).  
- Fix scrum import.  
- Require due date on tasks/goals.  
- If all subgoals done, prompt to mark parent done.  
- Phase 9: Custom Kanban columns, weighted progress, goal templates, printable reports, voice-to-goal.  

// Championship Comment: The roadmap is the Hulkster's entrance music — follow it, but always obey the tenets. Next feature? Go slow to go fast, brother!