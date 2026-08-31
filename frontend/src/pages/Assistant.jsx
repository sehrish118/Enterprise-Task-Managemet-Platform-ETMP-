import { useState, useRef, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { ArrowLeft, Send, Bot, User as UserIcon, Plus, Trash2, MessageSquare, Paperclip, X, Loader2, CheckCircle2 } from "lucide-react";
import client from "../api/client";
import Card from "../components/Card";
import Button from "../components/Button";
import { useAuth } from "../context/AuthContext";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export default function Assistant() {
    const { orgId } = useParams();
    const { user: currentUser } = useAuth();

    const [sessions, setSessions] = useState([]);
    const [activeSessionId, setActiveSessionId] = useState(null);
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);
    const [sessionsLoading, setSessionsLoading] = useState(true);
    const [error, setError] = useState("");
    const bottomRef = useRef(null);
    const API_BASE = client.defaults.baseURL;
    const [attachedFile, setAttachedFile] = useState(null); // { id, filename, status }
    const [uploading, setUploading] = useState(false);
    const fileInputRef = useRef(null);

    const loadSessions = () => {
        setSessionsLoading(true);
        client
            .get(`/organizations/${orgId}/assistant/sessions`)
            .then((res) => setSessions(res.data))
            .catch(() => setSessions([]))
            .finally(() => setSessionsLoading(false));
    };

    useEffect(loadSessions, [orgId]);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    const handleNewChat = () => {
        setActiveSessionId(null);
        setMessages([]);
        setError("");
        setAttachedFile(null);
    };

    const handleSelectSession = async (sessionId) => {
        setActiveSessionId(sessionId);
        setError("");
        setAttachedFile(null);
        try {
            const res = await client.get(
                `/organizations/${orgId}/assistant/sessions/${sessionId}`
            );
            setMessages(
                res.data.messages.map((m) => ({
                    role: m.role.toLowerCase(),
                    content: m.content,
                }))
            );
        } catch (err) {
            setError("Failed to load this conversation.");
        }
    };

    const handleDeleteSession = async (sessionId, e) => {
        e.stopPropagation();
        if (!confirm("Delete this conversation?")) return;
        try {
            await client.delete(`/organizations/${orgId}/assistant/sessions/${sessionId}`);
            setSessions((prev) => prev.filter((s) => s.id !== sessionId));
            if (activeSessionId === sessionId) handleNewChat();
        } catch (err) {
            setError("Failed to delete conversation.");
        }
    };

    async function streamChat({ message, sessionId, token, onDelta, onSessionId }) {
        const response = await fetch(
            `${API_BASE}/organizations/${orgId}/assistant/chat/stream`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`,
                },
                body: JSON.stringify({ message, session_id: sessionId }),
            }
        );

        if (!response.ok || !response.body) {
            const errData = await response.json().catch(() => null);
            throw new Error(errData?.detail || "Failed to get a response.");
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const events = buffer.split("\n\n");
            buffer = events.pop(); // keep incomplete trailing chunk

            for (const rawEvent of events) {
                if (!rawEvent.trim()) continue;

                const lines = rawEvent.split("\n");
                let eventType = "message";
                let data = "";
                for (const line of lines) {
                    if (line.startsWith("event:")) eventType = line.slice(6).trim();
                    if (line.startsWith("data:")) data = line.slice(5).trim();
                }

                if (eventType === "session") {
                    onSessionId(data);
                } else if (eventType === "done") {
                    return;
                } else {
                    try {
                        const parsed = JSON.parse(data);
                        if (parsed.delta) onDelta(parsed.delta);
                    } catch {
                        // ignore malformed chunk
                    }
                }
            }
        }
    }

    const pollDocumentStatus = (documentId) => {
        const interval = setInterval(async () => {
            try {
                const res = await client.get(
                    `/organizations/${orgId}/documents/${documentId}`
                );
                if (res.data.status === "COMPLETED") {
                    setAttachedFile((prev) =>
                        prev && prev.id === documentId ? { ...prev, status: "COMPLETED" } : prev
                    );
                    clearInterval(interval);
                } else if (res.data.status === "FAILED" || res.data.status === "REJECTED") {
                    setAttachedFile((prev) =>
                        prev && prev.id === documentId
                            ? { ...prev, status: res.data.status, reason: res.data.rejection_reason }
                            : prev
                    );
                    clearInterval(interval);
                }
            } catch {
                clearInterval(interval);
            }
        }, 2000);
    };

    const handleFileSelect = async (e) => {
        const file = e.target.files?.[0];
        if (!file) return;
        e.target.value = ""; // allow re-selecting the same file later

        setUploading(true);
        setError("");

        const formData = new FormData();
        formData.append("file", file);

        try {
            const res = await client.post(
                `/organizations/${orgId}/documents`,
                formData,
                { headers: { "Content-Type": "multipart/form-data" } }
            );
            setAttachedFile({
                id: res.data.id,
                filename: res.data.filename,
                status: res.data.status, // "PROCESSING"
            });
            pollDocumentStatus(res.data.id);
        } catch (err) {
            setError(err.response?.data?.detail || "Failed to upload the document.");
        } finally {
            setUploading(false);
        }
    };

    const handleSend = async (e) => {
        e.preventDefault();
        const trimmed = input.trim();
        if (!trimmed || loading) return;

        // If a file is attached, tell the model explicitly which document
        // the user means — otherwise "this file"/"attached" is meaningless
        // to the LLM, which has no visibility into what was uploaded.
        const messageToSend = attachedFile
            ? `${trimmed}\n\n(Referring to the uploaded document: "${attachedFile.filename}")`
            : trimmed;

        // Show the user's original wording in the chat (not the appended hint).
        setMessages((prev) => [...prev, { role: "user", content: trimmed }]);
        setInput("");
        setError("");
        setLoading(true);

        // Placeholder assistant message that we'll fill in as chunks arrive.
        // While its content is empty, it renders as the "Thinking..." bubble
        // (see the isPendingPlaceholder check below) instead of a separate
        // second bubble.
        setMessages((prev) => [...prev, { role: "assistant", content: "" }]);

        const token = localStorage.getItem("access_token");
        let newSessionId = null;

        try {
            await streamChat({
                message: messageToSend,
                sessionId: activeSessionId,
                token,
                onSessionId: (sid) => {
                    newSessionId = sid;
                },
                onDelta: (piece) => {
                    setMessages((prev) => {
                        const updated = [...prev];
                        const lastIndex = updated.length - 1;
                        updated[lastIndex] = {
                            ...updated[lastIndex],
                            content: updated[lastIndex].content + piece,
                        };
                        return updated;
                    });
                },
            });

            if (!activeSessionId && newSessionId) {
                setActiveSessionId(newSessionId);
                loadSessions();
            } else if (newSessionId) {
                setSessions((prev) =>
                    [...prev].sort((a, b) =>
                        a.id === newSessionId ? -1 : b.id === newSessionId ? 1 : 0
                    )
                );
            }
        } catch (err) {
            setError(err.message || "Failed to get a response. Please try again.");
            // Remove the empty placeholder bubble on failure.
            setMessages((prev) => prev.slice(0, -1));
        } finally {
            setLoading(false);
        }
    };

    return (
        <div>
            <Link
                to={`/organizations/${orgId}`}
                className="inline-flex items-center gap-1 text-sm text-blue-600 mb-4 hover:underline"
            >
                <ArrowLeft size={14} /> Back to Organization
            </Link>

            <h1 className="text-2xl font-bold text-slate-800 mb-1">Assistant</h1>
            <p className="text-slate-400 text-sm mb-5">
                Ask about members, teams, projects, tasks, or uploaded documents.
            </p>

            <div className="flex gap-4 h-[70vh]">
                {/* Sidebar */}
                <div className="w-64 shrink-0 flex flex-col">
                    <Button onClick={handleNewChat} className="mb-3 w-full">
                        <span className="flex items-center justify-center gap-2">
                            <Plus size={16} /> New Chat
                        </span>
                    </Button>

                    <Card className="flex-1 overflow-y-auto p-2">
                        {sessionsLoading ? (
                            <p className="text-sm text-slate-400 px-2 py-2">Loading...</p>
                        ) : sessions.length === 0 ? (
                            <p className="text-sm text-slate-400 px-2 py-2">No conversations yet.</p>
                        ) : (
                            <ul className="space-y-1">
                                {sessions.map((s) => (
                                    <li
                                        key={s.id}
                                        onClick={() => handleSelectSession(s.id)}
                                        className={`group flex items-center justify-between gap-2 px-3 py-2 rounded-lg text-sm cursor-pointer ${
                                            activeSessionId === s.id
                                                ? "bg-blue-50 text-blue-700"
                                                : "text-slate-600 hover:bg-slate-50"
                                        }`}
                                    >
                                        <span className="flex items-center gap-2 truncate">
                                            <MessageSquare size={14} className="shrink-0" />
                                            <span className="truncate">{s.title}</span>
                                        </span>
                                        <button
                                            onClick={(e) => handleDeleteSession(s.id, e)}
                                            className="opacity-0 group-hover:opacity-100 text-slate-400 hover:text-red-500 shrink-0"
                                        >
                                            <Trash2 size={14} />
                                        </button>
                                    </li>
                                ))}
                            </ul>
                        )}
                    </Card>
                </div>

                {/* Chat panel */}
                <Card className="flex-1 flex flex-col">
                    <div className="flex-1 overflow-y-auto px-1 py-2 space-y-4">
                        {messages.length === 0 && (
                            <div className="flex gap-3 justify-start">
                                <div className="w-8 h-8 shrink-0 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center">
                                    <Bot size={16} />
                                </div>
                                <div className="max-w-[75%] rounded-lg px-4 py-2 text-sm bg-slate-100 text-slate-800">
                                    Hi! I can help you with questions about this organization — members, teams, projects, tasks, and uploaded documents. What would you like to know?
                                </div>
                            </div>
                        )}

                        {messages.map((m, i) => {
                            // The last assistant message is still empty while we're
                            // waiting for the first streamed token — show a single
                            // "Thinking..." bubble in its place instead of a
                            // separate second bubble.
                            const isPendingPlaceholder =
                                loading &&
                                i === messages.length - 1 &&
                                m.role === "assistant" &&
                                m.content === "";

                            return (
                                <div
                                    key={i}
                                    className={`flex gap-3 ${m.role === "user" ? "justify-end" : "justify-start"}`}
                                >
                                    {m.role === "assistant" && (
                                        <div className="w-8 h-8 shrink-0 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center">
                                            <Bot size={16} />
                                        </div>
                                    )}
                                    <div
                                        className={`max-w-[75%] rounded-lg px-4 py-2 text-sm whitespace-pre-wrap ${
                                            m.role === "user"
                                                ? "bg-blue-600 text-white"
                                                : isPendingPlaceholder
                                                ? "bg-slate-100 text-slate-400"
                                                : "bg-slate-100 text-slate-800"
                                        }`}
                                    >
                                        {isPendingPlaceholder ? (
                                            <div className="flex items-center gap-1 py-1">
                                                <span className="typing-dot w-2 h-2 bg-slate-400 rounded-full" />
                                                <span className="typing-dot w-2 h-2 bg-slate-400 rounded-full" />
                                                <span className="typing-dot w-2 h-2 bg-slate-400 rounded-full" />
                                            </div>
                                        ) : m.role === "assistant" ? (
                                            <div className="prose prose-sm max-w-none prose-p:my-1 prose-table:text-xs prose-th:px-2 prose-th:py-1 prose-td:px-2 prose-td:py-1">
                                                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                                    {m.content}
                                                </ReactMarkdown>
                                            </div>
                                        ) : (
                                            m.content
                                        )}
                                    </div>
                                    {m.role === "user" && (
                                        <div className="w-8 h-8 shrink-0 rounded-full bg-slate-200 text-slate-600 flex items-center justify-center text-xs font-semibold">
                                            {currentUser?.full_name?.[0]?.toUpperCase() || <UserIcon size={14} />}
                                        </div>
                                    )}
                                </div>
                            );
                        })}

                        <div ref={bottomRef} />
                    </div>

                    {error && (
                        <div className="mb-2 px-3 py-2 bg-red-50 text-red-600 text-sm rounded-lg">
                            {error}
                        </div>
                    )}

                    {attachedFile && (
                        <div className="flex items-center gap-2 px-3 py-2 mb-2 bg-blue-50 rounded-lg text-sm text-blue-700 w-fit">
                            {attachedFile.status === "PROCESSING" && (
                                <Loader2 size={14} className="animate-spin" />
                            )}
                            {attachedFile.status === "COMPLETED" && (
                                <CheckCircle2 size={14} className="text-green-600" />
                            )}
                            {(attachedFile.status === "FAILED" || attachedFile.status === "REJECTED") && (
                                <span className="text-red-500 text-xs">
                                    {attachedFile.status === "REJECTED"
                                        ? attachedFile.reason || "Rejected: not company-related."
                                        : "Failed"}
                                </span>
                            )}
                            <span className="truncate max-w-[200px]">{attachedFile.filename}</span>
                            <button
                                type="button"
                                onClick={() => setAttachedFile(null)}
                                className="text-blue-400 hover:text-blue-700"
                            >
                                <X size={14} />
                            </button>
                        </div>
                    )}
                    <form onSubmit={handleSend} className="flex gap-2 pt-3 border-t border-slate-100">
                        <input
                            ref={fileInputRef}
                            type="file"
                            accept=".pdf,.docx,.txt"
                            onChange={handleFileSelect}
                            className="hidden"
                        />
                        <button
                            type="button"
                            onClick={() => fileInputRef.current?.click()}
                            disabled={uploading || loading}
                            className="px-3 py-2 rounded-lg border border-slate-300 text-slate-500 hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {uploading ? <Loader2 size={16} className="animate-spin" /> : <Paperclip size={16} />}
                        </button>
                        <input
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Ask something about this organization..."
                            disabled={loading}
                            className="flex-1 px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-slate-50"
                        />
                        <Button type="submit" disabled={loading || !input.trim()}>
                            <Send size={16} />
                        </Button>
                    </form>
                </Card>
            </div>
        </div>
    );
}