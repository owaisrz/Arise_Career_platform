import React, { useState, useEffect } from 'react';
import { 
  CalendarRange, 
  CheckCircle2, 
  Circle, 
  Clock, 
  Sparkles, 
  Plus, 
  Flame, 
  RefreshCw, 
  Check, 
  SkipForward,
  AlertCircle
} from 'lucide-react';
import { api } from '../api/client';
import { useAuth } from '../context/AuthContext';

export const CareerPlan: React.FC = () => {
  const { user } = useAuth();
  const [plan, setPlan] = useState<any | null>(null);
  const [tasks, setTasks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedStage, setSelectedStage] = useState<string>('all');
  const [completingTaskId, setCompletingTaskId] = useState<string | null>(null);
  const [evidenceNote, setEvidenceNote] = useState('');
  const [showEvidenceModal, setShowEvidenceModal] = useState(false);
  const [targetRoleInput, setTargetRoleInput] = useState('Full Stack Software Engineer');
  const [generating, setGenerating] = useState(false);

  const fetchPlan = async () => {
    try {
      setLoading(true);
      const res = await api.careerPlans.current();
      setPlan(res.plan);
      setTasks(res.tasks || []);
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPlan();
  }, [user]);

  const handleGeneratePlan = async () => {
    try {
      setGenerating(true);
      await api.careerPlans.generate(targetRoleInput);
      await fetchPlan();
    } catch (err: any) {
      alert(err.message || 'Failed to generate plan');
    } finally {
      setGenerating(false);
    }
  };

  const handleTaskToggle = async (task: any) => {
    if (task.status === 'completed') {
      // Revert to pending
      await api.careerPlans.updateTask(task.id, 'pending');
      await fetchPlan();
    } else {
      // Open evidence prompt
      setCompletingTaskId(task.id);
      setShowEvidenceModal(true);
    }
  };

  const submitTaskCompletion = async () => {
    if (!completingTaskId) return;
    try {
      await api.careerPlans.updateTask(completingTaskId, 'completed', evidenceNote);
      setShowEvidenceModal(false);
      setEvidenceNote('');
      setCompletingTaskId(null);
      await fetchPlan();
    } catch (err: any) {
      alert(err.message || 'Failed to complete task');
    }
  };

  const handleSkipTask = async (taskId: string) => {
    const reason = prompt('Reason for skipping this task?');
    if (!reason) return;
    try {
      await api.careerPlans.updateTask(taskId, 'skipped', undefined, reason);
      await fetchPlan();
    } catch (err: any) {
      alert(err.message || 'Failed to skip task');
    }
  };

  const stages = [
    'Days 1–7: Assess and prioritize',
    'Days 8–14: Learn and build evidence',
    'Days 15–21: Apply strategically',
    'Days 22–30: Prepare and improve',
  ];

  const filteredTasks = selectedStage === 'all' 
    ? tasks 
    : tasks.filter((t) => t.stage.toLowerCase().includes(selectedStage.toLowerCase().slice(0, 8)));

  return (
    <div className="space-y-6">
      {/* Editorial Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#DCE9E0] text-[#163B32] text-xs font-semibold mb-2 border border-[#79B9AC]/40">
            <CalendarRange className="w-3.5 h-3.5 text-[#163B32]" />
            <span>Structured Goal Progression</span>
          </div>
          <h1 className="text-2xl md:text-3xl font-bold text-[#163B32] tracking-tight">
            Adaptive 30-Day Career Plan
          </h1>
          <p className="text-sm text-[#69756E] mt-1 max-w-2xl">
            A milestone roadmap systematically bridging identified skill gaps with tangible project evidence and interview preparation.
          </p>
        </div>

        {plan && (
          <button
            onClick={handleGeneratePlan}
            disabled={generating}
            className="px-4 py-2 rounded-xl bg-white/80 hover:bg-white text-[#163B32] border border-[#E4E4DA] text-xs font-semibold flex items-center gap-2 transition self-start md:self-auto shadow-sm"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${generating ? 'animate-spin' : ''}`} />
            <span>Recalibrate Roadmap</span>
          </button>
        )}
      </div>

      {plan ? (
        <div className="space-y-6">
          {/* Progress Overview Banner */}
          <div className="glass-panel p-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-[#79B9AC]">Targeting Goal</span>
                <h2 className="text-lg font-bold text-[#163B32]">{plan.target_role}</h2>
                <p className="text-xs text-[#69756E] mt-0.5">
                  Day {plan.current_day} of 30 · {plan.completed_tasks} of {plan.total_tasks} milestones completed
                </p>
              </div>

              <div className="text-right">
                <span className="text-2xl font-extrabold text-[#163B32]">{plan.progress_percentage}%</span>
                <span className="text-[10px] text-[#69756E] block font-semibold">Completed</span>
              </div>
            </div>

            <div className="w-full bg-[#E4E4DA] h-3 rounded-full overflow-hidden">
              <div 
                className="bg-gradient-to-r from-[#163B32] via-[#79B9AC] to-[#C47B54] h-full rounded-full transition-all duration-500" 
                style={{ width: `${plan.progress_percentage}%` }} 
              />
            </div>
          </div>

          {/* Stage Filter Tabs */}
          <div className="flex gap-2 overflow-x-auto pb-1">
            <button
              onClick={() => setSelectedStage('all')}
              className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition ${
                selectedStage === 'all' ? 'bg-[#163B32] text-white shadow-sm' : 'bg-white/70 text-[#69756E] hover:bg-white'
              }`}
            >
              All 30 Days ({tasks.length})
            </button>
            {stages.map((stg) => (
              <button
                key={stg}
                onClick={() => setSelectedStage(stg)}
                className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition ${
                  selectedStage === stg ? 'bg-[#163B32] text-white shadow-sm' : 'bg-white/70 text-[#69756E] hover:bg-white'
                }`}
              >
                {stg}
              </button>
            ))}
          </div>

          {/* Tasks List */}
          <div className="space-y-3">
            {filteredTasks.map((task) => {
              const isDone = task.status === 'completed';
              const isSkipped = task.status === 'skipped';
              return (
                <div
                  key={task.id}
                  className={`glass-panel p-5 transition flex flex-col md:flex-row md:items-start justify-between gap-4 ${
                    isDone ? 'bg-emerald-50/40 border-emerald-200' : isSkipped ? 'opacity-60 bg-gray-50' : ''
                  }`}
                >
                  <div className="flex items-start gap-3.5">
                    <button
                      onClick={() => handleTaskToggle(task)}
                      className={`mt-0.5 w-5 h-5 rounded-md border flex items-center justify-center transition flex-shrink-0 ${
                        isDone 
                          ? 'bg-[#163B32] border-[#163B32] text-white' 
                          : 'border-[#69756E]/40 hover:border-[#163B32] bg-white'
                      }`}
                    >
                      {isDone && <Check className="w-3.5 h-3.5" />}
                    </button>

                    <div>
                      <div className="flex flex-wrap items-center gap-2 mb-1">
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-[#DCE9E0] text-[#163B32]">
                          {task.due_date || `Day ${task.day_number}`}
                        </span>
                        <span className="text-[11px] font-medium text-[#69756E]">{task.stage}</span>
                        {task.linked_skill && (
                          <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-white text-[#163B32] border border-[#E4E4DA]">
                            Skill: {task.linked_skill}
                          </span>
                        )}
                        <span className={`text-[9px] uppercase font-bold px-1.5 py-0.2 rounded ${
                          task.priority === 'High' ? 'text-red-800 bg-red-100' : 'text-gray-700 bg-gray-100'
                        }`}>
                          {task.priority} Priority
                        </span>
                      </div>

                      <h3 className={`text-sm font-bold ${isDone ? 'line-through text-[#69756E]' : 'text-[#163B32]'}`}>
                        {task.title}
                      </h3>
                      <p className="text-xs text-[#69756E] mt-1 leading-relaxed">{task.description}</p>

                      {task.completion_evidence && (
                        <div className="mt-2.5 p-2 rounded-lg bg-emerald-50 text-[11px] text-emerald-900 border border-emerald-200 font-medium">
                          <strong>Attached Evidence:</strong> {task.completion_evidence}
                        </div>
                      )}

                      {task.skip_reason && (
                        <div className="mt-2 text-[11px] text-gray-500 italic">
                          Skipped: {task.skip_reason}
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center gap-2 self-end md:self-start flex-shrink-0 pt-2 md:pt-0">
                    <span className="text-[11px] text-[#69756E] flex items-center gap-1">
                      <Clock className="w-3.5 h-3.5" />
                      <span>{task.duration_hours} hrs</span>
                    </span>
                    {!isDone && !isSkipped && (
                      <button
                        onClick={() => handleSkipTask(task.id)}
                        className="text-[11px] text-[#69756E] hover:text-black px-2 py-1 rounded hover:bg-black/5"
                      >
                        Skip
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      ) : (
        /* Empty State & Generation */
        <div className="glass-panel p-12 text-center max-w-lg mx-auto space-y-4">
          <CalendarRange className="w-12 h-12 text-[#79B9AC] mx-auto" />
          <h2 className="text-xl font-bold text-[#163B32]">No Active 30-Day Plan</h2>
          <p className="text-xs text-[#69756E] leading-relaxed">
            Generate an adaptive plan grounded in your verified candidate skills and target role requirements.
          </p>

          <div className="pt-2">
            <label className="text-xs font-bold text-[#163B32] block mb-1.5 text-left">Target Career Role</label>
            <input
              type="text"
              value={targetRoleInput}
              onChange={(e) => setTargetRoleInput(e.target.value)}
              placeholder="e.g. Junior Full Stack Engineer, Data Analyst"
              className="w-full px-3 py-2 text-xs rounded-xl bg-white border border-[#E4E4DA] mb-3"
            />
            <button
              onClick={handleGeneratePlan}
              disabled={generating}
              className="w-full py-2.5 px-4 rounded-xl bg-[#163B32] text-white text-xs font-semibold hover:bg-[#102C26] transition flex items-center justify-center gap-2 shadow-sm"
            >
              {generating ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4 text-[#79B9AC]" />}
              <span>Generate Personalized 30-Day Plan</span>
            </button>
          </div>
        </div>
      )}

      {/* Complete Task Evidence Modal */}
      {showEvidenceModal && (
        <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass-modal max-w-md w-full p-6 space-y-4">
            <h3 className="font-bold text-sm text-[#163B32]">Record Milestone Evidence</h3>
            <p className="text-xs text-[#69756E]">
              Add a brief reference, commit URL, or note verifying this milestone's completion:
            </p>
            <textarea
              rows={3}
              value={evidenceNote}
              onChange={(e) => setEvidenceNote(e.target.value)}
              placeholder="e.g. Published GitHub commit for FastAPI endpoints, ran unit tests with 92% coverage."
              className="w-full p-3 text-xs rounded-xl bg-white border border-[#E4E4DA]"
            />
            <div className="flex justify-end gap-2">
              <button
                onClick={() => { setShowEvidenceModal(false); setCompletingTaskId(null); }}
                className="px-3.5 py-1.5 rounded-lg text-xs font-medium text-[#69756E] hover:bg-black/5"
              >
                Cancel
              </button>
              <button
                onClick={submitTaskCompletion}
                className="px-4 py-1.5 rounded-lg bg-[#163B32] text-white text-xs font-semibold hover:bg-[#102C26]"
              >
                Confirm & Mark Complete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
