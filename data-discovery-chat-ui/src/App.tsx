import React, { useEffect, useRef } from 'react';
import { io, Socket } from 'socket.io-client';
import ChatWindow from './components/ChatWindow';
import ArtifactWindow from './components/ArtifactWindow';
import { useAppStore, Message } from './store'; // Import store and types
import './App.css'; 

const SOCKET_SERVER_URL = 'http://localhost:3001';

function App() {
  // Get state and actions from Zustand store
  const { 
    addMessage, 
    setArtifact, 
    setSocketConnected,
  } = useAppStore(state => ({
    addMessage: state.addMessage,
    setArtifact: state.setArtifact,
    setSocketConnected: state.setSocketConnected,
  }));
  // No need to select messages, artifactContent, isArtifactVisible here as components will select them

  const socketRef = useRef<Socket | null>(null);

  useEffect(() => {
    socketRef.current = io(SOCKET_SERVER_URL);
    console.log('Attempting to connect to WebSocket server...');

    socketRef.current.on('connect', () => {
      console.log('Connected to WebSocket server:', socketRef.current?.id);
      setSocketConnected(true);
    });

    socketRef.current.on('disconnect', (reason) => {
      console.log('Disconnected from WebSocket server:', reason);
      setSocketConnected(false);
    });

    socketRef.current.on('ai_message', (aiMessage: Message) => {
      console.log('Received ai_message via WebSocket:', aiMessage);
      addMessage(aiMessage);
    });

    socketRef.current.on('connect_error', (error) => {
      console.error('WebSocket Connection Error:', error);
      setSocketConnected(false);
      const connectErrorMessage: Message = {
        id: Date.now().toString() + '-ws-connect-error',
        text: 'Error: Cannot connect to real-time chat. Backend might be offline.',
        sender: 'ai',
      };
      addMessage(connectErrorMessage);
    });
    
    return () => {
      if (socketRef.current) {
        console.log('Disconnecting WebSocket...');
        socketRef.current.disconnect();
        socketRef.current = null;
      }
    };
  }, [addMessage, setSocketConnected]);


  const handleGenerateArtifact = async (query: string) => {
    try {
      const response = await fetch('http://localhost:3001/api/generate-artifact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Artifact API Error:', response.status, errorText);
        setArtifact({ type: 'message', content: `Error generating artifact. Status: ${response.status}. ${errorText}` });
        return;
      }

      const data = await response.json();
      if (data && data.type) {
        setArtifact(data);
      } else {
        setArtifact({ type: 'message', content: JSON.stringify(data, null, 2) });
      }
    } catch (error) {
      console.error('Fetch Artifact Error:', error);
      setArtifact({ type: 'message', content: 'Error: Could not connect to the artifact generation server.' });
    }
  };

  const handleSendMessage = async (newMessageText: string) => {
    if (!newMessageText.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString() + '-user',
      text: newMessageText,
      sender: 'user',
    };
    addMessage(userMessage); // Add user message to store

    const artifactKeywords = ["generate", "show me", "what is", "create", "display"];
    const shouldGenerateArtifact = artifactKeywords.some(keyword => newMessageText.toLowerCase().includes(keyword));

    if (shouldGenerateArtifact) {
      await handleGenerateArtifact(newMessageText);
    }

    try {
      const response = await fetch('http://localhost:3001/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: newMessageText }),
      });

      const responseData = await response.json();
      if (!response.ok || !responseData.success) {
        const errorText = responseData.message || await response.text();
        console.error('Chat API Error (POST):', response.status, errorText);
        if (!socketRef.current || !socketRef.current.connected) {
          addMessage({
            id: Date.now().toString() + '-http-post-error',
            text: `Error: Message not sent to server. Status: ${response.status}. ${errorText}`,
            sender: 'ai',
          });
        }
      } else {
        console.log("Message POST successful, waiting for WebSocket reply...");
      }
    } catch (error) {
      console.error('Fetch Chat Error (POST):', error);
      if (!socketRef.current || !socketRef.current.connected) {
        addMessage({
          id: Date.now().toString() + '-http-post-fetch-error',
          text: 'Error: Failed to send message to server. Check connection.',
          sender: 'ai',
        });
      }
    }
  };
  
  // isArtifactVisible will be selected by ArtifactWindow itself or a wrapper here
  const isArtifactVisible = useAppStore(state => state.isArtifactVisible);

  return (
    <div className="App flex flex-col md:flex-row h-screen bg-gray-100">
      <div className="flex-grow md:w-3/5 lg:w-2/3 p-2 flex flex-col">
        {/* ChatWindow will get messages from store, onSendMessage is passed from App */}
        <ChatWindow onSendMessage={handleSendMessage} />
      </div>
      {isArtifactVisible && (
        <div className="md:w-2/5 lg:w-1/3 p-2 flex flex-col">
          {/* ArtifactWindow will get its state from store */}
          <ArtifactWindow /> 
        </div>
      )}
    </div>
  );
}

export default App;
