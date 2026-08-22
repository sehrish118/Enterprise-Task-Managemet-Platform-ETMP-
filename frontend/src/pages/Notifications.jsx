import { useEffect, useState } from "react";
import { Bell, Check } from "lucide-react";
import client from "../api/client";
import Card from "../components/Card";
import EmptyState from "../components/EmptyState";

export default function Notifications() {
    const [notifications, setNotifications] = useState([]);
    const [loading, setLoading] = useState(true);

    const load = () => {
        setLoading(true);
        client
            .get("/notifications")
            .then((res) => setNotifications(res.data))
            .finally(() => setLoading(false));
    };

    useEffect(load, []);

    const handleMarkRead = async (id) => {
        await client.post(`/notifications/${id}/mark-read`);
        load();
    };

    return (
        <div>
            <h1 className="text-2xl font-bold text-slate-800">Notifications</h1>

            <div className="mt-6">
                {loading ? (
                    <p className="text-slate-400 text-sm">Loading...</p>
                ) : notifications.length === 0 ? (
                    <Card><EmptyState icon={Bell} title="No notifications yet" /></Card>
                ) : (
                    <Card>
                        <ul className="divide-y divide-slate-100">
                            {notifications.map((n) => (
                                <li key={n.id} className="py-3 flex justify-between items-start gap-4">
                                    <div>
                                        <p className={`text-sm ${n.is_read ? "text-slate-500" : "text-slate-800 font-medium"}`}>
                                            {n.title}
                                        </p>
                                        <p className="text-xs text-slate-400 mt-0.5">{n.message}</p>
                                    </div>
                                    {!n.is_read && (
                                        <button
                                            onClick={() => handleMarkRead(n.id)}
                                            className="flex items-center gap-1 text-xs text-blue-600 hover:underline flex-shrink-0"
                                        >
                                            <Check size={14} /> Mark read
                                        </button>
                                    )}
                                </li>
                            ))}
                        </ul>
                    </Card>
                )}
            </div>
        </div>
    );
}