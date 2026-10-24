import React, { useState } from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { 
  LayoutDashboard, 
  User as UserIcon, 
  FileSearch, 
  Compass, 
  ShieldCheck, 
  CalendarRange, 
  KanbanSquare, 
  MessagesSquare, 
  FileText, 
  Scale, 
  History, 
  LogOut, 
  LogIn, 
  Menu, 
  X, 
  Sparkles,
  ExternalLink,
  ChevronRight
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const Layout: React.FC = () => {
  const { user, logout, login } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const navigate = useNavigate();

  const navItems = [
    { to: '/', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/profile', label: 'My Profile', icon: UserIcon },
    { to: '/scanner', label: 'Document Scanner', icon: FileSearch, badge: 'Evidence' },
    { to: '/jobs', label: 'Discover Jobs', icon: Compass },
    { to: '/checker', label: 'Job Trust Checker', icon: ShieldCheck, badge: 'Risk Triage' },
    { to: '/career-plan', label: '30-Day Career Plan', icon: CalendarRange },
    { to: '/applications', label: 'Applications', icon: KanbanSquare },
    { to: '/interviews', label: 'Interview Studio', icon: MessagesSquare },
    { to: '/resumes', label: 'Resume Studio', icon: FileText, badge: 'Privacy' },
    { to: '/fairness', label: 'Fairness & Audit', icon: Scale },
    { to: '/audit', label: 'Activity History', icon: History },
  ];

  const handleDemoLogin = async () => {
    try {
      await login('alex.morgan@careerloom.dev', 'password123');
    } catch (err: any) {
      alert(err.message || 'Demo login failed');
    }
  };

  return (
    <div className="min-h-screen bg-[#F6F3EC] relative flex flex-col md:flex-row overflow-x-hidden">
      {/* Organic atmospheric background shapes */}
      <div className="fixed top-[-100px] left-[-100px] w-[500px] h-[500px] rounded-full ambient-glow-forest pointer-events-none z-0" />
      <div className="fixed bottom-[-150px] right-[-100px] w-[600px] h-[600px] rounded-full ambient-glow-copper pointer-events-none z-0" />

      {/* Desktop Glass Sidebar */}
      <aside className="hidden md:flex flex-col w-72 glass-sidebar z-20 sticky top-0 h-screen p-5 text-white">
        {/* Brand Header */}
        <div className="flex items-center gap-3.5 px-2 py-3 border-b border-white/10 mb-5">
          <img src="/logo.svg" alt="Careerloom Logo" className="w-10 h-10 drop-shadow-md" />
          <div>
            <div className="flex items-center gap-1.5">
              <span className="font-bold text-xl tracking-tight text-white">Careerloom</span>
              <span className="text-[10px] font-semibold bg-[#79B9AC]/20 text-[#79B9AC] px-1.5 py-0.5 rounded border border-[#79B9AC]/30">NCSP</span>
            </div>
            <p className="text-[11px] text-[#DCE9E0]/70 font-medium">Every skill has a story.</p>
          </div>
        </div>

        {/* Navigation links */}
        <nav className="flex-1 space-y-1 overflow-y-auto pr-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `flex items-center justify-between px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-white/15 text-white shadow-sm border border-white/20'
                      : 'text-[#DCE9E0]/80 hover:bg-white/10 hover:text-white'
                  }`
                }
              >
                <div className="flex items-center gap-3">
                  <Icon className="w-4 h-4 text-[#79B9AC]" />
                  <span>{item.label}</span>
                </div>
                {item.badge && (
                  <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-[#79B9AC]/20 text-[#79B9AC] border border-[#79B9AC]/30">
                    {item.badge}
                  </span>
                )}
              </NavLink>
            );
          })}
        </nav>

        {/* Bottom User Controls */}
        <div className="pt-4 border-t border-white/10">
          {user ? (
            <div className="p-3 rounded-xl bg-white/10 border border-white/15 flex items-center justify-between">
              <div className="truncate pr-2">
                <p className="text-xs font-semibold text-white truncate">{user.full_name}</p>
                <p className="text-[11px] text-[#DCE9E0]/70 truncate">{user.email}</p>
              </div>
              <button
                onClick={logout}
                title="Log out"
                className="p-1.5 rounded-lg hover:bg-white/15 text-[#DCE9E0] hover:text-white transition"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <div className="space-y-2">
              <button
                onClick={handleDemoLogin}
                className="w-full flex items-center justify-center gap-2 py-2 px-3 rounded-xl bg-[#79B9AC] text-[#102C26] font-semibold text-xs hover:bg-[#68a89b] transition shadow-sm"
              >
                <Sparkles className="w-3.5 h-3.5" />
                <span>Demo Sign-In (Alex)</span>
              </button>
              <button
                onClick={() => navigate('/login')}
                className="w-full flex items-center justify-center gap-2 py-2 px-3 rounded-xl bg-white/10 hover:bg-white/15 text-white font-medium text-xs transition border border-white/15"
              >
                <LogIn className="w-3.5 h-3.5" />
                <span>Candidate Login</span>
              </button>
            </div>
          )}
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 z-10">
        {/* Top bar */}
        <header className="sticky top-0 z-20 px-4 md:px-8 py-3.5 glass-panel-strong border-b border-[#E4E4DA] flex items-center justify-between backdrop-blur-md">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 rounded-lg bg-black/5 hover:bg-black/10 text-[#202823]"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
            <div className="flex items-center gap-2 text-xs font-medium text-[#69756E]">
              <span className="hidden sm:inline">IMPACTX 2026</span>
              <ChevronRight className="w-3.5 h-3.5 hidden sm:inline text-[#79B9AC]" />
              <span className="text-[#163B32] font-semibold">National Career Intelligence</span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <NavLink
              to="/scanner"
              className="hidden sm:flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-semibold bg-[#163B32] text-white hover:bg-[#102C26] transition shadow-sm"
            >
              <FileSearch className="w-3.5 h-3.5 text-[#79B9AC]" />
              <span>Scan Document</span>
            </NavLink>
            <NavLink
              to="/checker"
              className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-xs font-semibold bg-[#DCE9E0] text-[#163B32] hover:bg-[#c9ddce] transition border border-[#79B9AC]/40"
            >
              <ShieldCheck className="w-3.5 h-3.5 text-[#163B32]" />
              <span>Job Trust Checker</span>
            </NavLink>
          </div>
        </header>

        {/* Mobile Navigation Drawer */}
        {mobileMenuOpen && (
          <div className="md:hidden glass-modal m-3 p-4 fixed inset-x-0 top-16 z-30 shadow-2xl border border-white/60">
            <nav className="space-y-1 mb-4">
              {navItems.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  onClick={() => setMobileMenuOpen(false)}
                  className={({ isActive }) =>
                    `flex items-center justify-between px-3.5 py-2.5 rounded-xl text-sm font-medium ${
                      isActive ? 'bg-[#163B32] text-white' : 'text-[#202823] hover:bg-black/5'
                    }`
                  }
                >
                  <div className="flex items-center gap-3">
                    <item.icon className="w-4 h-4 text-[#79B9AC]" />
                    <span>{item.label}</span>
                  </div>
                  {item.badge && (
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-[#79B9AC]/20 text-[#163B32]">
                      {item.badge}
                    </span>
                  )}
                </NavLink>
              ))}
            </nav>
            {user ? (
              <button
                onClick={() => {
                  logout();
                  setMobileMenuOpen(false);
                }}
                className="w-full flex items-center justify-center gap-2 py-2 px-3 rounded-xl bg-red-100 text-red-800 text-xs font-medium"
              >
                <LogOut className="w-4 h-4" />
                <span>Log out ({user.full_name})</span>
              </button>
            ) : (
              <button
                onClick={() => {
                  handleDemoLogin();
                  setMobileMenuOpen(false);
                }}
                className="w-full py-2 px-3 rounded-xl bg-[#163B32] text-white text-xs font-semibold"
              >
                Sign In as Demo Candidate
              </button>
            )}
          </div>
        )}

        {/* Dynamic Page Outlet */}
        <main className="flex-1 p-4 md:p-8 max-w-7xl mx-auto w-full">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
