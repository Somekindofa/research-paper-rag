import React, { useState, useEffect, useRef } from 'react';
import './App.css';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: Source[];
  mode?: string;
}

interface Source {
  title: string;
  authors: string;
  year: number;
  score: number;
  content: string;
  index: number;
}

interface Status {
  lm_studio_status: string;
  available_models: string[];
  library_status: {
    total_pdfs?: number;
    indexed_pdfs?: number;
    chunks?: number;
    pending_pdfs?: number;
    error?: string;
  };
  indexing_in_progress: boolean;
  indexing_status: string;
}

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [forceRetrieval, setForceRetrieval] = useState(false);
  const [selectedModel, setSelectedModel] = useState('');
  const [numDocs, setNumDocs] = useState(5);
  const [threshold, setThreshold] = useState(75);
  const [status, setStatus] = useState<Status | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/status');
      const data = await response.json();
      setStatus(data);
      if (data.available_models.length > 0 && !selectedModel) {
        setSelectedModel(data.available_models[0]);
      }
    } catch (error) {
      console.error('Error fetching status:', error);
    }
  };

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: Message = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: input,
          force_retrieval: forceRetrieval,
          selected_model: selectedModel,
          num_docs: numDocs,
          relevance_threshold: threshold / 100
        })
      });

      const data = await response.json();
      const assistantMessage: Message = {
        role: 'assistant',
        content: data.answer,
        sources: data.sources,
        mode: data.mode
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Error: Could not connect to the server.'
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const startIndexing = async () => {
    try {
      await fetch('http://localhost:8000/api/index', { method: 'POST' });
      fetchStatus();
    } catch (error) {
      console.error('Error starting indexing:', error);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="App">
      <header className="app-header">
        <h1>📚 Research RAG Assistant</h1>
        <p>AI-powered research paper query and analysis system</p>
      </header>

      <div className="main-container">
        <div className="chat-column">
          <div className="force-retrieval-toggle">
            <label>
              <input
                type="checkbox"
                checked={forceRetrieval}
                onChange={(e) => setForceRetrieval(e.target.checked)}
              />
              🔍 <strong>Force Retrieval</strong>
            </label>
            <p className="toggle-info">
              {forceRetrieval
                ? '✓ ON: Searching documents with citations'
                : '✗ OFF: Simple LLM chat (faster)'}
            </p>
          </div>

          <div className="chat-messages">
            {messages.map((msg, idx) => (
              <div key={idx} className={`message ${msg.role}`}>
                <div className="message-content">
                  {msg.content}
                  {msg.mode && (
                    <span className="mode-badge">{msg.mode}</span>
                  )}
                </div>
                {msg.sources && msg.sources.length > 0 && (
                  <div className="sources">
                    <h4>📚 Sources ({msg.sources.length}):</h4>
                    {msg.sources.map((source, sidx) => (
                      <div key={sidx} className="source">
                        <strong>[{source.index}] {source.title}</strong>
                        <br />
                        <em>{source.authors}</em> ({source.year}) - Score: {source.score.toFixed(2)}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
            {loading && (
              <div className="message assistant loading">
                <div className="loading-dots">Thinking...</div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="chat-input">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask a question about your research papers..."
              rows={3}
              disabled={loading}
            />
            <button onClick={sendMessage} disabled={loading || !input.trim()}>
              {loading ? 'Sending...' : 'Send'}
            </button>
          </div>
        </div>

        <div className="settings-column">
          <div className="settings-panel">
            <h3>⚙️ Settings</h3>

            <div className="setting-item">
              <label htmlFor="model">🤖 Model</label>
              <select
                id="model"
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
              >
                {status?.available_models.map((model) => (
                  <option key={model} value={model}>
                    {model}
                  </option>
                ))}
              </select>
            </div>

            <div className="setting-item">
              <label htmlFor="numDocs">
                📄 Documents: {numDocs}
              </label>
              <input
                type="range"
                id="numDocs"
                min="1"
                max="20"
                value={numDocs}
                onChange={(e) => setNumDocs(parseInt(e.target.value))}
              />
            </div>

            <div className="setting-item">
              <label htmlFor="threshold">
                🎯 Relevance: {threshold}%
              </label>
              <input
                type="range"
                id="threshold"
                min="50"
                max="100"
                step="5"
                value={threshold}
                onChange={(e) => setThreshold(parseInt(e.target.value))}
              />
            </div>
          </div>

          <div className="status-panel">
            <h3>📊 System Status</h3>

            <div className="status-item">
              <strong>LM Studio:</strong>
              <span className={`status-badge ${status?.lm_studio_status}`}>
                {status?.lm_studio_status || 'checking...'}
              </span>
            </div>

            {status?.library_status && !status.library_status.error && (
              <>
                <div className="status-item">
                  <strong>PDFs:</strong> {status.library_status.total_pdfs || 0}
                </div>
                <div className="status-item">
                  <strong>Indexed:</strong> {status.library_status.indexed_pdfs || 0}
                </div>
                <div className="status-item">
                  <strong>Chunks:</strong> {status.library_status.chunks || 0}
                </div>
                <div className="status-item">
                  <strong>Pending:</strong> {status.library_status.pending_pdfs || 0}
                </div>
              </>
            )}
          </div>

          <div className="indexing-panel">
            <h3>📥 Indexing</h3>
            {status?.indexing_in_progress ? (
              <div className="indexing-status">
                {status.indexing_status}
              </div>
            ) : (
              <button onClick={startIndexing} className="index-button">
                Start Indexing
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
