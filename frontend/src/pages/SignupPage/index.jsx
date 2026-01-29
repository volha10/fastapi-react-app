import React, { useEffect } from 'react'


const SignupPage = () => {

  useEffect(() => {
    const handleSignup = async () => {
      const mockUser = {
        name: "User 1",
        email: "user1@gmail.com",
        password: "user1password"  
      };

      try {
        const response = await fetch("http://localhost:8000/signup", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify(mockUser),
        }

        );

        const result = await response.json()
        console.log("Response: ", result)
      }

      catch(error) { 
        console.error("Error: ", error)

      }
    }

    handleSignup();
  }, []) // [] ensures this only runs once when the component mounts

  return (
    <div>
        Signup Page
    </div>
  )
}

export default SignupPage
