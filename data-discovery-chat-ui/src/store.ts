import { create } from 'zustand';

export interface Message {
  id: string;
  text: string;
  sender: 'user' | 'ai' | 'ai_error';
  isStreaming?: boolean;
}

// --- Artifact Types ---
export interface BaseArtifactData {
  id: string; // Unique ID for this streaming artifact instance
  type: 'code' | 'data' | 'message';
  isStreaming: boolean;
  title?: string; // Generic title, can be set from metadata
}

export interface CodeArtifactData extends BaseArtifactData {
  type: 'code';
  language: string;
  content: string;
}

export interface DataArtifactData extends BaseArtifactData {
  type: 'data';
  format: string; // e.g., 'json_table_rows'
  columns: string[];
  rows: any[][];
}

export interface MessageArtifactData extends BaseArtifactData {
  type: 'message';
  content: string;
}

export type ArtifactContentType = CodeArtifactData | DataArtifactData | MessageArtifactData | string | null;
// 'string' is for simple error messages or non-typed content, null when no artifact

// --- Socket.IO Event Payload Types for Artifact Streaming ---
export interface ArtifactStreamStartPayload {
  artifact_id: string;
  artifact_type: 'code' | 'data' | 'message';
  metadata: any; // e.g., { language: 'python', title: 'My Script' } or { title: 'Sales Data', columns: ['A', 'B'] }
}

export interface ArtifactStreamChunkPayload {
  artifact_id: string;
  chunk_data: any; // string for code, array for data row
}

export interface ArtifactStreamEndPayload {
  artifact_id: string;
}

// --- Chat Message Streaming Types (already defined) ---
export interface AiMessageChunk { id: string; text: string; sender: 'ai' | 'ai_error'; is_first_chunk: boolean; }
export interface AiMessageEnd { id: string; sender: 'ai' | 'ai_error'; full_response: string; }

interface AppState {
  messages: Message[];
  artifactContent: ArtifactContentType;
  isArtifactVisible: boolean;
  socketConnected: boolean;
  addMessage: (message: Message) => void;
  closeArtifact: () => void;
  setSocketConnected: (isConnected: boolean) => void;
  handleAiMessageChunk: (chunk: AiMessageChunk) => void;
  handleAiMessageEnd: (data: AiMessageEnd) => void;
  handleArtifactStreamStart: (payload: ArtifactStreamStartPayload) => void;
  handleArtifactStreamChunk: (payload: ArtifactStreamChunkPayload) => void;
  handleArtifactStreamEnd: (payload: ArtifactStreamEndPayload) => void;
}

export const useAppStore = create<AppState>((set, get) => ({
  messages: [],
  artifactContent: null,
  isArtifactVisible: false,
  socketConnected: false,

  addMessage: (message) => set((state) => ({ messages: [...state.messages, message] })),
  closeArtifact: () => set(() => ({ isArtifactVisible: false, artifactContent: null })),
  setSocketConnected: (isConnected) => set(() => ({ socketConnected: isConnected })),

  handleAiMessageChunk: (chunk) => set((state) => {
    const existingMsgIdx = state.messages.findIndex(m => m.id === chunk.id);
    if (chunk.is_first_chunk || existingMsgIdx === -1) {
      return { messages: [...state.messages, { id: chunk.id, text: chunk.text, sender: chunk.sender, isStreaming: true }] };
    } else {
      const newMessages = [...state.messages];
      newMessages[existingMsgIdx] = { ...newMessages[existingMsgIdx], text: newMessages[existingMsgIdx].text + chunk.text, sender: chunk.sender, isStreaming: true };
      return { messages: newMessages };
    }
  }),

  handleAiMessageEnd: (data) => set((state) => {
    const existingMsgIdx = state.messages.findIndex(m => m.id === data.id);
    if (existingMsgIdx !== -1) {
      const newMessages = [...state.messages];
      newMessages[existingMsgIdx] = { ...newMessages[existingMsgIdx], text: data.full_response, sender: data.sender, isStreaming: false };
      return { messages: newMessages };
    } else { // Should not happen if first_chunk logic is robust
      return { messages: [...state.messages, { id: data.id, text: data.full_response, sender: data.sender, isStreaming: false }] };
    }
  }),

  handleArtifactStreamStart: (payload) => {
    let newArtifact: ArtifactContentType = null;
    if (payload.artifact_type === 'code') {
      newArtifact = {
        id: payload.artifact_id,
        type: 'code',
        language: payload.metadata?.language || 'plaintext',
        title: payload.metadata?.title || 'Code Snippet',
        content: '',
        isStreaming: true,
      };
    } else if (payload.artifact_type === 'data') {
      newArtifact = {
        id: payload.artifact_id,
        type: 'data',
        format: payload.metadata?.format || 'json_table_rows',
        title: payload.metadata?.title || 'Data Table',
        columns: payload.metadata?.columns || [],
        rows: [],
        isStreaming: true,
      };
    } else if (payload.artifact_type === 'message') {
      newArtifact = {
        id: payload.artifact_id,
        type: 'message',
        title: payload.metadata?.title || 'Message',
        content: '',
        isStreaming: true,
      };
    }
    set({ artifactContent: newArtifact, isArtifactVisible: true });
  },

  handleArtifactStreamChunk: (payload) => set((state) => {
    if (!state.artifactContent || typeof state.artifactContent === 'string' || state.artifactContent.id !== payload.artifact_id) {
      console.error('Artifact chunk received for unknown or mismatched artifact ID:', payload, state.artifactContent);
      return {}; // No change
    }
    let updatedContent = state.artifactContent;
    if (updatedContent.type === 'code' && typeof payload.chunk_data === 'string') {
      updatedContent = { ...updatedContent, content: updatedContent.content + payload.chunk_data };
    } else if (updatedContent.type === 'data' && Array.isArray(payload.chunk_data)) {
      updatedContent = { ...updatedContent, rows: [...updatedContent.rows, payload.chunk_data] };
    } else if (updatedContent.type === 'message' && typeof payload.chunk_data === 'string') {
      updatedContent = { ...updatedContent, content: updatedContent.content + payload.chunk_data };
    }
    return { artifactContent: updatedContent };
  }),

  handleArtifactStreamEnd: (payload) => set((state) => {
    if (!state.artifactContent || typeof state.artifactContent === 'string' || state.artifactContent.id !== payload.artifact_id) {
      return {}; // No change if artifact not found or ID mismatch
    }
    return { artifactContent: { ...state.artifactContent, isStreaming: false } };
  }),
}));
