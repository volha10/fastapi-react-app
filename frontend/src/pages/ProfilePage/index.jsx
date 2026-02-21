import { useContext } from "react";
import { AuthContext } from "../../context/AuthContext";

const ProfilePage = () => {

    const { user, loading } = useContext(AuthContext);
    console.log("Profile page: ", user);

    if (loading) {
            return <div className='p-10'>Loading...</div>

    }

    return (
        <div className='p-10 bg-gray-900 text-white flex-grow min-h-full'>
            <h1 className='text-3xl font-bold mb-4'>Profile Page</h1>
            {user ? (
                <div className='bg-gray-800 container'>
                    <p>Email: {user.email}</p>
                    <p>Username: {user.name}</p>
                </div>
            ) : (
                <div className='bg-gray-800 rounded-lg'>
                    <p className='text-white text-lg'>Please sign in to see your profile information.</p>
                </div>
            )}

        </div>
    )
};

export default ProfilePage