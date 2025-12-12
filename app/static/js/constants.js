// static/js/constants.js
// ETERNAL SINGLE SOURCE OF TRUTH — TENET #3 DOMINATION

console.log('constants.js LOADED — HULKAMANIA IS ARMED');

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

// FIXED: Keys are lowercase strings — matches DB/API output
const CATEGORY_COLORS = {
  work:       'blue',
  health:     'green',
  family:     'orange',
  financial:  'yellow',
  spiritual:  'indigo',
  social:     'purple',
  marital:    'pink',
  hobby:      'red'
};

const GOAL_TIMEFRAMES = {
  yearly:     'yearly',
  quarterly:  'quarterly',
  monthly:    'monthly',
  weekly:     'weekly',
  daily:      'daily'
};

// Expose globally
Object.assign(window, {
  GOAL_STATUS,
  GOAL_CATEGORY,
  TASK_STATUS,
  GOAL_TIMEFRAMES,
  CATEGORY_COLORS
});


Date.prototype.getWeek = function() {
  const d = new Date(this);
  d.setHours(0,0,0,0);
  d.setDate(d.getDate() + 4 - (d.getDay() || 7));
  const yearStart = new Date(d.getFullYear(),0,1);
  return Math.ceil((((d - yearStart) / 86400000) + 1)/7);
};

// Debug
console.log('CATEGORY_COLORS loaded:', window.CATEGORY_COLORS);