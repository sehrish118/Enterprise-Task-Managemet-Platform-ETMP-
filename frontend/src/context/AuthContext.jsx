import { createContext, useContext, useState, useEffect } from "react";
import client from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const token = localStorage.getItem("access_token");
        if (!token) {
            setLoading(false);
            return;
        }
        client
            .get("/auth/me")
            .then((res) => setUser(res.data))
            .catch(() => localStorage.removeItem("access_token"))
            .finally(() => setLoading(false));
    }, []);

    // const login = async (email, password) => {
    //     const res = await client.post("/auth/login", { email, password });
    //     localStorage.setItem("access_token", res.data.access_token);
    //     const me = await client.get("/auth/me");
    //     setUser(me.data);
    // };

    

    const login = async (email, password) => {
        const res = await client.post("/auth/login", { email, password });
        localStorage.setItem("access_token", res.data.access_token);
        const me = await client.get("/auth/me");
        setUser(me.data);
        return me.data; 
    
    };
    

    const logout = () => {
        localStorage.removeItem("access_token");
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, loading, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
}

export const useAuth = () => useContext(AuthContext);