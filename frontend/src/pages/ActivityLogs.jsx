import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { ArrowLeft, ScrollText } from "lucide-react";
import client from "../api/client";
import Card from "../components/Card";
import EmptyState from "../components/EmptyState";

export default function ActivityLogs() {
    const { orgId } = useParams();
    const [logs, setLogs] = useState([]);
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        setLoading(true);
        client
            .get(`/organizations/${orgId}/activity-logs`)
            .then((res) => setLogs(res.data))
            .catch((err) => setError(err.response?.data?.detail || "Failed to load activity logs"))
            .finally(() => setLoading(false));
    }, [orgId]);

    const formatDate = (iso) =>
        new Date(iso).toLocaleString(undefined, {
            dateStyle: "medium",
            timeStyle: "short",
        });

    const actionLabels = {
        task_assigned: "Task assigned",
    };

    if (loading) return <p className="text-slate-400 text-sm">Loading...</p>;
    if (error) return <p className="text-red-500 text-sm">{error}</p>;

    return (
        <div>
            <Link to={`/organizations/${orgId}/dashboard`} className="inline-flex items-center gap-1 text-sm text-blue-600 mb-4 hover:underline">
                <ArrowLeft size={14} /> Dashboard
            </Link>

            <h1 className="text-2xl font-bold text-slate-800">Activity Logs</h1>

            <div className="mt-6">
                {logs.length === 0 ? (
                    <Card><EmptyState icon={ScrollText} title="No activity yet" /></Card>
                ) : (
                    <Card>
                        <ul className="divide-y divide-slate-100">
                            {logs.map((log) => (
                                <li key={log.id} className="py-3 flex justify-between items-center">
                                    <span className="text-sm text-slate-700">
                                        {actionLabels[log.action] || log.action}
                                        <span className="text-slate-400"> — {log.entity_type}</span>
                                    </span>
                                    <span className="text-xs text-slate-400">{formatDate(log.created_at)}</span>
                                </li>
                            ))}
                        </ul>
                    </Card>
                )}
            </div>
        </div>
    );
}