import { useState } from "react";
import { useSearchParams, useNavigate, Link } from "react-router-dom";
import client from "../api/client";
import Card from "../components/Card";
import Button from "../components/Button";

export default function AcceptInvite() {
    const [searchParams] = useSearchParams();
    const token = searchParams.get("token");
    const navigate = useNavigate();

    const [fullName, setFullName] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    if (!token) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-slate-50 px-4">
                <Card className="max-w-md w-full text-center py-8">
                    <h2 className="text-xl font-bold text-red-600 mb-2">Invalid Invitation Link</h2>
                    <p className="text-slate-600 text-sm mb-4">No invitation token was found in the link.</p>
                    <Link to="/login" className="text-blue-600 hover:underline text-sm font-medium">Go to Login</Link>
                </Card>
            </div>
        );
    }

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError("");
        setLoading(true);

        try {
            await client.post("/auth/accept-invite", {
                token: token,
                full_name: fullName,
                password: password,
            });

            // Accept hone ke baad login page par redirect kar dein
            alert("Account created and added to the organization! Please login now.");
            navigate("/login");
        } catch (err) {
            setError(err.response?.data?.detail || "Failed to accept invitation or token expired.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-slate-50 px-4">
            <Card className="max-w-md w-full p-6">
                <div className="mb-6 text-center">
                    <h1 className="text-2xl font-bold text-slate-800">Join Your Team</h1>
                    <p className="text-slate-500 text-sm mt-1">Complete your profile to accept the invitation</p>
                </div>

                {error && <div className="mb-4 px-3 py-2 bg-red-50 text-red-600 text-sm rounded-lg">{error}</div>}

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-slate-600 mb-1">Full Name</label>
                        <input
                            type="text"
                            required
                            value={fullName}
                            onChange={(e) => setFullName(e.target.value)}
                            placeholder="John Doe"
                            className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-slate-600 mb-1">Password</label>
                        <input
                            type="password"
                            required
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="••••••••"
                            className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                    </div>

                    <Button type="submit" disabled={loading} className="w-full py-2.5">
                        {loading ? "Joining..." : "Accept Invitation & Create Account"}
                    </Button>
                </form>
            </Card>
        </div>
    );
}