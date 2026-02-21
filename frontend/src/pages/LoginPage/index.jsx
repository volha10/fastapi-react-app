import { useContext, useEffect, useState } from 'react'
import { Link } from 'react-router-dom';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../../context/AuthContext';

const LoginPage = () => {
  const navigate = useNavigate();

  const { user, fetchMe, loading } = useContext(AuthContext);

  const [formData, setFormData] = useState({
    email: "",
    password: ""
  });

  const [error, setError] = useState("");

  useEffect(() => {
    if (user) {
      navigate("/");
    }
  }, [user, navigate]);

  if (loading) {
    return <div className='p-10'>Loading...</div>
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    try {
      console.log(formData);

      const params = new URLSearchParams();
      // using the 'username' field instead of 'email' for Swagger UI compatibility (Authorize button)
      params.append("username", formData.email);
      params.append("password", formData.password);

      const response = await fetch("http://localhost:8000/api/v1/users/signin", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded"
        },
        body: params.toString(),
      });

      const result = await response.json();

      if (response.ok) {
        console.log("Success: ", JSON.stringify(result));
        localStorage.setItem("access_token", result.access_token);

        await fetchMe();

        navigate("/");

      } else if (response.status == 401) {
        console.log("Error: ", result);
        setError(result.detail);
      }
      else {
        console.log("Error: ", result);
        setError("Something went wrong. Try again later.");
      }
    }
    catch (error) {
      console.log("Error: ", error);
      setError("Something went wrong. Try again later.");
    }
  }

  const handleChange = async (e) => {
    // Dynamically update the state based on input 'name'
    setFormData({
      ...formData, // 1. Copy all existing data (Spread Operator)
      [e.target.name]: e.target.value // 2. Update ONLY the field that changed
    });
  }

  return (
    <section className="text-gray-400 bg-gray-900 body-font flex-grow min-h-full">
      <div className="container px-5 py-24 mx-auto flex flex-wrap items-center justify-center">
        <form onSubmit={handleSubmit} className="lg:w-2/6 md:w-1/2 bg-gray-800 bg-opacity-50 rounded-lg p-8 flex flex-col w-full mt-10 md:mt-0">
          <h2 className="text-white text-lg font-medium title-font mb-5">Sign In</h2>
          {/* Error message with icon */}
          {error && (
            <div className="flex items-center gap-1 mb-3">
              <svg xmlns="http://www.w3.org" className="h-3 w-3 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              <p className="text-red-400 text-[11px] font-medium uppercase tracking-wider">
                {error}
              </p>
            </div>
          )}
          <div className="relative mb-4">
            <label htmlFor="email" className="leading-7 text-sm text-gray-400">
              Email
            </label>
            <input
              autoComplete='off'
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className="w-full bg-gray-600 bg-opacity-20 focus:bg-transparent focus:ring-2 focus:ring-yellow-900 rounded border border-gray-600 focus:border-yellow-500 text-base outline-none text-gray-100 py-1 px-3 leading-8 transition-colors duration-200 ease-in-out"
              required
            />
          </div>
          <div className="relative mb-4">
            <div className='flex justify-between items-center'>
              <label htmlFor="password" className="leading-7 text-sm text-gray-400">
                Password
              </label>
              <Link
                to="/forgot-password"
                className="text-xs text-gray-400 hover:underline text-sm"
              >
                Forgot Password?
              </Link>
            </div>
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
            Sign In
          </button>
          <Link
            to="/signup"
            className="text-center w-full block text-yellow-500 hover:underline text-xs mt-4"
          >
            Do not have an account? Create a new account.
          </Link>
        </form>
      </div>
    </section>
  )
}

export default LoginPage
