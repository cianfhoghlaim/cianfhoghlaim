"use client";

import cn from "classnames";
import Markdown from "react-markdown";
import { markdownComponents } from "./markdown-components";
import { AnimatePresence, motion } from "framer-motion";
import { useEffect, useMemo, useRef, useState } from "react";
import { ChevronDownIcon, ChevronUpIcon, SpinnerIcon } from "./icons";
import { UIMessage } from "ai";
import { PRICE_PER_INFERENCE_TOKEN_WEI } from "@/lib/constants";

interface ReasoningPart {
  type: "reasoning";
  text: string;
}

interface ReasoningMessagePartProps {
  part: ReasoningPart;
  isReasoning: boolean;
}

export function ReasoningMessagePart({
  part,
  isReasoning,
}: ReasoningMessagePartProps) {
  const [isExpanded, setIsExpanded] = useState(true);

  const variants = {
    collapsed: {
      height: 0,
      opacity: 0,
      marginTop: 0,
      marginBottom: 0,
    },
    expanded: {
      height: "auto",
      opacity: 1,
      marginTop: "1rem",
      marginBottom: 0,
    },
  };

  useEffect(() => {
    if (!isReasoning) {
      setIsExpanded(false);
    }
  }, [isReasoning]);

  return (
    <div className="flex flex-col">
      {isReasoning ? (
        <div className="flex flex-row gap-2 items-center">
          <div className="text-sm font-medium">Reasoning</div>
          <div className="animate-spin">
            <SpinnerIcon />
          </div>
        </div>
      ) : (
        <div className="flex flex-row gap-2 items-center">
          <div className="text-sm font-medium">Reasoned for a few seconds</div>
          <button
            className={cn(
              "rounded-full cursor-pointer dark:hover:bg-zinc-800 hover:bg-zinc-200",
              {
                "dark:bg-zinc-800 bg-zinc-200": isExpanded,
              },
            )}
            onClick={() => {
              setIsExpanded(!isExpanded);
            }}
          >
            {isExpanded ? <ChevronDownIcon /> : <ChevronUpIcon />}
          </button>
        </div>
      )}

      <AnimatePresence initial={false}>
        {isExpanded && (
          <motion.div
            key="reasoning"
            className="flex flex-col gap-4 pl-3 text-sm border-l dark:text-zinc-400 text-zinc-600 dark:border-zinc-800"
            initial="collapsed"
            animate="expanded"
            exit="collapsed"
            variants={variants}
            transition={{ duration: 0.2, ease: "easeInOut" }}
          >
            <Markdown components={markdownComponents}>
              {part.text}
            </Markdown>

            {/* <Markdown components={markdownComponents}>{reasoning}</Markdown> */}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

interface TextMessagePartProps {
  text: string;
}

export function TextMessagePart({ text }: TextMessagePartProps) {
  return (
    <div className="flex flex-col gap-4">
      <Markdown components={markdownComponents}>{text}</Markdown>
    </div>
  );
}

interface CostCardProps {
  totalTokens: number;
  allowanceLeft?: string;
}

export function CostCard({ totalTokens, allowanceLeft }: CostCardProps) {
  const costInWei = PRICE_PER_INFERENCE_TOKEN_WEI * totalTokens;
  const costInUsdc = costInWei / 10 ** 6; // USDC has 6 decimals

  const allowanceLeftUsdc = allowanceLeft
    ? Number(BigInt(allowanceLeft)) / 10 ** 6
    : null;

  return (
    <div className="flex flex-row items-center gap-2 text-xs dark:text-zinc-500 text-zinc-600 mt-2">
      <div className="dark:bg-zinc-800 bg-zinc-200 rounded-lg px-3 py-1.5">
        Inference Cost -{" "}
        <span className="font-medium">${costInUsdc.toFixed(6)}</span>
      </div>
      {allowanceLeftUsdc !== null && (
        <div className="dark:bg-zinc-800 bg-zinc-200 rounded-lg px-3 py-1.5">
          Allowance Left -{" "}
          <span className="font-medium">${allowanceLeftUsdc.toFixed(6)}</span>
        </div>
      )}
    </div>
  );
}

interface MessagesProps {
  messages: Array<UIMessage>;
  status: "error" | "submitted" | "streaming" | "ready";
}

export function Messages({ messages, status }: MessagesProps) {
  const messagesRef = useRef<HTMLDivElement>(null);
  const messagesLength = useMemo(() => messages.length, [messages]);

  useEffect(() => {
    if (messagesRef.current) {
      messagesRef.current.scrollTop = messagesRef.current.scrollHeight;
    }
  }, [messagesLength]);

  return (
    <div
      className="flex overflow-y-scroll flex-col gap-8 items-center w-full [&::-webkit-scrollbar]:hidden [-ms-overflow-style:none] [scrollbar-width:none]"
      ref={messagesRef}
    >
      {messages.map((message) => {
        // Extract token usage from message metadata if available
        const metadata = message.metadata as { totalTokens: number; allowanceLeft?: string } | undefined;
        const totalTokens = metadata?.totalTokens;
        const allowanceLeft = metadata?.allowanceLeft;

        return (
          <div
            key={message.id}
            className={cn(
              "flex flex-col gap-4 w-full last-of-type:mb-12 first-of-type:mt-16",
            )}
          >
            <div
              className={cn("flex flex-col gap-4", {
                "dark:bg-zinc-800 bg-zinc-200 p-2 rounded-xl w-fit ml-auto":
                  message.role === "user",
                "": message.role === "assistant",
              })}
            >
              {message.parts.map((part, partIndex) => {
                if (part.type === "text") {
                  return (
                    <TextMessagePart
                      key={`${message.id}-${partIndex}`}
                      text={part.text}
                    />
                  );
                }

                if (part.type === "reasoning") {
                  return (
                    <ReasoningMessagePart
                      key={`${message.id}-${partIndex}`}
                      part={part}
                      isReasoning={
                        status === "streaming" &&
                        partIndex === message.parts.length - 1
                      }
                    />
                  );
                }
              })}
              {message.role === "assistant" && totalTokens && (
                <CostCard totalTokens={totalTokens} allowanceLeft={allowanceLeft} />
              )}
            </div>
          </div>
        );
      })}

      {status === "submitted" && (
        <div className="mb-12 w-full text-zinc-500">Hmm...</div>
      )}
    </div>
  );
}
