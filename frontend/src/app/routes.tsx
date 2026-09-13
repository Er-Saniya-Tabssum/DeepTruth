import React from 'react'
import LandingPage from '../pages/LandingPage'
import LoginPage from '../pages/LoginPage'
import RegisterPage from '../pages/RegisterPage'
import DashboardPage from '../pages/DashboardPage'
import AnalyzePage from '../pages/AnalyzePage'
import HistoryPage from '../pages/HistoryPage'
import ResultPage from '../pages/ResultPage'
import NotFoundPage from '../pages/NotFoundPage'
import ProtectedRoute from '../components/layout/ProtectedRoute'

const routes = [
  { path: '/', element: <LandingPage /> },
  { path: '/login', element: <LoginPage /> },
  { path: '/register', element: <RegisterPage /> },
  { path: '/dashboard', element: <ProtectedRoute><DashboardPage/></ProtectedRoute> },
  { path: '/analyze', element: <ProtectedRoute><AnalyzePage/></ProtectedRoute> },
  { path: '/history', element: <ProtectedRoute><HistoryPage/></ProtectedRoute> },
  { path: '/results/:analysisId', element: <ProtectedRoute><ResultPage/></ProtectedRoute> },
  { path: '*', element: <NotFoundPage/> }
]

export default routes
