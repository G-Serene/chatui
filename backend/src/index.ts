import express, { Request, Response } from 'express';
import cors from 'cors';
import http from 'http';
import { Server as SocketIOServer } from 'socket.io';
import { v4 as uuidv4 } from 'uuid';

const app = express();
const server = http.createServer(app);
const io = new SocketIOServer(server, {
  cors: {
    origin: "http://localhost:5173", // Frontend URL
    methods: ["GET", "POST"]
  }
});

const port = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json());

interface ChatRequestBody {
  message: string;
}

// POST endpoint for /api/chat
app.post('/api/chat', (req: Request, res: Response) => {
  const body = req.body as ChatRequestBody;

  if (!body || typeof body.message !== 'string') {
    return res.status(400).json({ error: 'Invalid request body, "message" field is required and must be a string.' });
  }

  const receivedMessage = body.message;
  const lowerCaseMessage = receivedMessage.toLowerCase();
  console.log(`Received message via HTTP POST: "${receivedMessage}"`);

  setTimeout(() => {
    let aiReplyText: string;
    const discoveryKeywords = ["find", "search", "generate", "show me", "what is", "create", "display"];

    if (discoveryKeywords.some(keyword => lowerCaseMessage.includes(keyword))) {
      aiReplyText = "I've processed your request. If it's something I can generate an artifact for, you might see it in the artifact window, or you can try a more specific command like 'generate sales data table'.";
    } else {
      aiReplyText = `AI says: You sent "${receivedMessage}". This is a mock AI response.`;
    }
    
    const aiMessage = {
      id: uuidv4(),
      text: aiReplyText,
      sender: 'ai' as 'user' | 'ai'
    };
    
    io.emit('ai_message', aiMessage); 
    console.log(`Emitted ai_message: "${aiReplyText}"`);
  }, 500);

  res.status(200).json({ success: true, message: "Message received and is being processed." });
});

// --- Artifact Generation Logic ---

interface ArtifactDefinition {
  id: string;
  description: string;
  keywords: string[];
  artifact: CodeArtifact | DataArtifact | MessageArtifact; // Using existing types
}

interface ArtifactRequestBody {
  query: string;
}

interface CodeArtifact {
  type: 'code';
  language: string;
  content: string;
}

interface DataArtifact {
  type: 'data';
  format: string;
  content: Record<string, any>; 
}

interface MessageArtifact {
  type: 'message';
  content: string;
}

type ArtifactResponseBody = CodeArtifact | DataArtifact | MessageArtifact;

const mockArtifacts: ArtifactDefinition[] = [
  {
    id: 'sales-data-table',
    description: 'A mock JSON data table for sales figures.',
    keywords: ["sales", "revenue", "table", "data", "report"],
    artifact: {
      type: 'data',
      format: 'json',
      content: {
        title: "Quarterly Sales Report",
        columns: ["Quarter", "Product Category", "Total Sales", "Units Sold"],
        rows: [
          ["Q1 2024", "Electronics", 150000, 350],
          ["Q1 2024", "Appliances", 120000, 200],
          ["Q2 2024", "Electronics", 175000, 400],
          ["Q2 2024", "Appliances", 110000, 180],
        ]
      }
    }
  },
  {
    id: 'product-inventory-table',
    description: 'A mock JSON data table for product inventory.',
    keywords: ["product", "inventory", "stock", "table", "data"],
    artifact: {
        type: 'data',
        format: 'json',
        content: {
            title: "Product Inventory Levels",
            columns: ["Product ID", "Name", "Category", "Stock Level", "Reorder Point"],
            rows: [
                ["PID001", "Laptop Pro X", "Electronics", 75, 50],
                ["PID002", "Smart Thermostat", "Home Automation", 120, 100],
                ["PID003", "Wireless Mouse", "Accessories", 300, 150],
                ["PID004", "Coffee Maker Deluxe", "Appliances", 45, 50],
            ]
        }
    }
  },
  {
    id: 'python-user-processing-script',
    description: 'A mock Python code snippet for user processing.',
    keywords: ["python", "user", "script", "code", "processing", "analysis"],
    artifact: {
      type: 'code',
      language: 'python',
      content: "# Mock Python script for user data processing\n\ndef process_users(user_list):\n  active_users = []\n  for user in user_list:\n    if user.get('is_active'):\n      print(f\"Processing active user: {user.get('name')}\")\n      active_users.append(user)\n  return active_users\n\n# Example usage:\n# users = [{'name': 'Alice', 'is_active': True}, {'name': 'Bob', 'is_active': False}]\n# process_users(users)"
    }
  },
  {
    id: 'sql-active-customers-query',
    description: 'A mock SQL query for fetching active customers.',
    keywords: ["sql", "active", "customer", "query", "database"],
    artifact: {
      type: 'code',
      language: 'sql',
      content: "SELECT\n  customer_id,\n  first_name,\n  last_name,\n  email,\n  last_login_date\nFROM\n  customers\nWHERE\n  is_active = TRUE\n  AND last_login_date >= CURRENT_DATE - INTERVAL '30 days'\nORDER BY\n  last_login_date DESC;"
    }
  },
  {
    id: 'javascript-ui-validation-script',
    description: 'A mock JavaScript code snippet for UI form validation.',
    keywords: ["javascript", "js", "ui", "form", "validation", "script", "code"],
    artifact: {
      type: 'code',
      language: 'javascript',
      content: "// Mock JavaScript for UI form validation\n\nfunction validateEmail(email) {\n  if (!email) return false;\n  const emailRegex = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;\n  return emailRegex.test(email);\n}\n\nfunction validatePassword(password) {\n  if (!password || password.length < 8) return false;\n  // Add more complex rules if needed\n  return true;\n}\n\n// Example usage:\n// const emailInput = document.getElementById('email');\n// const isValid = validateEmail(emailInput.value);\n// console.log('Email is valid:', isValid);"
    }
  }
];

// POST endpoint for /api/generate-artifact
app.post('/api/generate-artifact', (req: Request, res: Response) => {
  const body = req.body as ArtifactRequestBody;

  if (!body || typeof body.query !== 'string') {
    return res.status(400).json({ error: 'Invalid request body, "query" field is required and must be a string.' });
  }

  const query = body.query.toLowerCase();
  console.log(`Received artifact generation query: "${body.query}"`);

  let matchedArtifact: ArtifactResponseBody | null = null;

  for (const item of mockArtifacts) {
    if (item.keywords.some(keyword => query.includes(keyword.toLowerCase()))) {
      matchedArtifact = item.artifact;
      console.log(`Matched artifact: "${item.description}" based on query keywords.`);
      break; 
    }
  }

  if (matchedArtifact) {
    res.json(matchedArtifact);
  } else {
    console.log('No specific artifact matched. Returning default message.');
    res.json({
      type: "message",
      content: "No specific artifact could be generated for your query. Please try phrases like 'generate sales table' or 'show python script for users'."
    } as MessageArtifact);
  }
});

// Socket.IO connection handling
io.on('connection', (socket) => {
  console.log(`User connected: ${socket.id}`);

  socket.on('disconnect', () => {
    console.log(`User disconnected: ${socket.id}`);
  });

  // Example: listen for messages from client (optional for current task)
  // socket.on('user_message', (msg) => {
  //   console.log(`Message from ${socket.id}: ${msg.text}`);
  //   // Here you could broadcast this message to other users if it's a group chat
  // });
});


// Start the server
server.listen(port, () => { // Use server.listen instead of app.listen
  console.log(`Backend server with Socket.IO is running on http://localhost:${port}`);
});
