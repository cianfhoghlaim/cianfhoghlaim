/**
 * Stack Recommender Agent
 *
 * Agno-based agent that recommends self-hosted software
 * based on user requirements and preferences.
 */

import { useCopilotAction, useCopilotReadable } from "@copilotkit/react-core";

// Stack database for recommendations
const stackDatabase = [
  {
    name: "rybbit",
    category: "analytics",
    description: "Privacy-focused analytics platform",
    useCase: "website analytics, privacy-first, self-hosted alternative to Google Analytics",
    resources: { memory: "512Mi", cpu: 0.5 },
    complexity: "low",
  },
  {
    name: "langfuse",
    category: "ml-observability",
    description: "LLM observability and analytics",
    useCase: "LLM monitoring, prompt engineering, AI application debugging",
    resources: { memory: "1Gi", cpu: 1.0 },
    complexity: "medium",
  },
  {
    name: "excalidraw",
    category: "collaboration",
    description: "Virtual whiteboard for sketching",
    useCase: "diagramming, wireframing, team collaboration, whiteboarding",
    resources: { memory: "256Mi", cpu: 0.25 },
    complexity: "low",
  },
  {
    name: "glance",
    category: "dashboard",
    description: "Self-hosted dashboard",
    useCase: "homelab dashboard, service monitoring, link aggregation",
    resources: { memory: "128Mi", cpu: 0.1 },
    complexity: "low",
  },
  {
    name: "actual",
    category: "finance",
    description: "Privacy-focused budgeting",
    useCase: "personal finance, budgeting, expense tracking, bank sync",
    resources: { memory: "256Mi", cpu: 0.25 },
    complexity: "low",
  },
  {
    name: "marimo",
    category: "notebooks",
    description: "Reactive Python notebooks",
    useCase: "data science, interactive computing, Python notebooks, data exploration",
    resources: { memory: "1Gi", cpu: 1.0 },
    complexity: "medium",
  },
  {
    name: "paperless-ngx",
    category: "documents",
    description: "Document management system",
    useCase: "document scanning, OCR, paperless office, document organization",
    resources: { memory: "1Gi", cpu: 1.0 },
    complexity: "medium",
  },
];

export function useStackRecommenderAgent() {
  // Make stack data readable by CopilotKit
  useCopilotReadable({
    description: "Available self-hosted software stacks",
    value: JSON.stringify(stackDatabase, null, 2),
  });

  // Recommend stacks action
  useCopilotAction({
    name: "recommendStacks",
    description: "Recommend self-hosted stacks based on user requirements",
    parameters: [
      {
        name: "useCase",
        type: "string",
        description: "The user's use case or requirements",
        required: true,
      },
      {
        name: "resourceConstraint",
        type: "string",
        description: "Resource constraints (low, medium, high)",
        required: false,
      },
    ],
    handler: async ({ useCase, resourceConstraint }) => {
      const useCaseLower = useCase.toLowerCase();

      // Filter stacks by use case keywords
      let recommendations = stackDatabase.filter(
        (stack) =>
          stack.useCase.toLowerCase().includes(useCaseLower) ||
          stack.category.toLowerCase().includes(useCaseLower) ||
          stack.description.toLowerCase().includes(useCaseLower)
      );

      // Filter by resource constraint if specified
      if (resourceConstraint === "low") {
        recommendations = recommendations.filter(
          (s) => s.complexity === "low"
        );
      }

      // Return top 3 recommendations
      return recommendations.slice(0, 3).map((stack) => ({
        name: stack.name,
        description: stack.description,
        whyRecommended: `Matches your need for ${useCase}`,
        resources: stack.resources,
      }));
    },
  });

  // Compare stacks action
  useCopilotAction({
    name: "compareStacks",
    description: "Compare two or more self-hosted stacks",
    parameters: [
      {
        name: "stackNames",
        type: "string[]",
        description: "Names of stacks to compare",
        required: true,
      },
    ],
    handler: async ({ stackNames }) => {
      const stacks = stackDatabase.filter((s) =>
        stackNames.map((n: string) => n.toLowerCase()).includes(s.name.toLowerCase())
      );

      return stacks.map((stack) => ({
        name: stack.name,
        category: stack.category,
        description: stack.description,
        useCase: stack.useCase,
        resources: stack.resources,
        complexity: stack.complexity,
      }));
    },
  });

  // Get stack details action
  useCopilotAction({
    name: "getStackDetails",
    description: "Get detailed information about a specific stack",
    parameters: [
      {
        name: "stackName",
        type: "string",
        description: "Name of the stack",
        required: true,
      },
    ],
    handler: async ({ stackName }) => {
      const stack = stackDatabase.find(
        (s) => s.name.toLowerCase() === stackName.toLowerCase()
      );

      if (!stack) {
        return { error: `Stack "${stackName}" not found` };
      }

      return {
        name: stack.name,
        category: stack.category,
        description: stack.description,
        useCase: stack.useCase,
        resources: stack.resources,
        complexity: stack.complexity,
        deploymentUrl: `/deploy?stack=${stack.name}`,
      };
    },
  });
}
