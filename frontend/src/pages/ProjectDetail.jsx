// // // // import { useEffect, useState } from "react";
// // // // import { useParams, useNavigate, Link } from "react-router-dom";
// // // // import { ArrowLeft, UserPlus, Trash2, ListTodo } from "lucide-react";
// // // // import { useAuth } from "../context/AuthContext";
// // // // import client from "../api/client";
// // // // import Card from "../components/Card";
// // // // import Button from "../components/Button";

// // // // export default function ProjectDetail() {
// // // //     const { orgId, projectId } = useParams();
// // // //     const navigate = useNavigate();
// // // //     const [project, setProject] = useState(null);
// // // //     const [members, setMembers] = useState([]);
// // // //     const [error, setError] = useState("");
// // // //     const [name, setName] = useState("");
// // // //     const [status, setStatus] = useState("ACTIVE");
// // // //     const [showAddForm, setShowAddForm] = useState(false);
// // // //     const [email, setEmail] = useState("");
// // // //     const [role, setRole] = useState("MEMBER");
// // // //     const [formError, setFormError] = useState("");
// // // //     const { user: currentUser } = useAuth();
// // // //     const [selectedUserId, setSelectedUserId] = useState("");
// // // //     const [orgMembers, setOrgMembers] = useState([]);
    

// // // //     const load = () => {
// // // //         client.get(`/organizations/${orgId}/projects/${projectId}`).then((res) => {
// // // //             setProject(res.data);
// // // //             setName(res.data.name);
// // // //             setStatus(res.data.status);
// // // //         });
// // // //         client.get(`/organizations/${orgId}/projects/${projectId}/members`).then((res) => setMembers(res.data));
// // // //     };

// // // //     useEffect(load, [orgId, projectId]);

// // // //     const handleUpdate = async (e) => {
// // // //         e.preventDefault();
// // // //         setError("");
// // // //         try {
// // // //             await client.patch(`/organizations/${orgId}/projects/${projectId}`, { name, status });
// // // //             load();
// // // //         } catch (err) {
// // // //             setError(err.response?.data?.detail || "Failed to update project");
// // // //         }
// // // //     };

// // // //     useEffect(() => {
// // // //     const fetchOrgMembers = async () => {
// // // //         try {
// // // //             // Organization members fetch karne ke liye endpoint
// // // //             const res = await client.get(`/organizations/${organizationId}/members`);
// // // //             setOrgMembers(res.data);
// // // //         } catch (err) {
// // // //             console.error("Failed to load organization members", err);
// // // //         }
// // // //     };

// // // //     if (organizationId) {
// // // //         fetchOrgMembers();
// // // //     }
// // // // }, [organizationId]);

// // // //     const handleDelete = async () => {
// // // //         if (!confirm("Delete this project?")) return;
// // // //         try {
// // // //             await client.delete(`/organizations/${orgId}/projects/${projectId}`);
// // // //             navigate(`/organizations/${orgId}/projects`);
// // // //         } catch (err) {
// // // //             setError(err.response?.data?.detail || "Failed to delete project");
// // // //         }
// // // //     };

// // // //     // const handleAddMember = async (e) => {
// // // //     //     e.preventDefault();
// // // //     //     setFormError("");
// // // //     //     try {
// // // //     //         await client.post(`/organizations/${orgId}/projects/${projectId}/members`, { email, role });
// // // //     //         setEmail("");
// // // //     //         setShowAddForm(false);
// // // //     //         load();   // <-- ye members list reload karta hai
// // // //     //     } catch (err) {
// // // //     //         setFormError(err.response?.data?.detail || "Failed to add member");
// // // //     //     }
// // // //     // };

// // // //    const handleAddMember = async (e) => {
// // // //     e.preventDefault(); // Page refresh hone se rokega
// // // //     setFormError("");

// // // //     try {
// // // //         // Updated payload: Sending 'user_id' instead of 'email'
// // // //         await client.post(
// // // //             `/organizations/${organizationId}/projects/${projectId}/members`,
// // // //             {
// // // //                 user_id: selectedUserId,
// // // //                 role: role
// // // //             }
// // // //         );

// // // //         setShowAddForm(false);
// // // //         setSelectedUserId("");
// // // //         fetchProjectMembers(); // Project members ki list refresh karein
// // // //     } catch (err) {
// // // //         setFormError(err.response?.data?.detail || "Failed to add member");
// // // //     }
// // // // };

// // // //     if (!project) return <p className="text-slate-400 text-sm">Loading...</p>;

// // // //     return (
// // // //         <div>
// // // //             <Link to={`/organizations/${orgId}/projects`} className="inline-flex items-center gap-1 text-sm text-blue-600 mb-4 hover:underline">
// // // //                 <ArrowLeft size={14} /> Projects
// // // //             </Link>

// // // //             {error && <div className="mb-4 px-3 py-2 bg-red-50 text-red-600 text-sm rounded-lg">{error}</div>}

// // // //             <Card>
// // // //                 <form onSubmit={handleUpdate} className="flex gap-3 items-end mb-3">
// // // //                     <div className="flex-1">
// // // //                         <label className="block text-sm font-medium text-slate-600 mb-1">Project Name</label>
// // // //                         <input
// // // //                             value={name}
// // // //                             onChange={(e) => setName(e.target.value)}
// // // //                             className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
// // // //                         />
// // // //                     </div>
// // // //                     <div>
// // // //                         <label className="block text-sm font-medium text-slate-600 mb-1">Status</label>
// // // //                         <select
// // // //                             value={status}
// // // //                             onChange={(e) => setStatus(e.target.value)}
// // // //                             className="px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
// // // //                         >
// // // //                             <option value="ACTIVE">Active</option>
// // // //                             <option value="ON_HOLD">On Hold</option>
// // // //                             <option value="COMPLETED">Completed</option>
// // // //                             <option value="ARCHIVED">Archived</option>
// // // //                         </select>
// // // //                     </div>
// // // //                     <Button type="submit">Save</Button>
// // // //                     <Button type="button" variant="danger" onClick={handleDelete}>
// // // //                         <Trash2 size={16} />
// // // //                     </Button>
// // // //                 </form>
// // // //                 <Link to={`/organizations/${orgId}/projects/${projectId}/tasks`}>
// // // //                     <Button variant="secondary">
// // // //                         <span className="flex items-center gap-2"><ListTodo size={16} /> View Tasks</span>
// // // //                     </Button>
// // // //                 </Link>
// // // //             </Card>

// // // //            <div className="flex justify-between items-center mt-8 mb-3">
// // // //     <h2 className="text-lg font-semibold text-slate-800">Members</h2>
// // // //     <Button onClick={() => setShowAddForm(!showAddForm)}>
// // // //         <span className="flex items-center gap-2"><UserPlus size={16} /> Add Member</span>
// // // //     </Button>
// // // // </div>
// // // // {showAddForm && (
// // // //     <Card className="mb-4">
// // // //         {formError && (
// // // //             <div className="mb-3 px-3 py-2 bg-red-50 text-red-600 text-sm rounded-lg">
// // // //                 {formError}
// // // //             </div>
// // // //         )}
// // // //         <form onSubmit={handleAddMember} className="flex gap-3 items-end">
// // // //             <div className="flex-1">
// // // //                 <label className="block text-sm font-medium text-slate-600 mb-1">
// // // //                     Select Member
// // // //                 </label>
// // // //                <select
// // // //     value={selectedUserId}
// // // //     onChange={(e) => setSelectedUserId(e.target.value)}
// // // //     required
// // // //     className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
// // // // >
// // // //     <option value="">-- Select Organization Member --</option>
// // // //     {orgMembers && orgMembers.length > 0 ? (
// // // //         orgMembers.map((member) => (
// // // //             <option 
// // // //                 key={member.user_id || member.id} 
// // // //                 value={member.user_id || member.id}
// // // //             >
// // // //                 {member.user_full_name || member.full_name || member.name} ({member.email})
// // // //             </option>
// // // //         ))
// // // //     ) : (
// // // //         <option disabled>No organization members available</option>
// // // //     )}
// // // // </select>
// // // //             </div>

// // // //             <div>
// // // //                 <label className="block text-sm font-medium text-slate-600 mb-1">Role</label>
// // // //                 <select
// // // //                     value={role}
// // // //                     onChange={(e) => setRole(e.target.value)}
// // // //                     className="px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
// // // //                 >
// // // //                     <option value="MEMBER">Member</option>
// // // //                     <option value="PROJECT_MANAGER">Project Manager</option>
// // // //                 </select>
// // // //             </div>

// // // //             <Button type="submit" disabled={!selectedUserId}>Add</Button>
// // // //         </form>
// // // //     </Card>
// // // // )}
// // // //             <Card>
// // // //                 <ul className="divide-y divide-slate-100">
// // // //                     {members.map((m) => (
// // // //                         <li key={m.id} className="py-3 flex justify-between items-center">
// // // //                             <span className="text-sm text-slate-700">
// // // //                                 {m.user_full_name}
// // // //                                 {m.user_id === currentUser?.id && (
// // // //                                     <span className="text-slate-400 ml-1">(you)</span>
// // // //                                 )}
// // // //                             </span>
// // // //                             <span className="text-xs px-2 py-1 bg-slate-100 rounded-full text-slate-500">{m.role}</span>
// // // //                         </li>
// // // //                     ))}
// // // //                 </ul>
// // // //             </Card>
// // // //         </div>
// // // //     );
// // // // }








// // // import { useEffect, useState } from "react";
// // // import { useParams, useNavigate, Link } from "react-router-dom";
// // // import { ArrowLeft, UserPlus, Trash2, ListTodo } from "lucide-react";
// // // import { useAuth } from "../context/AuthContext";
// // // import client from "../api/client";
// // // import Card from "../components/Card";
// // // import Button from "../components/Button";

// // // export default function ProjectDetail() {
// // //     const { orgId, projectId } = useParams();
// // //     const navigate = useNavigate();
// // //     const [project, setProject] = useState(null);
// // //     const [members, setMembers] = useState([]);
// // //     const [error, setError] = useState("");
// // //     const [name, setName] = useState("");
// // //     const [status, setStatus] = useState("ACTIVE");
// // //     const [showAddForm, setShowAddForm] = useState(false);
// // //     const [role, setRole] = useState("MEMBER");
// // //     const [formError, setFormError] = useState("");
// // //     const { user: currentUser } = useAuth();
// // //     const [selectedUserId, setSelectedUserId] = useState("");
// // //     const [orgMembers, setOrgMembers] = useState([]);

// // //     const load = () => {
// // //         client.get(`/organizations/${orgId}/projects/${projectId}`).then((res) => {
// // //             setProject(res.data);
// // //             setName(res.data.name);
// // //             setStatus(res.data.status);
// // //         });
// // //         client.get(`/organizations/${orgId}/projects/${projectId}/members`).then((res) => setMembers(res.data));
// // //     };

// // //     useEffect(load, [orgId, projectId]);

// // //     useEffect(() => {
// // //     const fetchOrgMembers = async () => {
// // //         try {
// // //             // Updated endpoint with trailing slash or alternative path
// // //             const res = await client.get(`/organizations/${orgId}/members/`);
// // //             setOrgMembers(res.data);
// // //         } catch (err) {
// // //             console.error("Failed to load organization members:", err.response?.status);
// // //             // Fallback for fallback routing if needed
// // //             if (err.response?.status === 405 || err.response?.status === 404) {
// // //                 try {
// // //                     const fallbackRes = await client.get(`/organizations/${orgId}/users`);
// // //                     setOrgMembers(fallbackRes.data);
// // //                 } catch (fallbackErr) {
// // //                     console.error("Fallback route also failed", fallbackErr);
// // //                 }
// // //             }
// // //         }
// // //     };

// // //     if (orgId) {
// // //         fetchOrgMembers();
// // //     }
// // // }, [orgId]);

// // //     const handleUpdate = async (e) => {
// // //         e.preventDefault();
// // //         setError("");
// // //         try {
// // //             await client.patch(`/organizations/${orgId}/projects/${projectId}`, { name, status });
// // //             load();
// // //         } catch (err) {
// // //             setError(err.response?.data?.detail || "Failed to update project");
// // //         }
// // //     };

// // //     const handleDelete = async () => {
// // //         if (!confirm("Delete this project?")) return;
// // //         try {
// // //             await client.delete(`/organizations/${orgId}/projects/${projectId}`);
// // //             navigate(`/organizations/${orgId}/projects`);
// // //         } catch (err) {
// // //             setError(err.response?.data?.detail || "Failed to delete project");
// // //         }
// // //     };

// // //     const handleAddMember = async (e) => {
// // //         e.preventDefault();
// // //         setFormError("");

// // //         try {
// // //             // Fixed: orgId variable used instead of organizationId
// // //             await client.post(
// // //                 `/organizations/${orgId}/projects/${projectId}/members`,
// // //                 {
// // //                     user_id: selectedUserId,
// // //                     role: "MEMBER"
// // //                 }
// // //             );

// // //             setShowAddForm(false);
// // //             setSelectedUserId("");
// // //             load(); // Fixed: Calls load() to refresh project members list
// // //         } catch (err) {
// // //             setFormError(err.response?.data?.detail || "Failed to add member");
// // //         }
// // //     };

// // //     if (!project) return <p className="text-slate-400 text-sm">Loading...</p>;

// // //     return (
// // //         <div>
// // //             <Link to={`/organizations/${orgId}/projects`} className="inline-flex items-center gap-1 text-sm text-blue-600 mb-4 hover:underline">
// // //                 <ArrowLeft size={14} /> Projects
// // //             </Link>

// // //             {error && <div className="mb-4 px-3 py-2 bg-red-50 text-red-600 text-sm rounded-lg">{error}</div>}

// // //             <Card>
// // //                 <form onSubmit={handleUpdate} className="flex gap-3 items-end mb-3">
// // //                     <div className="flex-1">
// // //                         <label className="block text-sm font-medium text-slate-600 mb-1">Project Name</label>
// // //                         <input
// // //                             value={name}
// // //                             onChange={(e) => setName(e.target.value)}
// // //                             className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
// // //                         />
// // //                     </div>
// // //                     <div>
// // //                         <label className="block text-sm font-medium text-slate-600 mb-1">Status</label>
// // //                         <select
// // //                             value={status}
// // //                             onChange={(e) => setStatus(e.target.value)}
// // //                             className="px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
// // //                         >
// // //                             <option value="ACTIVE">Active</option>
// // //                             <option value="ON_HOLD">On Hold</option>
// // //                             <option value="COMPLETED">Completed</option>
// // //                             <option value="ARCHIVED">Archived</option>
// // //                         </select>
// // //                     </div>
// // //                     <Button type="submit">Save</Button>
// // //                     <Button type="button" variant="danger" onClick={handleDelete}>
// // //                         <Trash2 size={16} />
// // //                     </Button>
// // //                 </form>
// // //                 <Link to={`/organizations/${orgId}/projects/${projectId}/tasks`}>
// // //                     <Button variant="secondary">
// // //                         <span className="flex items-center gap-2"><ListTodo size={16} /> View Tasks</span>
// // //                     </Button>
// // //                 </Link>
// // //             </Card>

// // //             <div className="flex justify-between items-center mt-8 mb-3">
// // //                 <h2 className="text-lg font-semibold text-slate-800">Members</h2>
// // //                 <Button onClick={() => setShowAddForm(!showAddForm)}>
// // //                     <span className="flex items-center gap-2"><UserPlus size={16} /> Add Member</span>
// // //                 </Button>
// // //             </div>

// // //             {showAddForm && (
// // //                 <Card className="mb-4">
// // //                     {formError && (
// // //                         <div className="mb-3 px-3 py-2 bg-red-50 text-red-600 text-sm rounded-lg">
// // //                             {formError}
// // //                         </div>
// // //                     )}
// // //                     <form onSubmit={handleAddMember} className="flex gap-3 items-end">
// // //                         <div className="flex-1">
// // //                             <label className="block text-sm font-medium text-slate-600 mb-1">
// // //                                 Select Member
// // //                             </label>
// // //                             <select
// // //                                 value={selectedUserId}
// // //                                 onChange={(e) => setSelectedUserId(e.target.value)}
// // //                                 required
// // //                                 className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
// // //                             >
// // //                                 <option value="">-- Select Organization Member --</option>
// // //                                 {orgMembers && orgMembers.length > 0 ? (
// // //                                     orgMembers.map((member) => (
// // //                                         <option 
// // //                                             key={member.user_id || member.id} 
// // //                                             value={member.user_id || member.id}
// // //                                         >
// // //                                             {member.user_full_name || member.full_name || member.name} ({member.email})
// // //                                         </option>
// // //                                     ))
// // //                                 ) : (
// // //                                     <option disabled>No organization members available</option>
// // //                                 )}
// // //                             </select>
// // //                         </div>
// // // {/* 
// // //                         <div>
// // //                             <label className="block text-sm font-medium text-slate-600 mb-1">Role</label>
// // //                             <select
// // //                                 value={role}
// // //                                 onChange={(e) => setRole(e.target.value)}
// // //                                 className="px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
// // //                             >
// // //                                 <option value="MEMBER">Member</option>
// // //                                 <option value="PROJECT_MANAGER">Project Manager</option>
// // //                             </select>
// // //                         </div> */}

// // //                         <Button type="submit">Add Member</Button>
// // //                     </form>
// // //                 </Card>
// // //             )}

// // //             <Card>
// // //                 <ul className="divide-y divide-slate-100">
// // //                     {members.map((m) => (
// // //                         <li key={m.id} className="py-3 flex justify-between items-center">
// // //                             <span className="text-sm text-slate-700">
// // //                                 {m.user_full_name}
// // //                                 {m.user_id === currentUser?.id && (
// // //                                     <span className="text-slate-400 ml-1">(you)</span>
// // //                                 )}
// // //                             </span>
// // //                             <span className="text-xs px-2 py-1 bg-slate-100 rounded-full text-slate-500">{m.role}</span>
// // //                         </li>
// // //                     ))}
// // //                 </ul>
// // //             </Card>
// // //         </div>
// // //     );
// // // }


import { useEffect, useState, useCallback } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { ArrowLeft, UserPlus, Trash2, ListTodo } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import client from "../api/client";
import Card from "../components/Card";
import Button from "../components/Button";

export default function ProjectDetail() {
    const { orgId, projectId } = useParams();
    const navigate = useNavigate();
    const { user: currentUser } = useAuth();

    const [project, setProject] = useState(null);
    const [members, setMembers] = useState([]);
    const [orgMembers, setOrgMembers] = useState([]);
    const [name, setName] = useState("");
    const [status, setStatus] = useState("ACTIVE");
    const [selectedUserId, setSelectedUserId] = useState("");
    
    const [showAddForm, setShowAddForm] = useState(false);
    const [error, setError] = useState("");
    const [formError, setFormError] = useState("");

    const load = useCallback(() => {
        client.get(`/organizations/${orgId}/projects/${projectId}`)
            .then((res) => {
                setProject(res.data);
                setName(res.data.name);
                setStatus(res.data.status);
            })
            .catch((err) => setError(err.response?.data?.detail || "Failed to load project"));

        client.get(`/organizations/${orgId}/projects/${projectId}/members`)
            .then((res) => setMembers(res.data))
            .catch((err) => console.error("Failed to load project members", err));
    }, [orgId, projectId]);

    useEffect(() => {
        load();
    }, [load]);

    useEffect(() => {
        const fetchOrgMembers = async () => {
            try {
                const res = await client.get(`/organizations/${orgId}/users`);
                setOrgMembers(res.data);
            } catch (err) {
                console.error("Failed to load organization members:", err.response?.status);
            }
        };

        if (orgId) {
            fetchOrgMembers();
        }
    }, [orgId]);

    const handleUpdate = async (e) => {
        e.preventDefault();
        setError("");
        try {
            await client.patch(`/organizations/${orgId}/projects/${projectId}`, { name, status });
            load();
        } catch (err) {
            setError(err.response?.data?.detail || "Failed to update project");
        }
    };

    const handleDelete = async () => {
        if (!confirm("Delete this project?")) return;
        try {
            await client.delete(`/organizations/${orgId}/projects/${projectId}`);
            navigate(`/organizations/${orgId}/projects`);
        } catch (err) {
            setError(err.response?.data?.detail || "Failed to delete project");
        }
    };

    const handleAddMember = async (e) => {
        e.preventDefault();
        setFormError("");

        try {
            await client.post(
                `/organizations/${orgId}/projects/${projectId}/members`,
                {
                    user_id: selectedUserId,
                    role: "MEMBER"
                }
            );

            setShowAddForm(false);
            setSelectedUserId("");
            load();
        } catch (err) {
            setFormError(err.response?.data?.detail || "Failed to add member");
        }
    };

    const handleRemoveMember = async (userId) => {
        if (!confirm("Are you sure you want to remove this member from the project?")) return;
        try {
            await client.delete(`/organizations/${orgId}/projects/${projectId}/members/${userId}`);
            load();
        } catch (err) {
            setError(err.response?.data?.detail || "Failed to remove member");
        }
    };

    if (!project) return <p className="text-slate-400 text-sm p-4">Loading...</p>;

    // Filter out users who are already project members
    const availableOrgMembers = orgMembers.filter(
        (orgMember) => !members.some((m) => (m.user_id || m.id) === (orgMember.user_id || orgMember.id))
    );

    return (
        <div>
            <Link to={`/organizations/${orgId}/projects`} className="inline-flex items-center gap-1 text-sm text-blue-600 mb-4 hover:underline">
                <ArrowLeft size={14} /> Projects
            </Link>

            {error && <div className="mb-4 px-3 py-2 bg-red-50 text-red-600 text-sm rounded-lg">{error}</div>}

            <Card>
                <form onSubmit={handleUpdate} className="flex gap-3 items-end mb-3">
                    <div className="flex-1">
                        <label className="block text-sm font-medium text-slate-600 mb-1">Project Name</label>
                        <input
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-slate-600 mb-1">Status</label>
                        <select
                            value={status}
                            onChange={(e) => setStatus(e.target.value)}
                            className="px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                        >
                            <option value="ACTIVE">Active</option>
                            <option value="ON_HOLD">On Hold</option>
                            <option value="COMPLETED">Completed</option>
                            <option value="ARCHIVED">Archived</option>
                        </select>
                    </div>
                    <Button type="submit">Save</Button>
                    <Button type="button" variant="danger" onClick={handleDelete}>
                        <Trash2 size={16} />
                    </Button>
                </form>

                <Link to={`/organizations/${orgId}/projects/${projectId}/tasks`}>
                    <Button variant="secondary">
                        <span className="flex items-center gap-2"><ListTodo size={16} /> View Tasks</span>
                    </Button>
                </Link>
            </Card>

            <div className="flex justify-between items-center mt-8 mb-3">
                <h2 className="text-lg font-semibold text-slate-800">Members</h2>
                <Button onClick={() => setShowAddForm(!showAddForm)}>
                    <span className="flex items-center gap-2"><UserPlus size={16} /> Add Member</span>
                </Button>
            </div>

            {showAddForm && (
                <Card className="mb-4">
                    {formError && (
                        <div className="mb-3 px-3 py-2 bg-red-50 text-red-600 text-sm rounded-lg">
                            {formError}
                        </div>
                    )}
                    <form onSubmit={handleAddMember} className="flex gap-3 items-end">
                        <div className="flex-1">
                            <label className="block text-sm font-medium text-slate-600 mb-1">
                                Select Member
                            </label>
                            <select
                                value={selectedUserId}
                                onChange={(e) => setSelectedUserId(e.target.value)}
                                required
                                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                            >
                                <option value="">-- Select Organization Member --</option>
                                {availableOrgMembers.length > 0 ? (
                                    availableOrgMembers.map((member) => {
                                        const userId = member.user_id || member.id;
                                        const displayName = member.user_full_name || member.full_name || member.name;
                                        return (
                                            <option key={userId} value={userId}>
                                                {displayName} ({member.email})
                                            </option>
                                        );
                                    })
                                ) : (
                                    <option disabled>No available members to add</option>
                                )}
                            </select>
                        </div>
                        <Button type="submit">Add Member</Button>
                    </form>
                </Card>
            )}

            <Card>
                <ul className="divide-y divide-slate-100">
                    {members.map((m) => {
                        const memberId = m.user_id || m.id;
                        const isManager = m.role === "PROJECT_MANAGER" || m.role === "LEAD";
                        const isLastMember = members.length === 1;
                        const isDisabled = isManager || isLastMember;

                        return (
                            <li key={memberId} className="py-3 flex justify-between items-center">
                                <span className="text-sm text-slate-700">
                                    {m.user_full_name || m.full_name || m.name}
                                    {memberId === currentUser?.id && (
                                        <span className="text-slate-400 ml-1">(you)</span>
                                    )}
                                </span>
                                <div className="flex items-center gap-3">
                                    <span className="text-xs px-2 py-1 bg-slate-100 rounded-full text-slate-500">
                                        {m.role}
                                    </span>
                                    
                                    <button
                                        onClick={() => handleRemoveMember(memberId)}
                                        disabled={isDisabled}
                                        className={`p-1 transition-colors ${
                                            isDisabled 
                                                ? "text-slate-300 cursor-not-allowed" 
                                                : "text-slate-400 hover:text-red-600"
                                        }`}
                                        title={
                                            isManager
                                                ? "Cannot remove Project Manager"
                                                : isLastMember
                                                ? "Cannot remove last member. Delete project instead."
                                                : "Remove Member"
                                        }
                                    >
                                        <Trash2 size={16} />
                                    </button>
                                </div>
                            </li>
                        );
                    })}
                </ul>
            </Card>
        </div>
    );
}



