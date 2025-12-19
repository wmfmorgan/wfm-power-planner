Issue List

- **Issue #1: Violation of Tenet #34 - New Tailwind Classes in Templates**

  Multiple templates (e.g., templates/shared/event_modal.html, templates/shared/goal_modal.html, templates/shared/task_modal.html) contain new Tailwind classes like `flex`, `flex-col`, `grid-cols-1`, `md:grid-cols-2`, `gap-4`, `bg-dark`, `border-4`, `border-yellow-400`, etc. Tenet #34 bans all new Tailwind classes; all new styling must use pure semantic CSS in main.css. Replace with semantic classes like `.flex`, `.gap-4`, `.bg-dark`, etc., defined in main.css.

- **Issue #2: Inline Event Handlers in Templates Violate Tenet #1**

  Templates like templates/calendar/day.html have `data-action="toggle-calendar"` with implied JS handling, but actual onclick/onchange are absent. However, in templates/shared/kanban.html and others, no direct inline JS, but ensure all events are delegated in JS files. Confirm no `onclick` etc. slipped in; if any, move to delegated listeners in goal_manager.js or similar.

- **Issue #3: Potential Bug in ICS Parsing - Timezone Handling Inconsistent**

  In app/calendar_routes.py, `_parse_dt` function mixes pytz and dateutil.tz, with hardcoded "America/Chicago". This violates Tenet #3 (single source of truth) and may cause timezone errors for users outside Central. Use browser local time or configurable TZ; test with non-US events.

- **Issue #4: Design Choice - No Error Handling in JS Fetch Calls**

  In files like static/js/goal_manager.js, static/js/tasks_day.js, etc., fetch() calls lack .catch() for network errors, leading to silent failures. Violates Tenet #15 (championship code); add proper error handling with user alerts and logging.

- **Issue #5: Cleanliness - Duplicate Code in Render Functions**

  In static/js/tasks_day.js and static/js/tasks_global.js, `createTaskCard` functions are nearly identical. Violates Tenet #13 (refactor hurts maintainability); extract to shared utility in kanban_core.js.

- **Issue #6: Bug - Recurrence Type Not Properly Handled in Task Create STATUS: DONE**  

  In app/services/task_service.py, `recurrence_type=TaskRecurrenceType[recurrence_type.upper()].value` assumes uppercase input, but frontend sends lowercase. May cause KeyError; normalize input or use .get().

- **Issue #7: Violation of Tenet #21 - Enums Not Fully Mirrored in JS**

  In static/js/constants.js, TASK_PRIORITY and TASK_RECURRENCE_TYPE missing; only GOAL enums present. Tenet #21 requires mirroring in constants.js for single source; add them to prevent drift.

- **Issue #8: Design Choice - Full Page Reloads on Updates**

  Multiple JS files (e.g., goal_manager.js, task_modal.js) use location.reload() after API calls. Violates Tenet #11 (offline-first) potential; refactor to dynamic refresh for better UX and offline support.

- **Issue #9: Cleanliness - Unused Code in Models**

  In app/models/task.py, fields like `is_habit`, `current_streak` are defined but not used in routes/services. Phase 3.3 backlog, but remove or comment as TODO to avoid bloat (Tenet #13).

- **Issue #10: Potential Bug - ltree Path in Import/Export STATUS: DONE**

  In app/services/goal_service.py, export serializes path as str, but import rebuilds using new IDs. Test deeply for deep hierarchies; may fail on >5 levels (Tenet #16). Add validation.

- **Issue #11: Monolithic ICS Parsing Logic in calendar_routes.py**

  The `_parse_dt` and full ICS parsing/processing code (lines 50-200+) in `app/calendar_routes.py` is a large block embedded in the route handler. This violates code cleanliness and maintainability (Tenet #13). Extract the parsing logic into a dedicated helper file like `app/helpers/ics_parser.py` or move to `calendar_service.py` for better separation of concerns.

- **Issue #12: Export/Import Endpoints in goals_routes.py Should Move to Dedicated Service STATUS: DONE**
  
  The `/api/export` and `/api/import` routes in `app/goals_routes.py` handle data serialization and DB operations directly. This mixes routing with business logic. Relocate the core export/import functions to `app/services/data_service.py` (new file) to enforce Tenet #17 (all DB writes through service layer) and reduce route file size.

- **Issue #13: goal_manager.js Handles Too Many Concerns (Tree, Modal, Calendar Kanban)**

  `static/js/goal_manager.js` (300+ lines) manages goal tree delegation, modal population/saving, period goal fetching/rendering, and sortable init. This is monolithic. Break into: `goal_tree.js` for tree-specific (toggle, expand, inline edits), `goal_modal.js` for shared modal logic, `period_goals.js` for calendar kanban. Update base.html and other templates to load the specific modules.

- **Issue #14: Inconsistent File Naming in static/js/lib**

  `static/js/lib/sortable.min.js` uses "lib" subfolder, but it's the only file there. For consistency with other JS files in static/js/, rename to `static/js/sortable.min.js` and update all imports (e.g., in base.html).

- **Issue #15: templates/shared/kanban.html Assumes kanban_id and kanban_statuses Context**

  The shared Kanban template relies on `kanban_id`, `kanban_statuses`, `kanban_type` being passed via {% with %}. This is fine but not documented. Add a comment block at the top of the file explaining required context variables for better maintainability when reused.

- **Issue #16: app/date_utils.py Contains Multiple Unrelated Functions**

  `app/date_utils.py` has `get_iso_week_for_goal`, `get_iso_year_for_goal`, `get_sunday_of_week`, `get_first_of_month`. The ISO week/year functions are specific to goal timeframes, while sunday/first are calendar general. Split into `app/goal_utils.py` for goal-specific and keep calendar ones here.

- **Issue #17: Large __init__.py with Template Filters and Context Processors**

  `app/__init__.py` has grown with many template filters (`date_format`, `month_name`, `days_in_month`, `iso_week`, `first_day_weekday`) and context processors. This makes the app factory file bloated. Extract to new `app/template_utils.py` and import/register in __init__.py.

- **Issue #18: services/__init__.py is Empty – Remove or Use for Exports**

  `app/services/__init__.py` is blank. Either remove if unnecessary or use to export all services (`from .goal_service import *` etc.) for cleaner imports in routes.

- **Issue #19: models/task.py Has Unused Habit/Streak Fields**

  Fields like `is_habit`, `current_streak`, etc., in `app/models/task.py` are defined but not used in any routes/services/templates. This adds unnecessary schema bloat. Comment them as "Phase 4: Habit Streaks" or remove until implemented.

- **Issue #20: Duplicate Render Functions in JS Files**

  `createTaskCard` in `static/js/tasks_day.js` and `static/js/tasks_global.js` are identical. Extract to shared `static/js/task_utils.js` and import in both for DRY (Tenet #13).