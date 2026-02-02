import { useState } from 'react'
import { Link } from 'react-router-dom';

const SignupPage = () => {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: ""
  });

  const [error, setError] = useState("");
  const [commonError, setCommonError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setCommonError("");

    try {
      const response = await fetch("http://localhost:8000/api/v1/users/signup", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(formData),
      });

      const result = await response.json();

      if (response.ok) {
        console.log("Success: ", JSON.stringify(result));

      } else if (response.status == 409) {
        console.log("Error: ", result);
        setError(result.detail);
      }
      else {
        console.log("Error: ", result);
        setCommonError("Something went wrong. Try again later.");
      }
    }
    catch (error) {
      console.log("Error: ", error);
      setCommonError("Something went wrong. Try again later.");
    }
  }

  const handleChange = async (e) => {
    if (error) {
      setError("");
    }
    else if (commonError) {
      setCommonError("");
    }

    // Dynamically update the state based on input 'name'
    setFormData({
      ...formData, // 1. Copy all existing data (Spread Operator)
      [e.target.name]: e.target.value // 2. Update ONLY the field that changed
    });
  }

  return (
    <section className="text-gray-400 bg-gray-900 body-font">
      <div className="container px-5 py-24 mx-auto flex flex-wrap items-center justify-center">
        <form onSubmit={handleSubmit} className="lg:w-2/6 md:w-1/2 bg-gray-800 bg-opacity-50 rounded-lg p-8 flex flex-col w-full mt-10 md:mt-0">
          <h2 className="text-white text-lg font-medium title-font mb-5">Sign Up</h2>
          {/* Common Error message */}
          {commonError && (
            <div className="flex items-center gap-1 mb-3">
              <svg xmlns="http://www.w3.org" className="h-3 w-3 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              <p className="text-red-400 text-[11px] font-medium uppercase tracking-wider">
                {commonError}
              </p>
            </div>
          )}
          <div className="relative mb-4">
            <label htmlFor="name" className="leading-7 text-sm text-gray-400">
              Full Name<span>*</span>
            </label>
            <input
              autoComplete='off'
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              className="w-full bg-gray-600 bg-opacity-20 focus:bg-transparent focus:ring-2 focus:ring-yellow-900 rounded border border-gray-600 focus:border-yellow-500 text-base outline-none text-gray-100 py-1 px-3 leading-8 transition-colors duration-200 ease-in-out"
              required
            />
          </div>
          <div className="relative mb-4">
            <label htmlFor="email" className={`leading-7 text-sm text-gray-400 ${error ? "text-red-400" : "text-gray-400"}`}>
              Email<span>*</span>
            </label>
            <input
              autoComplete='off'
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className={`w-full bg-gray-600 bg-opacity-20 focus:bg-transparent focus:ring-2 focus:ring-yellow-900 rounded border border-gray-600 focus:border-yellow-500 text-base outline-none text-gray-100 py-1 px-3 leading-8 transition-colors duration-200 ease-in-out ${error ? "border-red-400 focus:ring-red-900" : "border-gray-600 focus:ring-yellow-900"
                }`}
              required
            />

            {/* Error message with icon */}
            {error && (
              <div className="flex items-center gap-1 mt-1.5">
                <svg xmlns="http://www.w3.org" className="h-3 w-3 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                <p className="text-red-400 text-[11px] font-medium uppercase tracking-wider">
                  {error}
                </p>
              </div>
            )}

          </div>
          <div className="relative mb-4">
            <label htmlFor="password" className="leading-7 text-sm text-gray-400">
              Password<span>*</span>
            </label>
            <input
              autoComplete='off'
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              className="w-full bg-gray-600 bg-opacity-20 focus:bg-transparent focus:ring-2 focus:ring-yellow-900 rounded border border-gray-600 focus:border-yellow-500 text-base outline-none text-gray-100 py-1 px-3 leading-8 transition-colors duration-200 ease-in-out"
              required
            />
          </div>
          <button type="submit" className="text-white bg-yellow-500 border-0 py-2 px-8 focus:outline-none hover:bg-yellow-600 rounded text-lg">
            Create account
          </button>
          <Link
            to="/login"
            className="text-center w-full block text-yellow-500 hover:underline text-xs mt-4"
          >
            Already have an account? Sign in instead.
          </Link>
        </form>
      </div>
    </section>
  )
}

export default SignupPage
