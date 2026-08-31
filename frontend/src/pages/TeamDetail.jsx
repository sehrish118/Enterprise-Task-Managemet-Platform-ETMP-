import { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { ArrowLeft, UserPlus, Trash2, CheckCircle } from "lucide-react";

import client from "../api/client";
import Card from "../components/Card";
import Button from "../components/Button";

export default function TeamDetail() {
    const { orgId, teamId } = useParams();
    const navigate = useNavigate();
    const [team, setTeam] = useState(null);
    const [members, setMembers] = useState([]);
    const [error, setError] = useState("");
    const [name, setName] = useState("");
    const [showAddForm, setShowAddForm] = useState(false);
    
    // State Changes for Invite Form
    const [fullName, setFullName] = useState("");
    const [email, setEmail] = useState("");
    const [role, setRole] = useState("MEMBER");
    
    const [formError, setFormError] = useState("");
    const [successMsg, setSuccessMsg] = useState("");
    const [loadingInvite, setLoadingInvite] = useState(false);

    const load = () => {
        client.get(`/organizations/${orgId}/teams/${teamId}`).then((res) => {
            setTeam(res.data);
            setName(res.data.name);
        }).catch((err) => setError(err.response?.data?.detail || "Failed to load team"));

        client.get(`/organizations/${orgId}/teams/${teamId}/members`).then((res) => setMembers(res.data))
        .catch((err) => setError(err.response?.data?.detail || "Failed to load members"));
    };

    useEffect(load, [orgId, teamId]);
    
    useEffect(() => {
        if (!formError) return;
        const timer = setTimeout(() => {
            setFormError("");
        }, 3000);
        return () => clearTimeout(timer);
    }, [formError]);

    const handleUpdate = async (e) => {
        e.preventDefault();
        setError("");
        try {
            await client.patch(`/organizations/${orgId}/teams/${teamId}`, { name });
            load();
        } catch (err) {
            setError(err.response?.data?.detail || "Failed to update team");
        }
    };

    const handleDelete = async () => {
        if (!confirm("Delete this team?")) return;
        try {
            await client.delete(`/organizations/${orgId}/teams/${teamId}`);
            navigate(`/organizations/${orgId}/teams`);
        } catch (err) {
            setError(err.response?.data?.detail || "Failed to delete team");
        }
    };

    // UPDATED: Now sends full_name along with email and role
    const handleAddMember = async (e) => {
        e.preventDefault();
        setFormError("");
        setSuccessMsg("");
        setLoadingInvite(true);
        try {
            const res = await client.post(`/organizations/${orgId}/teams/${teamId}/invite`, { 
                full_name: fullName, 
                email: email, 
                role: role 
            });
            
            const message = res.data?.message || `Operation completed for ${email}`;
            setSuccessMsg(message);
            
            if (res.data?.type === "DIRECT_ADD") {
                load();
            }

            setFullName("");
            setEmail("");
            setRole("MEMBER");
        } catch (err) {
            setFormError(err.response?.data?.detail || "Failed to add/invite member");
        } finally {
            setLoadingInvite(false);
        }
    };

    const handleRemoveMember = async (userId) => {
        if (!confirm("Are you sure you want to remove this member from the team?")) return;
        
        setError("");
        try {
            await client.delete(`/organizations/${orgId}/teams/${teamId}/members/${userId}`);
            load();
        } catch (err) {
            setError(err.response?.data?.detail || "Failed to remove member");
        }
    };

    if (!team) return <p className="text-slate-400 text-sm">Loading...</p>;

    return (
        <div>
            <Link to={`/organizations/${orgId}/teams`} className="inline-flex items-center gap-1 text-sm text-blue-600 mb-4 hover:underline">
                <ArrowLeft size={14} /> Teams
            </Link>

            {error && <div className="mb-4 px-3 py-2 bg-red-50 text-red-600 text-sm rounded-lg">{error}</div>}

            <Card>
                <form onSubmit={handleUpdate} className="flex gap-3 items-end mb-3">
                    <div className="flex-1">
                        <label className="block text-sm font-medium text-slate-600 mb-1">Team Name</label>
                        <input
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                    </div>
                    <Button type="submit">Save</Button>
                    <Button type="button" variant="danger" onClick={handleDelete}>
                        <Trash2 size={16} />
                    </Button>
                </form>
            </Card>

            <div className="flex justify-between items-center mt-8 mb-3">
                <h2 className="text-lg font-semibold text-slate-800">Members</h2>
                <Button onClick={() => {
                    setShowAddForm(!showAddForm);
                    setSuccessMsg("");
                    setFormError("");
                }}>
                    <span className="flex items-center gap-2"><UserPlus size={16} /> Add Member</span>
                </Button>
            </div>

            {showAddForm && (
                <Card className="mb-4">
                    {formError && <div className="mb-3 px-3 py-2 bg-red-50 text-red-600 text-sm rounded-lg">{formError}</div>}
                    {successMsg && (
                        <div className="mb-3 px-3 py-2 bg-emerald-50 text-emerald-600 text-sm rounded-lg flex items-center gap-2">
                            <CheckCircle size={16} /> {successMsg}
                        </div>
                    )}
                    <form onSubmit={handleAddMember} className="grid grid-cols-1 md:grid-cols-4 gap-3 items-end">
                        {/* 1. Full Name Field */}
                        <div>
                            <label className="block text-sm font-medium text-slate-600 mb-1">Full Name</label>
                            <input
                                type="text"
                                value={fullName}
                                onChange={(e) => setFullName(e.target.value)}
                                required
                                placeholder="John Doe"
                                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                        </div>

                        {/* 2. User Email Field */}
                        <div>
                            <label className="block text-sm font-medium text-slate-600 mb-1">User Email</label>
                            <input
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                                placeholder="member@company.com"
                                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                        </div>

                        {/* 3. Role Field */}
                        <div>
                            <label className="block text-sm font-medium text-slate-600 mb-1">Role</label>
                            <select
                                value={role}
                                onChange={(e) => setRole(e.target.value)}
                                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                            >
                                <option value="MEMBER">Member</option>
                                <option value="TEAM_LEAD">Team Lead</option>
                            </select>
                        </div>

                        {/* Submit Button */}
                        <Button type="submit" disabled={loadingInvite} className="w-full">
                            {loadingInvite ? "Processing..." : "Add / Invite"}
                        </Button>
                    </form>
                </Card>
            )}

            <Card>
                <ul className="divide-y divide-slate-100">
                    {members.map((m) => (
                        <li 
                            key={m.id} 
                            className="py-3 flex justify-between items-center group px-2 rounded-lg hover:bg-slate-50/50 transition-colors"
                        >
                            <span className="text-sm text-slate-700 font-medium">
                                {m.user_full_name || m.name}
                            </span>

                            <div className="flex items-center gap-3">
                                <span className="text-xs px-2.5 py-1 bg-slate-100 rounded-full text-slate-500 font-medium">
                                    {m.role}
                                </span>

                                <button
                                    type="button"
                                    onClick={() => handleRemoveMember(m.user_id || m.id)}
                                    title="Remove member"
                                    className="opacity-0 group-hover:opacity-100 p-1.5 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-md transition-all duration-150"
                                >
                                    <Trash2 size={15} />
                                </button>
                            </div>
                        </li>
                    ))}
                </ul>
            </Card>
        </div>
    );
}