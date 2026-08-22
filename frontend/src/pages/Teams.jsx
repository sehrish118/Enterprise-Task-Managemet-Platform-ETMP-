import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { Users2, ArrowLeft, Plus } from "lucide-react";
import client from "../api/client";
import Card from "../components/Card";
import Button from "../components/Button";
import EmptyState from "../components/EmptyState";

export default function Teams() {
    const { orgId } = useParams();
    const [teams, setTeams] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [showForm, setShowForm] = useState(false);
    const [name, setName] = useState("");
    const [formError, setFormError] = useState("");

    const load = () => {
        setLoading(true);
        client
            .get(`/organizations/${orgId}/teams`)
            .then((res) => setTeams(res.data))
            .catch((err) => setError(err.response?.data?.detail || "Failed to load teams"))
            .finally(() => setLoading(false));
    };

    useEffect(load, [orgId]);

    const handleCreate = async (e) => {
        e.preventDefault();
        setFormError("");
        try {
            await client.post(`/organizations/${orgId}/teams`, { name });
            setName("");
            setShowForm(false);
            load();
        } catch (err) {
            setFormError(err.response?.data?.detail || "Failed to create team");
        }
    };

    return (
        <div>
            <Link to={`/organizations/${orgId}`} className="inline-flex items-center gap-1 text-sm text-blue-600 mb-4 hover:underline">
                <ArrowLeft size={14} /> Organization
            </Link>

            <div className="flex justify-between items-center">
                <h1 className="text-2xl font-bold text-slate-800">Teams</h1>
                <Button onClick={() => setShowForm(!showForm)}>
                    <span className="flex items-center gap-2"><Plus size={16} /> New Team</span>
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
                ) : teams.length === 0 ? (
                    <Card><EmptyState icon={Users2} title="No teams yet" /></Card>
                ) : (
                    <div className="grid grid-cols-2 gap-4">
                        {teams.map((team) => (
                            <Link key={team.id} to={`/organizations/${orgId}/teams/${team.id}`}>
                                <Card className="hover:border-blue-300 transition-colors cursor-pointer flex items-center gap-3">
                                    <div className="p-2.5 bg-purple-50 rounded-lg text-purple-600">
                                        <Users2 size={18} />
                                    </div>
                                    <p className="font-semibold text-slate-800">{team.name}</p>
                                </Card>
                            </Link>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}