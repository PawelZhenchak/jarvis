
"use client";

import { useState, useRef, useEffect, type FormEvent } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { useToast } from "@/hooks/use-toast";
import { Send, Loader2, Mic } from "lucide-react";
import type { Message } from "@/lib/types";
import { ChatMessage } from "./chat-message";
import { summarizeChat } from "@/ai/flows/summarize-chat";

// Helper to check if window is defined
const isBrowser = typeof window !== "undefined";

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [selectedVoice, setSelectedVoice] = useState<SpeechSynthesisVoice | null>(null);
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isSummarizing, setIsSummarizing] = useState(false);
  const [summary, setSummary] = useState<string | null>(null);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  
  const [voicesLoadedAndMaleVoiceSelected, setVoicesLoadedAndMaleVoiceSelected] = useState(false);

  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const recognitionRef = useRef<any>(null);
  const lastSpokenTextRef = useRef<string | null>(null);
  const hasSpokenWelcomeRef = useRef<boolean>(false);
  const { toast } = useToast();

  // --- Speech Recognition Setup ---
  useEffect(() => {
    if (!isBrowser) return;

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = true;
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = 'pl-PL';

      recognitionRef.current.onresult = (event: any) => {
        const transcript = Array.from(event.results)
          .map((result: any) => result[0])
          .map((result) => result.transcript)
          .join('');
        setInput(transcript);
      };

      recognitionRef.current.onerror = (event: any) => {
        console.error("Błąd rozpoznawania mowy:", event.error);
        toast({
          title: "Błąd mikrofonu",
          description: `Nie udało się uruchomić nagrywania: ${event.error}`,
          variant: "destructive",
        });
        setIsRecording(false);
      };

      recognitionRef.current.onend = () => {
        setIsRecording(false);
      };
    } else {
      console.warn("Twoja przeglądarka nie wspiera rozpoznawania mowy.");
    }
  }, [toast]);

  // --- Speech Synthesis Voice Loading ---
  useEffect(() => {
    if (!isBrowser) return;

    const loadVoices = () => {
      const voices = window.speechSynthesis.getVoices();
      const maleVoice = voices.find(
        (voice) =>
          voice.lang === 'pl-PL' &&
          (voice.name.toLowerCase().includes('male') ||
            voice.name.toLowerCase().includes('man') ||
            voice.name.toLowerCase().includes('poland') ||
            voice.name.toLowerCase().includes('pl'))
      );
      if (maleVoice) {
        setSelectedVoice(maleVoice);
        setVoicesLoadedAndMaleVoiceSelected(true);
      } else {
        // Fallback to any Polish voice if no specific male voice is found
        const anyPolishVoice = voices.find((voice) => voice.lang === 'pl-PL');
        if (anyPolishVoice) {
          setSelectedVoice(anyPolishVoice);
          setVoicesLoadedAndMaleVoiceSelected(true);
        } else {
          console.warn("Nie znaleziono polskiego głosu.");
        }
      }
    };

    // Voices might not be immediately available
    if (window.speechSynthesis.onvoiceschanged !== undefined) {
      window.speechSynthesis.onvoiceschanged = loadVoices;
    }
    loadVoices(); // Try to load voices immediately

  }, []); // Empty dependency array means this runs once on mount

  const handleToggleRecording = () => {
    if (!recognitionRef.current) {
        toast({
            title: "Funkcja niedostępna",
            description: "Twoja przeglądarka nie wspiera rozpoznawania mowy.",
            variant: "destructive",
        });
        return;
    }
    if (isRecording) {
      recognitionRef.current.stop();
    } else {
      recognitionRef.current.start();
    }
    setIsRecording(!isRecording);
  };

  const speak = (text: string) => {
    if (!isBrowser || !window.speechSynthesis) return;
    // Prevent speaking the same text immediately again
    if (lastSpokenTextRef.current === text) {
      return;
    }
    lastSpokenTextRef.current = text;

    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'pl-PL';
    utterance.pitch = 0.9; // Slightly lower pitch
    utterance.rate = 0.95; // Slightly slower rate

    // Ensure selectedVoice is set before assigning
    if (selectedVoice) {
      utterance.voice = selectedVoice;
    } else {
      // Fallback: try to find a voice if selectedVoice is not yet set
      const voices = window.speechSynthesis.getVoices();
      const maleVoice = voices.find(
        (voice) =>
          voice.lang === 'pl-PL' &&
          (voice.name.toLowerCase().includes('male') ||
            voice.name.toLowerCase().includes('man') ||
            voice.name.toLowerCase().includes('poland') ||
            voice.name.toLowerCase().includes('pl'))
      );
      if (maleVoice) {
        utterance.voice = maleVoice;
      } else {
        const anyPolishVoice = voices.find((voice) => voice.lang === 'pl-PL');
        if (anyPolishVoice) {
          utterance.voice = anyPolishVoice;
        }
      }
    }

    window.speechSynthesis.speak(utterance);

    // Clear lastSpokenTextRef after speech ends to allow re-speaking later if needed
    utterance.onend = () => {
      lastSpokenTextRef.current = null;
    };
    utterance.onerror = () => {
      lastSpokenTextRef.current = null;
    };
  };

  // --- Chat Session Management ---
  useEffect(() => {
    if (!isBrowser) return;
    const handleStorageChange = () => {
      const activeSessionId = localStorage.getItem('active_chat_session');
      if (activeSessionId && activeSessionId !== currentSessionId) {
        const sessions = JSON.parse(localStorage.getItem('chat_sessions') || '{}');
        const activeSession = sessions[activeSessionId];
        if (activeSession) {
          setMessages(activeSession.messages);
          setCurrentSessionId(activeSessionId);
        } else {
          // If active session ID exists but no data, clear it
          localStorage.removeItem('active_chat_session');
          setCurrentSessionId(null);
        }
      } else if (!activeSessionId && currentSessionId) {
        // If no active session ID but currentSessionId is set, clear it
        setCurrentSessionId(null);
      }
    };
    
    handleStorageChange();
    window.addEventListener('chat-session-changed', handleStorageChange);
    return () => {
      window.removeEventListener('chat-session-changed', handleStorageChange);
    };
  }, [currentSessionId]);

  // Initial chat setup and welcome message
  useEffect(() => {
    if (!isBrowser || !voicesLoadedAndMaleVoiceSelected || hasSpokenWelcomeRef.current) return; // Wait for voice, and ensure it's spoken only once

    const activeSessionId = localStorage.getItem('active_chat_session');
    if (!activeSessionId && messages.length === 0) {
      const initialMessageContent = "Cześć! Jestem Jarvis PZ. W czym mogę Ci dzisiaj pomóc?";
      
      // Add a small delay to ensure voice is fully loaded
      const timeoutId = setTimeout(() => {
        setMessages([
          {
            id: String(Date.now()),
            role: 'assistant',
            content: initialMessageContent,
          },
        ]);
        speak(initialMessageContent);
        hasSpokenWelcomeRef.current = true; // Mark as spoken
      }, 0); // 0ms delay

      return () => clearTimeout(timeoutId); // Cleanup on unmount
    }
  }, [voicesLoadedAndMaleVoiceSelected, messages]); // Depend on voicesLoadedAndMaleVoiceSelected and messages

  const startNewChat = () => {
    setMessages([]); // Clear messages
    setCurrentSessionId(null);
    if (isBrowser) {
        localStorage.removeItem('active_chat_session');
    }
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
    if (!isBrowser) return;
    const sessions = JSON.parse(localStorage.getItem('chat_sessions') || '{}');
    const currentSession = sessions[sessionId] || { messages: [], createdAt: new Date() };
    
    if (!currentSession.title) {
        const firstUserMessage = updatedMessages.find(m => m.role === 'user');
        if (firstUserMessage) {
            const title = firstUserMessage.content.substring(0, 30);
            currentSession.title = title + (firstUserMessage.content.length > 30 ? '...' : '');
        }
    }

    sessions[sessionId] = { ...currentSession, messages: updatedMessages };
    localStorage.setItem('chat_sessions', JSON.stringify(sessions));
    window.dispatchEvent(new Event('chat-session-changed'));
  };

  // --- Message Handling ---
  const handleSendMessage = async (e: FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isSending) return;

    if (isRecording) {
        recognitionRef.current?.stop();
        setIsRecording(false);
    }

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
    if (!sessionId && isBrowser) {
      sessionId = `session_${Date.now()}`;
      setCurrentSessionId(sessionId);
      localStorage.setItem('active_chat_session', sessionId);
    }

    if (sessionId) {
        saveMessagesToSession(sessionId, newMessages);
    }

    try {
      const response = await fetch('/api/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: currentInput, chat_id: sessionId }),
      });

      if (!response.ok) throw new Error('Network response was not ok');

      const data = await response.json();
      const assistantMessage: Message = {
        id: String(Date.now() + 1),
        role: 'assistant',
        content: data.content,
      };

      speak(data.content); // Read the assistant's message aloud

      const finalMessages = [...newMessages, assistantMessage];
      setMessages(finalMessages);

      if (sessionId) {
        saveMessagesToSession(sessionId, finalMessages);
      }
    } catch (error) {
      console.error('Błąd podczas wysyłania wiadomości:', error);
      toast({
        title: 'Błąd',
        description: 'Nie udało się uzyskać odpowiedzi od asystenta.',
        variant: 'destructive',
      });
       const assistantMessage: Message = {
        id: String(Date.now() + 1),
        role: 'assistant',
        content: "Przepraszam, mam problem z połączeniem. Spróbuj ponownie.",
      };
      setMessages([...newMessages, assistantMessage]);

    } finally {
      setIsSending(false);
    }
  };
  
  // --- Summarization ---
  const handleSummarize = async () => {
    if (messages.length < 2) {
      toast({
        title: "Za mało historii",
        description: "Porozmawiaj trochę dłużej, zanim poprosisz o podsumowanie.",
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
      console.error("Błąd podsumowania:", error);
      toast({
        title: "Błąd",
        description: "Nie udało się zrobić podsumowania. Spróbuj ponownie.",
        variant: "destructive",
      });
    } finally {
      setIsSummarizing(false);
    }
  };

  // --- Render ---
  return (
    <div className="flex flex-col h-full w-full">
        <main className="flex-1 overflow-hidden">
          <ScrollArea className="h-full" ref={scrollAreaRef}>
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
              placeholder="Napisz wiadomość lub użyj mikrofonu..."
              className="flex-1"
              disabled={isSending}
              autoFocus
            />
            <Button type="button" size="icon" variant={isRecording ? "destructive" : "outline"} onClick={handleToggleRecording} disabled={isSending}>
              <Mic className="h-4 w-4" />
              <span className="sr-only">{isRecording ? "Zatrzymaj nagrywanie" : "Rozpocznij nagrywanie"}</span>
            </Button>
            <Button type="submit" size="icon" disabled={isSending || !input.trim()}>
              {isSending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
              <span className="sr-only">Wyślij wiadomość</span>
            </Button>
          </form>
        </footer>

        <Dialog open={!!summary} onOpenChange={() => setSummary(null)}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Podsumowanie czatu</DialogTitle>
              <DialogDescription>
                Oto podsumowanie waszej rozmowy:
              </DialogDescription>
            </DialogHeader>
            <p className="text-sm text-muted-foreground">{summary}</p>
          </DialogContent>
        </Dialog>
    </div>
  );
}
