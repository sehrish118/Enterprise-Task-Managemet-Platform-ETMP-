// import { useEffect, useState } from "react";
// import { ListChecks, AlertCircle, Bell } from "lucide-react";
// import client from "../api/client";
// import Card from "../components/Card";
// import EmptyState from "../components/EmptyState";
// import { useAuth } from "../context/AuthContext";

// export default function Dashboard() {
//     const { user } = useAuth();
//     const [data, setData] = useState(null);
//     const [loading, setLoading] = useState(true);

//     useEffect(() => {
//         client
//             .get("/dashboard/me")
//             .then((res) => setData(res.data))
//             .finally(() => setLoading(false));
//     }, []);

//     if (loading) {
//         return <div className="text-slate-400 text-sm">Loading dashboard...</div>;
//     }

//     return (
//         <div>
//             <h1 className="text-2xl font-bold text-slate-800">Welcome, {user?.full_name}</h1>
//             <p className="text-slate-500 mt-1">Here's what's happening with your work.</p>

//             <div className="grid grid-cols-3 gap-4 mt-6">
//                 <Card className="flex items-center gap-4">
//                     <div className="p-3 bg-blue-50 rounded-lg text-blue-600">
//                         <ListChecks size={20} />
//                     </div>
//                     <div>
//                         <p className="text-2xl font-bold text-slate-800">{data.assigned_tasks_count}</p>
//                         <p className="text-sm text-slate-400">Assigned Tasks</p>
//                     </div>
//                 </Card>

//                 <Card className="flex items-center gap-4">
//                     <div className="p-3 bg-red-50 rounded-lg text-red-500">
//                         <AlertCircle size={20} />
//                     </div>
//                     <div>
//                         <p className="text-2xl font-bold text-slate-800">{data.overdue_tasks_count}</p>
//                         <p className="text-sm text-slate-400">Overdue</p>
//                     </div>
//                 </Card>

//                 <Card className="flex items-center gap-4">
//                     <div className="p-3 bg-amber-50 rounded-lg text-amber-500">
//                         <Bell size={20} />
//                     </div>
//                     <div>
//                         <p className="text-2xl font-bold text-slate-800">{data.unread_notifications_count}</p>
//                         <p className="text-sm text-slate-400">Unread</p>
//                     </div>
//                 </Card>
//             </div>

//             <h2 className="text-lg font-semibold text-slate-800 mt-8 mb-3">Recent Tasks</h2>
//             <Card>
//                 {data.recent_tasks.length === 0 ? (
//                     <EmptyState icon={ListChecks} title="No tasks assigned yet" />
//                 ) : (
//                     <ul className="divide-y divide-slate-100">
//                         {data.recent_tasks.map((task) => (
//                             <li key={task.id} className="py-3 flex justify-between items-center">
//                                 <span className="text-slate-700">{task.title}</span>
//                                 <span className="text-xs px-2 py-1 bg-slate-100 rounded-full text-slate-500">
//                                     {task.priority}
//                                 </span>
//                             </li>
//                         ))}
//                     </ul>
//                 )}
//             </Card>
//         </div>
//     );
// }


import { useEffect, useState, useCallback } from "react";
import { ListChecks, AlertCircle, Bell, CheckCircle2 } from "lucide-react";
import client from "../api/client";
import Card from "../components/Card";
import EmptyState from "../components/EmptyState";
import { useAuth } from "../context/AuthContext";

export default function Dashboard() {
    const { user } = useAuth();
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [updatingTaskId, setUpdatingTaskId] = useState(null);

    const fetchDashboardData = useCallback(() => {
        client
            .get("/dashboard/me")
            .then((res) => setData(res.data))
            .catch((err) => console.error("Failed to load dashboard:", err))
            .finally(() => setLoading(false));
    }, []);

    useEffect(() => {
        fetchDashboardData();
    }, [fetchDashboardData]);

    const handleStatusChange = async (taskId, newStatus) => {
        setUpdatingTaskId(taskId);
        
        // Optimistic UI Update
        const previousData = { ...data };
        setData((prev) => ({
            ...prev,
            recent_tasks: prev.recent_tasks.map((t) =>
                t.id === taskId ? { ...t, status: newStatus } : t
            ),
        }));

        try {
            await client.patch(`/tasks/${taskId}`, { status: newStatus });
            fetchDashboardData(); // Refresh counts from backend
        } catch (err) {
            console.error("Failed to update task status:", err);
            setData(previousData); // Rollback on failure
        } finally {
            setUpdatingTaskId(null);
        }
    };

    if (loading) {
        return <div className="text-slate-400 text-sm p-4">Loading dashboard...</div>;
    }

    const statusBadgeStyles = {
        TODO: "bg-slate-100 text-slate-600 border-slate-200",
        IN_PROGRESS: "bg-blue-50 text-blue-700 border-blue-200",
        IN_REVIEW: "bg-amber-50 text-amber-700 border-amber-200",
        COMPLETED: "bg-emerald-50 text-emerald-700 border-emerald-200",
    };

    return (
        <div>
            <h1 className="text-2xl font-bold text-slate-800">Welcome, {user?.full_name}</h1>
            <p className="text-slate-500 mt-1">Here's what's happening with your work.</p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
                <Card className="flex items-center gap-4">
                    <div className="p-3 bg-blue-50 rounded-lg text-blue-600">
                        <ListChecks size={20} />
                    </div>
                    <div>
                        <p className="text-2xl font-bold text-slate-800">{data?.assigned_tasks_count || 0}</p>
                        <p className="text-sm text-slate-400">Assigned Tasks</p>
                    </div>
                </Card>

                <Card className="flex items-center gap-4">
                    <div className="p-3 bg-red-50 rounded-lg text-red-500">
                        <AlertCircle size={20} />
                    </div>
                    <div>
                        <p className="text-2xl font-bold text-slate-800">{data?.overdue_tasks_count || 0}</p>
                        <p className="text-sm text-slate-400">Overdue</p>
                    </div>
                </Card>

                <Card className="flex items-center gap-4">
                    <div className="p-3 bg-amber-50 rounded-lg text-amber-500">
                        <Bell size={20} />
                    </div>
                    <div>
                        <p className="text-2xl font-bold text-slate-800">{data?.unread_notifications_count || 0}</p>
                        <p className="text-sm text-slate-400">Unread Notifications</p>
                    </div>
                </Card>
            </div>

            <h2 className="text-lg font-semibold text-slate-800 mt-8 mb-3">Recent Tasks</h2>
            <Card>
                {!data?.recent_tasks || data.recent_tasks.length === 0 ? (
                    <EmptyState icon={ListChecks} title="No tasks assigned yet" />
                ) : (
                    <ul className="divide-y divide-slate-100">
                        {data.recent_tasks.map((task) => {
                            const isCompleted = task.status === "COMPLETED";
                            const isUpdating = updatingTaskId === task.id;

                            return (
                                <li key={task.id} className="py-3 flex items-center justify-between gap-4">
                                    {/* Checkbox and Task Title */}
                                    <div className="flex items-center gap-3 min-w-0 flex-1">
                                        <button
                                            onClick={() => handleStatusChange(task.id, isCompleted ? "TODO" : "COMPLETED")}
                                            disabled={isUpdating}
                                            className="text-slate-400 hover:text-emerald-600 focus:outline-none transition-colors disabled:opacity-50"
                                            title={isCompleted ? "Mark as To Do" : "Mark as Completed"}
                                        >
                                            <CheckCircle2
                                                size={18}
                                                className={isCompleted ? "text-emerald-600 fill-emerald-50" : "text-slate-300"}
                                            />
                                        </button>
                                        <div className="min-w-0 flex-1">
                                            <p className={`text-sm font-medium truncate ${isCompleted ? "line-through text-slate-400" : "text-slate-800"}`}>
                                                {task.title}
                                            </p>
                                            {task.description && (
                                                <p className="text-xs text-slate-400 truncate">{task.description}</p>
                                            )}
                                        </div>
                                    </div>

                                    {/* Priority & Interactive Status Dropdown */}
                                    <div className="flex items-center gap-3 shrink-0">
                                        <span className="text-xs font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-500 uppercase">
                                            {task.priority || "MEDIUM"}
                                        </span>

                                        <select
                                            value={task.status || "TODO"}
                                            disabled={isUpdating}
                                            onChange={(e) => handleStatusChange(task.id, e.target.value)}
                                            className={`text-xs font-medium px-2 py-1 rounded-md border focus:outline-none cursor-pointer transition-colors ${
                                                statusBadgeStyles[task.status] || statusBadgeStyles.TODO
                                            }`}
                                        >
                                            <option value="TODO">To Do</option>
                                            <option value="IN_PROGRESS">In Progress</option>
                                            <option value="IN_REVIEW">In Review</option>
                                            <option value="COMPLETED">Completed</option>
                                        </select>
                                    </div>
                                </li>
                            );
                        })}
                    </ul>
                )}
            </Card>
        </div>
    );
}
