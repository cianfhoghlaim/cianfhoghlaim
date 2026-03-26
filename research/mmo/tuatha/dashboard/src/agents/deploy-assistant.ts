/**
 * Deploy Assistant Agent
 *
 * Agno-based agent that helps deploy stacks to Komodo
 * and generates configuration files.
 */

import { useCopilotAction, useCopilotReadable } from "@copilotkit/react-core";

// Server configuration
const servers = [
  { id: "srv-1", name: "bunchloch-main", available: true },
  { id: "srv-2", name: "bunchloch-worker", available: true },
  { id: "srv-3", name: "bunchloch-gpu", available: true },
];

// Compose templates
const composeTemplates: Record<string, string> = {
  langfuse: `version: "3.8"
services:
  langfuse:
    image: langfuse/langfuse:latest
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/langfuse
      - NEXTAUTH_SECRET=\${NEXTAUTH_SECRET}
      - NEXTAUTH_URL=\${NEXTAUTH_URL}
    depends_on:
      - db
  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=langfuse
    volumes:
      - langfuse_data:/var/lib/postgresql/data
volumes:
  langfuse_data:`,

  glance: `version: "3.8"
services:
  glance:
    image: glanceapp/glance:latest
    ports:
      - "8080:8080"
    volumes:
      - ./glance.yml:/app/glance.yml
    restart: unless-stopped`,

  excalidraw: `version: "3.8"
services:
  excalidraw:
    image: excalidraw/excalidraw:latest
    ports:
      - "80:80"
    restart: unless-stopped`,
};

export function useDeployAssistantAgent() {
  // Make server info readable
  useCopilotReadable({
    description: "Available Komodo servers for deployment",
    value: JSON.stringify(servers, null, 2),
  });

  // Generate compose file action
  useCopilotAction({
    name: "generateCompose",
    description: "Generate a Docker Compose file for a stack",
    parameters: [
      {
        name: "stackName",
        type: "string",
        description: "Name of the stack to generate compose for",
        required: true,
      },
      {
        name: "customEnv",
        type: "object",
        description: "Custom environment variables",
        required: false,
      },
    ],
    handler: async ({ stackName, customEnv }) => {
      const template = composeTemplates[stackName.toLowerCase()];

      if (!template) {
        return {
          error: `No compose template found for "${stackName}"`,
          suggestion: "Available templates: " + Object.keys(composeTemplates).join(", "),
        };
      }

      return {
        stackName,
        composeContent: template,
        envVars: customEnv || {},
        instructions: [
          `1. Save this as docker-compose.yml`,
          `2. Set required environment variables`,
          `3. Run: docker-compose up -d`,
        ],
      };
    },
  });

  // Deploy to Komodo action
  useCopilotAction({
    name: "deployToKomodo",
    description: "Deploy a stack to a Komodo server",
    parameters: [
      {
        name: "stackName",
        type: "string",
        description: "Name of the stack to deploy",
        required: true,
      },
      {
        name: "serverId",
        type: "string",
        description: "ID of the target server",
        required: true,
      },
    ],
    handler: async ({ stackName, serverId }) => {
      const server = servers.find((s) => s.id === serverId || s.name === serverId);

      if (!server) {
        return {
          success: false,
          error: `Server "${serverId}" not found`,
          availableServers: servers.map((s) => s.name),
        };
      }

      if (!server.available) {
        return {
          success: false,
          error: `Server "${server.name}" is not available`,
        };
      }

      // In a real implementation, this would call the Komodo API
      return {
        success: true,
        message: `Deployment of "${stackName}" to "${server.name}" initiated`,
        deploymentId: `deploy-${Date.now()}`,
        steps: [
          { step: "Validating compose file", status: "completed" },
          { step: "Pulling images", status: "in_progress" },
          { step: "Creating containers", status: "pending" },
          { step: "Starting services", status: "pending" },
        ],
      };
    },
  });

  // Generate Ansible playbook action
  useCopilotAction({
    name: "generateAnsible",
    description: "Generate an Ansible playbook for infrastructure provisioning",
    parameters: [
      {
        name: "task",
        type: "string",
        description: "The task to generate playbook for (e.g., 'install-periphery', 'deploy-stack')",
        required: true,
      },
      {
        name: "targetServers",
        type: "string[]",
        description: "Target server names",
        required: true,
      },
    ],
    handler: async ({ task, targetServers }) => {
      let playbook = "";

      if (task === "install-periphery") {
        playbook = `---
- name: Install Komodo Periphery Agent
  hosts: ${targetServers.join(",")}
  become: yes
  tasks:
    - name: Download periphery binary
      get_url:
        url: https://github.com/mbecker20/komodo/releases/latest/download/periphery
        dest: /usr/local/bin/periphery
        mode: '0755'

    - name: Create periphery config directory
      file:
        path: /etc/periphery
        state: directory
        mode: '0755'

    - name: Copy periphery config
      template:
        src: periphery.config.toml.j2
        dest: /etc/periphery/config.toml

    - name: Create systemd service
      template:
        src: periphery.service.j2
        dest: /etc/systemd/system/periphery.service

    - name: Start and enable periphery
      systemd:
        name: periphery
        state: started
        enabled: yes
        daemon_reload: yes`;
      } else if (task === "deploy-stack") {
        playbook = `---
- name: Deploy Docker Stack
  hosts: ${targetServers.join(",")}
  become: yes
  vars:
    stack_name: "{{ stack_name }}"
  tasks:
    - name: Ensure Docker is installed
      apt:
        name: docker.io
        state: present

    - name: Copy compose file
      copy:
        src: "{{ stack_name }}/docker-compose.yml"
        dest: "/opt/stacks/{{ stack_name }}/docker-compose.yml"

    - name: Start stack
      community.docker.docker_compose:
        project_src: "/opt/stacks/{{ stack_name }}"
        state: present`;
      } else {
        return {
          error: `Unknown task: "${task}"`,
          availableTasks: ["install-periphery", "deploy-stack"],
        };
      }

      return {
        task,
        targetServers,
        playbook,
        usage: `ansible-playbook -i inventory.yml playbook.yml`,
      };
    },
  });

  // Check deployment status action
  useCopilotAction({
    name: "checkDeploymentStatus",
    description: "Check the status of a deployment",
    parameters: [
      {
        name: "deploymentId",
        type: "string",
        description: "The deployment ID to check",
        required: true,
      },
    ],
    handler: async ({ deploymentId }) => {
      // Mock status - in real implementation, query Komodo API
      return {
        deploymentId,
        status: "running",
        progress: 75,
        containers: [
          { name: "app", status: "running", health: "healthy" },
          { name: "db", status: "running", health: "healthy" },
        ],
        logs: "Container started successfully...",
      };
    },
  });
}
