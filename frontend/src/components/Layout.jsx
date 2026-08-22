import { Link, Outlet, useNavigate } from "react-router-dom";
import { LayoutDashboard, Building2, Bell, User, LogOut } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { Sun, Moon } from "lucide-react";
import { useTheme } from "../context/ThemeContext";


export default function Layout() {
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate("/login");
    };
    const { isDark, toggleTheme } = useTheme();

    const navItems = [
        { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
        { to: "/organizations", label: "Organizations", icon: Building2 },
        { to: "/notifications", label: "Notifications", icon: Bell },
        { to: "/profile", label: "Profile", icon: User },
    ];

    return (
        <div className="flex h-screen bg-slate-50 dark:bg-slate-900">
            <aside className="w-64 bg-white dark:bg-slate-800 border-r border-slate-200 dark:border-slate-700 flex flex-col">
                <div className="px-6 py-5 border-b border-slate-200 dark:border-slate-700">
                    <h1 className="text-lg font-bold text-blue-600 dark:text-blue-400">ETMP</h1>

                    <p className="text-xs text-slate-400 mt-0.5">Task Management</p>
                </div>

                <nav className="flex-1 px-3 py-4 space-y-1">
                    {navItems.map(({ to, label, icon: Icon }) => (
                        <Link
                            key={to}
                            to={to}
                            className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-slate-600 hover:bg-blue-50 hover:text-blue-600 transition-colors"
                        >
                            <Icon size={18} />
                            {label}
                        </Link>
                    ))}
                </nav>

                <div className="px-3 py-4 border-t border-slate-200">
                    <div className="px-3 py-2 mb-2">
                        <p className="text-sm font-medium text-slate-800 truncate">
                            {user?.full_name}
                        </p>
                        <p className="text-xs text-slate-400 truncate">{user?.email}</p>
                    </div>
                    <button
                        onClick={handleLogout}
                        className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-red-500 hover:bg-red-50 w-full transition-colors"
                    >
                        <LogOut size={18} />
                        Logout
                    </button>
                    <button
                        onClick={toggleTheme}
                        className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 w-full transition-colors"
                    >
                        {isDark ? <Sun size={18} /> : <Moon size={18} />}
                        {isDark ? "Light Mode" : "Dark Mode"}
                    </button>
                </div>
            </aside>

            {/* Main content */}
            <main className="flex-1 overflow-y-auto">
                <div className="max-w-5xl mx-auto px-8 py-8">
                    <Outlet />
                </div>
            </main>
        </div>
    );
}