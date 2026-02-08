import React, { useContext } from 'react'
import { Link } from 'react-router-dom';

import { AuthContext } from '../context/AuthContext';


const Navbar = () => {

  const { user, logout, loading } = useContext(AuthContext);

  console.log(user);
  console.log(loading);

  if (loading) {
    return (
      <header className="text-gray-600 body-font">
        <div className="container mx-auto flex p-5 items-center justify-between">
          <div className="h-6 w-32 bg-gray-200 animate-pulse rounded"></div>
        </div>
      </header>
    );
  }

  return (
    <header className="text-gray-600 body-font">
      <div className="container mx-auto flex flex-wrap p-5 flex-col md:flex-row items-center">
        <a className="flex title-font font-medium items-center text-gray-900 mb-4 md:mb-0">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            stroke="currentColor"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            className="w-10 h-10 text-white p-2 bg-yellow-500 rounded-full"
            viewBox="0 0 24 24"
          >
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
          </svg>
          <span className="ml-3 text-xl">Authentication</span>
        </a>
        <nav className="md:ml-auto flex flex-wrap items-center text-base justify-center">
          <Link to={'/'} className="mr-5 hover:text-gray-900">Home</Link>
          {!user ? (
            <>
              <Link to={'/login'} className="mr-5 hover:text-gray-900">Sign in</Link>
              <Link to={'/signup'} className="mr-5 hover:text-gray-900">Sign up</Link>
            </>

          ) : (
            <>
              <span className="mr-5 text-gray-900 font-medium">Hi, {user.name}</span>
              <Link to={'/profile'} className="mr-5 hover:text-gray-900">Profile</Link>
            </>
          )}

        </nav>

        {user && (
          <button onClick={logout}
            className="inline-flex items-center bg-gray-100 border-0 py-1 px-3 focus:outline-none hover:bg-gray-200 rounded text-base mt-4 md:mt-0">
            Sign out
            <svg
              fill="none"
              stroke="currentColor"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              className="w-4 h-4 ml-1"
              viewBox="0 0 24 24"
            >
              <path d="M5 12h14M12 5l7 7-7 7" />
            </svg>
          </button>
        )}
      </div>
    </header>
  );
};

export default Navbar
