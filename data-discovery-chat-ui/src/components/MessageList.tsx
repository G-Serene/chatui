import React, { useEffect, useRef } from 'react';
import MessageItem from './MessageItem';
import { useAppStore } from '../store'; // Import the Zustand store

// MessageListProps is no longer needed as messages come from the store
// interface MessageListProps {
//   messages: Message[];
// }

const MessageList: React.FC = () => {
  const messages = useAppStore((state) => state.messages); // Get messages from store
  const messagesEndRef = useRef<null | HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]); // Dependency on messages from the store

  return (
    <div className="flex-grow overflow-y-auto p-4 space-y-4 bg-gray-50">
      {messages.map(msg => (
        <MessageItem key={msg.id} message={msg} />
      ))}
      <div ref={messagesEndRef} />
    </div>
  );
};

export default MessageList;
