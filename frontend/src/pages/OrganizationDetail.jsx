import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { Users, ArrowLeft, UserPlus,MessageSquare  } from "lucide-react";
import client from "../api/client";
import Card from "../components/Card";
import Button from "../components/Button";
import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";
import { Info } from "lucide-react";

export default function OrganizationDetail() {
    const { orgId } = useParams();
    const [org, setOrg] = useState(null);
    const [members, setMembers] = useState([]);
    const [showAddForm, setShowAddForm] = useState(false);
    const [email, setEmail] = useState("");
    const [roleName, setRoleName] = useState("Member");
    const { user: currentUser } = useAuth();
    const [myRole, setMyRole] = useState(null);

    const [error, setError] = useState("");
    const [loading, setLoading] = useState(true);
    const [name, setName] = useState("");
    const [updateError, setUpdateError] = useState("");
    const [updateSuccess, setUpdateSuccess] = useState("");
    const navigate = useNavigate();

    const myMembership = members?.find((m) => m.id === currentUser?.id);
    // const myRole = myMembership?.role;
    const isAdminOrOwner = members !== null;


    const load = () => {
        setLoading(true);
        setError("");

        client
            .get(`/organizations/${orgId}`)
            .then((res) => { setOrg(res.data); setName(res.data.name); })
            .catch((err) => setError(err.response?.data?.detail || "Failed to load organization"))
            .finally(() => setLoading(false));

        client
            .get(`/organizations/${orgId}/users`)
            .then((res) => setMembers(res.data))
           .catch((err) => {
            console.error("Error fetching members:", err);
            setMembers([]); 
        });

        client
            .get(`/organizations/${orgId}/my-membership`)
            .then((res) => setMyRole(res.data.role))
            .catch(() => setMyRole(null));
    };
    useEffect(load, [orgId]);

    const handleAddMember = async (e) => {
        e.preventDefault();
        setError("");
        try {
            await client.post(`/organizations/${orgId}/members`, { email, role_name: roleName });
            setEmail("");
            setShowAddForm(false);
            load();
        } catch (err) {
            setError(err.response?.data?.detail || "Failed to add member");
        }
    };

    const handleUpdateOrg = async (e) => {
        e.preventDefault();
        setUpdateError("");
        setUpdateSuccess("");
        try {
            const res = await client.patch(`/organizations/${orgId}`, { name });
            setOrg(res.data);
            setUpdateSuccess("Organization updated");
        } catch (err) {
            setUpdateError(err.response?.data?.detail || "Failed to update organization");
        }
    };

    const handleDeactivate = async (userId) => {
        if (!confirm("Deactivate this user?")) return;
        try {
            await client.post(`/organizations/${orgId}/users/${userId}/deactivate`);
            load();
        } catch (err) {
            setError(err.response?.data?.detail || "Failed to deactivate user");
        }
    };


    const handleActivate = async (userId) => {
        try {
            await client.post(`/organizations/${orgId}/users/${userId}/activate`);
            load();
        } catch (err) {
            setError(err.response?.data?.detail || "Failed to activate user");
        }
    };



    const handleDeleteOrg = async () => {
        if (!confirm(`Delete "${org.name}"? This cannot be undone.`)) return;
        try {
            await client.delete(`/organizations/${orgId}`);
            navigate("/organizations");
        } catch (err) {
            setError(err.response?.data?.detail || "Only the Owner can delete this organization");
        }
    };



    if (loading) return <p className="text-slate-400 text-sm">Loading...</p>;
    if (error) return <p className="text-red-500 text-sm">{error}</p>;
    if (!org) return <p className="text-slate-400 text-sm">Loading...</p>;



    return (
    <div>
        <Link to="/organizations" className="inline-flex items-center gap-1 text-sm text-blue-600 mb-4 hover:underline">
            <ArrowLeft size={14} /> Organizations
        </Link>

        <h1 className="text-2xl font-bold text-slate-800">{org?.name}</h1>
        <p className="text-slate-400 text-sm">{org?.slug}</p>

        {(myRole === "Owner" || myRole === "Admin") && (
            <Card className="mt-4">
                {updateError && <div className="mb-3 px-3 py-2 bg-red-50 text-red-600 text-sm rounded-lg">{updateError}</div>}
                {updateSuccess && <div className="mb-3 px-3 py-2 bg-green-50 text-green-600 text-sm rounded-lg">{updateSuccess}</div>}
                <form onSubmit={handleUpdateOrg} className="flex gap-3 items-end">
                    <div className="flex-1">
                        <label className="block text-sm font-medium text-slate-600 mb-1">Organization Name</label>
                        <input
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                    </div>

                    <Button type="submit">Save</Button>
                    {myRole === "Owner" && (
                        <Button type="button" variant="danger" onClick={handleDeleteOrg}>
                            Delete Organization
                        </Button>
                    )}
                </form>
            </Card>
        )}

        <div className="flex gap-3 mt-5">
    <Link to={`/organizations/${orgId}/teams`}>
        <Button variant="secondary">Teams</Button>
    </Link>
    <Link to={`/organizations/${orgId}/projects`}>
        <Button variant="secondary">Projects</Button>
    </Link>
    {(myRole === "Owner" || myRole === "Admin") && (
    <Link to={`/organizations/${orgId}/dashboard`}>
        <Button variant="secondary">Dashboard</Button>
    </Link>
)}
    <Link to={`/organizations/${orgId}/assistant`}>
        <Button variant="secondary">
            <span className="flex items-center gap-2">
                <MessageSquare size={16} /> Assistant
            </span>
        </Button>
    </Link>
</div>

        {myRole === "Member" && (
            <Card className="mt-4">
                <div className="flex items-center gap-3">
                    <div className="p-2.5 bg-blue-50 rounded-lg text-blue-600">
                        <Info size={18} />
                    </div>
                    <div>
                        <p className="font-medium text-slate-800">You're a Member of this organization</p>
                        <p className="text-sm text-slate-400 mt-0.5">
                            Browse Teams and Projects above. To create a new project, use the Projects page.
                        </p>
                    </div>
                </div>
            </Card>
        )}

        {/* Members List Section */}
        <div className="mt-8">
                        {/* <div className="flex justify-between items-center mb-3">
                <h2 className="text-lg font-semibold text-slate-800">Members</h2>
                {(myRole === "Owner" || myRole === "Admin") && (
                    <Button onClick={() => setShowAddForm(!showAddForm)}>
                        <span className="flex items-center gap-2">
                            <UserPlus size={16} /> Add Member
                        </span>
                    </Button>
                )}
            </div> */}


            {/* Add Member Form (Only for Owner/Admin) */}
            {showAddForm && (myRole === "Owner" || myRole === "Admin") && (
                <Card className="mb-4">
                    {error && (
                        <div className="mb-3 px-3 py-2 bg-red-50 text-red-600 text-sm rounded-lg">{error}</div>
                    )}
                    <p className="text-xs text-slate-400 mb-3">
                        User must already have an account. They can register at{" "}
                        <Link to="/register" target="_blank" className="text-blue-600 underline">
                            /register
                        </Link>{" "}
                        first.
                    </p>
                    <form onSubmit={handleAddMember} className="flex gap-3 items-end">
                        <div className="flex-1">
                            <label className="block text-sm font-medium text-slate-600 mb-1">Email</label>
                            <input
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-slate-600 mb-1">Role</label>
                            <select
                                value={roleName}
                                onChange={(e) => setRoleName(e.target.value)}
                                className="px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                            >
                                <option value="Member">Member</option>
                                <option value="Admin">Admin</option>
                            </select>
                        </div>
                        <Button type="submit">Add</Button>
                    </form>
                </Card>
            )}

            {/* Members Card */}
            <Card>
                {Array.isArray(members) && members.length > 0 ? (
                    <ul className="divide-y divide-slate-100">
                        {members.map((m) => (
                            <li key={m.id} className="py-3 flex items-center justify-between gap-3">
                                <div className="flex items-center gap-3">
                                    <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold ${
                                        m.is_active ? "bg-blue-100 text-blue-600" : "bg-slate-100 text-slate-400"
                                    }`}>
                                        {m.full_name?.[0]?.toUpperCase() || "U"}
                                    </div>
                                    <div>
                                        <p className={`text-sm font-medium ${m.is_active ? "text-slate-800" : "text-slate-400"}`}>
                                            {m.full_name}
                                        </p>
                                        <p className="text-xs text-slate-400">{m.email}</p>
                                    </div>
                                </div>

                                {/* Sirf Owner ko Deactivate/Reactivate actions milenge */}
                                {myRole === "Owner" && (
                                    <div>
                                        {!m.is_active ? (
                                            <button
                                                onClick={() => handleActivate(m.id)}
                                                className="text-xs text-green-600 hover:underline"
                                            >
                                                Reactivate
                                            </button>
                                        ) : m.id !== currentUser?.id ? (
                                            <button
                                                onClick={() => handleDeactivate(m.id)}
                                                className="text-xs text-red-500 hover:underline"
                                            >
                                                Deactivate
                                            </button>
                                        ) : null}
                                    </div>
                                )}
                            </li>
                        ))}
                    </ul>
                ) : (
                    <p className="text-sm text-slate-400 py-2">No members available or loading...</p>
                )}
            </Card>
        </div>
    </div>
);
}
