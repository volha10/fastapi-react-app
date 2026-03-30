import React, { createContext, useEffect, useState } from "react";

export const AuthContext = createContext();

const AuthProvider = ({ children }) => {
    console.log("AUTH PROVIDER IS RUNNING");

    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    const refresh = async () => {
        const refreshToken = localStorage.getItem("refresh_token");

        if (!refreshToken) return null;

        try {
            const response = await fetch("http://localhost:8000/api/v1/users/refresh", {
                method: "POST",
                headers: { "X-Refresh-Token": refreshToken },
            });

            const result = await response.json();

            if (response.ok) {
                // Rotation: save new both tokens
                localStorage.setItem("refresh_token", result.refresh_token);
                localStorage.setItem("access_token", result.access_token);

                return result.access_token;
            }
            else {
                console.log("Refresh failed", result);
            }
        }

        catch (error) {
            console.log("Refresh failed", error);
        }

        // If refresh fails, clear everything
        await logout();
        return null;

    }

    const fetchMe = async () => {
        // Delay of 5 seconds for testing
        await new Promise(resolve => setTimeout(resolve, 5000));

        const accessToken = localStorage.getItem("access_token");
        if (!accessToken) {
            setLoading(false);
            return;
        };

        try {
            console.log("Send request to get user data");
            let response = await fetch("http://localhost:8000/api/v1/users/me", {
                method: "GET",
                headers: { Authorization: `Bearer ${accessToken}` },
            });

            // Check if token expired
            if (response.status === 401) {
                console.log("Access token expired, attempting refresh...");
                const newAccessToken = await refresh();

                if (newAccessToken) {
                    // Retry 'me' with the new Access token
                    response = await fetch("http://localhost:8000/api/v1/users/me", {
                        method: "GET",
                        headers: { Authorization: `Bearer ${newAccessToken}` }
                    });
                }
            }

            const result = await response.json();
            if (response.ok) {
                console.log("Success fetching me: ", result);
                setUser(result);

            } else {
                console.log("Error fetching me: ", result);
                await logout(); // Session truly invalid
            }
        }
        catch (error) {
            console.log("Error fetching me: ", error);
        }
        finally {
            setLoading(false);
        }
    }

    const logout = async () => {
        const refreshToken = localStorage.getItem("refresh_token");

        if (refreshToken) {
            try {
                const response = await fetch("http://localhost:8000/api/v1/users/logout", {
                    method: "POST",
                    headers: { "X-Refresh-Token": refreshToken }
                });
                if (response.ok) {
                    console.log("Successfully logout");
                } else {
                    const result = await response.json();
                    console.log("Logout failed: ", result);
                }

            } catch (error) {
                console.log("Server logout failed: ", error);
            }
        }
        cleanLocalStorageAndUser();
    }

    const cleanLocalStorageAndUser = () => {
        localStorage.removeItem("refresh_token");
        localStorage.removeItem("access_token");

        setUser(null);
    }

    useEffect(() => {
        fetchMe();
    }, []);

    return (
        <AuthContext.Provider value={{ user, logout, loading, fetchMe }}>{children}</AuthContext.Provider>
    )
}

export default AuthProvider