import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { LogIn, Sparkles, AlertCircle, ArrowRight } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const Login: React.FC = () => {
  const { login, register } = useAuth();
  const navigate = useNavigate();
  const [isRegistering, setIsRegistering] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [preferredRole, setPreferredRole] = useState('Full Stack Software Engineer');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setLoading(true);
      setError(null);
      if (isRegistering) {
        await register({ email, password, full_name: fullName, preferred_role: preferredRole });
      } else {
        await login(email, password);
      }
      navigate('/');
    } catch (err: any) {
      setError(err.message || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  const handleDemoSignIn = async () => {
    try {
      setLoading(true);
      setError(null);
      await login('alex.morgan@careerloom.dev', 'password123');
      navigate('/');
    } catch (err: any) {
      setError(err.message || 'Demo sign in failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto my-12">
      <div className="glass-panel p-8 space-y-6">
        <div className="text-center space-y-2">
          <img src="/logo.svg" alt="Careerloom" className="w-12 h-12 mx-auto drop-shadow-md" />
          <h1 className="text-2xl font-bold text-[#163B32] tracking-tight">
            {isRegistering ? 'Create Candidate Account' : 'Welcome to Careerloom'}
          </h1>
          <p className="text-xs text-[#69756E]">
            Every skill has a story. Every step builds a career.
          </p>
        </div>

        {error && (
          <div className="p-3.5 rounded-xl bg-red-50 border border-red-200 text-xs text-red-800 flex items-center gap-2">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Demo Fast Login */}
        <button
          type="button"
          onClick={handleDemoSignIn}
          disabled={loading}
          className="w-full py-2.5 px-4 rounded-xl bg-[#79B9AC] text-[#102C26] font-bold text-xs hover:bg-[#68a89b] transition flex items-center justify-center gap-2 shadow-sm"
        >
          <Sparkles className="w-4 h-4" />
          <span>One-Click Sign In as Alex Morgan (Demo)</span>
        </button>

        <div className="flex items-center gap-3 my-2 text-xs text-[#69756E]">
          <div className="h-[1px] bg-[#E4E4DA] flex-1" />
          <span>or continue with credentials</span>
          <div className="h-[1px] bg-[#E4E4DA] flex-1" />
        </div>

        <form onSubmit={handleSubmit} className="space-y-3.5">
          {isRegistering && (
            <>
              <div>
                <label className="text-xs font-bold text-[#163B32] block mb-1">Full Name</label>
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="e.g. Alex Morgan"
                  className="w-full px-3 py-2 text-xs rounded-xl bg-white border border-[#E4E4DA]"
                  required
                />
              </div>
              <div>
                <label className="text-xs font-bold text-[#163B32] block mb-1">Target Career Role</label>
                <input
                  type="text"
                  value={preferredRole}
                  onChange={(e) => setPreferredRole(e.target.value)}
                  placeholder="e.g. Full Stack Engineer, Data Analyst"
                  className="w-full px-3 py-2 text-xs rounded-xl bg-white border border-[#E4E4DA]"
                />
              </div>
            </>
          )}

          <div>
            <label className="text-xs font-bold text-[#163B32] block mb-1">Email Address</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="alex@careerloom.dev"
              className="w-full px-3 py-2 text-xs rounded-xl bg-white border border-[#E4E4DA]"
              required
            />
          </div>

          <div>
            <label className="text-xs font-bold text-[#163B32] block mb-1">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full px-3 py-2 text-xs rounded-xl bg-white border border-[#E4E4DA]"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 px-4 rounded-xl bg-[#163B32] text-white text-xs font-semibold hover:bg-[#102C26] transition flex items-center justify-center gap-2 shadow-sm"
          >
            <LogIn className="w-4 h-4 text-[#79B9AC]" />
            <span>{isRegistering ? 'Create Account' : 'Sign In'}</span>
          </button>
        </form>

        <div className="text-center pt-2 border-t border-[#E4E4DA]">
          <button
            type="button"
            onClick={() => { setIsRegistering(!isRegistering); setError(null); }}
            className="text-xs font-medium text-[#163B32] hover:underline"
          >
            {isRegistering ? 'Already have an account? Sign in' : "Don't have an account? Create one"}
          </button>
        </div>
      </div>
    </div>
  );
};
