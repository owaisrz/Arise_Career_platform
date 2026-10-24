import React, { useState, useEffect } from 'react';
import { 
  Search, 
  Filter, 
  Compass, 
  ShieldCheck, 
  Bookmark, 
  ArrowRight, 
  CheckCircle2, 
  AlertCircle, 
  CalendarRange, 
  KanbanSquare, 
  ExternalLink,
  X
} from 'lucide-react';
import { api } from '../api/client';
import { useAuth } from '../context/AuthContext';

export const Jobs: React.FC = () => {
  const { user } = useAuth();
  const [jobs, setJobs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [arrangement, setArrangement] = useState('all');
  const [selectedJob, setSelectedJob] = useState<any | null>(null);
  const [savingJobId, setSavingJobId] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const fetchJobs = async () => {
    try {
      setLoading(true);
      const res = await api.jobs.list({
        q: searchTerm || undefined,
        work_arrangement: arrangement !== 'all' ? arrangement : undefined,
        sort: 'match',
      });
      setJobs(res);
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs();
  }, [arrangement]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchJobs();
  };

  const handleSaveJob = async (jobId: string) => {
    try {
      setSavingJobId(jobId);
      await api.jobs.save(jobId, 'saved', 'Saved from job discovery');
      setMessage('Job bookmarked successfully');
      setTimeout(() => setMessage(null), 3000);
    } catch (err: any) {
      alert(err.message || 'Failed to bookmark job');
    } finally {
      setSavingJobId(null);
    }
  };

  const handleCreateApplication = async (jobId: string) => {
    try {
      await api.applications.create(jobId, 'Saved');
      alert('Job successfully moved to your Application Pipeline (Saved stage).');
      setSelectedJob(null);
    } catch (err: any) {
      alert(err.message || 'Failed to add application');
    }
  };

  const handleCreatePlanForJob = async (job: any) => {
    try {
      await api.careerPlans.generate(job.title, job.id);
      alert(`Created adaptive 30-day career plan tailored to ${job.title}!`);
      setSelectedJob(null);
    } catch (err: any) {
      alert(err.message || 'Failed to create plan');
    }
  };

  return (
    <div className="space-y-6">
      {/* Editorial Header */}
      <div>
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#DCE9E0] text-[#163B32] text-xs font-semibold mb-2 border border-[#79B9AC]/40">
          <Compass className="w-3.5 h-3.5 text-[#163B32]" />
          <span>Evidence-Based Alignment</span>
        </div>
        <h1 className="text-2xl md:text-3xl font-bold text-[#163B32] tracking-tight">
          Discover Jobs & Explainable Matching
        </h1>
        <p className="text-sm text-[#69756E] mt-1 max-w-2xl">
          Match scores reflect tangible project evidence and validated skills. No demographic proxies, college pedigree bias, or hidden filters.
        </p>
      </div>

      {message && (
        <div className="p-3.5 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-medium">
          {message}
        </div>
      )}

      {/* Filter and Search Bar */}
      <div className="glass-panel p-4 flex flex-col md:flex-row gap-3 items-center justify-between">
        <form onSubmit={handleSearchSubmit} className="w-full md:w-96 relative">
          <Search className="w-4 h-4 text-[#69756E] absolute left-3 top-2.5" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search role, skills (e.g. Python, React), employer..."
            className="w-full pl-9 pr-3 py-2 rounded-xl text-xs bg-white border border-[#E4E4DA] focus:outline-none focus:ring-1 focus:ring-[#163B32]"
          />
        </form>

        <div className="flex items-center gap-3 w-full md:w-auto overflow-x-auto pb-1 md:pb-0">
          <div className="flex items-center gap-1.5 text-xs text-[#69756E]">
            <Filter className="w-3.5 h-3.5 text-[#79B9AC]" />
            <span className="font-semibold">Arrangement:</span>
          </div>
          {['all', 'remote', 'hybrid', 'onsite'].map((type) => (
            <button
              key={type}
              onClick={() => setArrangement(type)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold capitalize transition ${
                arrangement === type ? 'bg-[#163B32] text-white' : 'bg-white/70 text-[#69756E] hover:bg-white'
              }`}
            >
              {type}
            </button>
          ))}
        </div>
      </div>

      {/* Job Grid / List */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 animate-pulse">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-44 glass-panel rounded-2xl" />
          ))}
        </div>
      ) : jobs.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {jobs.map((job) => (
            <div
              key={job.id}
              className="glass-panel p-6 flex flex-col justify-between hover:border-[#163B32] transition group cursor-pointer"
              onClick={() => setSelectedJob(job)}
            >
              <div>
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <span className="text-xs font-semibold text-[#69756E]">{job.employer}</span>
                    <h3 className="text-base font-bold text-[#163B32] group-hover:text-[#79B9AC] transition">
                      {job.title}
                    </h3>
                  </div>
                  <div className="text-right flex-shrink-0">
                    <span className="text-sm font-extrabold text-[#163B32] block">
                      {job.match_score}% Match
                    </span>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full inline-block mt-0.5 ${
                      job.risk_tier === 'Elevated risk indicators'
                        ? 'bg-red-100 text-red-800'
                        : job.risk_tier === 'Needs verification'
                        ? 'bg-amber-100 text-amber-800'
                        : 'bg-emerald-100 text-emerald-800'
                    }`}>
                      {job.risk_tier}
                    </span>
                  </div>
                </div>

                <p className="text-xs text-[#69756E] line-clamp-2 mt-2 leading-relaxed">
                  {job.description}
                </p>

                {/* Skills tags */}
                <div className="flex flex-wrap gap-1.5 mt-3.5">
                  {job.required_skills?.map((sk: string) => (
                    <span key={sk} className="text-[10px] font-medium px-2 py-0.5 rounded-md bg-[#DCE9E0] text-[#163B32]">
                      {sk}
                    </span>
                  ))}
                </div>
              </div>

              <div className="pt-4 mt-4 border-t border-[#E4E4DA] flex items-center justify-between text-xs">
                <span className="font-semibold text-[#202823]">
                  {job.salary_text || job.location}
                </span>
                <div className="flex items-center gap-2">
                  <button
                    onClick={(e) => { e.stopPropagation(); handleSaveJob(job.id); }}
                    className="p-1.5 rounded-lg hover:bg-black/5 text-[#69756E] hover:text-[#163B32] transition"
                    title="Bookmark Job"
                  >
                    <Bookmark className="w-4 h-4" />
                  </button>
                  <button
                    onClick={(e) => { e.stopPropagation(); setSelectedJob(job); }}
                    className="inline-flex items-center gap-1 font-semibold text-[#163B32] hover:text-[#79B9AC] transition"
                  >
                    <span>Inspect</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="glass-panel p-12 text-center text-[#69756E] space-y-2">
          <Compass className="w-10 h-10 text-[#79B9AC] mx-auto opacity-70" />
          <h3 className="text-base font-bold text-[#163B32]">No matching jobs found</h3>
          <p className="text-xs max-w-sm mx-auto">Try clearing search keywords or selecting all work arrangements.</p>
        </div>
      )}

      {/* Explainable Match Detail Modal */}
      {selectedJob && (
        <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass-modal max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6 space-y-6">
            <div className="flex items-start justify-between gap-4 border-b border-[#E4E4DA] pb-4">
              <div>
                <span className="text-xs font-semibold text-[#69756E]">{selectedJob.employer}</span>
                <h2 className="text-xl font-bold text-[#163B32]">{selectedJob.title}</h2>
                <div className="flex items-center gap-2 text-xs text-[#69756E] mt-1">
                  <span>{selectedJob.location}</span>
                  <span>·</span>
                  <span className="capitalize">{selectedJob.work_arrangement}</span>
                  {selectedJob.salary_text && (
                    <>
                      <span>·</span>
                      <span className="font-semibold text-[#163B32]">{selectedJob.salary_text}</span>
                    </>
                  )}
                </div>
              </div>
              <button
                onClick={() => setSelectedJob(null)}
                className="p-1.5 rounded-lg hover:bg-black/5 text-[#69756E]"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Match Breakdown & Evidence Attribution */}
            <div className="p-4 rounded-xl bg-white/80 border border-[#E4E4DA] space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-[#163B32]">
                  Match Explanation ({selectedJob.match_score}% Score)
                </span>
                <span className="text-[10px] text-[#69756E]">50% Skills · 20% Project Evidence · 20% Preferred</span>
              </div>
              <p className="text-xs text-[#202823] leading-relaxed">
                {selectedJob.explanation?.summary}
              </p>

              {/* Matched skills with evidence */}
              <div>
                <span className="text-[10px] uppercase font-bold text-emerald-800 block mb-1.5">
                  Demonstrated Competencies (Supported by Candidate Evidence)
                </span>
                <div className="space-y-1.5">
                  {selectedJob.explanation?.matched_required?.map((m: any, i: number) => (
                    <div key={i} className="flex items-center justify-between text-xs p-2 rounded-lg bg-emerald-50/70 border border-emerald-200">
                      <div className="flex items-center gap-2">
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 flex-shrink-0" />
                        <span className="font-bold text-emerald-950">{m.skill}</span>
                        <span className="text-[10px] text-[#69756E]">({m.proficiency})</span>
                      </div>
                      <span className="text-[10px] font-semibold text-emerald-800">
                        {m.supported_by_project ? '✓ Verified in Project' : 'Listed in Profile'}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Missing skills */}
              {selectedJob.explanation?.missing_required?.length > 0 && (
                <div>
                  <span className="text-[10px] uppercase font-bold text-amber-800 block mb-1">
                    Missing Required Skills to Address in 30-Day Plan:
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {selectedJob.explanation.missing_required.map((ms: string) => (
                      <span key={ms} className="text-[10px] font-medium px-2 py-0.5 rounded bg-amber-50 text-amber-900 border border-amber-200">
                        • {ms}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Description */}
            <div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-[#163B32] mb-1.5">Job Description</h4>
              <p className="text-xs text-[#69756E] whitespace-pre-line leading-relaxed bg-white/50 p-4 rounded-xl border border-[#E4E4DA]">
                {selectedJob.description}
              </p>
            </div>

            {/* Action Bar */}
            <div className="flex flex-wrap gap-2 pt-2 border-t border-[#E4E4DA]">
              <button
                onClick={() => handleCreatePlanForJob(selectedJob)}
                className="flex-1 py-2.5 px-4 rounded-xl bg-[#163B32] text-white text-xs font-semibold hover:bg-[#102C26] transition flex items-center justify-center gap-2 shadow-sm"
              >
                <CalendarRange className="w-4 h-4 text-[#79B9AC]" />
                <span>Build 30-Day Plan for this Job</span>
              </button>
              <button
                onClick={() => handleCreateApplication(selectedJob.id)}
                className="py-2.5 px-4 rounded-xl bg-[#DCE9E0] text-[#163B32] text-xs font-semibold hover:bg-[#cbe0d0] transition flex items-center justify-center gap-1.5"
              >
                <KanbanSquare className="w-4 h-4" />
                <span>Add to Pipeline</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
