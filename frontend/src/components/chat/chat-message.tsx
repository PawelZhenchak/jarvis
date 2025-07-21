import { cn } from "@/lib/utils"
import type { Message } from "@/lib/types"
import { ChatAvatar } from "./chat-avatar"

interface ChatMessageProps {
  message: Message;
  isRelevant?: boolean;
}

export function ChatMessage({ message, isRelevant = false }: ChatMessageProps) {
  const { role, content } = message;
  
  return (
    <div
      className={cn(
        "flex items-start gap-3 my-4 animate-in fade-in-20 slide-in-from-bottom-4 duration-500 ease-out",
        { "justify-end": role === "user" }
      )}
    >
      {role === "assistant" && <ChatAvatar role={role} />}
      <div
        className={cn(
          "max-w-[75%] rounded-2xl p-4 shadow-sm",
          {
            "bg-primary text-primary-foreground": role === "user",
            "bg-card text-card-foreground": role === "assistant",
            "ring-2 ring-accent ring-offset-2 ring-offset-background": isRelevant,
          }
        )}
      >
        <p className="text-sm leading-relaxed whitespace-pre-wrap">{content}</p>
      </div>
      {role === "user" && <ChatAvatar role={role} />}
    </div>
  );
}
