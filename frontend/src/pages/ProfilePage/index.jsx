import { useContext, useEffect, useState } from "react";
import { AuthContext } from "../../context/AuthContext";

const ProfilePage = () => {

    const { user, loading, updateProfile } = useContext(AuthContext);

    const [isEditing, setIsEditing] = useState(false);
    const [newName, setNewName] = useState("");

    console.log("Profile page: ", user);

    if (loading) {
        return <div className='p-10'>Loading...</div>
    }

    const handleSave = async () => {
        const result = await updateProfile(newName);

        if (result.success) {
            setIsEditing(false);
        } else {
            console.error(result.error)
        }
    };

    useEffect(() => {
        if (user && !isEditing) setNewName(user.name);
    }, [isEditing]);


    return (
        <section className="text-gray-400 bg-gray-900 body-font flex-grow min-h-full">
            <div className="container px-5 py-24 mx-auto flex flex-wrap items-center justify-center">
                <div className="lg:w-2/6 md:w-1/2 bg-gray-800 bg-opacity-50 rounded-lg p-8 flex flex-col w-full mt-10 md:mt-0 border border-gray-700">
                    <h2 className="text-white text-lg font-medium title-font mb-5">Profile Settings</h2>

                    {user ? (
                        <div className="flex flex-col w-full">
                            {/* Email Field (Read Only) */}
                            <div className="relative mb-4">
                                <label className="leading-7 text-sm text-gray-400">Email</label>
                                <div className="w-full bg-gray-600 bg-opacity-10 rounded border border-gray-600 text-base py-1 px-3 leading-8 text-gray-500 italic">
                                    {user.email}
                                </div>
                            </div>

                            {/* Full Name Field */}
                            <div className="relative mb-4">
                                <label className="leading-7 text-sm text-gray-400">Full Name</label>
                                {isEditing ? (
                                    <div className="flex flex-col gap-3">
                                        <input
                                            value={newName}
                                            onChange={(e) => setNewName(e.target.value)}
                                            autoFocus
                                            className="w-full bg-gray-600 bg-opacity-20 focus:bg-transparent focus:ring-2 focus:ring-yellow-900 rounded border border-gray-600 focus:border-yellow-500 text-base outline-none text-gray-100 py-1 px-3 leading-8 transition-colors duration-200 ease-in-out"
                                        />
                                        <div className="flex gap-2">
                                            <button
                                                onClick={handleSave}
                                                className="flex-1 text-white bg-yellow-500 border-0 py-1 px-4 focus:outline-none hover:bg-yellow-600 rounded text-md transition-colors"
                                            >
                                                Save
                                            </button>
                                            <button
                                                onClick={() => setIsEditing(false)}
                                                className="flex-1 text-gray-400 bg-gray-700 border-0 py-1 px-4 focus:outline-none hover:bg-gray-600 rounded text-md transition-colors"
                                            >
                                                Cancel
                                            </button>
                                        </div>
                                    </div>
                                ) : (
                                    <div className="flex justify-between items-center bg-gray-600 bg-opacity-20 rounded border border-gray-600 py-1 px-3 leading-8">
                                        <span className="text-gray-100">{user.name}</span>
                                        <button
                                            onClick={() => setIsEditing(true)}
                                            className="text-yellow-500 hover:text-yellow-400 text-sm font-medium transition-colors"
                                        >
                                            Edit
                                        </button>
                                    </div>
                                )}
                            </div>
                        </div>
                    ) : (
                        <p className="text-center text-sm">Please sign in to view your profile.</p>
                    )}
                </div>
            </div>
        </section>
    );
};

export default ProfilePage
