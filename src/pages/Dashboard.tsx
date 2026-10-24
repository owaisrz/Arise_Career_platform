import React, { useState, useEffect } from 'react';
import { NavLink } from 'react-router-dom';
import { 
  Sparkles, 
  ArrowRight, 
  CheckCircle2, 
  Clock, 
  ShieldCheck, 
  FileSearch, 
  Briefcase, 
  Award, 
  Flame, 
  Calendar,
  AlertCircle
} from 'lucide-react';
import { api } from '../api/client';
import { useAuth } from '../context/AuthContext';

export const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboard = async () => {
    try {
      setLoading(true);
      setError(null);
      const summary = await api.dashboard.summary();
      setData(summary);
    } catch (err: any) {
      setError(err.message || 'Unable to load candidate dashboard.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, [user]);

  if (loading) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="h-44 glass-panel rounded-2xl" />
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-28 glass-panel rounded-xl" />
          ))}
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="glass-panel p-8 text-center max-w-lg mx-auto my-12">
        <AlertCircle className="w-12 h-12 text-[#C47B54] mx-auto mb-3" />
        <h2 className="text-xl font-bold text-[#163B32]">Welcome to Careerloom</h2>
        <p className="text-sm text-[#69756E] mt-2 mb-6">
          Sign in or use the demo account to unlock evidence-based matching, document extraction, and your 30-day plan.
        </p>
        <NavLink
          to="/login"
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-[#163B32] text-white font-medium text-sm hover:bg-[#102C26] transition shadow-md"
        >
          <span>Sign In to Continue</span>
          <ArrowRight className="w-4 h-4" />
        </NavLink>
      </div>
    );
  }

  const { candidate, stats, next_suggested_action, career_plan, next_task, recommended_opportunities, recent_activity } = data;

  return (
    <div className="space-y-8">
      {/* Editorial Welcome Header */}
      <section className="glass-panel p-6 md:p-8 relative overflow-hidden">
        <div className="max-w-2xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#DCE9E0] text-[#163B32] text-xs font-semibold mb-3 border border-[#79B9AC]/40">
            <Sparkles className="w-3.5 h-3.5 text-[#163B32]" />
            <span>National Career Service Journey</span>
          </div>
          <h1 className="text-2xl md:text-3xl font-bold text-[#163B32] tracking-tight">
            Welcome back, {candidate?.full_name || 'Candidate'}
          </h1>
          <p className="text-sm text-[#69756E] mt-1.5 leading-relaxed">
            Targeting: <strong className="text-[#102C26]">{candidate?.preferred_role || 'Full Stack Engineer'}</strong>. Every skill claim in your profile is anchored to verifiable projects and document references.
          </p>

          {/* Next Action Pill */}
          <div className="mt-5 p-3.5 rounded-xl bg-white/70 border border-[#E4E4DA] flex items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-[#79B9AC]/20 flex items-center justify-center text-[#163B32] flex-shrink-0">
                <Flame className="w-4 h-4 text-[#C47B54]" />
              </div>
              <div className="text-xs">
                <span className="text-[10px] font-bold uppercase tracking-wider text-[#C47B54]">Suggested Next Action</span>
                <p className="font-medium text-[#202823] mt-0.5">{next_suggested_action}</p>
              </div>
            </div>
            <NavLink
              to="/scanner"
              className="text-xs font-semibold text-[#163B32] hover:text-[#79B9AC] flex items-center gap-1 flex-shrink-0 transition"
            >
              <span>Take Step</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </NavLink>
          </div>
        </div>
      </section>

      {/* Real Statistics Metric Cards */}
      <section className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Profile Completeness */}
        <div className="glass-panel p-5">
          <div className="flex items-center justify-between text-xs text-[#69756E] mb-2">
            <span>Profile Completeness</span>
            <span className="font-bold text-[#163B32]">{stats?.profile_completeness}%</span>
          </div>
          <div className="w-full bg-[#E4E4DA] h-2 rounded-full overflow-hidden mb-3">
            <div 
              className="bg-[#163B32] h-full rounded-full transition-all duration-500" 
              style={{ width: `${stats?.profile_completeness}%` }} 
            />
          </div>
          <p className="text-[11px] text-[#69756E]">
            {stats?.verified_skills_count} verified skills across {stats?.projects_count} projects.
          </p>
        </div>

        {/* Active Applications */}
        <div className="glass-panel p-5">
          <div className="flex items-center justify-between text-xs text-[#69756E] mb-1">
            <span>Active Pipeline</span>
            <Briefcase className="w-4 h-4 text-[#79B9AC]" />
          </div>
          <div className="text-2xl font-bold text-[#163B32]">{stats?.active_applications_count}</div>
          <p className="text-[11px] text-[#69756E] mt-1">
            {stats?.total_applications_count} total applications recorded.
          </p>
        </div>

        {/* Saved Jobs */}
        <div className="glass-panel p-5">
          <div className="flex items-center justify-between text-xs text-[#69756E] mb-1">
            <span>Saved Opportunities</span>
            <ShieldCheck className="w-4 h-4 text-[#79B9AC]" />
          </div>
          <div className="text-2xl font-bold text-[#163B32]">{stats?.saved_jobs_count}</div>
          <p className="text-[11px] text-[#69756E] mt-1">
            Triaged via multi-signal scam engine.
          </p>
        </div>

        {/* Documents Processed */}
        <div className="glass-panel p-5">
          <div className="flex items-center justify-between text-xs text-[#69756E] mb-1">
            <span>Documents Scanned</span>
            <FileSearch className="w-4 h-4 text-[#79B9AC]" />
          </div>
          <div className="text-2xl font-bold text-[#163B32]">{stats?.documents_count}</div>
          <p className="text-[11px] text-[#69756E] mt-1">
            With verbatim claim attribution.
          </p>
        </div>
      </section>

      {/* Split Section: Career Plan & Recommended Opportunities */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left 2 Cols: 30-Day Plan & Recommended Roles */}
        <div className="lg:col-span-2 space-y-6">
          {/* 30-Day Plan Snapshot */}
          <div className="glass-panel p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <span className="text-[10px] uppercase font-bold tracking-wider text-[#79B9AC]">Adaptive Plan</span>
                <h3 className="text-base font-bold text-[#163B32]">30-Day Career Acceleration Plan</h3>
              </div>
              <NavLink 
                to="/career-plan" 
                className="text-xs font-semibold text-[#163B32] hover:text-[#79B9AC] flex items-center gap-1 transition"
              >
                <span>Full Plan</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </NavLink>
            </div>

            {career_plan ? (
              <div>
                <div className="flex items-center justify-between text-xs mb-1.5">
                  <span className="font-medium text-[#202823]">
                    {career_plan.completed_tasks} of {career_plan.total_tasks} tasks finished
                  </span>
                  <span className="font-bold text-[#163B32]">{career_plan.progress_percentage}%</span>
                </div>
                <div className="w-full bg-[#E4E4DA] h-2.5 rounded-full overflow-hidden mb-4">
                  <div 
                    className="bg-gradient-to-r from-[#163B32] to-[#79B9AC] h-full rounded-full transition-all duration-500" 
                    style={{ width: `${career_plan.progress_percentage}%` }} 
                  />
                </div>

                {next_task && (
                  <div className="p-4 rounded-xl bg-white/80 border border-[#E4E4DA] flex items-start justify-between gap-3">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-[#DCE9E0] text-[#163B32]">
                          {next_task.due_date}
                        </span>
                        <span className="text-[11px] text-[#69756E]">{next_task.stage}</span>
                      </div>
                      <p className="text-sm font-semibold text-[#163B32]">{next_task.title}</p>
                    </div>
                    <NavLink
                      to="/career-plan"
                      className="px-3 py-1.5 rounded-lg bg-[#163B32] text-white text-xs font-medium hover:bg-[#102C26] transition"
                    >
                      View Task
                    </NavLink>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-6">
                <p className="text-xs text-[#69756E] mb-3">No active career plan. Generate a custom 30-day plan targeting your goal role.</p>
                <NavLink
                  to="/career-plan"
                  className="px-4 py-2 rounded-xl bg-[#163B32] text-white text-xs font-semibold hover:bg-[#102C26] transition shadow-sm"
                >
                  Generate 30-Day Plan
                </NavLink>
              </div>
            )}
          </div>

          {/* Recommended Jobs */}
          <div className="glass-panel p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <span className="text-[10px] uppercase font-bold tracking-wider text-[#79B9AC]">Explainable Matches</span>
                <h3 className="text-base font-bold text-[#163B32]">Curated Opportunities</h3>
              </div>
              <NavLink 
                to="/jobs" 
                className="text-xs font-semibold text-[#163B32] hover:text-[#79B9AC] flex items-center gap-1 transition"
              >
                <span>View All Jobs</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </NavLink>
            </div>

            <div className="space-y-3">
              {recommended_opportunities && recommended_opportunities.length > 0 ? (
                recommended_opportunities.map((job: any) => (
                  <div 
                    key={job.id} 
                    className="p-4 rounded-xl bg-white/70 hover:bg-white/90 border border-[#E4E4DA] transition flex flex-col md:flex-row md:items-center justify-between gap-3"
                  >
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-bold text-[#163B32]">{job.title}</span>
                        <span className="text-xs font-medium text-[#69756E]">· {job.employer}</span>
                      </div>
                      <p className="text-xs text-[#69756E] mt-0.5">{job.summary}</p>
                      <div className="flex flex-wrap gap-1.5 mt-2">
                        {job.matched_skills?.map((sk: string) => (
                          <span key={sk} className="text-[10px] font-medium px-2 py-0.5 rounded-md bg-[#DCE9E0] text-[#163B32]">
                            ✓ {sk}
                          </span>
                        ))}
                      </div>
                    </div>
                    <div className="flex items-center gap-3 self-end md:self-center">
                      <div className="text-right">
                        <span className="text-xs font-bold text-[#163B32]">{job.match_score}% Match</span>
                        <p className="text-[10px] text-[#69756E]">{job.work_arrangement}</p>
                      </div>
                      <NavLink
                        to={`/jobs`}
                        className="px-3 py-1.5 rounded-lg border border-[#163B32] text-[#163B32] hover:bg-[#163B32] hover:text-white text-xs font-semibold transition"
                      >
                        Inspect
                      </NavLink>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-xs text-[#69756E] text-center py-4">No matching jobs found yet.</p>
              )}
            </div>
          </div>
        </div>

        {/* Right Col: Recent Activity & Quick Tools */}
        <div className="space-y-6">
          {/* Quick Tools Panel */}
          <div className="glass-panel p-5">
            <h4 className="text-xs font-bold uppercase tracking-wider text-[#163B32] mb-3">Quick Workflows</h4>
            <div className="space-y-2">
              <NavLink
                to="/scanner"
                className="flex items-center justify-between p-3 rounded-xl bg-white/70 hover:bg-white/95 border border-[#E4E4DA] transition text-xs font-medium text-[#202823]"
              >
                <div className="flex items-center gap-2.5">
                  <FileSearch className="w-4 h-4 text-[#79B9AC]" />
                  <span>Upload & Verify Resume</span>
                </div>
                <ArrowRight className="w-3.5 h-3.5 text-[#69756E]" />
              </NavLink>
              <NavLink
                to="/checker"
                className="flex items-center justify-between p-3 rounded-xl bg-white/70 hover:bg-white/95 border border-[#E4E4DA] transition text-xs font-medium text-[#202823]"
              >
                <div className="flex items-center gap-2.5">
                  <ShieldCheck className="w-4 h-4 text-[#C47B54]" />
                  <span>Check Job for Scam Signals</span>
                </div>
                <ArrowRight className="w-3.5 h-3.5 text-[#69756E]" />
              </NavLink>
              <NavLink
                to="/interviews"
                className="flex items-center justify-between p-3 rounded-xl bg-white/70 hover:bg-white/95 border border-[#E4E4DA] transition text-xs font-medium text-[#202823]"
              >
                <div className="flex items-center gap-2.5">
                  <Clock className="w-4 h-4 text-[#163B32]" />
                  <span>Practice Interview Questions</span>
                </div>
                <ArrowRight className="w-3.5 h-3.5 text-[#69756E]" />
              </NavLink>
            </div>
          </div>

          {/* Real Activity Stream */}
          <div className="glass-panel p-5">
            <div className="flex items-center justify-between mb-3">
              <h4 className="text-xs font-bold uppercase tracking-wider text-[#163B32]">Recent Activity</h4>
              <NavLink to="/audit" className="text-[11px] text-[#69756E] hover:text-[#163B32]">View Log</NavLink>
            </div>
            <div className="space-y-3">
              {recent_activity && recent_activity.length > 0 ? (
                recent_activity.map((act: any) => (
                  <div key={act.id} className="text-xs border-l-2 border-[#79B9AC] pl-3 py-0.5">
                    <p className="font-medium text-[#202823] capitalize">
                      {act.event_type.replace(/_/g, ' ')}
                    </p>
                    <p className="text-[10px] text-[#69756E] mt-0.5">
                      {act.created_at ? new Date(act.created_at).toLocaleDateString() : 'Recent'}
                    </p>
                  </div>
                ))
              ) : (
                <p className="text-xs text-[#69756E]">No recent activity recorded.</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
