import axios from "axios";

const API_BASE_URL = "http://127.0.0.1:8000/api/v1";

const client = axios.create({
    baseURL: API_BASE_URL,
});

// Attach the JWT to every request automatically
client.interceptors.request.use((config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// If any request comes back 401, the token is invalid/expired — log out
client.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            localStorage.removeItem("access_token");
            window.location.href = "/login";
        }
        return Promise.reject(error);
    }
);

export default client;