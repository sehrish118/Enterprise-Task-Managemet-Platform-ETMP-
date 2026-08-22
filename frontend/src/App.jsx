// import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
// import { AuthProvider } from "./context/AuthContext";
// import ProtectedRoute from "./components/ProtectedRoute";
// import Layout from "./components/Layout";
// import Login from "./pages/Login";
// import Register from "./pages/Register";
// import Dashboard from "./pages/Dashboard";
// import Organizations from "./pages/Organizations";
// import OrganizationDetail from "./pages/OrganizationDetail";
// import Teams from "./pages/Teams";
// import TeamDetail from "./pages/TeamDetail";
// import Projects from "./pages/Projects";
// import ProjectDetail from "./pages/ProjectDetail";
// import Tasks from "./pages/Tasks";
// import TaskDetail from "./pages/TaskDetail";
// import Notifications from "./pages/Notifications";
// import Profile from "./pages/Profile";
// import OrgDashboard from "./pages/OrgDashboard";
// import ActivityLogs from "./pages/ActivityLogs";
// import { ThemeProvider } from "./context/ThemeContext";
// import AcceptInvite from "./pages/AcceptInvite";
// function App() {
//   return (
//     <ThemeProvider>
//       <BrowserRouter>
//         <AuthProvider>
//           <Routes>

//             <Route path="/login" element={<Login />} />
//             <Route path="/register" element={<Register />} />

//             <Route
//               element={
//                 <ProtectedRoute>
//                   <Layout />
//                 </ProtectedRoute>
//               }
//             >
//               <Route path="/dashboard" element={<Dashboard />} />
//               <Route path="/organizations" element={<Organizations />} />
//               <Route path="/organizations/:orgId" element={<OrganizationDetail />} />
//               <Route path="/organizations/:orgId/teams" element={<Teams />} />
//               <Route path="/organizations/:orgId/teams/:teamId" element={<TeamDetail />} />
//               <Route path="/organizations/:orgId/projects" element={<Projects />} />
//               <Route path="/organizations/:orgId/projects/:projectId" element={<ProjectDetail />} />
//               <Route path="/organizations/:orgId/projects/:projectId/tasks" element={<Tasks />} />
//               <Route path="/organizations/:orgId/projects/:projectId/tasks/:taskId" element={<TaskDetail />} />
//               <Route path="/notifications" element={<Notifications />} />
//               <Route path="/profile" element={<Profile />} />
//               <Route path="/organizations/:orgId/dashboard" element={<OrgDashboard />} />
//               <Route path="/organizations/:orgId/activity-logs" element={<ActivityLogs />} />
//             </Route>

//             <Route path="/" element={<Navigate to="/dashboard" replace />} />
//           </Routes>
//         </AuthProvider>
//       </BrowserRouter>
//     </ThemeProvider>
//   );
// }


// export default App;



import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import Layout from "./components/Layout";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import Organizations from "./pages/Organizations";
import OrganizationDetail from "./pages/OrganizationDetail";
import Teams from "./pages/Teams";
import TeamDetail from "./pages/TeamDetail";
import Projects from "./pages/Projects";
import ProjectDetail from "./pages/ProjectDetail";
import Tasks from "./pages/Tasks";
import TaskDetail from "./pages/TaskDetail";
import Notifications from "./pages/Notifications";
import Profile from "./pages/Profile";
import OrgDashboard from "./pages/OrgDashboard";
import ActivityLogs from "./pages/ActivityLogs";
import { ThemeProvider } from "./context/ThemeContext";
import AcceptInvite from "./pages/AcceptInvite";

function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <AuthProvider>
          <Routes>
            {/* Public Routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/accept-invite" element={<AcceptInvite />} />

            {/* Protected Routes */}
            <Route
              element={
                <ProtectedRoute>
                  <Layout />
                </ProtectedRoute>
              }
            >
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/organizations" element={<Organizations />} />
              <Route path="/organizations/:orgId" element={<OrganizationDetail />} />
              <Route path="/organizations/:orgId/teams" element={<Teams />} />
              <Route path="/organizations/:orgId/teams/:teamId" element={<TeamDetail />} />
              <Route path="/organizations/:orgId/projects" element={<Projects />} />
              <Route path="/organizations/:orgId/projects/:projectId" element={<ProjectDetail />} />
              <Route path="/organizations/:orgId/projects/:projectId/tasks" element={<Tasks />} />
              <Route path="/organizations/:orgId/projects/:projectId/tasks/:taskId" element={<TaskDetail />} />
              <Route path="/notifications" element={<Notifications />} />
              <Route path="/profile" element={<Profile />} />
              <Route path="/organizations/:orgId/dashboard" element={<OrgDashboard />} />
              <Route path="/organizations/:orgId/activity-logs" element={<ActivityLogs />} />
            </Route>

            <Route path="/" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;