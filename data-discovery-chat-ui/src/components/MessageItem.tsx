import React from 'react';
import { Message } from '../App'; // Import the Message interface

interface MessageItemProps {
  message: Message;
}

const MessageItem: React.FC<MessageItemProps> = ({ message }) => {
  const isUser = message.sender === 'user';

  // Base classes for all message bubbles
  const bubbleBaseClasses = "p-3 rounded-xl max-w-xs md:max-w-md lg:max-w-lg break-words shadow-md";
  
  // Classes specific to user messages
  const userBubbleClasses = `${bubbleBaseClasses} bg-blue-600 text-white`;
  
  // Classes specific to AI messages
  const aiBubbleClasses = `${bubbleBaseClasses} bg-gray-200 text-gray-800`;

  // Container classes to handle alignment
  const containerBaseClasses = "flex mb-2";
  const userContainerClasses = `${containerBaseClasses} justify-end`;
  const aiContainerClasses = `${containerBaseClasses} justify-start`;

  return (
    <div className={isUser ? userContainerClasses : aiContainerClasses}>
      <div className={isUser ? userBubbleClasses : aiBubbleClasses}>
        <div className="font-semibold text-sm mb-1">{isUser ? 'You' : 'AI Assistant'}</div>
        <div className="text-base">{message.text}</div>
      </div>
    </div>
  );
};

export default MessageItem;
