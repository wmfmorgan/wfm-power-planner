// static/js/constants.js
// ETERNAL SINGLE SOURCE OF TRUTH — TENET #3 DOMINATION
// NO MODULES. NO BUNDLER. NO WEAKNESS. PURE SCRIPT-TAG HULKAMANIA.

const GOAL_STATUS = {
  BACKLOG: "backlog",
  TODO: "todo",
  DOING: "doing",
  BLOCKED: "blocked",
  DONE: "done",
  CANCELLED: "cancelled"
};

const GOAL_CATEGORY = {
  MARITAL: "marital",
  SOCIAL: "social",
  FINANCIAL: "financial",
  WORK: "work",
  FAMILY: "family",
  SPIRITUAL: "spiritual",
  HEALTH: "health",
  HOBBY: "hobby"
};

const TASK_STATUS = {
  BACKLOG: "backlog",
  TODO: "todo",
  DOING: "doing",
  BLOCKED: "blocked",
  DONE: "done"
};

// CHAMPIONSHIP COLOR MAPPING — USED IN KANBAN CARDS
const CATEGORY_COLORS = {
  [GOAL_CATEGORY.WORK]:       'blue',
  [GOAL_CATEGORY.HEALTH]:     'green',
  [GOAL_CATEGORY.FAMILY]:     'orange',
  [GOAL_CATEGORY.FINANCIAL]: 'yellow',
  [GOAL_CATEGORY.SPIRITUAL]:  'indigo',
  [GOAL_CATEGORY.SOCIAL]:     'purple',
  [GOAL_CATEGORY.MARITAL]:    'pink',
  [GOAL_CATEGORY.HOBBY]:      'red'
};

// Expose to global scope — because we load scripts in order, this is our "module system"
Object.assign(window, {
  GOAL_STATUS,
  GOAL_CATEGORY,
  TASK_STATUS,
  CATEGORY_COLORS
});