import { useContext } from "react";
import { AuthContext } from "../context/AuthContext";
import { Navigate } from "react-router-dom";

const ProtectedRoute = ({ children }) => {

    const { user, loading } = useContext(AuthContext);

    if (loading) {
        return <div className="p-10">
            <p>Verifying Session...</p>
        </div>
    }

    if (!user) {
        return <Navigate to={"/login"}></Navigate>
    }

    return children
}

export default ProtectedRoute;