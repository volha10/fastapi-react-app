import { Routes, Route } from 'react-router-dom'
import HomePage from './pages/HomePage'
import LoginPage from './pages/LoginPage'
import SignupPage from './pages/SignupPage'
import Navbar from './components/Navbar'
import Footer from './components/Footer'
import ProtectedRoute from './routes/ProtectedRoute'
import ProfilePage from './pages/ProfilePage'


function App() {

  return (
    <>
      <Navbar />
      <div>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/profile" element={
            <ProtectedRoute>
              <ProfilePage />
            </ProtectedRoute>
          } />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />
        </Routes>
      </div>
      <Footer />
    </>
  )
}

export default App
