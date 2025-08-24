'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { ChatMessage } from './chat-message';
import { useToast } from '@/hooks/use-toast';
import { Loader2, Mic } from 'lucide-react'; // Usunięto MicOff, dodamy logikę w locie
import { Message } from '@/types/global';

type ListeningState = 'idle' | 'listening' | 'processing';

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
  const isSpeakingRef = useRef(false);
  const listeningStateRef = useRef(listeningState);
  const { toast } = useToast();

  // Refs for silence detection
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const sourceRef = useRef<MediaStreamAudioSourceNode | null>(null);
  const silenceStartRef = useRef<number>(Date.now());
  const animationFrameIdRef = useRef<number | null>(null);
  const isSpeakingActivityRef = useRef<boolean>(false);

  const SILENCE_THRESHOLD = 0.01; 
  const SILENCE_DURATION = 2000; 

  useEffect(() => {
    listeningStateRef.current = listeningState;
  }, [listeningState]);

  const speak = (text: string, onEndCallback?: () => void) => {
    if (!isBrowser || !window.speechSynthesis || !text.trim()) {
      onEndCallback?.();
      return;
    }
    window.speechSynthesis.cancel();
    isSpeakingRef.current = true;
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'pl-PL';
    const voices = window.speechSynthesis.getVoices();
    const polishVoice = voices.find(v => v.lang === 'pl-PL');
    if (polishVoice) utterance.voice = polishVoice;

    utterance.onend = () => {
      isSpeakingRef.current = false;
      if (listeningStateRef.current !== 'idle') {
        startListening();
      }
      onEndCallback?.();
    };
    utterance.onerror = (event) => {
      console.error("Speech synthesis error:", event);
      isSpeakingRef.current = false;
      if (listeningStateRef.current !== 'idle') {
        startListening();
      }
      onEndCallback?.();
    };
    window.speechSynthesis.speak(utterance);
  };

  const handleSendMessage = async (command: string) => {
    if (!command.trim()) {
      setListeningState('listening');
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
      speak(data.content);
    } catch (error) {
      console.error('Błąd podczas wysyłania wiadomości:', error);
      const errorMessage = "Przepraszam, mam problem z połączeniem.";
      const assistantMessage: Message = { id: String(Date.now() + 1), role: 'assistant', content: errorMessage };
      setMessages([...newMessages, assistantMessage]);
      speak(errorMessage);
    }
  };

  const sendAudioToBackend = async (audioBlob: Blob) => {
    // If the blob is smaller than a certain threshold, consider it empty/silence
    // and just restart the listening process without hitting the backend.
    if (audioBlob.size < 1000) { 
        console.log("Empty audio blob detected, restarting listening.");
        startListening();
        return;
    }

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
        handleSendMessage(recognizedText);
      } else {
        setNotification("Nie rozpoznano mowy. Spróbuj ponownie.");
        setTimeout(() => setNotification(null), 3000);
        startListening(); // Go back to listening
      }
    } catch (error) {
      console.error('Błąd podczas wysyłania audio do backendu:', error);
      setNotification("Problem z połączeniem STT. Spróbuj ponownie.");
      setTimeout(() => setNotification(null), 5000);
      startListening(); // Go back to listening
    }
  };

  const startSilenceDetection = (stream: MediaStream) => {
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    audioContextRef.current = audioContext;
    const analyser = audioContext.createAnalyser();
    analyser.fftSize = 2048;
    analyserRef.current = analyser;
    const source = audioContext.createMediaStreamSource(stream);
    sourceRef.current = source;
    source.connect(analyser);
    const dataArray = new Uint8Array(analyser.frequencyBinCount);
    silenceStartRef.current = Date.now();
    isSpeakingActivityRef.current = false;
    const detect = () => {
      if (!mediaRecorderRef.current) return;
      analyser.getByteTimeDomainData(dataArray);
      let sum = 0;
      for (let i = 0; i < dataArray.length; i++) {
        sum += Math.pow((dataArray[i] / 128.0) - 1, 2);
      }
      const rms = Math.sqrt(sum / dataArray.length);
      if (rms > SILENCE_THRESHOLD) {
        isSpeakingActivityRef.current = true;
        silenceStartRef.current = Date.now();
      } else if (isSpeakingActivityRef.current) {
        if (Date.now() - silenceStartRef.current > SILENCE_DURATION) {
          console.log("Silence detected, stopping recording.");
          if (mediaRecorderRef.current.state !== 'inactive') {
            mediaRecorderRef.current.stop();
          }
          isSpeakingActivityRef.current = false;
        }
      }
      animationFrameIdRef.current = requestAnimationFrame(detect);
    };
    animationFrameIdRef.current = requestAnimationFrame(detect);
  };

  const stopSilenceDetection = () => {
    if (animationFrameIdRef.current) cancelAnimationFrame(animationFrameIdRef.current);
    sourceRef.current?.disconnect();
    analyserRef.current?.disconnect();
    audioContextRef.current?.close();
  };

  const startListening = async () => {
    if (isSpeakingRef.current) return;
    setListeningState('listening');
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];
      mediaRecorderRef.current.ondataavailable = (event) => audioChunksRef.current.push(event.data);
      mediaRecorderRef.current.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        sendAudioToBackend(audioBlob);
        stream.getTracks().forEach(track => track.stop());
        stopSilenceDetection();
      };
      mediaRecorderRef.current.start();
      startSilenceDetection(stream);
    } catch (error) {
      console.error("Error accessing microphone:", error);
      setNotification("Błąd dostępu do mikrofonu. Sprawdź uprawnienia.");
      setListeningState('idle');
    }
  };

  const stopConversation = () => {
    setListeningState('idle');
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }
    window.speechSynthesis.cancel();
    isSpeakingRef.current = false;
  };

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

  const getStatusText = () => {
    switch (listeningState) {
      case 'idle': return 'Jarvis śpi. Kliknij, aby rozpocząć rozmowę.';
      case 'listening': return 'Słucham...';
      case 'processing': return 'Myślę...';
      default: return 'Gotowy';
    }
  };

  const handleButtonClick = () => {
    if (listeningState === 'idle') {
      startListening();
    } else {
      stopConversation();
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
          variant={listeningState === 'listening' ? 'destructive' : 'default'}
        >
          {listeningState === 'processing' ? (
            <Loader2 className="h-8 w-8 animate-spin" />
          ) : (
            <Mic className="h-8 w-8" />
          )}
          <span className="sr-only">{listeningState === 'idle' ? 'Uruchom Jarvisa' : 'Zatrzymaj Jarvisa'}</span>
        </Button>
        {notification && <p className="text-sm text-yellow-500 mt-2">{notification}</p>}
        <p className="text-sm text-muted-foreground mt-2">{getStatusText()}</p>
      </footer>
    </div>
  );
}