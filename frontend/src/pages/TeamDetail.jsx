
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
    }, 3000); // 4 seconds baad clear ho jayega
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

   

    // UPDATED: Dynamic handling for Direct Add (Existing Org Member) vs Email Invite (New User)
    const handleAddMember = async (e) => {
        e.preventDefault();
        setFormError("");
        setSuccessMsg("");
        setLoadingInvite(true);
        try {
            const res = await client.post(`/organizations/${orgId}/teams/${teamId}/invite`, { email, role });
            
            const message = res.data?.message || `Operation completed for ${email}`;
            setSuccessMsg(message);
            
            // Agar user directly add hua hai, toh team members list refresh karein
            if (res.data?.type === "DIRECT_ADD") {
                load();
            }

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
        load(); // Refresh member list
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
                    <form onSubmit={handleAddMember} className="flex gap-3 items-end">
                        <div className="flex-1">
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
                        <div>
                            <label className="block text-sm font-medium text-slate-600 mb-1">Role</label>
                            <select
                                value={role}
                                onChange={(e) => setRole(e.target.value)}
                                className="px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                            >
                                <option value="MEMBER">Member</option>
                                <option value="TEAM_LEAD">Team Lead</option>
                            </select>
                        </div>
                        <Button type="submit" disabled={loadingInvite}>
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
                {/* Member Name */}
                <span className="text-sm text-slate-700 font-medium">
                    {m.user_full_name || m.name}
                </span>

                {/* Role Badge + Delete Icon */}
                <div className="flex items-center gap-3">
                    <span className="text-xs px-2.5 py-1 bg-slate-100 rounded-full text-slate-500 font-medium">
                        {m.role}
                    </span>

                    {/* Delete Button (Only visible on hover) */}
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