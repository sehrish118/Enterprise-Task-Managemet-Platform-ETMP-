// // import { useEffect, useState, useCallback } from "react";
// // import { useParams, Link, useNavigate } from "react-router-dom";
// // import { ArrowLeft, Trash2, UserPlus, Clock, Tag } from "lucide-react";
// // import client from "../api/client";
// // import Card from "../components/Card";
// // import Button from "../components/Button";

// // const PRIORITY_COLORS = {
// //   LOW: "bg-slate-100 text-slate-600",
// //   MEDIUM: "bg-blue-50 text-blue-600",
// //   HIGH: "bg-amber-50 text-amber-600",
// //   URGENT: "bg-red-50 text-red-600",
// // };

// // export default function TaskDetail() {
// //   const params = useParams();
// //   const orgId = params.orgId || params.organizationId;
// //   const projectId = params.projectId;
// //   const taskId = params.taskId || params.id;

// //   const navigate = useNavigate();

// //   const [task, setTask] = useState(null);
// //   const [statuses, setStatuses] = useState([]);
// //   const [assignees, setAssignees] = useState([]);
// //   const [loading, setLoading] = useState(true);
// //   const [error, setError] = useState("");

// //   const [assignEmail, setAssignEmail] = useState("");
// //   const [assigning, setAssigning] = useState(false);
// //   const [assignError, setAssignError] = useState("");

// //   // UUID verification: Invalid literal strings baseline par requests block rahengi
// //   const isValidTaskId = Boolean(
// //     taskId && taskId !== "undefined" && taskId !== "null" && taskId.trim() !== ""
// //   );

// //   const loadTaskData = useCallback(async () => {
// //     if (!isValidTaskId || !orgId) {
// //       setError("Invalid Task or Organization parameters provided.");
// //       setLoading(false);
// //       return;
// //     }

// //     setLoading(true);
// //     setError("");

// //     try {
// //       const taskReq = client.get(
// //         `/organizations/${orgId}/projects/${projectId}/tasks/${taskId}`
// //       );
// //       const statusReq = client.get(`/organizations/${orgId}/task-statuses`);
// //       const assigneeReq = client
// //         .get(
// //           `/organizations/${orgId}/projects/${projectId}/tasks/${taskId}/assignees`
// //         )
// //         .catch(() => ({ data: [] }));

// //       const [taskRes, statusRes, assigneeRes] = await Promise.all([
// //         taskReq,
// //         statusReq,
// //         assigneeReq,
// //       ]);

// //       setTask(taskRes.data);
// //       setStatuses(statusRes.data || []);
      
// //       const rawAssignees = assigneeRes.data;
// //       setAssignees(
// //         Array.isArray(rawAssignees)
// //           ? rawAssignees
// //           : rawAssignees?.items || []
// //       );
// //     } catch (err) {
// //       const detail = err.response?.data?.detail;
// //       setError(
// //         typeof detail === "string" ? detail : "Failed to load task details."
// //       );
// //     } finally {
// //       setLoading(false);
// //     }
// //   }, [orgId, projectId, taskId, isValidTaskId]);

// //   useEffect(() => {
// //     loadTaskData();
// //   }, [loadTaskData]);

// //   // Handle Status Update
// //   const handleStatusChange = async (newStatusId) => {
// //     try {
// //       const res = await client.patch(
// //         `/organizations/${orgId}/projects/${projectId}/tasks/${taskId}`,
// //         { status_id: newStatusId }
// //       );
// //       setTask(res.data);
// //     } catch (err) {
// //       alert(err.response?.data?.detail || "Failed to update status");
// //     }
// //   };

// //   // Handle Task Deletion
// //   const handleDeleteTask = async () => {
// //     if (!window.confirm("Are you sure you want to delete this task?")) return;
// //     try {
// //       await client.delete(
// //         `/organizations/${orgId}/projects/${projectId}/tasks/${taskId}`
// //       );
// //       navigate(`/organizations/${orgId}/projects/${projectId}/tasks`);
// //     } catch (err) {
// //       alert(err.response?.data?.detail || "Failed to delete task");
// //     }
// //   };

// //   // Handle Assignee Submit
// //   const handleAssignSubmit = async (e) => {
// //     e.preventDefault();
// //     if (!assignEmail.trim()) return;

// //     setAssigning(true);
// //     setAssignError("");

// //     try {
// //       await client.post(
// //         `/organizations/${orgId}/projects/${projectId}/tasks/${taskId}/assignees`,
// //         { email: assignEmail.trim() }
// //       );
// //       setAssignEmail("");
// //       await loadTaskData();
// //     } catch (err) {
// //       setAssignError(
// //         err.response?.data?.detail || "Failed to assign user to task"
// //       );
// //     } finally {
// //       setAssigning(false);
// //     }
// //   };

// //   if (!isValidTaskId) {
// //     return (
// //       <div className="p-6 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm space-y-3">
// //         <p className="font-semibold">Invalid Task Request</p>
// //         <p className="text-xs text-red-500">
// //           The task parameter in the route is missing or evaluated to undefined.
// //         </p>
// //         <Link
// //           to={`/organizations/${orgId || ""}/projects/${projectId || ""}/tasks`}
// //           className="inline-flex items-center gap-1 text-blue-600 hover:underline font-medium text-xs"
// //         >
// //           <ArrowLeft size={14} /> Back to Tasks List
// //         </Link>
// //       </div>
// //     );
// //   }

// //   if (loading) {
// //     return <div className="p-4 text-slate-400 text-sm">Loading task details...</div>;
// //   }

// //   if (error) {
// //     return (
// //       <div className="p-6 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm space-y-2">
// //         <p className="font-semibold">{error}</p>
// //         <Link
// //           to={`/organizations/${orgId}/projects/${projectId}/tasks`}
// //           className="inline-flex items-center gap-1 text-blue-600 hover:underline font-medium"
// //         >
// //           <ArrowLeft size={14} /> Back to Tasks List
// //         </Link>
// //       </div>
// //     );
// //   }

// //   if (!task) return null;

// //   return (
// //     <div className="max-w-4xl mx-auto space-y-6">
// //       <div className="flex justify-between items-center">
// //         <Link
// //           to={`/organizations/${orgId}/projects/${projectId}/tasks`}
// //           className="inline-flex items-center gap-1 text-sm text-blue-600 hover:underline"
// //         >
// //           <ArrowLeft size={14} /> Back to Tasks
// //         </Link>
// //         <button
// //           onClick={handleDeleteTask}
// //           className="text-red-600 hover:text-red-700 text-sm flex items-center gap-1 focus:outline-none"
// //         >
// //           <Trash2 size={16} /> Delete Task
// //         </button>
// //       </div>

// //       <Card>
// //         <div className="space-y-4">
// //           <div className="flex justify-between items-start gap-4">
// //             <h1 className="text-2xl font-bold text-slate-800">{task.title}</h1>
// //             <span
// //               className={`text-xs px-2.5 py-1 rounded-full font-semibold ${
// //                 PRIORITY_COLORS[task.priority] || "bg-slate-100 text-slate-600"
// //               }`}
// //             >
// //               {task.priority || "MEDIUM"}
// //             </span>
// //           </div>

// //           <p className="text-slate-600 text-sm whitespace-pre-wrap">
// //             {task.description || "No description provided."}
// //           </p>

// //           <div className="pt-4 border-t border-slate-100 flex flex-wrap gap-6 text-sm text-slate-500">
// //             <div className="flex items-center gap-2">
// //               <Tag size={16} className="text-slate-400" />
// //               <span className="font-medium text-slate-700">Status:</span>
// //               <select
// //                 value={task.status_id || ""}
// //                 onChange={(e) => handleStatusChange(e.target.value)}
// //                 className="px-2.5 py-1 text-xs border border-slate-300 rounded-md bg-white font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer"
// //               >
// //                 {statuses.map((s) => (
// //                   <option key={s.id} value={s.id}>
// //                     {s.name}
// //                   </option>
// //                 ))}
// //               </select>
// //             </div>

// //             {task.due_date && (
// //               <div className="flex items-center gap-2">
// //                 <Clock size={16} className="text-slate-400" />
// //                 <span className="font-medium text-slate-700">Due:</span>
// //                 <span>{new Date(task.due_date).toLocaleDateString()}</span>
// //               </div>
// //             )}
// //           </div>
// //         </div>
// //       </Card>

// //       <Card>
// //         <h2 className="text-lg font-semibold text-slate-800 mb-3 flex items-center gap-2">
// //           <UserPlus size={18} /> Assignees
// //         </h2>

// //         {assignees.length === 0 ? (
// //           <p className="text-sm text-slate-400 mb-4">No user assigned to this task yet.</p>
// //         ) : (
// //           <div className="flex flex-wrap gap-2 mb-4">
// //             {assignees.map((user) => (
// //               <span
// //                 key={user.id || user.user_id || user.email}
// //                 className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-slate-100 text-slate-700 border border-slate-200"
// //               >
// //                 {user.user_full_name || user.full_name || user.user_email || user.email || "Assigned User"}
// //               </span>
// //             ))}
// //           </div>
// //         )}

// //         <form onSubmit={handleAssignSubmit} className="flex gap-2 max-w-md">
// //           <input
// //             type="email"
// //             placeholder="User email to assign..."
// //             value={assignEmail}
// //             onChange={(e) => setAssignEmail(e.target.value)}
// //             required
// //             className="flex-1 px-3 py-1.5 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
// //           />
// //           <Button type="submit" disabled={assigning}>
// //             {assigning ? "Assigning..." : "Assign"}
// //           </Button>
// //         </form>
// //         {assignError && <p className="text-xs text-red-500 mt-2">{assignError}</p>}
// //       </Card>
// //     </div>
// //   );
// // }



// import { useEffect, useState, useCallback } from "react";
// import { useParams, Link, useNavigate } from "react-router-dom";
// import { ArrowLeft, Trash2, UserPlus, Clock, Tag, MessageSquare, Paperclip, Send } from "lucide-react";
// import client from "../api/client";
// import Card from "../components/Card";
// import Button from "../components/Button";

// const PRIORITY_COLORS = {
//   LOW: "bg-slate-100 text-slate-600",
//   MEDIUM: "bg-blue-50 text-blue-600",
//   HIGH: "bg-amber-50 text-amber-600",
//   URGENT: "bg-red-50 text-red-600",
// };

// export default function TaskDetail() {
//   const params = useParams();
//   const orgId = params.orgId || params.organizationId;
//   const projectId = params.projectId;
//   const taskId = params.taskId || params.id;

//   const navigate = useNavigate();

//   const [task, setTask] = useState(null);
//   const [statuses, setStatuses] = useState([]);
//   const [assignees, setAssignees] = useState([]);
//   const [comments, setComments] = useState([]);
//   const [attachments, setAttachments] = useState([]);

//   const [loading, setLoading] = useState(true);
//   const [error, setError] = useState("");

//   const [assignEmail, setAssignEmail] = useState("");
//   const [assigning, setAssigning] = useState(false);
//   const [assignError, setAssignError] = useState("");

//   // Comment & Attachment States
//   const [newComment, setNewComment] = useState("");
//   const [commenting, setCommenting] = useState(false);
//   const [selectedFile, setSelectedFile] = useState(null);
//   const [uploading, setUploading] = useState(false);

//   const isValidTaskId = Boolean(
//     taskId && taskId !== "undefined" && taskId !== "null" && taskId.trim() !== ""
//   );

//   const loadTaskData = useCallback(async () => {
//     if (!isValidTaskId || !orgId) {
//       setError("Invalid Task or Organization parameters provided.");
//       setLoading(false);
//       return;
//     }

//     setLoading(true);
//     setError("");

//     try {
//       const taskReq = client.get(
//         `/organizations/${orgId}/projects/${projectId}/tasks/${taskId}`
//       );
//       const statusReq = client.get(`/organizations/${orgId}/task-statuses`);
//       const assigneeReq = client
//         .get(
//           `/organizations/${orgId}/projects/${projectId}/tasks/${taskId}/assignees`
//         )
//         .catch(() => ({ data: [] }));

//       const commentReq = client
//         .get(`/organizations/${orgId}/projects/${projectId}/tasks/${taskId}/comments`)
//         .catch(() => ({ data: [] }));

//       const attachmentReq = client
//         .get(`/organizations/${orgId}/projects/${projectId}/tasks/${taskId}/attachments`)
//         .catch(() => ({ data: [] }));

//       const [taskRes, statusRes, assigneeRes, commentRes, attachmentRes] = await Promise.all([
//         taskReq,
//         statusReq,
//         assigneeReq,
//         commentReq,
//         attachmentReq,
//       ]);

//       setTask(taskRes.data);
//       setStatuses(statusRes.data || []);
      
//       const rawAssignees = assigneeRes.data;
//       setAssignees(
//         Array.isArray(rawAssignees)
//           ? rawAssignees
//           : rawAssignees?.items || []
//       );

//       setComments(Array.isArray(commentRes.data) ? commentRes.data : commentRes.data?.items || []);
//       setAttachments(Array.isArray(attachmentRes.data) ? attachmentRes.data : attachmentRes.data?.items || []);
//     } catch (err) {
//       const detail = err.response?.data?.detail;
//       setError(
//         typeof detail === "string" ? detail : "Failed to load task details."
//       );
//     } finally {
//       setLoading(false);
//     }
//   }, [orgId, projectId, taskId, isValidTaskId]);

//   useEffect(() => {
//     loadTaskData();
//   }, [loadTaskData]);

//   // Handle Status Update
//   const handleStatusChange = async (newStatusId) => {
//     try {
//       const res = await client.patch(
//         `/organizations/${orgId}/projects/${projectId}/tasks/${taskId}`,
//         { status_id: newStatusId }
//       );
//       setTask(res.data);
//     } catch (err) {
//       alert(err.response?.data?.detail || "Failed to update status");
//     }
//   };

//   // Handle Task Deletion
//   const handleDeleteTask = async () => {
//     if (!window.confirm("Are you sure you want to delete this task?")) return;
//     try {
//       await client.delete(
//         `/organizations/${orgId}/projects/${projectId}/tasks/${taskId}`
//       );
//       navigate(`/organizations/${orgId}/projects/${projectId}/tasks`);
//     } catch (err) {
//       alert(err.response?.data?.detail || "Failed to delete task");
//     }
//   };

//   // Handle Assignee Submit
//   const handleAssignSubmit = async (e) => {
//     e.preventDefault();
//     if (!assignEmail.trim()) return;

//     setAssigning(true);
//     setAssignError("");

//     try {
//       await client.post(
//         `/organizations/${orgId}/projects/${projectId}/tasks/${taskId}/assignees`,
//         { email: assignEmail.trim() }
//       );
//       setAssignEmail("");
//       await loadTaskData();
//     } catch (err) {
//       setAssignError(
//         err.response?.data?.detail || "Failed to assign user to task"
//       );
//     } finally {
//       setAssigning(false);
//     }
//   };

//   // Add Comment
//   const handleAddComment = async (e) => {
//     e.preventDefault();
//     if (!newComment.trim()) return;
//     setCommenting(true);
//     try {
//       await client.post(
//         `/organizations/${orgId}/projects/${projectId}/tasks/${taskId}/comments`,
//         { content: newComment.trim() }
//       );
//       setNewComment("");
//       await loadTaskData();
//     } catch (err) {
//       alert(err.response?.data?.detail || "Failed to post comment");
//     } finally {
//       setCommenting(false);
//     }
//   };

//   // Upload Attachment
//   const handleFileUpload = async (e) => {
//     e.preventDefault();
//     if (!selectedFile) return;
//     setUploading(true);
//     const formData = new FormData();
//     formData.append("file", selectedFile);

//     try {
//       await client.post(
//         `/organizations/${orgId}/projects/${projectId}/tasks/${taskId}/attachments`,
//         formData,
//         { headers: { "Content-Type": "multipart/form-data" } }
//       );
//       setSelectedFile(null);
//       await loadTaskData();
//     } catch (err) {
//       alert(err.response?.data?.detail || "Failed to upload file");
//     } finally {
//       setUploading(false);
//     }
//   };

//   if (!isValidTaskId) {
//     return (
//       <div className="p-6 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm space-y-3">
//         <p className="font-semibold">Invalid Task Request</p>
//         <p className="text-xs text-red-500">
//           The task parameter in the route is missing or evaluated to undefined.
//         </p>
//         <Link
//           to={`/organizations/${orgId || ""}/projects/${projectId || ""}/tasks`}
//           className="inline-flex items-center gap-1 text-blue-600 hover:underline font-medium text-xs"
//         >
//           <ArrowLeft size={14} /> Back to Tasks List
//         </Link>
//       </div>
//     );
//   }

//   if (loading) {
//     return <div className="p-4 text-slate-400 text-sm">Loading task details...</div>;
//   }

//   if (error) {
//     return (
//       <div className="p-6 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm space-y-2">
//         <p className="font-semibold">{error}</p>
//         <Link
//           to={`/organizations/${orgId}/projects/${projectId}/tasks`}
//           className="inline-flex items-center gap-1 text-blue-600 hover:underline font-medium"
//         >
//           <ArrowLeft size={14} /> Back to Tasks List
//         </Link>
//       </div>
//     );
//   }

//   if (!task) return null;

//   return (
//     <div className="max-w-4xl mx-auto space-y-6 pb-12">
//       {/* Top Header */}
//       <div className="flex justify-between items-center">
//         <Link
//           to={`/organizations/${orgId}/projects/${projectId}/tasks`}
//           className="inline-flex items-center gap-1 text-sm text-blue-600 hover:underline"
//         >
//           <ArrowLeft size={14} /> Back to Tasks
//         </Link>
//         <button
//           onClick={handleDeleteTask}
//           className="text-red-600 hover:text-red-700 text-sm flex items-center gap-1 focus:outline-none"
//         >
//           <Trash2 size={16} /> Delete Task
//         </button>
//       </div>

//       {/* Task Information Card */}
//       <Card>
//         <div className="space-y-4">
//           <div className="flex justify-between items-start gap-4">
//             <h1 className="text-2xl font-bold text-slate-800">{task.title}</h1>
//             <span
//               className={`text-xs px-2.5 py-1 rounded-full font-semibold ${
//                 PRIORITY_COLORS[task.priority] || "bg-slate-100 text-slate-600"
//               }`}
//             >
//               {task.priority || "MEDIUM"}
//             </span>
//           </div>

//           <p className="text-slate-600 text-sm whitespace-pre-wrap">
//             {task.description || "No description provided."}
//           </p>

//           <div className="pt-4 border-t border-slate-100 flex flex-wrap gap-6 text-sm text-slate-500">
//             <div className="flex items-center gap-2">
//               <Tag size={16} className="text-slate-400" />
//               <span className="font-medium text-slate-700">Status:</span>
//               <select
//                 value={task.status_id || ""}
//                 onChange={(e) => handleStatusChange(e.target.value)}
//                 className="px-2.5 py-1 text-xs border border-slate-300 rounded-md bg-white font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer"
//               >
//                 {statuses.map((s) => (
//                   <option key={s.id} value={s.id}>
//                     {s.name}
//                   </option>
//                 ))}
//               </select>
//             </div>

//             {task.due_date && (
//               <div className="flex items-center gap-2">
//                 <Clock size={16} className="text-slate-400" />
//                 <span className="font-medium text-slate-700">Due:</span>
//                 <span>{new Date(task.due_date).toLocaleDateString()}</span>
//               </div>
//             )}
//           </div>
//         </div>
//       </Card>

//       {/* Assignees Card */}
//       <Card>
//         <h2 className="text-lg font-semibold text-slate-800 mb-3 flex items-center gap-2">
//           <UserPlus size={18} /> Assignees
//         </h2>

//         {assignees.length === 0 ? (
//           <p className="text-sm text-slate-400 mb-4">No user assigned to this task yet.</p>
//         ) : (
//           <div className="flex flex-wrap gap-2 mb-4">
//             {assignees.map((user) => (
//               <span
//                 key={user.id || user.user_id || user.email}
//                 className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-slate-100 text-slate-700 border border-slate-200"
//               >
//                 {user.user_full_name || user.full_name || user.user_email || user.email || "Assigned User"}
//               </span>
//             ))}
//           </div>
//         )}

//         <form onSubmit={handleAssignSubmit} className="flex gap-2 max-w-md">
//           <input
//             type="email"
//             placeholder="User email to assign..."
//             value={assignEmail}
//             onChange={(e) => setAssignEmail(e.target.value)}
//             required
//             className="flex-1 px-3 py-1.5 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
//           />
//           <Button type="submit" disabled={assigning}>
//             {assigning ? "Assigning..." : "Assign"}
//           </Button>
//         </form>
//         {assignError && <p className="text-xs text-red-500 mt-2">{assignError}</p>}
//       </Card>

//       {/* Attachments Card */}
//       <Card>
//         <h2 className="text-lg font-semibold text-slate-800 mb-3 flex items-center gap-2">
//           <Paperclip size={18} /> Attachments
//         </h2>

//         {attachments.length === 0 ? (
//           <p className="text-sm text-slate-400 mb-4">No attachments uploaded yet.</p>
//         ) : (
//           <div className="space-y-2 mb-4">
//             {attachments.map((att) => (
//               <div
//                 key={att.id}
//                 className="flex justify-between items-center p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm"
//               >
//                 <span className="font-medium text-slate-700 truncate">{att.filename || att.file_name || "Attachment"}</span>
//                 {att.file_url && (
//                   <a
//                     href={att.file_url}
//                     target="_blank"
//                     rel="noreferrer"
//                     className="text-xs text-blue-600 hover:underline font-medium"
//                   >
//                     View / Download
//                   </a>
//                 )}
//               </div>
//             ))}
//           </div>
//         )}

//         <form onSubmit={handleFileUpload} className="flex items-center gap-2 max-w-md">
//           <input
//             type="file"
//             onChange={(e) => setSelectedFile(e.target.files[0])}
//             className="text-xs text-slate-500 file:mr-3 file:py-1.5 file:px-3 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 cursor-pointer"
//           />
//           <Button type="submit" disabled={uploading || !selectedFile}>
//             {uploading ? "Uploading..." : "Upload"}
//           </Button>
//         </form>
//       </Card>

//       {/* Comments Card */}
//       <Card>
//         <h2 className="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
//           <MessageSquare size={18} /> Comments ({comments.length})
//         </h2>

//         <div className="space-y-3 mb-6 max-h-80 overflow-y-auto">
//           {comments.length === 0 ? (
//             <p className="text-sm text-slate-400">No comments yet. Start the conversation!</p>
//           ) : (
//             comments.map((comment) => (
//               <div key={comment.id} className="p-3 bg-slate-50 rounded-lg border border-slate-100 text-sm">
//                 <div className="flex justify-between items-center mb-1 text-xs text-slate-500">
//                   <span className="font-semibold text-slate-700">
//                     {comment.user_name || comment.author || "User"}
//                   </span>
//                   <span>{comment.created_at ? new Date(comment.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ""}</span>
//                 </div>
//                 <p className="text-slate-700 whitespace-pre-wrap">{comment.content}</p>
//               </div>
//             ))
//           )}
//         </div>

//         <form onSubmit={handleAddComment} className="flex gap-2">
//           <input
//             type="text"
//             placeholder="Write a comment..."
//             value={newComment}
//             onChange={(e) => setNewComment(e.target.value)}
//             className="flex-1 px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
//           />
//           <Button type="submit" disabled={commenting || !newComment.trim()}>
//             <Send size={16} />
//           </Button>
//         </form>
//       </Card>
//     </div>
//   );
// }



import { useEffect, useState, useCallback } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { ArrowLeft, Trash2, UserPlus, Clock, Tag, MessageSquare, Paperclip, Send } from "lucide-react";
import client from "../api/client";
import Card from "../components/Card";
import Button from "../components/Button";

const PRIORITY_COLORS = {
  LOW: "bg-slate-100 text-slate-600",
  MEDIUM: "bg-blue-50 text-blue-600",
  HIGH: "bg-amber-50 text-amber-600",
  URGENT: "bg-red-50 text-red-600",
};

export default function TaskDetail() {
  const params = useParams();
  const orgId = params.orgId || params.organizationId;
  const projectId = params.projectId;
  const taskId = params.taskId || params.id;

  const navigate = useNavigate();

  const [task, setTask] = useState(null);
  const [statuses, setStatuses] = useState([]);
  const [assignees, setAssignees] = useState([]);
  const [comments, setComments] = useState([]);
  const [attachments, setAttachments] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [assignEmail, setAssignEmail] = useState("");
  const [assigning, setAssigning] = useState(false);
  const [assignError, setAssignError] = useState("");

  const [newComment, setNewComment] = useState("");
  const [commenting, setCommenting] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);

  const isValidTaskId = Boolean(
    taskId && taskId !== "undefined" && taskId !== "null" && taskId.trim() !== ""
  );

  const loadTaskData = useCallback(async () => {
    if (!isValidTaskId || !orgId || !projectId) {
      setError("Invalid Task, Project, or Organization parameters provided.");
      setLoading(false);
      return;
    }

    setLoading(true);
    setError("");

    try {
      const taskReq = client.get(
        `/organizations/${orgId}/projects/${projectId}/tasks/${taskId}`
      );
      const statusReq = client.get(`/organizations/${orgId}/task-statuses`);
      const assigneeReq = client
        .get(
          `/organizations/${orgId}/projects/${projectId}/tasks/${taskId}/assignees`
        )
        .catch(() => ({ data: [] }));

      const commentReq = client
        .get(`/organizations/${orgId}/projects/${projectId}/tasks/${taskId}/comments`)
        .catch(() => ({ data: [] }));

      const attachmentReq = client
        .get(`/organizations/${orgId}/projects/${projectId}/tasks/${taskId}/attachments`)
        .catch(() => ({ data: [] }));

      const [taskRes, statusRes, assigneeRes, commentRes, attachmentRes] = await Promise.all([
        taskReq,
        statusReq,
        assigneeReq,
        commentReq,
        attachmentReq,
      ]);

      setTask(taskRes.data);
      setStatuses(statusRes.data || []);
      
      const rawAssignees = assigneeRes.data;
      setAssignees(
        Array.isArray(rawAssignees)
          ? rawAssignees
          : rawAssignees?.items || []
      );

      setComments(Array.isArray(commentRes.data) ? commentRes.data : commentRes.data?.items || []);
      setAttachments(Array.isArray(attachmentRes.data) ? attachmentRes.data : attachmentRes.data?.items || []);
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(
        typeof detail === "string" ? detail : "Failed to load task details."
      );
    } finally {
      setLoading(false);
    }
  }, [orgId, projectId, taskId, isValidTaskId]);

  useEffect(() => {
    loadTaskData();
  }, [loadTaskData]);

  const handleStatusChange = async (newStatusId) => {
    try {
      const res = await client.patch(
        `/organizations/${orgId}/projects/${projectId}/tasks/${taskId}`,
        { status_id: newStatusId }
      );
      setTask(res.data);
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to update status");
    }
  };

  const handleDeleteTask = async () => {
    if (!window.confirm("Are you sure you want to delete this task?")) return;
    try {
      await client.delete(
        `/organizations/${orgId}/projects/${projectId}/tasks/${taskId}`
      );
      navigate(`/organizations/${orgId}/projects/${projectId}/tasks`);
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to delete task");
    }
  };

  const handleAssignSubmit = async (e) => {
    e.preventDefault();
    if (!assignEmail.trim()) return;

    setAssigning(true);
    setAssignError("");

    try {
      await client.post(
        `/organizations/${orgId}/projects/${projectId}/tasks/${taskId}/assignees`,
        { email: assignEmail.trim() }
      );
      setAssignEmail("");
      await loadTaskData();
    } catch (err) {
      setAssignError(
        err.response?.data?.detail || "Failed to assign user to task"
      );
    } finally {
      setAssigning(false);
    }
  };

  const handleAddComment = async (e) => {
    e.preventDefault();
    if (!newComment.trim()) return;
    setCommenting(true);
    try {
      await client.post(
        `/organizations/${orgId}/projects/${projectId}/tasks/${taskId}/comments`,
        { content: newComment.trim() }
      );
      setNewComment("");
      await loadTaskData();
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to post comment");
    } finally {
      setCommenting(false);
    }
  };

  const handleFileUpload = async (e) => {
    e.preventDefault();
    if (!selectedFile) return;
    setUploading(true);
    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      await client.post(
        `/organizations/${orgId}/projects/${projectId}/tasks/${taskId}/attachments`,
        formData,
        { headers: { "Content-Type": "multipart/form-data" } }
      );
      setSelectedFile(null);
      await loadTaskData();
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to upload file");
    } finally {
      setUploading(false);
    }
  };

  if (!isValidTaskId) {
    return (
      <div className="p-6 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm space-y-3">
        <p className="font-semibold">Invalid Task Request</p>
        <p className="text-xs text-red-500">
          The task parameter in the route is missing or evaluated to undefined.
        </p>
        <Link
          to={`/organizations/${orgId || ""}/projects/${projectId || ""}/tasks`}
          className="inline-flex items-center gap-1 text-blue-600 hover:underline font-medium text-xs"
        >
          <ArrowLeft size={14} /> Back to Tasks List
        </Link>
      </div>
    );
  }

  if (loading) {
    return <div className="p-4 text-slate-400 text-sm">Loading task details...</div>;
  }

  if (error) {
    return (
      <div className="p-6 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm space-y-2">
        <p className="font-semibold">{error}</p>
        <Link
          to={`/organizations/${orgId}/projects/${projectId}/tasks`}
          className="inline-flex items-center gap-1 text-blue-600 hover:underline font-medium"
        >
          <ArrowLeft size={14} /> Back to Tasks List
        </Link>
      </div>
    );
  }

  if (!task) return null;

  return (
    <div className="max-w-4xl mx-auto space-y-6 pb-12">
      <div className="flex justify-between items-center">
        <Link
          to={`/organizations/${orgId}/projects/${projectId}/tasks`}
          className="inline-flex items-center gap-1 text-sm text-blue-600 hover:underline"
        >
          <ArrowLeft size={14} /> Back to Tasks
        </Link>
        <button
          onClick={handleDeleteTask}
          className="text-red-600 hover:text-red-700 text-sm flex items-center gap-1 focus:outline-none"
        >
          <Trash2 size={16} /> Delete Task
        </button>
      </div>

      <Card>
        <div className="space-y-4">
          <div className="flex justify-between items-start gap-4">
            <h1 className="text-2xl font-bold text-slate-800">{task.title}</h1>
            <span
              className={`text-xs px-2.5 py-1 rounded-full font-semibold ${
                PRIORITY_COLORS[task.priority] || "bg-slate-100 text-slate-600"
              }`}
            >
              {task.priority || "MEDIUM"}
            </span>
          </div>

          <p className="text-slate-600 text-sm whitespace-pre-wrap">
            {task.description || "No description provided."}
          </p>

          <div className="pt-4 border-t border-slate-100 flex flex-wrap gap-6 text-sm text-slate-500">
            <div className="flex items-center gap-2">
              <Tag size={16} className="text-slate-400" />
              <span className="font-medium text-slate-700">Status:</span>
              <select
                value={task.status_id || ""}
                onChange={(e) => handleStatusChange(e.target.value)}
                className="px-2.5 py-1 text-xs border border-slate-300 rounded-md bg-white font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer"
              >
                {statuses.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.name}
                  </option>
                ))}
              </select>
            </div>

            {task.due_date && (
              <div className="flex items-center gap-2">
                <Clock size={16} className="text-slate-400" />
                <span className="font-medium text-slate-700">Due:</span>
                <span>{new Date(task.due_date).toLocaleDateString()}</span>
              </div>
            )}
          </div>
        </div>
      </Card>

      <Card>
        <h2 className="text-lg font-semibold text-slate-800 mb-3 flex items-center gap-2">
          <UserPlus size={18} /> Assignees
        </h2>

        {assignees.length === 0 ? (
          <p className="text-sm text-slate-400 mb-4">No user assigned to this task yet.</p>
        ) : (
          <div className="flex flex-wrap gap-2 mb-4">
            {assignees.map((user) => (
              <span
                key={user.id || user.user_id || user.email}
                className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-slate-100 text-slate-700 border border-slate-200"
              >
                {user.user_full_name || user.full_name || user.user_email || user.email || "Assigned User"}
              </span>
            ))}
          </div>
        )}

        <form onSubmit={handleAssignSubmit} className="flex gap-2 max-w-md">
          <input
            type="email"
            placeholder="User email to assign..."
            value={assignEmail}
            onChange={(e) => setAssignEmail(e.target.value)}
            required
            className="flex-1 px-3 py-1.5 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <Button type="submit" disabled={assigning}>
            {assigning ? "Assigning..." : "Assign"}
          </Button>
        </form>
        {assignError && <p className="text-xs text-red-500 mt-2">{assignError}</p>}
      </Card>

      <Card>
        <h2 className="text-lg font-semibold text-slate-800 mb-3 flex items-center gap-2">
          <Paperclip size={18} /> Attachments
        </h2>

        {attachments.length === 0 ? (
          <p className="text-sm text-slate-400 mb-4">No attachments uploaded yet.</p>
        ) : (
          <div className="space-y-2 mb-4">
            {attachments.map((att) => (
              <div
                key={att.id}
                className="flex justify-between items-center p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm"
              >
                <span className="font-medium text-slate-700 truncate">{att.filename || att.file_name || "Attachment"}</span>
                {att.file_url && (
                  <a
                    href={att.file_url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-xs text-blue-600 hover:underline font-medium"
                  >
                    View / Download
                  </a>
                )}
              </div>
            ))}
          </div>
        )}

        <form onSubmit={handleFileUpload} className="flex items-center gap-2 max-w-md">
          <input
            type="file"
            onChange={(e) => setSelectedFile(e.target.files[0])}
            className="text-xs text-slate-500 file:mr-3 file:py-1.5 file:px-3 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 cursor-pointer"
          />
          <Button type="submit" disabled={uploading || !selectedFile}>
            {uploading ? "Uploading..." : "Upload"}
          </Button>
        </form>
      </Card>

      <Card>
        <h2 className="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
          <MessageSquare size={18} /> Comments ({comments.length})
        </h2>

        <div className="space-y-3 mb-6 max-h-80 overflow-y-auto">
          {comments.length === 0 ? (
            <p className="text-sm text-slate-400">No comments yet. Start the conversation!</p>
          ) : (
            comments.map((comment) => (
              <div key={comment.id} className="p-3 bg-slate-50 rounded-lg border border-slate-100 text-sm">
                <div className="flex justify-between items-center mb-1 text-xs text-slate-500">
                  <span className="font-semibold text-slate-700">
                    {comment.user_full_name || comment.user_name || "User"}
                  </span>
                  <span>{comment.created_at ? new Date(comment.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ""}</span>
                </div>
                <p className="text-slate-700 whitespace-pre-wrap">{comment.content}</p>
              </div>
            ))
          )}
        </div>

        <form onSubmit={handleAddComment} className="flex gap-2">
          <input
            type="text"
            placeholder="Write a comment..."
            value={newComment}
            onChange={(e) => setNewComment(e.target.value)}
            className="flex-1 px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <Button type="submit" disabled={commenting || !newComment.trim()}>
            <Send size={16} />
          </Button>
        </form>
      </Card>
    </div>
  );
}