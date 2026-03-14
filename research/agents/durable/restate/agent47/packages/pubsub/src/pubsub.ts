import { StreamUIMessages } from "@coding-agent-monorepo/types";

export class Pubsub {
  channels: Map<string, Channel> = new Map();

  subscribe(topic: string, callback: (message: StreamUIMessages) => void) {
    if (!this.channels.has(topic)) {
      this.channels.set(topic, new Channel());
    }
    const channel = this.channels.get(topic)!;
    channel.subscribe(callback);
  }

  publish(topic: string, message: StreamUIMessages): void {
    if (!this.channels.has(topic)) {
      this.channels.set(topic, new Channel());
    }
    this.channels.get(topic)!.publish(message);
  }
}

class Channel {
  messages: StreamUIMessages[] = [];
  subscribers: Set<(message: StreamUIMessages) => void> = new Set();

  subscribe(callback: (message: StreamUIMessages) => void): void {
    this.messages.forEach((message) => callback(message));
    this.subscribers.add(callback);
  }

  publish(message: StreamUIMessages): void {
    this.messages.push(message);
    this.subscribers.forEach((callback) => callback(message));
  }
}

