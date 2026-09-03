import { CopilotKit } from "@copilotkit/react-core";
import { CopilotPopup } from "@copilotkit/react-ui";
import {
  Outlet,
  ScrollRestoration,
  createRootRoute,
} from "@tanstack/react-router";
import { Meta, Scripts } from "@tanstack/start";
import { createContext, useContext, useState, type ReactNode } from "react";

import "@copilotkit/react-ui/styles.css";

// ============================================================================
// Classroom Context for CoAgents Shared State
// ============================================================================

interface ClassroomContextValue {
  /** Current classroom ID */
  classroomId: string | null;
  /** Current user role */
  role: "teacher" | "student" | null;
  /** Current user ID */
  userId: string | null;
  /** Whether classroom mode is enabled */
  isClassroomMode: boolean;
  /** Enable classroom mode */
  enableClassroom: (classroomId: string, role: "teacher" | "student", userId: string) => void;
  /** Disable classroom mode */
  disableClassroom: () => void;
}

const ClassroomContext = createContext<ClassroomContextValue>({
  classroomId: null,
  role: null,
  userId: null,
  isClassroomMode: false,
  enableClassroom: () => {},
  disableClassroom: () => {},
});

export function useClassroomContext() {
  return useContext(ClassroomContext);
}

function ClassroomProvider({ children }: { children: ReactNode }) {
  const [classroomId, setClassroomId] = useState<string | null>(null);
  const [role, setRole] = useState<"teacher" | "student" | null>(null);
  const [userId, setUserId] = useState<string | null>(null);

  const enableClassroom = (id: string, userRole: "teacher" | "student", uid: string) => {
    setClassroomId(id);
    setRole(userRole);
    setUserId(uid);
  };

  const disableClassroom = () => {
    setClassroomId(null);
    setRole(null);
    setUserId(null);
  };

  return (
    <ClassroomContext.Provider
      value={{
        classroomId,
        role,
        userId,
        isClassroomMode: !!classroomId,
        enableClassroom,
        disableClassroom,
      }}
    >
      {children}
    </ClassroomContext.Provider>
  );
}

export const Route = createRootRoute({
  head: () => ({
    meta: [
      {
        charSet: "utf-8",
      },
      {
        name: "viewport",
        content: "width=device-width, initial-scale=1",
      },
      {
        title: "Irish Education Assistant",
      },
      {
        name: "description",
        content: "AI-powered search and Q&A for Irish curriculum resources",
      },
    ],
    links: [
      {
        rel: "stylesheet",
        href: "/styles.css",
      },
    ],
  }),
  component: RootComponent,
});

function RootComponent() {
  return (
    <RootDocument>
      <CopilotKit runtimeUrl="/api/copilotkit">
        <ClassroomProvider>
          <div className="min-h-screen bg-gray-50">
            <header className="bg-white shadow-sm border-b">
              <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-between">
                  <h1 className="text-2xl font-bold text-gray-900">
                    Irish Education Assistant
                  </h1>
                  <nav className="flex space-x-4">
                    <a
                      href="/"
                      className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md"
                    >
                      Dashboard
                    </a>
                    <a
                      href="/search"
                      className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md"
                    >
                      Search
                    </a>
                    <a
                      href="/classroom"
                      className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md"
                    >
                      Classroom
                    </a>
                  </nav>
                </div>
              </div>
            </header>
            <main className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
              <Outlet />
            </main>
          </div>
          <CopilotPopup
            labels={{
              title: "Education Assistant",
              initial:
                "Hello! I can help you search Irish curriculum documents, answer questions about the education system, find relevant resources, and assist with classroom activities.",
            }}
          />
        </ClassroomProvider>
      </CopilotKit>
    </RootDocument>
  );
}

function RootDocument({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <head>
        <Meta />
      </head>
      <body>
        {children}
        <ScrollRestoration />
        <Scripts />
      </body>
    </html>
  );
}
