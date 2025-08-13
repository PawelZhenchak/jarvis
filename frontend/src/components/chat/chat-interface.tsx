'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { ChatMessage } from './chat-message';
import { useToast } from '@/hooks/use-toast';
import { Loader2, Mic, MicOff } from 'lucide-react';
import { Message } from '@/types/global';

type ListeningState = 'idle' | 'waiting_for_wakeword' | 'in_conversation' | 'processing';

const isBrowser = typeof window !== 'undefined';

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [selectedVoice, setSelectedVoice] = useState<SpeechSynthesisVoice | null>(null);
  const [listeningState, setListeningState] = useState<ListeningState>('idle');
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);

  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const recognitionRef = useRef<any>(null);
  const sleepTimerRef = useRef<NodeJS.Timeout | null>(null);
  const commandTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const finalTranscriptRef = useRef<string>("");
  const isSpeakingRef = useRef(false); // New ref to track if Jarvis is speaking
  const listeningStateRef = useRef(listeningState); // Ref to hold the current listening state
  const { toast } = useToast();

  // Keep the ref in sync with the state
  useEffect(() => {
    listeningStateRef.current = listeningState;
  }, [listeningState]);

  // --- Core Functions ---
  const speak = (text: string, onEndCallback?: () => void) => {
    console.log("speak() called with text:", text);
    if (!isBrowser || !window.speechSynthesis) {
      console.error("Speech synthesis not supported.");
      onEndCallback?.();
      return;
    }
    window.speechSynthesis.cancel(); // Anuluj poprzednie wypowiedzi
    isSpeakingRef.current = true;
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'pl-PL';
    
    // Logowanie dostępnych głosów i wybranego głosu
    const voices = window.speechSynthesis.getVoices();
    console.log("Available voices:", voices);
    const polishVoice = voices.find(v => v.lang === 'pl-PL');
    console.log("Found Polish voice:", polishVoice);

    if (selectedVoice) {
      console.log("Using selected voice:", selectedVoice);
      utterance.voice = selectedVoice;
    } else if (polishVoice) {
      console.log("Using found Polish voice:", polishVoice);
      utterance.voice = polishVoice;
    } else {
      console.log("No Polish voice found, using default.");
    }

    utterance.onend = () => {
      console.log("Speech finished.");
      isSpeakingRef.current = false;
      onEndCallback?.();
    };
    utterance.onerror = (event) => {
      console.error("Speech synthesis error:", event);
      isSpeakingRef.current = false;
      onEndCallback?.();
    };
    
    console.log("Attempting to speak...");
    window.speechSynthesis.speak(utterance);
  };

  const handleSendMessage = async (command: string) => {
    console.log("handleSendMessage called with command:", command);
    if (!command.trim()) {
      setListeningState('in_conversation'); // Nothing to send, go back to listening
      console.log("handleSendMessage - command is empty, returning.");
      return;
    }
    setListeningState('processing');

    const userMessage: Message = { id: String(Date.now()), role: 'user', content: command };
    const newMessages = [...messages, userMessage];
    setMessages(newMessages);

    let sessionId = currentSessionId;
    if (!sessionId && isBrowser) {
      sessionId = `session_${Date.now()}`;
      setCurrentSessionId(sessionId);
      localStorage.setItem('active_chat_session', sessionId);
    }
    if (sessionId) saveMessagesToSession(sessionId, newMessages);

    try {
      const response = await fetch('http://localhost:5000/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: command, chat_id: sessionId }),
      });
      if (!response.ok) throw new Error('Network response was not ok');
      const data = await response.json();
      const assistantMessage: Message = { id: String(Date.now() + 1), role: 'assistant', content: data.content };
      setMessages([...newMessages, assistantMessage]);
      if (sessionId) saveMessagesToSession(sessionId, [...newMessages, assistantMessage]);
      speak(data.content, () => setListeningState('in_conversation'));
    } catch (error) {
      console.error('Błąd podczas wysyłania wiadomości:', error);
      const errorMessage = "Przepraszam, mam problem z połączeniem.";
      const assistantMessage: Message = { id: String(Date.now() + 1), role: 'assistant', content: errorMessage };
      setMessages([...newMessages, assistantMessage]);
      speak(errorMessage, () => setListeningState('in_conversation'));
    }
  };

  // --- Speech Recognition & State Machine ---
  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.onend = null; // Prevent automatic restart
      recognitionRef.current.stop();
    }
    setListeningState('idle');
    if (sleepTimerRef.current) clearTimeout(sleepTimerRef.current);
    if (commandTimeoutRef.current) clearTimeout(commandTimeoutRef.current);
    finalTranscriptRef.current = ""; // Clear any pending transcript
  };

  const startListening = () => {
    if (recognitionRef.current) {
      finalTranscriptRef.current = ""; // Clear transcript on start
      try {
        recognitionRef.current.start();
      } catch (error) {
        // Catch errors if recognition is already started, which can happen.
        console.log("Speech recognition already started.", error);
      }
    }
  };

  const resetSleepTimer = () => {
    if (sleepTimerRef.current) clearTimeout(sleepTimerRef.current);
    sleepTimerRef.current = setTimeout(() => {
      stopListening();
      toast({ title: "Jarvis śpi", description: "Kliknij przycisk, aby go obudzić." });
    }, 10 * 60 * 1000); // 10 minutes
  };

  useEffect(() => {
    if (!isBrowser) return;
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      toast({ title: "Błąd", description: "Twoja przeglądarka nie wspiera rozpoznawania mowy.", variant: "destructive" });
      return;
    }

    recognitionRef.current = new SpeechRecognition();
    const recognition = recognitionRef.current;
    recognition.lang = 'pl-PL';
    recognition.continuous = true;
    recognition.interimResults = true;

    recognition.onstart = () => {
      resetSleepTimer();
    };

    recognition.onresult = (event: any) => {
      // Ignore any results that come in while Jarvis is speaking.
      if (isSpeakingRef.current) {
        console.log("Ignoring recognition result while speaking.");
        return;
      }

      resetSleepTimer();

      let currentTranscript = '';
      let isFinal = false;
      for (let i = event.resultIndex; i < event.results.length; ++i) {
        currentTranscript += event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          isFinal = true;
        }
      }
      
      const processedTranscript = currentTranscript.trim().toLowerCase();
      console.log(`Result: "${processedTranscript}" (isFinal: ${isFinal})`);

      if (listeningStateRef.current === 'waiting_for_wakeword') {
        if (processedTranscript.includes('jarvis')) {
          setListeningState('in_conversation');
          speak("Słucham?");
          finalTranscriptRef.current = ""; // Clear transcript so "jarvis" isn't sent as a command
          if (commandTimeoutRef.current) clearTimeout(commandTimeoutRef.current);
        }
      } else if (listeningStateRef.current === 'in_conversation') {
        finalTranscriptRef.current = currentTranscript; // Keep updating with the latest transcript
        
        // Use a timeout to detect the end of speech
        if (commandTimeoutRef.current) clearTimeout(commandTimeoutRef.current);
        commandTimeoutRef.current = setTimeout(() => {
          console.log("Command timeout fired. Sending:", finalTranscriptRef.current);
          if (finalTranscriptRef.current.trim()) {
            handleSendMessage(finalTranscriptRef.current);
          }
          finalTranscriptRef.current = "";
        }, 1200); // 1.2 second delay after they stop talking
      }
    };

    recognition.onerror = (event: any) => {
      console.error("Recognition error:", event.error);

      if (event.error === 'not-allowed') {
        stopListening();
        toast({
          title: "Brak dostępu do mikrofonu",
          description: "Jarvis nie ma pozwolenia na używanie mikrofonu. Sprawdź ustawienia w swojej przeglądarce (ikonka w pasku adresu).",
          variant: "destructive",
          duration: 10000 // Show for 10 seconds
        });
      } else if (event.error !== 'no-speech' && event.error !== 'audio-capture') {
        // Handle other, more critical errors
        stopListening();
        toast({
          title: "Błąd mikrofonu",
          description: `Wystąpił błąd: ${event.error}.`,
          variant: "destructive"
        });
      }
      // For 'no-speech' or 'audio-capture', we do nothing and let the onend handler restart listening.
    };

    recognition.onend = () => {
      console.log("Recognition ended. State:", listeningStateRef.current);
      // Auto-restart listening as long as we are not idle or processing a command.
      if (listeningStateRef.current !== 'idle' && listeningStateRef.current !== 'processing') {
        startListening();
      }
    };

    const loadVoices = () => {
      const voices = window.speechSynthesis.getVoices();
      const polishVoice = voices.find(v => v.lang === 'pl-PL');
      if(polishVoice) setSelectedVoice(polishVoice);
    };
    loadVoices();
    window.speechSynthesis.onvoiceschanged = loadVoices;

    return () => { if (recognitionRef.current) recognitionRef.current.stop(); };
  }, []);


  // --- Session Management ---
  useEffect(() => {
    if (!isBrowser) return;
    const handleStorageChange = () => {
      const activeSessionId = localStorage.getItem('active_chat_session');
      if (activeSessionId) {
        const sessions = JSON.parse(localStorage.getItem('chat_sessions') || '{}');
        const activeSession = sessions[activeSessionId];
        if (activeSession) {
          setMessages(activeSession.messages);
          setCurrentSessionId(activeSessionId);
        }
      } else {
        setCurrentSessionId(null);
        setMessages([]);
      }
    };
    handleStorageChange();
    window.addEventListener('chat-session-changed', handleStorageChange);
    return () => window.removeEventListener('chat-session-changed', handleStorageChange);
  }, []);

  const saveMessagesToSession = (sessionId: string, updatedMessages: Message[]) => {
    if (!isBrowser) return;
    const sessions = JSON.parse(localStorage.getItem('chat_sessions') || '{}');
    const currentSession = sessions[sessionId] || { messages: [], createdAt: new Date().toISOString() };
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

  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTo({ top: scrollAreaRef.current.scrollHeight, behavior: "smooth" });
    }
  }, [messages]);

  // --- Render ---
  const getStatusText = () => {
    switch (listeningState) {
      case 'idle': return 'Jarvis śpi. Kliknij, aby go uruchomić.';
      case 'waiting_for_wakeword': return 'Powiedz "Jarvis", aby aktywować.';
      case 'in_conversation': return 'Słucham...';
      case 'processing': return 'Myślę...';
      default: return 'Gotowy';
    }
  };

  const handleButtonClick = () => {
    if (listeningState === 'idle') {
      setListeningState('waiting_for_wakeword');
      startListening();
    } else {
      stopListening();
    }
  }

  return (
    <div className="flex flex-col h-full w-full">
      <main className="flex-1 overflow-hidden">
        <ScrollArea className="h-full" ref={scrollAreaRef}>
          <div className="px-4 py-2">
            {messages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))}
            {listeningState === 'processing' && <ChatMessage message={{id: 'thinking', role: 'assistant', content: '...'}} />}
          </div>
        </ScrollArea>
      </main>

      <footer className="p-4 border-t bg-card/80 backdrop-blur-sm flex flex-col items-center justify-center text-center min-h-[96px]">
        <Button 
          size="lg"
          className="w-24 h-24 rounded-full disabled:opacity-100"
          onClick={handleButtonClick}
          disabled={listeningState === 'processing'}
        >
          {listeningState === 'processing' && <Loader2 className="h-8 w-8 animate-spin" />}
          {(listeningState === 'waiting_for_wakeword' || listeningState === 'in_conversation') && <Mic className="h-8 w-8" />}
          {listeningState === 'idle' && <MicOff className="h-8 w-8" />}
          <span className="sr-only">{listeningState === 'idle' ? 'Uruchom Jarvisa' : 'Zatrzymaj Jarvisa'}</span>
        </Button>
        <p className="text-sm text-muted-foreground mt-2">{getStatusText()}</p>
      </footer>
    </div>
  );
}