import { useEffect, useState } from "react";
import { ListChecks, AlertCircle, Bell } from "lucide-react";
import client from "../api/client";
import Card from "../components/Card";
import EmptyState from "../components/EmptyState";
import { useAuth } from "../context/AuthContext";

export default function Dashboard() {
    const { user } = useAuth();
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        client
            .get("/dashboard/me")
            .then((res) => setData(res.data))
            .finally(() => setLoading(false));
    }, []);

    if (loading) {
        return <div className="text-slate-400 text-sm">Loading dashboard...</div>;
    }

    return (
        <div>
            <h1 className="text-2xl font-bold text-slate-800">Welcome, {user?.full_name}</h1>
            <p className="text-slate-500 mt-1">Here's what's happening with your work.</p>

            <div className="grid grid-cols-3 gap-4 mt-6">
                <Card className="flex items-center gap-4">
                    <div className="p-3 bg-blue-50 rounded-lg text-blue-600">
                        <ListChecks size={20} />
                    </div>
                    <div>
                        <p className="text-2xl font-bold text-slate-800">{data.assigned_tasks_count}</p>
                        <p className="text-sm text-slate-400">Assigned Tasks</p>
                    </div>
                </Card>

                <Card className="flex items-center gap-4">
                    <div className="p-3 bg-red-50 rounded-lg text-red-500">
                        <AlertCircle size={20} />
                    </div>
                    <div>
                        <p className="text-2xl font-bold text-slate-800">{data.overdue_tasks_count}</p>
                        <p className="text-sm text-slate-400">Overdue</p>
                    </div>
                </Card>

                <Card className="flex items-center gap-4">
                    <div className="p-3 bg-amber-50 rounded-lg text-amber-500">
                        <Bell size={20} />
                    </div>
                    <div>
                        <p className="text-2xl font-bold text-slate-800">{data.unread_notifications_count}</p>
                        <p className="text-sm text-slate-400">Unread</p>
                    </div>
                </Card>
            </div>

            <h2 className="text-lg font-semibold text-slate-800 mt-8 mb-3">Recent Tasks</h2>
            <Card>
                {data.recent_tasks.length === 0 ? (
                    <EmptyState icon={ListChecks} title="No tasks assigned yet" />
                ) : (
                    <ul className="divide-y divide-slate-100">
                        {data.recent_tasks.map((task) => (
                            <li key={task.id} className="py-3 flex justify-between items-center">
                                <span className="text-slate-700">{task.title}</span>
                                <span className="text-xs px-2 py-1 bg-slate-100 rounded-full text-slate-500">
                                    {task.priority}
                                </span>
                            </li>
                        ))}
                    </ul>
                )}
            </Card>
        </div>
    );
}