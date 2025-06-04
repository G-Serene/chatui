import React, { useEffect, useRef } from 'react';
import { io, Socket } from 'socket.io-client';
import ChatWindow from './components/ChatWindow';
import ArtifactWindow from './components/ArtifactWindow';
import {
  useAppStore, Message, AiMessageChunk, AiMessageEnd,
  ArtifactStreamStartPayload, ArtifactStreamChunkPayload, ArtifactStreamEndPayload
} from './store';
import './App.css';

const SOCKET_SERVER_URL = 'http://localhost:3001';

function App() {
  const {
    addMessage,
    setSocketConnected,
    handleAiMessageChunk,
    handleAiMessageEnd,
    handleArtifactStreamStart,
    handleArtifactStreamChunk,
    handleArtifactStreamEnd
  } = useAppStore(state => ({
    addMessage: state.addMessage,
    setSocketConnected: state.setSocketConnected,
    handleAiMessageChunk: state.handleAiMessageChunk,
    handleAiMessageEnd: state.handleAiMessageEnd,
    handleArtifactStreamStart: state.handleArtifactStreamStart,
    handleArtifactStreamChunk: state.handleArtifactStreamChunk,
    handleArtifactStreamEnd: state.handleArtifactStreamEnd,
  }));

  const socketRef = useRef<Socket | null>(null);

  useEffect(() => {
    socketRef.current = io(SOCKET_SERVER_URL);
    console.log('Attempting to connect to WebSocket server...');

    socketRef.current.on('connect', () => { console.log('Connected:', socketRef.current?.id); setSocketConnected(true); });
    socketRef.current.on('disconnect', (reason) => { console.log('Disconnected:', reason); setSocketConnected(false); });
    socketRef.current.on('connect_error', (error) => {
      console.error('WS Connect Error:', error);
      setSocketConnected(false);
      addMessage({ id: Date.now().toString(), text: 'Error: Cannot connect to chat. Backend offline?', sender: 'ai_error' });
    });

    socketRef.current.on('ai_message_chunk', handleAiMessageChunk);
    socketRef.current.on('ai_message_end', handleAiMessageEnd);

    // New artifact streaming listeners
    socketRef.current.on('artifact_stream_start', handleArtifactStreamStart);
    socketRef.current.on('artifact_stream_chunk', handleArtifactStreamChunk);
    socketRef.current.on('artifact_stream_end', handleArtifactStreamEnd);

    return () => {
      if (socketRef.current) {
        console.log('Disconnecting WebSocket...');
        socketRef.current.off('connect');
        socketRef.current.off('disconnect');
        socketRef.current.off('connect_error');
        socketRef.current.off('ai_message_chunk', handleAiMessageChunk);
        socketRef.current.off('ai_message_end', handleAiMessageEnd);
        socketRef.current.off('artifact_stream_start', handleArtifactStreamStart);
        socketRef.current.off('artifact_stream_chunk', handleArtifactStreamChunk);
        socketRef.current.off('artifact_stream_end', handleArtifactStreamEnd);
        socketRef.current.disconnect();
        socketRef.current = null;
      }
    };
  }, [addMessage, setSocketConnected, handleAiMessageChunk, handleAiMessageEnd, handleArtifactStreamStart, handleArtifactStreamChunk, handleArtifactStreamEnd]);

  const handleSendMessage = async (newMessageText: string) => {
    if (!newMessageText.trim()) return;
    const userMessage: Message = { id: Date.now().toString() + '-user', text: newMessageText, sender: 'user' };
    addMessage(userMessage);

    if (socketRef.current && socketRef.current.connected) {
      socketRef.current.emit('send_chat_message', { message: newMessageText });
      console.log("Message sent via WebSocket: ", newMessageText);
    } else {
      console.error('Socket not connected. Cannot send message.');
      addMessage({ id: Date.now().toString() + '-socket-send-error', text: 'Error: Not connected to chat server. Message not sent.', sender: 'ai_error' });
    }
  };

  const isArtifactVisible = useAppStore(state => state.isArtifactVisible);

  return (
    <div className="App flex flex-col md:flex-row h-screen bg-gray-100">
      <div className="flex-grow md:w-3/5 lg:w-2/3 p-2 flex flex-col">
        <ChatWindow onSendMessage={handleSendMessage} />
      </div>
      {isArtifactVisible && (
        <div className="md:w-2/5 lg:w-1/3 p-2 flex flex-col">
          <ArtifactWindow />
        </div>
      )}
    </div>
  );
}

export default App;
