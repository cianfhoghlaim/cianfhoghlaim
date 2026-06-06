
import { StreamUIMessages } from '@coding-agent-monorepo/types';
import { HOST, PORT } from './common.js';

export type CreatePublisherClient = {
  topic: string;
};

export type PublisherClient = {
  publish: (message: StreamUIMessages) => void;
  close: () => void;  
}

export type CreateSubscriberClient = {
  topic: string;
  onMessage: (message: StreamUIMessages) => void;
  onOpen?: () => void;
  onError?: (error: Error) => void;
};

export type SubscriberClient = {
  close: () => void;
};


export const publisherClient = async ({ topic }: CreatePublisherClient): Promise<PublisherClient> => {

  const ws = new WebSocket(`ws://${HOST}:${PORT}/ws/publish/${topic}`);

  let resolve: (value: void | PromiseLike<void>) => void,
    reject: (arg0: Error) => void;

  const promise = new Promise<void>((_resolve, _reject) => {
    resolve = _resolve;
    reject = _reject;
  });
  
  // create a readable stream to emit messages

  ws.onopen = () => {
    resolve();
  };
  ws.onerror = (error) => {
    reject(new Error(`WebSocket error: ${error}`));
  };
  ws.onclose = () => {
    if (ws.readyState !== WebSocket.CLOSED) {
      reject(new Error("WebSocket closed unexpectedly"));
    }
  };

  await promise;

  return {
    publish: (message: StreamUIMessages) => {
      ws.send(JSON.stringify(message));
    },

    close: () => {
      ws.close();
    },
  };
};


export const subscriberClient = async ({
  topic,
  onMessage,
  onError
}: CreateSubscriberClient): Promise<SubscriberClient> => {
  const ws = new WebSocket(`ws://${HOST}:${PORT}/ws/subscribe/${topic}`);

  let resolve: (value: void | PromiseLike<void>) => void,
    reject: (arg0: Error) => void;

  const promise = new Promise<void>((_resolve, _reject) => {
    resolve = _resolve;
    reject = _reject;
  });

  // create a readable stream to emit messages

  ws.onopen = () => {
    resolve();
  };
  ws.onerror = (error) => {
    const err = new Error(`WebSocket error: ${error}`);
    reject(err);
    onError?.(err);
  };
  ws.onclose = () => {
    if (ws.readyState !== WebSocket.CLOSED) {
      reject(new Error('WebSocket closed unexpectedly'));
    }
  };
  ws.onmessage = (event) => {
    const message = JSON.parse(event.data) as StreamUIMessages;
    onMessage(message);
  };

  await promise;

  return {
    close: () => {
      ws.close();
    },
  };
};

