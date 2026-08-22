import { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { ArrowLeft, Trash2, UserPlus, Paperclip } from "lucide-react";
import client from "../api/client";
import Card from "../components/Card";
import Button from "../components/Button";
import { useAuth } from "../context/AuthContext";

export default function TaskDetail() {
    const { orgId, projectId, taskId } = useParams();
    const navigate = useNavigate();
    const { user: currentUser } = useAuth();

    const [task, setTask] = useState(null);
    const [assignees, setAssignees] = useState([]);
    const [comments, setComments] = useState([]);
    const [attachments, setAttachments] = useState([]);
    const [error, setError] = useState("");

    const [title, setTitle] = useState("");
    const [description, setDescription] = useState("");
    const [priority, setPriority] = useState("MEDIUM");
    const [dueDate, setDueDate] = useState("");

    const [assignEmail, setAssignEmail] = useState("");
    const [assignError, setAssignError] = useState("");

    const [commentText, setCommentText] = useState("");

    const [attFilename, setAttFilename] = useState("");
    const [attUrl, setAttUrl] = useState("");

    const load = () => {
        client.get(`/organizations/${orgId}/projects/${projectId}/tasks/${taskId}`).then((res) => {
            setTask(res.data);
            setTitle(res.data.title);
            setDescription(res.data.description || "");
            setPriority(res.data.priority);
            setDueDate(res.data.due_date ? res.data.due_date.split("T")[0] : "");
        });
        client.get(`/organizations/${orgId}/projects/${projectId}/tasks/${taskId}/assignees`).then((res) => setAssignees(res.data));
        client.get(`/organizations/${orgId}/tasks/${taskId}/comments`).then((res) => setComments(res.data));
        client.get(`/organizations/${orgId}/tasks/${taskId}/attachments`).then((res) => setAttachments(res.data));
    };

    useEffect(load, [orgId, projectId, taskId]);

    const handleUpdate = async (e) => {
        e.preventDefault();
        setError("");
        try {
            await client.patch(`/organizations/${orgId}/projects/${projectId}/tasks/${taskId}`, {
                title, description, priority,
                due_date: dueDate ? new Date(dueDate).toISOString() : null,
            });
            load();
        } catch (err) {
            setError(err.response?.data?.detail || "Failed to update task");
        }
    };

    const handleDelete = async () => {
        if (!confirm("Delete this task?")) return;
        try {
            await client.delete(`/organizations/${orgId}/projects/${projectId}/tasks/${taskId}`);
            navigate(`/organizations/${orgId}/projects/${projectId}/tasks`);
        } catch (err) {
            setError(err.response?.data?.detail || "Only the Project Manager can delete tasks");
        }
    };

    const handleAssign = async (e) => {
        e.preventDefault();
        setAssignError("");
        try {
            await client.post(`/organizations/${orgId}/projects/${projectId}/tasks/${taskId}/assignees`, {
                email: assignEmail,
            });
            setAssignEmail("");
            load();
        } catch (err) {
            setAssignError(err.response?.data?.detail || "Only the Project Manager can assign tasks");
        }
    };

    const handleComment = async (e) => {
        e.preventDefault();
        try {
            await client.post(`/organizations/${orgId}/tasks/${taskId}/comments`, { content: commentText });
            setCommentText("");
            load();
        } catch (err) {
            setError(err.response?.data?.detail || "Failed to post comment");
        }
    };

    const handleDeleteComment = async (commentId) => {
        try {
            await client.delete(`/organizations/${orgId}/tasks/${taskId}/comments/${commentId}`);
            load();
        } catch (err) {
            setError(err.response?.data?.detail || "Failed to delete comment");
        }
    };

    const handleAddAttachment = async (e) => {
        e.preventDefault();
        try {
            await client.post(`/organizations/${orgId}/tasks/${taskId}/attachments`, null, {
                params: {
                    original_filename: attFilename,
                    mime_type: "application/octet-stream",
                    size: 0,
                    file_url: attUrl,
                },
            });
            setAttFilename("");
            setAttUrl("");
            load();
        } catch (err) {
            setError(err.response?.data?.detail || "Failed to add attachment");
        }
    };

    if (!task) return <p className="text-slate-400 text-sm">Loading...</p>;

    return (
        <div>
            <Link to={`/organizations/${orgId}/projects/${projectId}/tasks`} className="inline-flex items-center gap-1 text-sm text-blue-600 mb-4 hover:underline">
                <ArrowLeft size={14} /> Tasks
            </Link>

            {error && <div className="mb-4 px-3 py-2 bg-red-50 text-red-600 text-sm rounded-lg">{error}</div>}

            <Card>
                <form onSubmit={handleUpdate} className="space-y-3">
                    <input
                        value={title}
                        onChange={(e) => setTitle(e.target.value)}
                        className="w-full text-lg font-semibold px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <textarea
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                        rows={2}
                        className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <div className="flex gap-3 items-end">
                        <select
                            value={priority}
                            onChange={(e) => setPriority(e.target.value)}
                            className="px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                            <option value="LOW">Low</option>
                            <option value="MEDIUM">Medium</option>
                            <option value="HIGH">High</option>
                            <option value="URGENT">Urgent</option>
                        </select>
                        <input
  type="date"
  value={dueDate}
  onChange={(e) => setDueDate(e.target.value)}
  className="px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
/>
                        <Button type="submit">Save</Button>
                        <Button type="button" variant="danger" onClick={handleDelete}>
                            <Trash2 size={16} />
                        </Button>
                    </div>
                </form>
            </Card>

            {/* Assignees */}
            <h2 className="text-lg font-semibold text-slate-800 mt-6 mb-2">Assignees</h2>
            <Card>
                {assignError && <div className="mb-3 px-3 py-2 bg-red-50 text-red-600 text-sm rounded-lg">{assignError}</div>}
                <form onSubmit={handleAssign} className="flex gap-3 items-end mb-3">
                    <div className="flex-1">
                        <input
                            type="email"
                            placeholder="user@example.com"
                            value={assignEmail}
                            onChange={(e) => setAssignEmail(e.target.value)}
                            required
                            className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                    </div>
                    <Button type="submit">
                        <span className="flex items-center gap-2"><UserPlus size={16} /> Assign</span>
                    </Button>
                </form>
                {assignees.length === 0 ? (
                    <p className="text-sm text-slate-400">No one assigned yet.</p>
                ) : (
                    <ul className="space-y-1">
                        {assignees.map((a) => (
                            <li key={a.id} className="text-sm text-slate-700">{a.user_full_name}</li>
                        ))}
                    </ul>
                )}
            </Card>

            {/* Attachments */}
            <h2 className="text-lg font-semibold text-slate-800 mt-6 mb-2 flex items-center gap-2">
                <Paperclip size={18} /> Attachments
            </h2>
            <Card>
                <form onSubmit={handleAddAttachment} className="flex gap-3 items-end mb-3">
                    <input
                        placeholder="File name"
                        value={attFilename}
                        onChange={(e) => setAttFilename(e.target.value)}
                        required
                        className="flex-1 px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <input
                        placeholder="https://..."
                        value={attUrl}
                        onChange={(e) => setAttUrl(e.target.value)}
                        required
                        className="flex-1 px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <Button type="submit">Add</Button>
                </form>
                {attachments.length === 0 ? (
                    <p className="text-sm text-slate-400">No attachments yet.</p>
                ) : (
                    <ul className="space-y-1">
                        {attachments.map((a) => (
                            <li key={a.id}>
                                <a href={a.file_url} target="_blank" rel="noreferrer" className="text-sm text-blue-600 hover:underline">
                                    {a.original_filename}
                                </a>
                            </li>
                        ))}
                    </ul>
                )}
            </Card>

            {/* Comments */}
            <h2 className="text-lg font-semibold text-slate-800 mt-6 mb-2">Comments</h2>
            <Card>
                <form onSubmit={handleComment} className="flex gap-3 items-end mb-4">
                    <input
                        placeholder="Write a comment..."
                        value={commentText}
                        onChange={(e) => setCommentText(e.target.value)}
                        required
                        className="flex-1 px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <Button type="submit">Post</Button>
                </form>
                {comments.length === 0 ? (
                    <p className="text-sm text-slate-400">No comments yet.</p>
                ) : (
                    <ul className="divide-y divide-slate-100">
                        {comments.map((c) => (
                            <li key={c.id} className="py-2 flex justify-between items-start">
                                <div>
                                    <p className="text-sm text-slate-700"><span className="font-medium">{c.user_full_name}:</span> {c.content}</p>
                                </div>
                                {c.user_id === currentUser?.id && (
                                    <button
                                        onClick={() => handleDeleteComment(c.id)}
                                        className="text-xs text-red-500 hover:underline ml-3"
                                    >
                                        Delete
                                    </button>
                                )}
                            </li>
                        ))}
                    </ul>
                )}
            </Card>
        </div>
    );
}