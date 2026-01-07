"use client";

import { useState, useEffect, useRef } from "react";
import Link from "next/link";
import {
  MessageSquare,
  Send,
  Sparkles,
  Target,
  BarChart3,
  Gamepad2,
  Zap,
  Bot,
  User,
  Trash2,
  Plus,
  Database,
  FileText,
  TrendingUp,
  Loader2,
  ExternalLink,
} from "lucide-react";
import {
  createChatSession,
  listChatSessions,
  getChatSessionHistory,
  sendChatMessage,
  deleteChatSession,
  getDocumentCounts,
} from "@/lib/api/chat";
import type {
  ChatSession,
  ChatMessage,
  ChatSource,
  DocumentCountResponse,
} from "@/types/chat";
import { motion, AnimatePresence } from "framer-motion";

export default function AssistantPage() {
  // Session management
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [currentSession, setCurrentSession] = useState<ChatSession | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [sessionLoading, setSessionLoading] = useState(false);

  // Message input
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);

  // Sources
  const [sources, setSources] = useState<ChatSource[]>([]);
  const [showSources, setShowSources] = useState(false);

  // Document stats
  const [docCounts, setDocCounts] = useState<DocumentCountResponse | null>(null);

  // Refs
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const navItems = [
    {
      id: "predictions",
      label: "ML Predictions",
      icon: Target,
      href: "/predictions",
      active: false,
    },
    {
      id: "dashboard",
      label: "Dashboard",
      icon: BarChart3,
      href: "/dashboard",
      active: false,
    },
    {
      id: "strategy",
      label: "Strategy Simulator",
      icon: Gamepad2,
      href: "/strategy",
      active: false,
    },
    {
      id: "assistant",
      label: "AI Assistant",
      icon: MessageSquare,
      href: "/assistant",
      active: true,
    },
  ];

  // Load sessions on mount
  useEffect(() => {
    loadSessions();
    loadDocumentCounts();
  }, []);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Focus input when session changes
  useEffect(() => {
    inputRef.current?.focus();
  }, [currentSession]);

  const loadSessions = async () => {
    try {
      setSessionLoading(true);
      const response = await listChatSessions({ limit: 50 });
      setSessions(response.sessions);

      // Auto-select first session if exists
      if (response.sessions.length > 0 && !currentSession) {
        await selectSession(response.sessions[0].id);
      }
    } catch (err) {
      console.error("Failed to load sessions:", err);
    } finally {
      setSessionLoading(false);
    }
  };

  const loadDocumentCounts = async () => {
    try {
      const counts = await getDocumentCounts();
      setDocCounts(counts);
    } catch (err) {
      console.error("Failed to load document counts:", err);
    }
  };

  const selectSession = async (sessionId: string) => {
    try {
      setLoading(true);
      const history = await getChatSessionHistory(sessionId);
      setCurrentSession(history.session);
      setMessages(history.messages);
      setSources([]);
      setShowSources(false);
    } catch (err) {
      console.error("Failed to load session:", err);
    } finally {
      setLoading(false);
    }
  };

  const createNewSession = async () => {
    try {
      setSessionLoading(true);
      const session = await createChatSession({
        title: `Chat ${new Date().toLocaleString()}`,
      });
      setSessions([session, ...sessions]);
      setCurrentSession(session);
      setMessages([]);
      setSources([]);
      setShowSources(false);
    } catch (err) {
      console.error("Failed to create session:", err);
    } finally {
      setSessionLoading(false);
    }
  };

  const deleteSession = async (sessionId: string) => {
    try {
      await deleteChatSession(sessionId);
      setSessions(sessions.filter((s) => s.id !== sessionId));
      if (currentSession?.id === sessionId) {
        setCurrentSession(null);
        setMessages([]);
        setSources([]);
      }
    } catch (err) {
      console.error("Failed to delete session:", err);
    }
  };

  const handleSendMessage = async () => {
    if (!input.trim() || sending || !currentSession) return;

    const userMessage = input.trim();
    setInput("");
    setSending(true);

    // Optimistically add user message
    const tempMessage: ChatMessage = {
      id: "temp",
      role: "user",
      content: userMessage,
      created_at: new Date().toISOString(),
    };
    setMessages([...messages, tempMessage]);

    try {
      const response = await sendChatMessage(currentSession.id, {
        message: userMessage,
        use_rag: true,
        top_k: 5,
        similarity_threshold: 0.7,
      });

      // Update with real messages
      setMessages([
        ...messages,
        {
          id: `user-${Date.now()}`,
          role: "user",
          content: userMessage,
          created_at: new Date().toISOString(),
        },
        response.message,
      ]);

      // Update sources
      if (response.sources && response.sources.length > 0) {
        setSources(response.sources);
        setShowSources(true);
      }
    } catch (err) {
      console.error("Failed to send message:", err);
      // Remove temp message on error
      setMessages(messages);
    } finally {
      setSending(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-red-950/20 to-slate-950 text-white">
      {/* Navigation */}
      <nav className="border-b border-red-500/20 bg-slate-950/50 backdrop-blur-xl">
        <div className="max-w-[1920px] mx-auto px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-8">
              <Link href="/" className="flex items-center gap-3 group">
                <div className="relative">
                  <div className="absolute inset-0 bg-red-500/20 blur-xl rounded-full group-hover:bg-red-500/30 transition-all" />
                  <Zap className="h-8 w-8 text-red-500 relative" />
                </div>
                <div className="flex flex-col">
                  <span className="text-xl font-bold bg-gradient-to-r from-red-500 to-orange-500 bg-clip-text text-transparent">
                    F1 Intelligence
                  </span>
                  <span className="text-xs text-slate-400">AI Assistant</span>
                </div>
              </Link>

              <div className="flex items-center gap-2">
                {navItems.map((item) => {
                  const Icon = item.icon;
                  return (
                    <Link
                      key={item.id}
                      href={item.href}
                      className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
                        item.active
                          ? "bg-gradient-to-r from-red-500/20 to-orange-500/20 text-white border border-red-500/30"
                          : "text-slate-400 hover:text-white hover:bg-slate-800/50"
                      }`}
                    >
                      <Icon className="h-4 w-4" />
                      <span className="text-sm font-medium">{item.label}</span>
                    </Link>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-[1920px] mx-auto px-8 py-8">
        <div className="grid grid-cols-12 gap-6 h-[calc(100vh-120px)]">
          {/* Session Sidebar */}
          <div className="col-span-3 flex flex-col gap-4">
            {/* Stats Card */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-gradient-to-br from-slate-900/90 to-slate-800/90 rounded-2xl p-6 border border-red-500/20 backdrop-blur-xl"
            >
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 bg-gradient-to-br from-red-500/20 to-orange-500/20 rounded-lg">
                  <Database className="h-5 w-5 text-red-400" />
                </div>
                <h3 className="text-sm font-semibold text-slate-300">
                  Knowledge Base
                </h3>
              </div>

              {docCounts && (
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-xs text-slate-400">Total Documents</span>
                    <span className="text-lg font-bold text-white">
                      {docCounts.total}
                    </span>
                  </div>
                  {Object.entries(docCounts.counts).map(([type, count]) => (
                    <div key={type} className="flex justify-between items-center">
                      <span className="text-xs text-slate-500 capitalize">
                        {type.replace("_", " ")}
                      </span>
                      <span className="text-sm text-slate-300">{count}</span>
                    </div>
                  ))}
                </div>
              )}
            </motion.div>

            {/* Sessions List */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="flex-1 bg-gradient-to-br from-slate-900/90 to-slate-800/90 rounded-2xl p-6 border border-red-500/20 backdrop-blur-xl overflow-hidden flex flex-col"
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-semibold text-slate-300">
                  Chat History
                </h3>
                <button
                  onClick={createNewSession}
                  disabled={sessionLoading}
                  className="p-2 bg-gradient-to-r from-red-500/20 to-orange-500/20 hover:from-red-500/30 hover:to-orange-500/30 rounded-lg transition-all disabled:opacity-50"
                >
                  {sessionLoading ? (
                    <Loader2 className="h-4 w-4 text-red-400 animate-spin" />
                  ) : (
                    <Plus className="h-4 w-4 text-red-400" />
                  )}
                </button>
              </div>

              <div className="flex-1 overflow-y-auto space-y-2">
                {sessions.map((session) => (
                  <div
                    key={session.id}
                    className={`group flex items-center justify-between p-3 rounded-lg cursor-pointer transition-all ${
                      currentSession?.id === session.id
                        ? "bg-gradient-to-r from-red-500/20 to-orange-500/20 border border-red-500/30"
                        : "bg-slate-800/50 hover:bg-slate-700/50"
                    }`}
                    onClick={() => selectSession(session.id)}
                  >
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-white truncate">
                        {session.title}
                      </p>
                      <p className="text-xs text-slate-400">
                        {new Date(session.updated_at).toLocaleDateString()}
                      </p>
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        deleteSession(session.id);
                      }}
                      className="opacity-0 group-hover:opacity-100 p-1 hover:bg-red-500/20 rounded transition-all"
                    >
                      <Trash2 className="h-4 w-4 text-red-400" />
                    </button>
                  </div>
                ))}

                {sessions.length === 0 && !sessionLoading && (
                  <div className="text-center py-8">
                    <MessageSquare className="h-12 w-12 text-slate-600 mx-auto mb-3" />
                    <p className="text-sm text-slate-500">No chat history</p>
                    <p className="text-xs text-slate-600 mt-1">
                      Create a new session to start
                    </p>
                  </div>
                )}
              </div>
            </motion.div>
          </div>

          {/* Chat Area */}
          <div className="col-span-9 flex flex-col gap-4">
            {currentSession ? (
              <>
                {/* Messages */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex-1 bg-gradient-to-br from-slate-900/90 to-slate-800/90 rounded-2xl border border-red-500/20 backdrop-blur-xl overflow-hidden flex flex-col"
                >
                  <div className="flex-1 overflow-y-auto p-6 space-y-6">
                    {messages.length === 0 && !loading && (
                      <div className="flex items-center justify-center h-full">
                        <div className="text-center">
                          <div className="relative inline-block mb-6">
                            <div className="absolute inset-0 bg-red-500/20 blur-2xl rounded-full" />
                            <Bot className="h-16 w-16 text-red-400 relative" />
                          </div>
                          <h2 className="text-2xl font-bold mb-2 bg-gradient-to-r from-red-400 to-orange-400 bg-clip-text text-transparent">
                            F1 Intelligence Assistant
                          </h2>
                          <p className="text-slate-400 max-w-md">
                            Ask me anything about F1 data, race sessions, driver
                            performance, or strategies. I'm powered by AI and have
                            access to comprehensive race data.
                          </p>
                        </div>
                      </div>
                    )}

                    <AnimatePresence>
                      {messages.map((message, idx) => (
                        <motion.div
                          key={message.id}
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          exit={{ opacity: 0, y: -20 }}
                          transition={{ delay: idx * 0.05 }}
                          className={`flex gap-4 ${
                            message.role === "user" ? "justify-end" : ""
                          }`}
                        >
                          {message.role === "assistant" && (
                            <div className="flex-shrink-0">
                              <div className="p-2 bg-gradient-to-br from-red-500/20 to-orange-500/20 rounded-lg">
                                <Bot className="h-5 w-5 text-red-400" />
                              </div>
                            </div>
                          )}

                          <div
                            className={`flex-1 max-w-3xl ${
                              message.role === "user" ? "flex justify-end" : ""
                            }`}
                          >
                            <div
                              className={`p-4 rounded-2xl ${
                                message.role === "user"
                                  ? "bg-gradient-to-r from-red-500/20 to-orange-500/20 border border-red-500/30"
                                  : "bg-slate-800/50"
                              }`}
                            >
                              <p className="text-sm text-white whitespace-pre-wrap">
                                {message.content}
                              </p>
                              {message.metadata?.num_sources && (
                                <div className="mt-2 pt-2 border-t border-slate-700/50">
                                  <p className="text-xs text-slate-400">
                                    <Sparkles className="h-3 w-3 inline mr-1" />
                                    Based on {message.metadata.num_sources} sources
                                  </p>
                                </div>
                              )}
                            </div>
                          </div>

                          {message.role === "user" && (
                            <div className="flex-shrink-0">
                              <div className="p-2 bg-slate-700/50 rounded-lg">
                                <User className="h-5 w-5 text-slate-300" />
                              </div>
                            </div>
                          )}
                        </motion.div>
                      ))}
                    </AnimatePresence>

                    {loading && (
                      <div className="flex justify-center">
                        <Loader2 className="h-6 w-6 text-red-400 animate-spin" />
                      </div>
                    )}

                    <div ref={messagesEndRef} />
                  </div>

                  {/* Input */}
                  <div className="border-t border-red-500/20 p-4 bg-slate-900/50">
                    <div className="flex gap-3">
                      <textarea
                        ref={inputRef}
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="Ask about F1 data, race sessions, driver performance..."
                        disabled={sending}
                        rows={1}
                        className="flex-1 bg-slate-800/50 border border-red-500/20 rounded-xl px-4 py-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-red-500/50 resize-none disabled:opacity-50"
                      />
                      <button
                        onClick={handleSendMessage}
                        disabled={!input.trim() || sending}
                        className="px-6 py-3 bg-gradient-to-r from-red-500 to-orange-500 hover:from-red-600 hover:to-orange-600 rounded-xl font-semibold transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                      >
                        {sending ? (
                          <Loader2 className="h-5 w-5 animate-spin" />
                        ) : (
                          <Send className="h-5 w-5" />
                        )}
                      </button>
                    </div>
                  </div>
                </motion.div>

                {/* Sources Panel */}
                {showSources && sources.length > 0 && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    className="bg-gradient-to-br from-slate-900/90 to-slate-800/90 rounded-2xl p-6 border border-red-500/20 backdrop-blur-xl"
                  >
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-sm font-semibold text-slate-300 flex items-center gap-2">
                        <FileText className="h-4 w-4 text-red-400" />
                        Sources ({sources.length})
                      </h3>
                      <button
                        onClick={() => setShowSources(false)}
                        className="text-xs text-slate-500 hover:text-slate-300"
                      >
                        Hide
                      </button>
                    </div>

                    <div className="grid grid-cols-2 gap-3">
                      {sources.map((source, idx) => (
                        <div
                          key={idx}
                          className="p-3 bg-slate-800/50 rounded-lg border border-slate-700/50"
                        >
                          <div className="flex items-start justify-between mb-2">
                            <p className="text-xs font-medium text-white truncate flex-1">
                              {source.document_title}
                            </p>
                            <span className="text-xs text-red-400 ml-2">
                              {(source.similarity * 100).toFixed(0)}%
                            </span>
                          </div>
                          <p className="text-xs text-slate-400 line-clamp-2">
                            {source.chunk_text}
                          </p>
                          <p className="text-xs text-slate-600 mt-1">
                            {source.document_type}
                          </p>
                        </div>
                      ))}
                    </div>
                  </motion.div>
                )}
              </>
            ) : (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex-1 bg-gradient-to-br from-slate-900/90 to-slate-800/90 rounded-2xl border border-red-500/20 backdrop-blur-xl flex items-center justify-center"
              >
                <div className="text-center">
                  <MessageSquare className="h-16 w-16 text-slate-600 mx-auto mb-4" />
                  <h2 className="text-xl font-bold text-slate-400 mb-2">
                    No Session Selected
                  </h2>
                  <p className="text-sm text-slate-500 mb-6">
                    Select a chat session or create a new one to start
                  </p>
                  <button
                    onClick={createNewSession}
                    disabled={sessionLoading}
                    className="px-6 py-3 bg-gradient-to-r from-red-500 to-orange-500 hover:from-red-600 hover:to-orange-600 rounded-xl font-semibold transition-all disabled:opacity-50 flex items-center gap-2 mx-auto"
                  >
                    <Plus className="h-5 w-5" />
                    New Chat Session
                  </button>
                </div>
              </motion.div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
