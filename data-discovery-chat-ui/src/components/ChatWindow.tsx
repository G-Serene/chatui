import React from 'react';
import MessageList from './MessageList';
import ChatInput from './ChatInput';
// Message type will be sourced from MessageList which gets it from the store via MessageItem

interface ChatWindowProps {
  onSendMessage: (message: string) => void; 
  // messages prop is removed as MessageList will get it from the store
}

const ChatWindow: React.FC<ChatWindowProps> = ({ onSendMessage }) => {
  return (
    <div className="flex flex-col h-full border border-gray-300 rounded-lg shadow-lg bg-white">
      <h1 className="text-xl font-semibold text-center p-4 bg-gray-100 border-b border-gray-200 rounded-t-lg text-gray-700">Data Discovery Chat</h1>
      {/* MessageList will now fetch its own messages from the store */}
      <MessageList /> 
      <ChatInput onSendMessage={onSendMessage} />
    </div>
  );
};

export default ChatWindow;
