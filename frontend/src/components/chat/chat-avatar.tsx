"use client";

import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { User, Bot } from 'lucide-react';
import type { Message } from '@/lib/types';

interface ChatAvatarProps {
  role: Message['role'];
}

export function ChatAvatar({ role }: ChatAvatarProps) {
  return (
    <Avatar className="h-8 w-8">
      <AvatarFallback className={role === 'user' ? 'bg-primary/80 text-primary-foreground' : 'bg-card text-card-foreground'}>
        {role === 'user' ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
      </AvatarFallback>
    </Avatar>
  );
}
