import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Building2, Plus } from "lucide-react";
import client from "../api/client";
import Card from "../components/Card";
import Button from "../components/Button";
import EmptyState from "../components/EmptyState";

export default function Organizations() {
    const [orgs, setOrgs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showForm, setShowForm] = useState(false);
    const [name, setName] = useState("");
    const [slug, setSlug] = useState("");
    const [error, setError] = useState("");
    const [submitting, setSubmitting] = useState(false);

    const loadOrgs = () => {
        setLoading(true);
        client
            .get("/organizations/me")
            .then((res) => setOrgs(res.data))
            .finally(() => setLoading(false));
    };

    useEffect(loadOrgs, []);

    const handleCreate = async (e) => {
        e.preventDefault();
        setError("");
        setSubmitting(true);
        try {
            await client.post("/organizations", { name, slug });
            setName("");
            setSlug("");
            setShowForm(false);
            loadOrgs();
        } catch (err) {
            setError(err.response?.data?.detail || "Failed to create organization");
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <div>
            <div className="flex justify-between items-center">
                <h1 className="text-2xl font-bold text-slate-800">Organizations</h1>
                <Button onClick={() => setShowForm(!showForm)}>
                    <span className="flex items-center gap-2">
                        <Plus size={16} /> New Organization
                    </span>
                </Button>
            </div>

            {showForm && (
                <Card className="mt-4">
                    {error && (
                        <div className="mb-3 px-3 py-2 bg-red-50 text-red-600 text-sm rounded-lg">{error}</div>
                    )}
                    <form onSubmit={handleCreate} className="space-y-3">
                        <div>
                            <label className="block text-sm font-medium text-slate-600 mb-1">Name</label>
                            <input
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                required
                                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-slate-600 mb-1">
                                Slug <span className="text-slate-400 font-normal">(lowercase, hyphens only)</span>
                            </label>
                            <input
                                value={slug}
                                onChange={(e) => setSlug(e.target.value)}
                                required
                                pattern="[a-z0-9]+(-[a-z0-9]+)*"
                                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                        </div>
                        <Button type="submit" disabled={submitting}>
                            {submitting ? "Creating..." : "Create"}
                        </Button>
                    </form>
                </Card>
            )}

            <div className="mt-6">
                {loading ? (
                    <p className="text-slate-400 text-sm">Loading...</p>
                ) : orgs.length === 0 ? (
                    <Card>
                        <EmptyState
                            icon={Building2}
                            title="No organizations yet"
                            description="Create one to get started"
                        />
                    </Card>
                ) : (
                    <div className="grid grid-cols-2 gap-4">
                        {orgs.map((org) => (
                            <Link key={org.id} to={`/organizations/${org.id}`}>
                                <Card className="hover:border-blue-300 transition-colors cursor-pointer">
                                    <div className="flex items-center gap-3">
                                        <div className="p-2.5 bg-blue-50 rounded-lg text-blue-600">
                                            <Building2 size={18} />
                                        </div>
                                        <div>
                                            <p className="font-semibold text-slate-800">{org.name}</p>
                                            <p className="text-xs text-slate-400">{org.slug}</p>
                                        </div>
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