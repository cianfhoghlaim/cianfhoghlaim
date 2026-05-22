import {
  createTodo,
  getTodos,
  updateTodo,
  deleteTodo,
  signup,
  signin,
  me,
  health,
  info,
} from "./procedures/index.js";

/**
 * Main oRPC router with all procedures organized by domain
 */
export const router = {
  // Todo procedures
  todo: {
    create: createTodo,
    list: getTodos,
    update: updateTodo,
    delete: deleteTodo,
  },

  // Auth procedures
  auth: {
    signup: signup,
    signin: signin,
    me: me,
  },

  // Public info procedures
  public: {
    health: health,
    info: info,
  },
};

export type AppRouter = typeof router;
