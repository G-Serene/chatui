import { create } from 'zustand';

// Interfaces (can be moved to a separate types.ts file if preferred)
export interface Message {
  id: string;
  text: string;
  sender: 'user' | 'ai';
}

export type ArtifactContentType = string | CodeArtifact | DataArtifact | MessageArtifactData;

export interface CodeArtifact {
  type: 'code';
  language: string;
  content: string;
}

export interface DataArtifact {
  type: 'data';
  format: string; // e.g., 'json', 'csv'
  content: {
    title?: string;
    columns: string[];
    rows: any[][];
  };
}

export interface MessageArtifactData { // Renamed to avoid conflict with Message interface
  type: 'message';
  content: string;
}

interface AppState {
  messages: Message[];
  artifactContent: ArtifactContentType | null;
  isArtifactVisible: boolean;
  socketConnected: boolean;
  
  // Actions
  addMessage: (message: Message) => void;
  setArtifact: (content: ArtifactContentType) => void;
  closeArtifact: () => void;
  setSocketConnected: (isConnected: boolean) => void;
  clearChat: () => void; // Example of another useful action
}

export const useAppStore = create<AppState>((set) => ({
  messages: [],
  artifactContent: null,
  isArtifactVisible: false,
  socketConnected: false,

  addMessage: (message) => 
    set((state) => ({ messages: [...state.messages, message] })),

  setArtifact: (content) => 
    set(() => ({ artifactContent: content, isArtifactVisible: true })),

  closeArtifact: () => 
    set(() => ({ isArtifactVisible: false, artifactContent: null })), // Also clear content on close

  setSocketConnected: (isConnected) => 
    set(() => ({ socketConnected: isConnected })),
  
  clearChat: () => 
    set(() => ({ messages: [] })),
}));

// Initialize with a default message or artifact if needed for testing/UX
// useAppStore.getState().setArtifact({
//   type: 'message',
//   content: "Welcome! Try sending a message or a query like 'generate sales table'."
// });
// useAppStore.getState().addMessage({
//   id: 'initial-ai-message',
//   text: "Hello! I'm your Data Discovery Assistant. How can I help you today?",
//   sender: 'ai'
// });
