import React, { useContext } from 'react'
import { AuthContext } from '../../context/AuthContext'


const HomePage = () => {

  const { user, loading } = useContext(AuthContext);
  console.log("Home page: ", user);

  if (loading) {
    return <div className='p-10'>Loading...</div>
  }

  return (
    <div className='p-10 bg-gray-900 text-white flex-grow min-h-screen'>
      <h1 className='text-3xl font-bold mb-4'>Home Page</h1>
      
      {user ? (
        <h2 className='text-xl'>Welcome back, {user.name}!</h2>
      ) : (
        <p className='text-lg opacity-80'>Please sign in.</p>
      )}
    </div>
  );
}

export default HomePage
