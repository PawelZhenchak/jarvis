
"use client";

import { useState, useRef, useEffect, type FormEvent, type KeyboardEvent } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { useToast } from "@/hooks/use-toast";
import { Send, Loader2 } from "lucide-react";
import type { Message } from "@/lib/types";
import { ChatMessage } from "./chat-message";
import { summarizeChat } from "@/ai/flows/summarize-chat";
import { semanticChatSearch } from "@/ai/flows/semantic-chat-search";

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [isSummarizing, setIsSummarizing] = useState(false);
  const [summary, setSummary] = useState<string | null>(null);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);


  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const { toast } = useToast();

  useEffect(() => {
    // This effect handles loading chats when the session changes
    const handleStorageChange = () => {
      const activeSessionId = localStorage.getItem('active_chat_session');
      if (activeSessionId && activeSessionId !== currentSessionId) {
        const sessions = JSON.parse(localStorage.getItem('chat_sessions') || '{}');
        const activeSession = sessions[activeSessionId];
        if (activeSession) {
          setMessages(activeSession.messages);
          setCurrentSessionId(activeSessionId);
        } else {
            // If the active session is not found, start a new one
             startNewChat();
        }
      } else if (!activeSessionId) {
        startNewChat();
      }
    };
    
    handleStorageChange(); // Initial load
    
    // Listen for custom event that signals a session change from the sidebar
    window.addEventListener('chat-session-changed', handleStorageChange);
    
    return () => {
      window.removeEventListener('chat-session-changed', handleStorageChange);
    };

  }, [currentSessionId]);

   const startNewChat = () => {
    setMessages([
        {
            id: String(Date.now()),
            role: 'assistant',
            content: "Hello! I'm Jarvis PZ. How can I assist you today?",
        },
    ]);
    setCurrentSessionId(null);
    localStorage.removeItem('active_chat_session');
  }

  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTo({
        top: scrollAreaRef.current.scrollHeight,
        behavior: "smooth",
      });
    }
  }, [messages]);

  const saveMessagesToSession = (sessionId: string, updatedMessages: Message[]) => {
    const sessions = JSON.parse(localStorage.getItem('chat_sessions') || '{}');
    const currentSession = sessions[sessionId] || { messages: [], createdAt: new Date() };
    
    // Create title from first user message if it doesn't exist
    if (!currentSession.title) {
        const firstUserMessage = updatedMessages.find(m => m.role === 'user');
        if (firstUserMessage) {
            currentSession.title = firstUserMessage.content.substring(0, 30) + (firstUserMessage.content.length > 30 ? '...' : '');
        }
    }

    sessions[sessionId] = {
        ...currentSession,
        messages: updatedMessages
    };

    localStorage.setItem('chat_sessions', JSON.stringify(sessions));
    // Dispatch event to notify sidebar of the update
    window.dispatchEvent(new Event('chat-session-changed'));
  };


  const handleSendMessage = async (e: FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isSending) return;

    console.log("Wysyłanie wiadomości...");

    const userMessage: Message = {
      id: String(Date.now()),
      role: 'user',
      content: input,
    };

    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    const currentInput = input;
    setInput('');
    setIsSending(true);

    let sessionId = currentSessionId;
    if (!sessionId) {
      sessionId = `session_${Date.now()}`;
      console.log(`Nowa sesja czatu: ${sessionId}`);
      setCurrentSessionId(sessionId);
      localStorage.setItem('active_chat_session', sessionId);
    }

    saveMessagesToSession(sessionId, newMessages);
    console.log(`Wiadomość zapisana w sesji: ${sessionId}`);

    try {
      console.log(`Wysyłanie do /api/ask:`, { message: currentInput, chat_id: sessionId });
      const response = await fetch('/api/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: currentInput, chat_id: sessionId }),
      });

      console.log(`Odpowiedź z serwera:`, response);

      if (!response.ok) {
        console.error("Błąd sieci lub serwera.");
        throw new Error('Network response was not ok');
      }

      const data = await response.json();
      console.log(`Otrzymane dane (JSON):`, data);

      const assistantMessage: Message = {
        id: String(Date.now() + 1),
        role: 'assistant',
        content: data.content,
      };

      const finalMessages = [...newMessages, assistantMessage];
      setMessages(finalMessages);

      if (sessionId) {
        saveMessagesToSession(sessionId, finalMessages);
        console.log("Odpowiedź asystenta zapisana w sesji.");
      }
    } catch (error) {
      console.error('Błąd podczas wysyłania wiadomości:', error);
      toast({
        title: 'Błąd',
        description: 'Nie udało się uzyskać odpowiedzi od asystenta.',
        variant: 'destructive',
      });
    } finally {
      setIsSending(false);
      console.log("Zakończono wysyłanie.");
    }
  };
  
  const handleSummarize = async () => {
    if (messages.length < 2) {
      toast({
        title: "Not enough history",
        description: "Please have a longer conversation before summarizing.",
        variant: "destructive",
      });
      return;
    }
    setIsSummarizing(true);
    try {
      const chatHistory = messages.map(m => `${m.role}: ${m.content}`).join('\n');
      const result = await summarizeChat({ chatHistory });
      setSummary(result.summary);
    } catch (error) {
      console.error("Summarization error:", error);
      toast({
        title: "Error",
        description: "Failed to summarize the chat. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsSummarizing(false);
    }
  };

  return (
    <div className="flex flex-col h-full w-full">
        <main className="flex-1 overflow-hidden">
          <ScrollArea className="h-full" viewportRef={scrollAreaRef}>
            <div className="px-4 py-2">
              {messages.map((message) => (
                <ChatMessage key={message.id} message={message} />
              ))}
              {isSending && <ChatMessage message={{id: 'thinking', role: 'assistant', content: '...'}} />}
            </div>
          </ScrollArea>
        </main>

        <footer className="p-4 border-t bg-card/80 backdrop-blur-sm">
          <form onSubmit={handleSendMessage} className="flex items-center gap-2">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your message..."
              className="flex-1"
              disabled={isSending}
              autoFocus
            />
            <Button type="submit" size="icon" disabled={isSending || !input.trim()}>
              {isSending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
              <span className="sr-only">Send message</span>
            </Button>
          </form>
        </footer>

        <Dialog open={!!summary} onOpenChange={() => setSummary(null)}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Chat Summary</DialogTitle>
              <DialogDescription>
                Here is a summary of your conversation:
              </DialogDescription>
            </DialogHeader>
            <p className="text-sm text-muted-foreground">{summary}</p>
          </DialogContent>
        </Dialog>
    </div>
  );
}
