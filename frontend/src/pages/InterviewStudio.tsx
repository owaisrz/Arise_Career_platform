import React, { useState, useEffect } from 'react';
import { 
  MessagesSquare, 
  Sparkles, 
  Send, 
  CheckCircle2, 
  HelpCircle, 
  RefreshCw, 
  Award, 
  FolderGit2,
  AlertCircle
} from 'lucide-react';
import { api } from '../api/client';
import { useAuth } from '../context/AuthContext';

export const InterviewStudio: React.FC = () => {
  const { user } = useAuth();
  const [roleTitle, setRoleTitle] = useState('Full Stack Software Engineer');
  const [interviewType, setInterviewType] = useState('Technical');
  const [session, setSession] = useState<any | null>(null);
  const [selectedQuestionIndex, setSelectedQuestionIndex] = useState(0);
  const [userResponse, setUserResponse] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [evaluation, setEvaluation] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);

  const handleCreateSession = async () => {
    try {
      setLoading(true);
      setEvaluation(null);
      setUserResponse('');
      const newSession = await api.interviews.createSession(roleTitle, interviewType);
      setSession(newSession);
      setSelectedQuestionIndex(0);
    } catch (err: any) {
      alert(err.message || 'Failed to start interview session');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    handleCreateSession();
  }, [interviewType]);

  const currentQuestion = session?.questions?.[selectedQuestionIndex];

  const handleSubmitPractice = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentQuestion || !userResponse.trim()) return;
    try {
      setSubmitting(true);
      const res = await api.interviews.submitPractice(currentQuestion.id, userResponse);
      setEvaluation(res);
    } catch (err: any) {
      alert(err.message || 'Failed to evaluate practice answer');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Editorial Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#DCE9E0] text-[#163B32] text-xs font-semibold mb-2 border border-[#79B9AC]/40">
            <MessagesSquare className="w-3.5 h-3.5 text-[#163B32]" />
            <span>Simulated Interview Practice</span>
          </div>
          <h1 className="text-2xl md:text-3xl font-bold text-[#163B32] tracking-tight">
            Interview Studio
          </h1>
          <p className="text-sm text-[#69756E] mt-1 max-w-2xl">
            Practice questions grounded in your actual projects, verified skills, and role expectations. Receive instant rubric evaluation against STAR methodology.
          </p>
        </div>

        {/* Interview Type Selector */}
        <div className="flex gap-1.5 p-1 rounded-xl bg-white/70 border border-[#E4E4DA] self-start sm:self-auto">
          {['Technical', 'Behavioral', 'Project-grounded', 'System Design'].map((type) => (
            <button
              key={type}
              onClick={() => setInterviewType(type)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                interviewType === type ? 'bg-[#163B32] text-white shadow-sm' : 'text-[#69756E] hover:text-[#163B32]'
              }`}
            >
              {type}
            </button>
          ))}
        </div>
      </div>

      {session && session.questions?.length > 0 ? (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Left Column (4 cols): Questions Navigator */}
          <div className="lg:col-span-4 space-y-3">
            <h3 className="text-xs font-bold uppercase tracking-wider text-[#163B32] px-1">
              Interview Questions ({session.questions.length})
            </h3>
            <div className="space-y-2">
              {session.questions.map((q: any, idx: number) => (
                <div
                  key={q.id}
                  onClick={() => {
                    setSelectedQuestionIndex(idx);
                    setEvaluation(q.latest_practice || null);
                    setUserResponse(q.latest_practice?.user_response || '');
                  }}
                  className={`p-3.5 rounded-xl border text-xs cursor-pointer transition ${
                    selectedQuestionIndex === idx
                      ? 'bg-white border-[#163B32] shadow-sm'
                      : 'bg-white/60 hover:bg-white/90 border-[#E4E4DA]'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="uppercase text-[9px] font-bold tracking-wider px-2 py-0.5 rounded bg-[#DCE9E0] text-[#163B32]">
                      {q.question_type.replace(/_/g, ' ')}
                    </span>
                    {q.latest_practice && (
                      <span className="text-[10px] font-bold text-emerald-700">
                        Score: {q.latest_practice.feedback_score}
                      </span>
                    )}
                  </div>
                  <p className="font-semibold text-[#163B32] line-clamp-2 mt-1">
                    {q.question_text}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Right Column (8 cols): Question Workspace & Answer Input */}
          <div className="lg:col-span-8 space-y-6">
            {currentQuestion && (
              <div className="glass-panel p-6 space-y-5">
                {/* Question Details */}
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-[10px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-[#163B32] text-white">
                      Question {selectedQuestionIndex + 1}
                    </span>
                    {currentQuestion.linked_skill && (
                      <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-[#DCE9E0] text-[#163B32]">
                        Topic: {currentQuestion.linked_skill}
                      </span>
                    )}
                    {currentQuestion.linked_project && (
                      <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-[#C47B54]/20 text-[#C47B54] border border-[#C47B54]/30 flex items-center gap-1">
                        <FolderGit2 className="w-3 h-3" />
                        <span>Project: {currentQuestion.linked_project}</span>
                      </span>
                    )}
                  </div>

                  <h2 className="text-base font-bold text-[#163B32] leading-snug">
                    {currentQuestion.question_text}
                  </h2>
                  <p className="text-xs text-[#69756E] mt-1.5 leading-relaxed">
                    <strong>Context & Objective:</strong> {currentQuestion.context_rationale}
                  </p>

                  {currentQuestion.suggested_framework && (
                    <div className="mt-3 p-3 rounded-xl bg-white/80 border border-[#E4E4DA] text-[11px] text-[#202823]">
                      <span className="font-bold text-[#163B32] block mb-0.5">Recommended Structure / STAR Guidance:</span>
                      <p className="text-[#69756E]">{currentQuestion.suggested_framework}</p>
                    </div>
                  )}
                </div>

                {/* Answer Submission Form */}
                <form onSubmit={handleSubmitPractice} className="space-y-3">
                  <div>
                    <label className="text-xs font-bold text-[#163B32] block mb-1">
                      Type Your Practice Response
                    </label>
                    <textarea
                      rows={6}
                      value={userResponse}
                      onChange={(e) => setUserResponse(e.target.value)}
                      placeholder="Structure your answer clearly. For behavioral and project questions, describe Situation, Task, Action, and Quantifiable Result..."
                      className="w-full p-3.5 text-xs rounded-xl bg-white border border-[#E4E4DA] focus:outline-none focus:ring-1 focus:ring-[#163B32] leading-relaxed"
                      required
                    />
                  </div>

                  <div className="flex justify-end">
                    <button
                      type="submit"
                      disabled={submitting || !userResponse.trim()}
                      className="px-5 py-2.5 rounded-xl bg-[#163B32] text-white text-xs font-semibold hover:bg-[#102C26] transition flex items-center gap-2 shadow-sm disabled:opacity-50"
                    >
                      {submitting ? (
                        <>
                          <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                          <span>Evaluating STAR Rubrics...</span>
                        </>
                      ) : (
                        <>
                          <Send className="w-3.5 h-3.5" />
                          <span>Evaluate Response</span>
                        </>
                      )}
                    </button>
                  </div>
                </form>

                {/* Instant Feedback Rubric */}
                {evaluation && (
                  <div className="p-5 rounded-2xl bg-white border border-[#E4E4DA] space-y-4 shadow-sm">
                    <div className="flex items-center justify-between pb-3 border-b border-[#E4E4DA]">
                      <div>
                        <span className="text-[10px] font-bold uppercase text-[#69756E]">Evaluation Result</span>
                        <h4 className="font-bold text-sm text-[#163B32]">{evaluation.feedback_summary}</h4>
                      </div>
                      <div className="text-right">
                        <span className="text-2xl font-extrabold text-[#163B32]">{evaluation.feedback_score}</span>
                        <span className="text-[10px] text-[#69756E] block font-semibold">/ 100 Score</span>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                      {/* Strengths */}
                      <div className="space-y-1.5 p-3 rounded-xl bg-emerald-50/70 border border-emerald-200">
                        <span className="font-bold text-emerald-900 block mb-1">Observed Strengths:</span>
                        {evaluation.strengths?.map((str: string, i: number) => (
                          <div key={i} className="flex items-start gap-1.5 text-emerald-950">
                            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 flex-shrink-0 mt-0.5" />
                            <span>{str}</span>
                          </div>
                        ))}
                      </div>

                      {/* Improvements */}
                      <div className="space-y-1.5 p-3 rounded-xl bg-amber-50/70 border border-amber-200">
                        <span className="font-bold text-amber-900 block mb-1">Recommended Improvements:</span>
                        {evaluation.improvements?.map((imp: string, i: number) => (
                          <div key={i} className="flex items-start gap-1.5 text-amber-950">
                            <HelpCircle className="w-3.5 h-3.5 text-amber-700 flex-shrink-0 mt-0.5" />
                            <span>{imp}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="glass-panel p-12 text-center text-[#69756E]">
          <RefreshCw className="w-8 h-8 animate-spin text-[#79B9AC] mx-auto mb-2" />
          <p className="text-xs">Generating role-specific questions...</p>
        </div>
      )}
    </div>
  );
};
