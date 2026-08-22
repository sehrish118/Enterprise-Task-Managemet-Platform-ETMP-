import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { ArrowLeft, FolderKanban, ListChecks, Users, TrendingUp, ScrollText } from "lucide-react";
import client from "../api/client";
import Card from "../components/Card";

const priorityColors = {
    LOW: "bg-slate-100 text-slate-500",
    MEDIUM: "bg-blue-50 text-blue-600",
    HIGH: "bg-amber-50 text-amber-600",
    URGENT: "bg-red-50 text-red-600",
};

export default function OrgDashboard() {
    const { orgId } = useParams();
    const [data, setData] = useState(null);
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        setLoading(true);
        client
            .get(`/organizations/${orgId}/dashboard`)
            .then((res) => setData(res.data))
            .catch((err) => setError(err.response?.data?.detail || "Failed to load dashboard"))
            .finally(() => setLoading(false));
    }, [orgId]);

    if (loading) return <p className="text-slate-400 text-sm">Loading...</p>;
    if (error) return <p className="text-red-500 text-sm">{error}</p>;

    const stats = [
        { label: "Total Projects", value: data.total_projects, icon: FolderKanban, color: "bg-indigo-50 text-indigo-600" },
        { label: "Active Projects", value: data.active_projects, icon: TrendingUp, color: "bg-green-50 text-green-600" },
        { label: "Total Tasks", value: data.total_tasks, icon: ListChecks, color: "bg-blue-50 text-blue-600" },
        { label: "Members", value: data.total_members, icon: Users, color: "bg-purple-50 text-purple-600" },
    ];

    const priorityEntries = Object.entries(data.tasks_by_priority || {});

    return (
        <div>
            <Link to={`/organizations/${orgId}`} className="inline-flex items-center gap-1 text-sm text-blue-600 mb-4 hover:underline">
                <ArrowLeft size={14} /> Organization
            </Link>

            <h1 className="text-2xl font-bold text-slate-800">Organization Dashboard</h1>

            <div className="grid grid-cols-4 gap-4 mt-6">
                {stats.map(({ label, value, icon: Icon, color }) => (
                    <Card key={label} className="flex items-center gap-4">
                        <div className={`p-3 rounded-lg ${color}`}>
                            <Icon size={20} />
                        </div>
                        <div>
                            <p className="text-2xl font-bold text-slate-800">{value}</p>
                            <p className="text-sm text-slate-400">{label}</p>
                        </div>
                    </Card>
                ))}
            </div>

            <h2 className="text-lg font-semibold text-slate-800 mt-8 mb-3">Tasks by Priority</h2>
            <Card>
                {priorityEntries.length === 0 ? (
                    <p className="text-sm text-slate-400">No tasks yet.</p>
                ) : (
                    <div className="space-y-3">
                        {priorityEntries.map(([priority, count]) => (
                            <div key={priority} className="flex items-center gap-3">
                                <span className={`text-xs px-2 py-1 rounded-full font-medium w-20 text-center ${priorityColors[priority]}`}>
                                    {priority}
                                </span>
                                <div className="flex-1 bg-slate-100 rounded-full h-2">
                                    <div
                                        className="bg-blue-500 h-2 rounded-full"
                                        style={{ width: `${Math.min(100, count * 20)}%` }}
                                    />
                                </div>
                                <span className="text-sm text-slate-600 font-medium w-6 text-right">{count}</span>
                            </div>
                        ))}
                    </div>
                )}
            </Card>

            <Link
                to={`/organizations/${orgId}/activity-logs`}
                className="inline-flex items-center gap-2 mt-6 text-sm text-blue-600 hover:underline"
            >
                <ScrollText size={16} /> View Activity Logs
            </Link>
        </div>
    );
}