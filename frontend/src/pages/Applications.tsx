import React, { useState, useEffect } from 'react';
import { 
  KanbanSquare, 
  Plus, 
  Trash2, 
  Calendar, 
  Clock, 
  FileText, 
  CheckCircle2, 
  MoreVertical,
  Briefcase
} from 'lucide-react';
import { api } from '../api/client';
import { useAuth } from '../context/AuthContext';

export const Applications: React.FC = () => {
  const { user } = useAuth();
  const [pipeline, setPipeline] = useState<{ [key: string]: any[] }>({});
  const [totalApps, setTotalApps] = useState(0);
  const [totalActive, setTotalActive] = useState(0);
  const [loading, setLoading] = useState(true);

  const stages = ['Saved', 'Planned', 'Applied', 'Assessment', 'Interview', 'Offer', 'Rejected', 'Withdrawn'];

  const fetchApplications = async () => {
    try {
      setLoading(true);
      const res = await api.applications.list();
      setPipeline(res.pipeline || {});
      setTotalApps(res.total_applications || 0);
      setTotalActive(res.total_active || 0);
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchApplications();
  }, [user]);

  const handleStageChange = async (appId: string, newStage: string) => {
    try {
      await api.applications.updateStage(appId, newStage);
      await fetchApplications();
    } catch (err: any) {
      alert(err.message || 'Failed to move application stage');
    }
  };

  const handleDelete = async (appId: string) => {
    if (!confirm('Remove application from pipeline?')) return;
    try {
      await api.applications.delete(appId);
      await fetchApplications();
    } catch (err: any) {
      alert(err.message || 'Failed to delete application');
    }
  };

  return (
    <div className="space-y-6">
      {/* Editorial Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#DCE9E0] text-[#163B32] text-xs font-semibold mb-2 border border-[#79B9AC]/40">
            <KanbanSquare className="w-3.5 h-3.5 text-[#163B32]" />
            <span>Application Pipeline</span>
          </div>
          <h1 className="text-2xl md:text-3xl font-bold text-[#163B32] tracking-tight">
            Application Journey & Stage Tracker
          </h1>
          <p className="text-sm text-[#69756E] mt-1">
            Track interview dates, assessments, follow-ups, and resume versions used across all submitted applications.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="px-3.5 py-2 rounded-xl bg-white border border-[#E4E4DA] text-xs font-medium text-[#202823]">
            Active In-Progress: <strong className="text-[#163B32] font-bold">{totalActive}</strong>
          </div>
        </div>
      </div>

      {/* Kanban Board Container */}
      <div className="overflow-x-auto pb-6">
        <div className="flex gap-4 min-w-[1200px]">
          {stages.map((stage) => {
            const items = pipeline[stage] || [];
            return (
              <div
                key={stage}
                className="w-80 flex-shrink-0 glass-panel p-4 flex flex-col rounded-2xl bg-white/50 border border-[#E4E4DA]"
              >
                {/* Column Header */}
                <div className="flex items-center justify-between pb-3 mb-3 border-b border-[#E4E4DA]">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-xs text-[#163B32]">{stage}</span>
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-[#DCE9E0] text-[#163B32]">
                      {items.length}
                    </span>
                  </div>
                </div>

                {/* Column Cards */}
                <div className="space-y-3 flex-1 overflow-y-auto max-h-[600px] pr-1">
                  {items.length > 0 ? (
                    items.map((app: any) => (
                      <div
                        key={app.id}
                        className="p-4 rounded-xl bg-white border border-[#E4E4DA] text-xs space-y-2.5 shadow-sm hover:shadow transition"
                      >
                        <div className="flex items-start justify-between gap-2">
                          <div>
                            <span className="text-[10px] font-semibold text-[#69756E] block">
                              {app.employer}
                            </span>
                            <h4 className="font-bold text-xs text-[#163B32] leading-snug">
                              {app.title}
                            </h4>
                          </div>
                          <button
                            onClick={() => handleDelete(app.id)}
                            className="text-[#69756E] hover:text-red-700 p-0.5"
                            title="Delete"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>

                        {app.notes && (
                          <p className="text-[11px] text-[#69756E] line-clamp-2 italic">
                            "{app.notes}"
                          </p>
                        )}

                        {app.interview_date && (
                          <div className="flex items-center gap-1.5 text-[10px] font-bold text-emerald-800 bg-emerald-50 px-2 py-1 rounded-md border border-emerald-200">
                            <Calendar className="w-3 h-3 text-emerald-600" />
                            <span>Interview: {app.interview_date}</span>
                          </div>
                        )}

                        {app.follow_up_date && !app.interview_date && (
                          <div className="flex items-center gap-1.5 text-[10px] text-[#C47B54] font-medium">
                            <Clock className="w-3 h-3" />
                            <span>Follow up: {app.follow_up_date}</span>
                          </div>
                        )}

                        {/* Stage Selector Dropdown */}
                        <div className="pt-2 border-t border-[#E4E4DA] flex items-center justify-between">
                          <span className="text-[10px] text-[#69756E] font-medium">Move stage:</span>
                          <select
                            value={app.stage}
                            onChange={(e) => handleStageChange(app.id, e.target.value)}
                            className="text-[10px] font-bold px-2 py-1 rounded bg-[#F6F3EC] border border-[#E4E4DA] text-[#163B32] focus:outline-none"
                          >
                            {stages.map((s) => (
                              <option key={s} value={s}>
                                {s}
                              </option>
                            ))}
                          </select>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="py-8 text-center text-[11px] text-[#69756E]">
                      No applications in {stage}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
