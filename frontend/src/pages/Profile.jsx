import { useState } from "react";
import client from "../api/client";
import Card from "../components/Card";
import Button from "../components/Button";
import { useAuth } from "../context/AuthContext";

export default function Profile() {
    const { user } = useAuth();
    const [fullName, setFullName] = useState(user?.full_name || "");
    const [currentPassword, setCurrentPassword] = useState("");
    const [newPassword, setNewPassword] = useState("");
    const [nameSuccess, setNameSuccess] = useState("");
    const [nameError, setNameError] = useState("");
    const [pwSuccess, setPwSuccess] = useState("");
    const [pwError, setPwError] = useState("");

    const handleUpdateName = async (e) => {
        e.preventDefault();
        setNameError("");
        setNameSuccess("");
        try {
            await client.patch("/users/me", { full_name: fullName });
            setNameSuccess("Profile updated");
        } catch (err) {
            setNameError(err.response?.data?.detail || "Failed to update profile");
        }
    };

    const handleChangePassword = async (e) => {
        e.preventDefault();
        setPwError("");
        setPwSuccess("");
        try {
            await client.post("/users/me/change-password", {
                current_password: currentPassword,
                new_password: newPassword,
            });
            setCurrentPassword("");
            setNewPassword("");
            setPwSuccess("Password changed successfully");
        } catch (err) {
            setPwError(err.response?.data?.detail || "Failed to change password");
        }
    };

    return (
        <div>
            <h1 className="text-2xl font-bold text-slate-800">My Profile</h1>

            <h2 className="text-lg font-semibold text-slate-800 mt-6 mb-2">Update Name</h2>
            <Card>
                {nameError && <div className="mb-3 px-3 py-2 bg-red-50 text-red-600 text-sm rounded-lg">{nameError}</div>}
                {nameSuccess && <div className="mb-3 px-3 py-2 bg-green-50 text-green-600 text-sm rounded-lg">{nameSuccess}</div>}
                <form onSubmit={handleUpdateName} className="flex gap-3 items-end">
                    <div className="flex-1">
                        <label className="block text-sm font-medium text-slate-600 mb-1">Full Name</label>
                        <input
                            value={fullName}
                            onChange={(e) => setFullName(e.target.value)}
                            required
                            className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                    </div>
                    <Button type="submit">Update</Button>
                </form>
            </Card>

            <h2 className="text-lg font-semibold text-slate-800 mt-6 mb-2">Change Password</h2>
            <Card>
                {pwError && <div className="mb-3 px-3 py-2 bg-red-50 text-red-600 text-sm rounded-lg">{pwError}</div>}
                {pwSuccess && <div className="mb-3 px-3 py-2 bg-green-50 text-green-600 text-sm rounded-lg">{pwSuccess}</div>}
                <form onSubmit={handleChangePassword} className="space-y-3 max-w-sm">
                    <div>
                        <label className="block text-sm font-medium text-slate-600 mb-1">Current Password</label>
                        <input
                            type="password"
                            value={currentPassword}
                            onChange={(e) => setCurrentPassword(e.target.value)}
                            required
                            className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-slate-600 mb-1">New Password</label>
                        <input
                            type="password"
                            value={newPassword}
                            onChange={(e) => setNewPassword(e.target.value)}
                            required
                            minLength={8}
                            className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                    </div>
                    <Button type="submit">Change Password</Button>
                </form>
            </Card>
        </div>
    );
}