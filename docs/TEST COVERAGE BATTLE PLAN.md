# WFM POWER PLANNER — TEST COVERAGE BATTLE PLAN

> **“Test hard. Code harder. DOMINATE FOREVER.”**  
> The private, offline-first, championship-caliber test suite for warriors who refuse to ship bugs.

Last updated: 2025-12-18

## 1. Victory Criteria
When this plan is complete, every major feature will be proven unbreakable:
- Goal CRUD + hierarchy + timeframe inheritance
- Task CRUD + day filtering + move
- Reflection notes autosave/load per horizon
- Calendar events manual + ICS import (UID dedupe)
- Export/Import round-trip (tree survives nuke)
- Auth + @login_required protection

**GREEN LIGHTS OR BUST.**

## 2. Test Foundation (ALREADY LOCKED IN — GREEN)
- `tests/conftest.py` — session app, function client, authenticated_client (login via route), db_session (full transaction rollback)
- Real local Postgres + ltree — no SQLite weakness
- Rollback eternal — local DB stays clean

## 3. Battle Plan — One Test File At A Time

| Order | Test File                        | Features Proven                                      | Victory Pose When Green |
|-------|----------------------------------|------------------------------------------------------|-------------------------|
| 1     | `test_goals_api.py`              | Goal create → fetch tree → delete                    | ✅ COMPLETE — 2025-12-18 |
| 2     | `test_tasks_api.py`              | Task create (global + day page) → fetch → move status → update → delete | Next target |
| 3     | `test_reflection_api.py`         | POST reflections → GET for daily/weekly/monthly       |                         |
| 4     | `test_calendar_events_api.py`    | Manual event CRUD + ICS import (UID dedupe)           |                         |
| 5     | `test_export_import.py`          | Export → Import → tree + tasks survive nuke           |                         |
| 6     | `test_auth.py`                   | Login/logout + @login_required protection             |                         |
| 7     | `test_edge_cases.py`             | Deep hierarchy, timeframe inheritance, invalid inputs|                         |

## 4. Execution Rules — TENET STYLE
- One file at a time — green before next.
- Use existing fixtures (`authenticated_client`, `db_session`).
- Assert status codes + JSON content.
- Rollback handles cleanup — no manual delete needed (but good for explicitness).
- Add meaningful asserts — e.g., check ltree path rebuilt on import.
- Run `pytest -v` after each — celebrate greens.

## 5. Current Status — 2025-12-18
| Milestone                  | Status       | Notes |
|----------------------------|--------------|-------|
| Test Foundation            | ✅ COMPLETE | Real Postgres, rollback eternal |
| Goal API CRUD              | ✅ COMPLETE | Green light achieved |
| Task API                   | In Progress  | Next beast |
| Total Coverage             | 15%          | Just getting jacked |

**BROTHER — THIS BATTLE PLAN IS SO JACKED IT MAKES THE ROADMAP LOOK LIKE A JOBBER!**

We ship one green test at a time.  
No rush. No weakness. No mercy.

**NEXT MOVE: test_tasks_api.py — FULL TASK DOMINATION**

Drop the word when you're ready, and I'll slam down the next test file like a Macho Man elbow from the top rope!

**WHATCHU GONNA DO WHEN TEST COVERAGE RUNS WILD ON YOU?!**  
**LEEEEEEEEEEEG DROP INCOMING!!!!** 💪🔥🦵✝️