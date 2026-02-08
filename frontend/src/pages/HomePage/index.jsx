import React, { useContext } from 'react'
import { AuthContext } from '../../context/AuthContext'


const HomePage = () => {

  const { user, loading } = useContext(AuthContext);
  console.log("Home page: ", user);

  if (loading) {
    return <div className='p-10'>Loading...</div>
  }

  return (
    <div className='p-10 bg-gray-900 text-white'>
      <h1 className='text-3xl font-bold mb-4'>Home Page</h1>
      {user ? (
        <div className='bg-gray-800 container'>
          <h2>Welcome back {user.name}!</h2>
        </div>
      ) : (
        <div className='bg-gray-800 rounded-lg'>
          <p className='text-white text-lg'>Please sign in to see your profile information.</p>
        </div>
      )}

    </div>
  )
}

export default HomePage
