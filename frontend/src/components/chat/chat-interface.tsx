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
  const [notification, setNotification] = useState<string | null>(null);

  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const [isRecording, setIsRecording] = useState(false); // Nowy stan do śledzenia nagrywania
  
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

    // Zatrzymaj rozpoznawanie mowy na czas mówienia
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }

    window.speechSynthesis.cancel(); // Anuluj poprzednie wypowiedzi
    isSpeakingRef.current = true;
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'pl-PL';
    
    // Logowanie dostępnych głosów i wybranego głosu
    const voices = window.speechSynthesis.getVoices();
    console.log("Available voices (inside speak):", voices); // Dodane logowanie
    const polishVoice = voices.find(v => v.lang === 'pl-PL');
    console.log("Found Polish voice (inside speak):", polishVoice); // Dodane logowanie

    if (selectedVoice) {
      console.log("Using selected voice (inside speak):", selectedVoice); // Dodane logowanie
      utterance.voice = selectedVoice;
    } else if (polishVoice) {
      console.log("Using found Polish voice (inside speak):", polishVoice); // Dodane logowanie
      utterance.voice = polishVoice;
    } else {
      console.log("No Polish voice found, using default (inside speak)."); // Dodane logowanie
    }

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
      
      // Wznów nasłuchiwanie, jeśli nie jesteśmy w stanie bezczynności
      if (listeningStateRef.current !== 'idle') {
        startListening();
      }

      onEndCallback?.();
    };
    utterance.onerror = (event) => {
      console.error("Speech synthesis error:", event);
      isSpeakingRef.current = false;

      // Na wszelki wypadek, wznów nasłuchiwanie również po błędzie
      if (listeningStateRef.current !== 'idle') {
        startListening();
      }

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
            const response = await fetch('http://localhost:9002/ask', {
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

  const sendAudioToBackend = async (audioBlob: Blob) => {
    setListeningState('processing');
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.webm');

    try {
      const response = await fetch('http://localhost:9002/stt', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Network response was not ok for STT');
      const data = await response.json();
      const recognizedText = data.text;

      if (recognizedText) {
        handleSendMessage(recognizedText); // Send recognized text as a message
      } else {
        setNotification("Nie rozpoznano mowy. Spróbuj ponownie.");
        setTimeout(() => setNotification(null), 3000);
        setListeningState('in_conversation'); // Go back to listening
      }
    } catch (error) {
      console.error('Błąd podczas wysyłania audio do backendu:', error);
      setNotification("Problem z połączeniem STT. Spróbuj ponownie.");
      setTimeout(() => setNotification(null), 5000);
      setListeningState('in_conversation'); // Go back to listening
    }
  };

  // --- Speech Recognition & State Machine (now with MediaRecorder) ---
  const startListening = async () => {
    if (isSpeakingRef.current) return; // Don't start listening if Jarvis is speaking

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        sendAudioToBackend(audioBlob);
        stream.getTracks().forEach(track => track.stop()); // Stop microphone access
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
      setListeningState('in_conversation'); // Start directly in conversation mode
      setNotification(null); // Clear any previous notifications
      resetSleepTimer();
    } catch (error) {
      console.error("Error accessing microphone:", error);
      setNotification("Błąd dostępu do mikrofonu. Sprawdź uprawnienia.");
      setTimeout(() => setNotification(null), 5000);
      setListeningState('idle');
    }
  };

  const stopListening = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }
    setIsRecording(false);
    setListeningState('idle');
    if (sleepTimerRef.current) clearTimeout(sleepTimerRef.current);
    if (commandTimeoutRef.current) clearTimeout(commandTimeoutRef.current);
    finalTranscriptRef.current = ""; // Clear any pending transcript
  };
  

  const resetSleepTimer = () => {
    if (sleepTimerRef.current) clearTimeout(sleepTimerRef.current);
    sleepTimerRef.current = setTimeout(() => {
      stopListening();
      toast({ title: "Jarvis śpi", description: "Kliknij przycisk, aby go obudzić." });
    }, 10 * 60 * 1000); // 10 minutes
  };

  


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
    if (isRecording) {
      return 'Nagrywam... Mów śmiało!';
    }
    switch (listeningState) {
      case 'idle': return 'Jarvis śpi. Kliknij, aby go uruchomić.';
      case 'processing': return 'Myślę...';
      default: return 'Gotowy';
    }
  };

  const handleButtonClick = () => {
    if (!isRecording) { // If not currently recording, start recording
      startListening();
    } else { // If currently recording, stop recording
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
          {isRecording && <Mic className="h-8 w-8" />}
          {!isRecording && <MicOff className="h-8 w-8" />}
          <span className="sr-only">{listeningState === 'idle' ? 'Uruchom Jarvisa' : 'Zatrzymaj Jarvisa'}</span>
        </Button>
        {notification && <p className="text-sm text-yellow-500 mt-2">{notification}</p>}
        <p className="text-sm text-muted-foreground mt-2">{getStatusText()}</p>
      </footer>
    </div>
  );
}