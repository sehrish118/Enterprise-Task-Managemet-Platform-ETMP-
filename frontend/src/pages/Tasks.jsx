import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { ArrowLeft, Plus, ListTodo } from "lucide-react";
import client from "../api/client";
import Card from "../components/Card";
import Button from "../components/Button";
import EmptyState from "../components/EmptyState";

const priorityColors = {
    LOW: "bg-slate-100 text-slate-500",
    MEDIUM: "bg-blue-50 text-blue-600",
    HIGH: "bg-amber-50 text-amber-600",
    URGENT: "bg-red-50 text-red-600",
};

const formatDueDate = (dueDateStr) => {
  if (!dueDateStr) return null;
  const due = new Date(dueDateStr);
  const now = new Date();
  const isOverdue = due < now;
  const label = due.toLocaleDateString(undefined, { month: "short", day: "numeric" });
  return { label, isOverdue };
};

export default function Tasks() {
    const { orgId, projectId } = useParams();
    const [tasks, setTasks] = useState([]);
    const [statuses, setStatuses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [showForm, setShowForm] = useState(false);
    const [title, setTitle] = useState("");
    const [description, setDescription] = useState("");
    const [statusId, setStatusId] = useState("");
    const [priority, setPriority] = useState("MEDIUM");
    const [dueDate, setDueDate] = useState("");
    const [formError, setFormError] = useState("");
    const [search, setSearch] = useState("");
    

    const load = () => {
        setLoading(true);
        Promise.all([
            client.get(`/organizations/${orgId}/projects/${projectId}/tasks`, {
                params: { search: search || undefined },
            }),
            client.get(`/organizations/${orgId}/task-statuses`),
        ])
            .then(([taskRes, statusRes]) => {
                setTasks(taskRes.data.items);
                setStatuses(statusRes.data);
                if (statusRes.data.length > 0 && !statusId) setStatusId(statusRes.data[0].id);
            })
            .catch((err) => setError(err.response?.data?.detail || "Failed to load tasks"))
            .finally(() => setLoading(false));
    };

    useEffect(load, [orgId, projectId, search]);

    const handleCreate = async (e) => {
        e.preventDefault();
        setFormError("");
        try {
            await client.post(`/organizations/${orgId}/projects/${projectId}/tasks`, {
                title,
                description: description || null,
                status_id: statusId,
                priority,
                due_date: dueDate ? new Date(dueDate).toISOString() : null, 
            });
            setTitle("");
            setDescription("");
            setDueDate(""); 
            setShowForm(false);
            load();
        } catch (err) {
            setFormError(err.response?.data?.detail || "Failed to create task");
        }
    };

    return (
        <div>
            <Link to={`/organizations/${orgId}/projects/${projectId}`} className="inline-flex items-center gap-1 text-sm text-blue-600 mb-4 hover:underline">
                <ArrowLeft size={14} /> Project
            </Link>

            <div className="flex justify-between items-center">
                <h1 className="text-2xl font-bold text-slate-800">Tasks</h1>
                <Button onClick={() => setShowForm(!showForm)}>
                    <span className="flex items-center gap-2"><Plus size={16} /> New Task</span>
                </Button>
            </div>

            <input
                placeholder="Search tasks..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="mt-4 w-full max-w-sm px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />

            {showForm && (
                <Card className="mt-4">
                    {statuses.length === 0 ? (
                        <p className="text-sm text-amber-600">
                            No task statuses exist yet for this organization. Create one first (e.g. "To Do") before adding tasks.
                        </p>
                    ) : (
                        <>
                            {formError && <div className="mb-3 px-3 py-2 bg-red-50 text-red-600 text-sm rounded-lg">{formError}</div>}
                            <form onSubmit={handleCreate} className="space-y-3">
                                <div>
                                    <label className="block text-sm font-medium text-slate-600 mb-1">Title</label>
                                    <input
                                        value={title}
                                        onChange={(e) => setTitle(e.target.value)}
                                        required
                                        className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-slate-600 mb-1">Description</label>
                                    <input
                                        value={description}
                                        onChange={(e) => setDescription(e.target.value)}
                                        className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    />
                                </div>
                                <div className="flex gap-3">
                                    <div className="flex-1">
                                        <label className="block text-sm font-medium text-slate-600 mb-1">Status</label>
                                        <select
                                            value={statusId}
                                            onChange={(e) => setStatusId(e.target.value)}
                                            className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                                        >
                                            {statuses.map((s) => (
                                                <option key={s.id} value={s.id}>{s.name}</option>
                                            ))}
                                        </select>
                                    </div>
                                    <div className="flex-1">
                                        <label className="block text-sm font-medium text-slate-600 mb-1">Priority</label>
                                        <select
                                            value={priority}
                                            onChange={(e) => setPriority(e.target.value)}
                                            className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                                        >
                                            <option value="LOW">Low</option>
                                            <option value="MEDIUM">Medium</option>
                                            <option value="HIGH">High</option>
                                            <option value="URGENT">Urgent</option>
                                        </select>
                                    </div>
                                </div>
                                <div>
  <label className="block text-sm font-medium text-slate-600 mb-1">Due Date (optional)</label>
  <input
    type="date"
    value={dueDate}
    onChange={(e) => setDueDate(e.target.value)}
    className="px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
  />
</div>
                                <Button type="submit">Create Task</Button>
                            </form>
                        </>
                    )}
                </Card>
            )}

            <div className="mt-6">
                {loading ? (
                    <p className="text-slate-400 text-sm">Loading...</p>
                ) : error ? (
                    <p className="text-red-500 text-sm">{error}</p>
                ) : tasks.length === 0 ? (
                    <Card><EmptyState icon={ListTodo} title="No tasks yet" /></Card>
                ) : (
                    <Card>
                        <ul className="divide-y divide-slate-100">
                            {tasks.map((t) => (
    <li key={t.id}>
        <Link
            to={`/organizations/${orgId}/projects/${projectId}/tasks/${t.id}`}
            className="py-3 flex justify-between items-center hover:bg-slate-50 -mx-6 px-6 transition-colors"
        >
            <span className="text-sm text-slate-700">{t.title}</span>
            
            <div className="flex items-center gap-2">
                {/* Priority Badge */}
                <span className={`text-xs px-2 py-1 rounded-full font-medium ${priorityColors[t.priority]}`}>
                    {t.priority}
                </span>

                {/* Due Date Badge */}
                {t.due_date && (() => {
                    const { label, isOverdue } = formatDueDate(t.due_date);
                    return (
                        <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                            isOverdue ? "bg-red-50 text-red-600" : "bg-slate-100 text-slate-500"
                        }`}>
                            {isOverdue ? "Overdue: " : "Due "}{label}
                        </span>
                    );
                })()}
            </div>
        </Link>
    </li>
))}
                        </ul>
                    </Card>
                )}
            </div>
        </div>
    );
}