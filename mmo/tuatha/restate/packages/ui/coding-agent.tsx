"use client"

import { useState, useEffect, useRef, useCallback, useMemo, memo } from "react"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Progress } from "@/components/ui/progress"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Badge } from "@/components/ui/badge"
import { useToast } from "@/hooks/use-toast"
import { Bot, User, Play, Square, CheckCircle, Clock, AlertCircle, Code, Send, FileCode, Wifi, WifiOff, Download } from 'lucide-react'

import type { StreamUIMessages } from "@coding-agent-monorepo/types"
import { subscriberClient, SubscriberClient } from "@coding-agent-monorepo/pubsub"

import Markdown from "react-markdown"
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism'
import remarkGfm from 'remark-gfm'

type UIPlanStep = {
  id: string
  title: string
  description: string
  status: 'pending' | 'running' | 'completed' | 'error'
}

type UIMessage = {
  id: number;
  type: 'user' | 'agent'
  content: string
  stepId?: string // Optional, used for tracking messages related to specific steps
}

const AGENT_ID = Math.random().toString(32).substring(2, 18);

// Memoized message component to prevent unnecessary re-renders
const MessageComponent = memo(({ message, markdownComponents }: { 
  message: UIMessage; 
  markdownComponents: any; 
}) => (
  <div className="flex gap-3">
    <Avatar className="w-8 h-8">
      {message.type === "agent" ? (
        <AvatarFallback className="bg-primary text-primary-foreground">
          <Bot className="w-4 h-4" />
        </AvatarFallback>
      ) : (
        <AvatarFallback>
          <User className="w-4 h-4" />
        </AvatarFallback>
      )}
    </Avatar>
    <div className="flex-1 space-y-1">
      <div className="flex items-center gap-2">
        <span className="text-sm font-medium">
          {message.type === "agent" ? "Agent" : "You"}
        </span>
      </div>
      <div className="text-sm text-muted-foreground">
        <div className="markdown">
          <Markdown
            remarkPlugins={[remarkGfm]}
            components={markdownComponents}
          >
            {message.content}
          </Markdown>
        </div>
      </div>
    </div>
  </div>
));

MessageComponent.displayName = 'MessageComponent';

export default function CodingAgentUI() {
  const [messages, setMessages] = useState<UIMessage[]>([
    {
      id: 1,
      type: "agent",
      content: `Hello! I'm your coding agent. Describe what you'd like me to build and I'll create a plan and execute it for you
> I'm here to help you build amazing projects! Just tell me what you need.`,
    },
  ]);
  
  const [currentPlan, setCurrentPlan] = useState<UIPlanStep[]>([])
  const [input, setInput] = useState('')
  const [isExecuting, setIsExecuting] = useState(false)
  const [isConnected, setIsConnected] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isWaitingForPlan, setWaitingForPlan] = useState(false)

  const messagesEventSourceRef = useRef<SubscriberClient | null>(null);
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);
  const { toast } = useToast()
  
  const completedSteps = useMemo(() => 
    currentPlan.filter(step => step.status === 'completed').length, [currentPlan]
  )
  const totalSteps = currentPlan.length
  const progress = useMemo(() => 
    totalSteps > 0 ? (completedSteps / totalSteps) * 100 : 0, [completedSteps, totalSteps]
  )
  
  // Auto-scroll to bottom when messages change - optimized to only run when actually needed
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (scrollAreaRef.current) {
        const scrollContainer = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]');
        if (scrollContainer) {
          const { scrollTop, scrollHeight, clientHeight } = scrollContainer;
          // Only scroll if we're near the bottom (within 100px) to avoid interrupting user scrolling
          if (scrollHeight - scrollTop - clientHeight < 100) {
            scrollContainer.scrollTop = scrollContainer.scrollHeight;
          }
        }
      }
    }, 0); // Use setTimeout to batch scroll operations

    return () => clearTimeout(timeoutId);
  }, [messages.length]); // Only depend on message count, not the entire messages array
  

    // Clean up event sources on unmount
  useEffect(() => {
    return () => {
     if (messagesEventSourceRef.current) {
       messagesEventSourceRef.current.close();
     }
     if (abortControllerRef.current) {
       abortControllerRef.current.abort();
     }
    };
  }, []);
  
 const onMessage = useCallback((message: StreamUIMessages) => {
    if (message.type === 'plan') {
      setCurrentPlan(message.plan);
      setWaitingForPlan(false);
    } else if (message.type === 'stepEnd' || message.type === 'stepStart') {
      setCurrentPlan((prev) => {
        const newPlan = prev.map((step) => {
          if (step.id === message.stepId) {
            return {
              ...step,
              status: message.type === 'stepEnd' ? 'completed' : 'running',
            } as UIPlanStep;
          }
          return step;
        });
        return newPlan;
      });
    } else if (message.type === 'text') {
      const updateMessage = (prev: UIMessage[]): UIMessage[] => {
        let lastMessage = prev[prev.length - 1];
        if (
          lastMessage &&
          lastMessage.type === 'agent' &&
          lastMessage.stepId === message.stepId
        ) {
          lastMessage = {
            id: lastMessage.id,
            type: 'agent',
            content: lastMessage.content + message.text,
            stepId: message.stepId,
          };
          return [...prev.slice(0, prev.length - 1), lastMessage];
        } else {
          lastMessage = {
            id: prev.length + 1,
            type: 'agent',
            content: message.text,
            stepId: message.stepId,
          };
          return [...prev, lastMessage];
        }
      };

      setMessages(updateMessage);
    }
  }, []);

  const connectToStreams = useCallback(async (currentTaskId: string) => {
    let client = messagesEventSourceRef.current;
    if (client) {
      client.close();
    }
    
    client = await subscriberClient({
      topic: currentTaskId,
      onMessage,
      onError: (error) => {
        console.error("error:", error);
        setIsConnected(false);
      },
    });
  
    setIsConnected(true);
    messagesEventSourceRef.current = client;
  }, [onMessage]);

  const disconnectFromStreams = useCallback(() => {
    if (messagesEventSourceRef.current) {
      messagesEventSourceRef.current.close();
      messagesEventSourceRef.current = null;
    }

    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }

    setIsConnected(false);
    setIsExecuting(false);
    setWaitingForPlan(false);
    setCurrentPlan([]);
   }, []);

  const handleSendMessage = useCallback(async () => {
    if (!input.trim() || isSubmitting) return
    
    setIsSubmitting(true)
    setWaitingForPlan(true);

    // Create abort controller for this request
    const abortController = new AbortController();
    abortControllerRef.current = abortController;

    // Add user message immediately
    setMessages((prev) => [
      ...prev,
      {
        id: prev.length + 1,
        type: "user",
        content: input,
      },
    ]);
    const currentInput = input
    setInput('')
    setCurrentPlan([]);
    
    try {
      // Submit to REST API
      const response = await fetch(
        `http://localhost:8080/agent/${AGENT_ID}/newMessage`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(currentInput),
          signal: abortController.signal,
        }
      );
      
      if (!response.ok) {
        throw new Error('Failed to submit prompt')
      }
      
      const {currentTaskId} = await response.json() as { currentTaskId: string };
      
      
      // Start execution and connect to streams
      setIsExecuting(true)
      await connectToStreams(currentTaskId)
      
      toast({
        title: "Request Submitted",
        description: "Your coding request has been submitted and is being processed.",
      })
      
    } catch (error) {
      // Don't show error if request was aborted
      if (error instanceof Error && error.name === 'AbortError') {
        return;
      }
      
      console.error('Error submitting prompt:', error)
      toast({
        title: "Error",
        description: "Failed to submit your request. Please try again.",
        variant: "destructive",
      })
      
      // Remove the user message if submission failed
      setMessages((prev) => prev.slice(0, -1));
      setInput(currentInput) // Restore the input
      setWaitingForPlan(false) // Reset waiting state
    } finally {
      setIsSubmitting(false)
      abortControllerRef.current = null;
    }
  }, [input, isSubmitting, connectToStreams, toast]);

  const handleStopExecution = useCallback(() => {
    disconnectFromStreams()
    setWaitingForPlan(false)
    setMessages((prev) => [
      ...prev,
      {
        id: prev.length + 1,
        type: "agent",
        content: "Execution has been stopped.",
      },
    ]);

    toast({
      title: "Execution Stopped",
      description: "The coding agent execution has been stopped.",
    })
    fetch(`http://localhost:8080/agent/${AGENT_ID}/cancelTask`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    }).catch((error) => {
      console.error("Error stopping execution:", error);
      toast({
        title: "Error",
        description: "Failed to stop the execution. Please try again.",
        variant: "destructive",
      });
    });
  }, [disconnectFromStreams, toast])
  
  const getStatusIcon = useCallback((status: UIPlanStep['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />
      case 'running':
        return <Clock className="w-4 h-4 text-blue-500 animate-spin" />
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-500" />
      default:
        return <Clock className="w-4 h-4 text-muted-foreground" />
    }
  }, [])

  const getStatusColor = useCallback((status: UIPlanStep['status']) => {
    switch (status) {
      case 'completed':
        return 'bg-green-500'
      case 'running':
        return 'bg-blue-500'
      case 'error':
        return 'bg-red-500'
      default:
        return 'bg-muted-foreground'
    }
  }, [])

  // Memoize Markdown components to prevent recreation on every render
  const markdownComponents = useMemo(() => ({
    code({ className, children, ...props }: any) {
      const match = /language-(\w+)/.exec(className || "");
      const isInline = !className || !match;

      if (!isInline) {
        return (
          <div data-language={match[1]}>
            <SyntaxHighlighter
              language={match[1]}
              PreTag="div"
              style={oneDark}
              customStyle={{
                margin: 0,
                borderRadius: "0.5rem",
              }}
            >
              {String(children).replace(/\n$/, "")}
            </SyntaxHighlighter>
          </div>
        );
      }

      return (
        <code className={className} {...props}>
          {children}
        </code>
      );
    },
    table: ({ children }: any) => (
      <div className="table-container">
        <table className="w-full border-collapse border border-border my-4">
          {children}
        </table>
      </div>
    ),
    th: ({ children }: any) => (
      <th className="border border-border px-3 py-2 text-left font-medium bg-muted/30">
        {children}
      </th>
    ),
    td: ({ children }: any) => (
      <td className="border border-border px-3 py-2">
        {children}
      </td>
    ),
    ul: ({ children }: any) => (
      <ul className="mb-3 ml-6 list-disc text-muted-foreground">
        {children}
      </ul>
    ),
    ol: ({ children }: any) => (
      <ol className="mb-3 ml-6 list-decimal text-muted-foreground">
        {children}
      </ol>
    ),
    li: ({ children }: any) => (
      <li className="mb-1">{children}</li>
    ),
    blockquote: ({ children }: any) => (
      <blockquote className="border-l-4 border-primary/30 pl-4 py-2 my-4 bg-muted/20 italic text-muted-foreground">
        {children}
      </blockquote>
    ),
  }), []);

  return (
    <div className="flex h-screen bg-background">
      {/* Left Panel - Chat */}
      <div className="flex flex-col w-1/2 border-r">
        <div className="p-4 border-b">
          <div className="flex items-center gap-2">
            <Bot className="w-6 h-6 text-primary" />
            <h1 className="text-xl font-semibold">Coding Agent</h1>
            <div className="flex items-center gap-2 ml-auto">
              {isConnected ? (
                <Wifi className="w-4 h-4 text-green-500" />
              ) : (
                <WifiOff className="w-4 h-4 text-muted-foreground" />
              )}
              <Badge variant={isExecuting ? "default" : "secondary"}>
                {isExecuting ? "Executing" : "Ready"}
              </Badge>
            </div>
          </div>
        </div>

        <div className="flex-1 overflow-hidden">
          <ScrollArea ref={scrollAreaRef} className="h-full p-4">
            <div className="space-y-4">
              {messages.map((message) => (
                <MessageComponent
                  key={`${message.id}`}
                  message={message}
                  markdownComponents={markdownComponents}
                />
              ))}
            </div>
          </ScrollArea>
        </div>

        <div className="p-4 border-t">
          <div className="flex gap-2">
            <Input
              placeholder="Describe what you want me to build..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
              disabled={isSubmitting}
            />
            <Button
              onClick={handleSendMessage}
              disabled={isSubmitting || !input.trim()}
            >
              {isSubmitting ? (
                <Clock className="w-4 h-4 animate-spin" />
              ) : (
                <Send className="w-4 h-4" />
              )}
            </Button>
          </div>
        </div>
      </div>

      {/* Right Panel - Plan & Execution */}
      <div className="flex flex-col w-1/2">
        <div className="p-4 border-b">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <FileCode className="w-5 h-5" />
              <h2 className="text-lg font-semibold">Execution Plan</h2>
            </div>
            <div className="flex items-center gap-2">
              {isExecuting ? (
                <>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleStopExecution}
                  >
                    <Square className="w-4 h-4 mr-1" />
                    Stop
                  </Button>
                </>
              ) : (
                <Button size="sm" disabled={!input.trim()}>
                  <Play className="w-4 h-4 mr-1" />
                  Execute
                </Button>
              )}
            </div>
          </div>

          {totalSteps > 0 && (
            <div className="mt-3">
              <div className="flex items-center justify-between text-sm text-muted-foreground mb-2">
                <span>Progress</span>
                <span>
                  {completedSteps}/{totalSteps} steps completed
                </span>
              </div>
              <Progress value={progress} className="h-2" />
            </div>
          )}
        </div>

        <ScrollArea className="flex-1 p-4">
          {isWaitingForPlan ? (
            <div className="flex items-center justify-center h-full text-muted-foreground">
              <div className="text-center">
                <FileCode className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>Waiting for execution plan...</p>
              </div>
            </div>
          ) : (
            <div className="space-y-3">
              {currentPlan.map((step, index) => (
                <Card key={step.id} className="relative">
                  <CardHeader className="pb-3">
                    <div className="flex items-start gap-3">
                      <div className="flex flex-col items-center">
                        <div
                          className={`w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-medium ${getStatusColor(
                            step.status
                          )}`}
                        >
                          {index + 1}
                        </div>
                        {index < currentPlan.length - 1 && (
                          <div className="w-px h-6 bg-border mt-2" />
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <CardTitle className="text-base">
                            {step.title}
                          </CardTitle>
                          {getStatusIcon(step.status)}
                        </div>
                        <CardDescription className="mt-1">
                          {step.description}
                        </CardDescription>
                      </div>
                    </div>
                  </CardHeader>
                </Card>
              ))}
            </div>
          )}
        </ScrollArea>

        <div className="p-4 border-t bg-muted/30">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Code className="w-4 h-4" />
            <span>
              {isExecuting
                ? "Agent is working on your request..."
                : isConnected
                  ? "Connected and ready to execute"
                  : "Ready to execute your next request"}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
