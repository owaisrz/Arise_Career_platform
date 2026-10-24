import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { Layout } from './components/Layout';
import { Dashboard } from './pages/Dashboard';
import { Profile } from './pages/Profile';
import { Scanner } from './pages/Scanner';
import { Jobs } from './pages/Jobs';
import { Checker } from './pages/Checker';
import { CareerPlan } from './pages/CareerPlan';
import { Applications } from './pages/Applications';
import { InterviewStudio } from './pages/InterviewStudio';
import { ResumeStudio } from './pages/ResumeStudio';
import { Fairness } from './pages/Fairness';
import { Audit } from './pages/Audit';
import { Login } from './pages/Login';

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Dashboard />} />
            <Route path="profile" element={<Profile />} />
            <Route path="scanner" element={<Scanner />} />
            <Route path="jobs" element={<Jobs />} />
            <Route path="checker" element={<Checker />} />
            <Route path="career-plan" element={<CareerPlan />} />
            <Route path="applications" element={<Applications />} />
            <Route path="interviews" element={<InterviewStudio />} />
            <Route path="resumes" element={<ResumeStudio />} />
            <Route path="fairness" element={<Fairness />} />
            <Route path="audit" element={<Audit />} />
            <Route path="login" element={<Login />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
};

export default App;
