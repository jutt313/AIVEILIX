import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import { ThemeProvider } from './context/ThemeContext'
import ProtectedRoute from './components/ProtectedRoute'
import Landing from './pages/Landing'
import Login from './pages/Login'
import Signup from './pages/Signup'
import ForgotPassword from './pages/ForgotPassword'
import Dashboard from './pages/Dashboard'
import Bucket from './pages/Bucket'
import Pricing from './pages/Pricing'
import TermsAndConditions from './pages/TermsAndConditions'
import PrivacyPolicy from './pages/PrivacyPolicy'
import Tokusho from './pages/Tokusho'
import Doc from './pages/Doc'
import LoginPageGif from './pages/LoginPageGif'
import BucketFullWorkflowGif from './pages/BucketFullWorkflowGif'
import OAuthAuthorize from './pages/OAuthAuthorize'

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            {/* Public routes */}
            <Route path="/" element={<Landing />} />
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />
            <Route path="/terms" element={<TermsAndConditions />} />
            <Route path="/terms-of-service" element={<TermsAndConditions />} />
            <Route path="/privacy" element={<PrivacyPolicy />} />
            <Route path="/tokusho" element={<Tokusho />} />
            <Route path="/specified-commercial-transactions" element={<Tokusho />} />
            <Route path="/pricing" element={<Pricing />} />
            <Route path="/doc" element={<Doc />} />
            <Route path="/login-page-gif" element={<LoginPageGif />} />
            <Route path="/bucket-workflow-gif" element={<BucketFullWorkflowGif />} />
            <Route path="/oauth/authorize" element={<OAuthAuthorize />} />

            {/* Protected routes */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/buckets/:id"
              element={
                <ProtectedRoute>
                  <Bucket />
                </ProtectedRoute>
              }
            />

            {/* 404 - redirect to home */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  )
}

export default App
