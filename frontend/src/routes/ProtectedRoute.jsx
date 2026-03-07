import { useContext } from "react";
import { AuthContext } from "../context/AuthContext";
import { Navigate, useLocation } from "react-router-dom";

const ProtectedRoute = ({ children }) => {

    const { user, loading } = useContext(AuthContext);
    const location = useLocation();

    if (loading) {
        return <div className="p-10">
            <p>Verifying Session...</p>
        </div>
    }

    if (!user) {
        return <Navigate to={"/login"} state={{ from: location }} replace></Navigate>
    }

    return children
}

export default ProtectedRoute;