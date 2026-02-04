import React, { createContext, useEffect, useState } from "react";

export const AuthContext = createContext();

const AuthProvider = ({ children }) => {
    console.log("AUTH PROVIDER IS RUNNING");

    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    const fetchMe = async () => {
        // Delay of 5 seconds for testing
        await new Promise(resolve => setTimeout(resolve, 5000));

        const access_token = localStorage.getItem("access_token");
        if (!access_token) {
            setLoading(false);
            return;

        };

        try {
            console.log("Send request to get user data");
            const response = await fetch("http://localhost:8000/api/v1/users/me", {
                method: "GET",
                headers: { Authorization: `Bearer ${access_token}` },

            });

            const result = await response.json();
            if (response.ok) {
                console.log("Success: ", result);
                setUser(result);

            } else {
                console.log("Error: ", result);
            }
        }
        catch (error) {
            console.log("Error: ", error);
        }
        finally {
            setLoading(false);
        }
    }

    const logout = () => {
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