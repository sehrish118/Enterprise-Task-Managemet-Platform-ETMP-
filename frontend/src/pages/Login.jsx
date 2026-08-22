import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Login() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);
    const { login } = useAuth();
    const navigate = useNavigate();

    // const handleSubmit = async (e) => {
    //     e.preventDefault();
    //     setError("");
    //     setLoading(true);
    //     try {
    //         await login(email, password);
    //         navigate("/dashboard");
    //     } catch (err) {
    //         setError(err.response?.data?.detail || "Login failed");
    //     } finally {
    //         setLoading(false);
    //     }
    // };


    // src/pages/Login.jsx

const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
        const userData = await login(email, password);

        // Check if user is an Owner or a Member
        // (Note: Adapt 'user_organizations' key based on your exact /auth/me API response)
        if (userData.is_owner || userData.role === "OWNER") {
            navigate("/dashboard");
        } else if (userData.organizations && userData.organizations.length > 0) {
            // Member ko direct uski assigned organization ke Teams view par redirect karein
            const firstOrgId = userData.organizations[0].id;
            navigate(`/organizations/${firstOrgId}/teams`);
        } else {
            // Fallback for general members
            navigate("/dashboard");
        }
    } catch (err) {
        setError(err.response?.data?.detail || "Login failed");
    } finally {
        setLoading(false);
    }
};

    return (
        <div className="min-h-screen bg-slate-50 flex items-center justify-center px-4">
            <div className="w-full max-w-sm">
                <div className="text-center mb-8">
                    <h1 className="text-2xl font-bold text-blue-600">ETMP</h1>
                    <p className="text-slate-400 text-sm mt-1">Enterprise Task Management</p>
                </div>

                <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-8">
                    <h2 className="text-lg font-semibold text-slate-800 mb-6">Sign in</h2>

                    {error && (
                        <div className="mb-4 px-3 py-2 bg-red-50 text-red-600 text-sm rounded-lg">
                            {error}
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div>
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
                            <label className="block text-sm font-medium text-slate-600 mb-1">Password</label>
                            <input
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                        </div>
                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full bg-blue-600 text-white py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors disabled:opacity-50"
                        >
                            {loading ? "Signing in..." : "Sign in"}
                        </button>
                    </form>
                </div>

                <p className="text-center text-sm text-slate-500 mt-6">
                    Don't have an account?{" "}
                    <Link to="/register" className="text-blue-600 font-medium hover:underline">
                        Register
                    </Link>
                </p>
            </div>
        </div>
    );
}