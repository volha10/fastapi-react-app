import { useState } from 'react'
import { Routes, Route } from 'react-router-dom'
import HomePage from './pages/HomePage'
import LoginPage from './pages/LoginPage'
import SignupPage from './pages/SignupPage'
import Navbar from './components/Navbar'
import Footer from './components/Footer'


function App() {

  return (
    <>
      <Navbar />
      <div>
          <Routes>
            <Route path="/" Component={HomePage} />
            <Route path="/login" Component={LoginPage} />
            <Route path="/signup" Component={SignupPage} />
        </Routes>
      </div>
      <Footer />
    </>
  )
}

export default App
