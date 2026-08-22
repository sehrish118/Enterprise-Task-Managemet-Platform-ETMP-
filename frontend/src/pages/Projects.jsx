import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { FolderKanban, ArrowLeft, Plus } from "lucide-react";
import client from "../api/client";
import Card from "../components/Card";
import Button from "../components/Button";
import EmptyState from "../components/EmptyState";

export default function Projects() {
    const { orgId } = useParams();
    const [projects, setProjects] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [showForm, setShowForm] = useState(false);
    const [name, setName] = useState("");
    const [formError, setFormError] = useState("");

    const load = () => {
        setLoading(true);
        client
            .get(`/organizations/${orgId}/projects`)
            .then((res) => setProjects(res.data))
            .catch((err) => setError(err.response?.data?.detail || "Failed to load projects"))
            .finally(() => setLoading(false));
    };

    useEffect(load, [orgId]);

    const handleCreate = async (e) => {
        e.preventDefault();
        setFormError("");
        try {
            await client.post(`/organizations/${orgId}/projects`, { name });
            setName("");
            setShowForm(false);
            load();
        } catch (err) {
            setFormError(err.response?.data?.detail || "Failed to create project");
        }
    };

    const statusColors = {
        ACTIVE: "bg-green-50 text-green-600",
        ON_HOLD: "bg-amber-50 text-amber-600",
        COMPLETED: "bg-blue-50 text-blue-600",
        ARCHIVED: "bg-slate-100 text-slate-500",
    };

    return (
        <div>
            <Link to={`/organizations/${orgId}`} className="inline-flex items-center gap-1 text-sm text-blue-600 mb-4 hover:underline">
                <ArrowLeft size={14} /> Organization
            </Link>

            <div className="flex justify-between items-center">
                <h1 className="text-2xl font-bold text-slate-800">Projects</h1>
                <Button onClick={() => setShowForm(!showForm)}>
                    <span className="flex items-center gap-2"><Plus size={16} /> New Project</span>
                </Button>
            </div>

            {showForm && (
                <Card className="mt-4">
                    {formError && <div className="mb-3 px-3 py-2 bg-red-50 text-red-600 text-sm rounded-lg">{formError}</div>}
                    <form onSubmit={handleCreate} className="flex gap-3 items-end">
                        <div className="flex-1">
                            <label className="block text-sm font-medium text-slate-600 mb-1">Name</label>
                            <input
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                required
                                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                        </div>
                        <Button type="submit">Create</Button>
                    </form>
                </Card>
            )}

            <div className="mt-6">
                {loading ? (
                    <p className="text-slate-400 text-sm">Loading...</p>
                ) : error ? (
                    <p className="text-red-500 text-sm">{error}</p>
                ) : projects.length === 0 ? (
                    <Card><EmptyState icon={FolderKanban} title="No projects visible to you yet" /></Card>
                ) : (
                    <div className="grid grid-cols-2 gap-4">
                        {projects.map((p) => (
                            <Link key={p.id} to={`/organizations/${orgId}/projects/${p.id}`}>
                                <Card className="hover:border-blue-300 transition-colors cursor-pointer">
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center gap-3">
                                            <div className="p-2.5 bg-indigo-50 rounded-lg text-indigo-600">
                                                <FolderKanban size={18} />
                                            </div>
                                            <p className="font-semibold text-slate-800">{p.name}</p>
                                        </div>
                                        <span className={`text-xs px-2 py-1 rounded-full font-medium ${statusColors[p.status]}`}>
                                            {p.status}
                                        </span>
                                    </div>
                                </Card>
                            </Link>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}