
"use client";

import { ScrollArea } from '@/components/ui/scroll-area';
import { Button } from '@/components/ui/button';
import { ArrowRight, PlusCircle } from 'lucide-react';
import { useEffect, useState } from 'react';

interface ChatSession {
  id: string;
  title: string;
  createdAt: string; 
}

export function CustomSidebar() {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);

  const loadSessions = () => {
    const storedSessions = JSON.parse(localStorage.getItem('chat_sessions') || '{}');
    const loadedSessions = Object.entries(storedSessions)
      .map(([id, sessionData]: [string, any]) => ({
        id,
        title: sessionData.title || 'New Chat',
        createdAt: sessionData.createdAt,
      }))
      .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()); // Sort by most recent
    
    setSessions(loadedSessions);
    setActiveSessionId(localStorage.getItem('active_chat_session'));
  };

  useEffect(() => {
    loadSessions();
    window.addEventListener('storage', loadSessions); // handles changes from other tabs
    window.addEventListener('chat-session-changed', loadSessions); // handles changes from this tab

    return () => {
      window.removeEventListener('storage', loadSessions);
      window.removeEventListener('chat-session-changed', loadSessions);
    };
  }, []);

  const handleSessionClick = (sessionId: string) => {
    localStorage.setItem('active_chat_session', sessionId);
    setActiveSessionId(sessionId);
    window.dispatchEvent(new Event('chat-session-changed'));
  };

  const handleNewChat = () => {
    localStorage.removeItem('active_chat_session');
    setActiveSessionId(null);
    window.dispatchEvent(new Event('chat-session-changed'));
  };
  
  return (
    <div className="relative w-72 bg-transparent text-white pt-10">
      {/* Tilted container */}
      <div className="absolute inset-0 bg-card/30 backdrop-blur-sm transform -skew-x-6 origin-top-left"></div>
      
      {/* Content inside the sidebar */}
      <div className="relative z-10 flex flex-col h-full items-center p-4">
        {/* Logo */}
        <div className="flex flex-col items-center gap-2 mt-4 mb-8">
          <div 
            className="w-20 h-20 rounded-full bg-white"
            style={{
              boxShadow: '0 0 15px 5px rgba(255, 255, 255, 0.4), 0 0 30px 10px rgba(173, 216, 230, 0.3)',
            }}
          ></div>
          <span className="text-lg font-bold text-white tracking-widest mt-2">Jarvis PZ</span>
        </div>

        {/* New Chat Button */}
        <Button onClick={handleNewChat} variant="ghost" className="w-full justify-center items-center gap-2 mb-4 text-white hover:text-white hover:bg-white/10 rounded-md">
            <PlusCircle className="h-4 w-4" />
            New Chat
        </Button>

        {/* History Section */}
        <div className="flex flex-col w-full text-left">
          <h2 className="text-sm font-semibold uppercase text-gray-400 mb-2 px-2">History</h2>
          <ScrollArea className="flex-1 -mr-4 pr-4">
              <div className="flex flex-col gap-2">
                {sessions.length > 0 ? sessions.map((session) => (
                    <Button 
                      key={session.id} 
                      variant="ghost" 
                      onClick={() => handleSessionClick(session.id)}
                      className="w-full justify-between items-center truncate text-white/80 hover:text-white hover:bg-white/10 rounded-none border-b border-primary/50 pb-3"
                    >
                        <span className="truncate">{session.title}</span>
                        <ArrowRight className="h-4 w-4 shrink-0 text-primary" />
                    </Button>
                )) : (
                  <p className="text-center text-white/50 text-sm p-4">No chat history yet.</p>
                )}
              </div>
          </ScrollArea>
        </div>
      </div>
    </div>
  );
}
