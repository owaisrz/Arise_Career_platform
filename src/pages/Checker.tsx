import React, { useState } from 'react';
import { 
  ShieldCheck, 
  ShieldAlert, 
  AlertTriangle, 
  CheckCircle, 
  HelpCircle, 
  ArrowRight, 
  Link as LinkIcon, 
  FileText, 
  ListPlus, 
  BarChart3, 
  RefreshCw, 
  Info,
  ExternalLink,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import { api } from '../api/client';

export const Checker: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'evaluate' | 'benchmark'>('evaluate');
  const [mode, setMode] = useState<'paste' | 'form' | 'url'>('paste');

  // Form states
  const [pastedText, setPastedText] = useState('');
  const [title, setTitle] = useState('');
  const [employer, setEmployer] = useState('');
  const [employerDomain, setEmployerDomain] = useState('');
  const [contactEmail, setContactEmail] = useState('');
  const [contactMessaging, setContactMessaging] = useState('');
  const [salaryText, setSalaryText] = useState('');
  const [urlInput, setUrlInput] = useState('');

  // Evaluation output
  const [loading, setLoading] = useState(false);
  const [evaluating, setEvaluating] = useState(false);
  const [result, setResult] = useState<any | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [expandedSignals, setExpandedSignals] = useState<{ [key: number]: boolean }>({ 0: true });

  // Benchmark output
  const [benchmarkData, setBenchmarkData] = useState<any | null>(null);
  const [benchmarkLoading, setBenchmarkLoading] = useState(false);

  const handleRetrieveUrl = async () => {
    if (!urlInput) return;
    try {
      setLoading(true);
      setError(null);
      const fetched = await api.jobs.retrieveUrl(urlInput);
      setTitle(fetched.title || 'Retrieved Job Posting');
      setPastedText(fetched.extracted_content || '');
      setMode('paste');
    } catch (err: any) {
      setError(err.message || 'Failed to retrieve URL safely.');
    } finally {
      setLoading(false);
    }
  };

  const handleRunAssessment = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setEvaluating(true);
      setError(null);

      const jobTitle = title || 'Job Listing';
      const jobEmployer = employer || 'Stated Employer';
      const jobDesc = mode === 'paste' ? pastedText : pastedText || `${title} at ${employer}`;

      if (!jobDesc.trim()) {
        throw new Error('Please provide job description text or title & employer to evaluate.');
      }

      const res = await api.assessments.evaluate({
        title: jobTitle,
        employer: jobEmployer,
        description: jobDesc,
        employer_domain: employerDomain,
        contact_email: contactEmail,
        contact_messaging: contactMessaging,
        salary_text: salaryText,
      });

      setResult(res);
      setExpandedSignals({ 0: true });
    } catch (err: any) {
      setError(err.message || 'Assessment failed.');
    } finally {
      setEvaluating(false);
    }
  };

  const loadBenchmark = async () => {
    try {
      setBenchmarkLoading(true);
      const data = await api.assessments.benchmark();
      setBenchmarkData(data);
    } catch (err: any) {
      setError(err.message || 'Failed to run benchmark');
    } finally {
      setBenchmarkLoading(false);
    }
  };

  const loadPreset = (preset: 'scam_payment' | 'scam_telegram' | 'scam_tech' | 'legit') => {
    if (preset === 'scam_payment') {
      setTitle('Data Entry Remote Assistant');
      setEmployer('Apex Global Solutions');
      setEmployerDomain('apex-jobportal.xyz');
      setContactEmail('apexjobs@gmail.com');
      setSalaryText('$180/hr');
      setPastedText(
        'Earn $180/hr data entry work from home! High compensation for simple typing. Please pay a processing fee of $75 to receive your starter security kit and hardware credentials before your application can proceed.'
      );
      setMode('paste');
    } else if (preset === 'scam_telegram') {
      setTitle('Executive Virtual Assistant');
      setEmployer('Swift Logistics');
      setEmployerDomain('swiftlogistics.top');
      setContactMessaging('Telegram: @swift_hiring_manager');
      setSalaryText('$4,000/week');
      setPastedText(
        'Immediate hire guaranteed! No interview needed. Contact strictly via Telegram @swift_hiring_manager to claim your placement. Advance money order will be sent for supplies.'
      );
      setMode('paste');
    } else if (preset === 'scam_tech') {
      setTitle('Senior Mobile Engineer');
      setEmployer('NextWave Tech');
      setEmployerDomain('nextwave.tech');
      setContactEmail('hr@nextwave.tech');
      setPastedText(
        'We are seeking a senior engineer with 12 years of experience in Flutter and Dart mobile development. Must have deep architectural knowledge of cross-platform state management.'
      );
      setMode('paste');
    } else {
      setTitle('Junior Full Stack Engineer');
      setEmployer('Meridian Health Technologies');
      setEmployerDomain('meridianhealth.com');
      setContactEmail('careers@meridianhealth.com');
      setSalaryText('₹8,50,000 - ₹11,00,000');
      setPastedText(
        'Looking for a Junior Full Stack Engineer with proficiency in Python, React, and PostgreSQL. Responsibilities include building responsive UI components, integrating RESTful APIs, and writing automated unit tests. The hiring process includes a recruiter screen, technical interview, and architectural discussion.'
      );
      setMode('paste');
    }
  };

  return (
    <div className="space-y-8">
      {/* Editorial Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#DCE9E0] text-[#163B32] text-xs font-semibold mb-2 border border-[#79B9AC]/40">
            <ShieldCheck className="w-3.5 h-3.5 text-[#163B32]" />
            <span>Multi-Signal Trust & Scam Triage</span>
          </div>
          <h1 className="text-2xl md:text-3xl font-bold text-[#163B32] tracking-tight">
            Job Trust Checker & Scam-Risk Assessment
          </h1>
          <p className="text-sm text-[#69756E] mt-1 max-w-2xl">
            Evaluate listings against observable signals: upfront fees, lookalike domains, informal messaging, and anachronistic technology release dates.
          </p>
        </div>

        {/* Tab switch */}
        <div className="flex items-center p-1 rounded-xl bg-white/70 border border-[#E4E4DA] self-start md:self-auto">
          <button
            onClick={() => setActiveTab('evaluate')}
            className={`px-4 py-2 rounded-lg text-xs font-semibold transition ${
              activeTab === 'evaluate' ? 'bg-[#163B32] text-white shadow-sm' : 'text-[#69756E] hover:text-[#163B32]'
            }`}
          >
            Live Risk Checker
          </button>
          <button
            onClick={() => {
              setActiveTab('benchmark');
              if (!benchmarkData) loadBenchmark();
            }}
            className={`px-4 py-2 rounded-lg text-xs font-semibold transition ${
              activeTab === 'benchmark' ? 'bg-[#163B32] text-white shadow-sm' : 'text-[#69756E] hover:text-[#163B32]'
            }`}
          >
            Evaluation Dataset & Matrix (42 Cases)
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-red-800 text-xs flex items-center gap-3">
          <AlertTriangle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {activeTab === 'evaluate' ? (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Left Column (5 cols): Submission Form & Presets */}
          <div className="lg:col-span-5 space-y-6">
            <div className="glass-panel p-6">
              {/* Presets */}
              <div className="mb-4">
                <span className="text-[10px] font-bold uppercase tracking-wider text-[#69756E] block mb-2">
                  Sample Test Presets
                </span>
                <div className="flex flex-wrap gap-1.5">
                  <button
                    type="button"
                    onClick={() => loadPreset('scam_payment')}
                    className="px-2.5 py-1 rounded-lg bg-red-50 hover:bg-red-100 text-red-800 text-[11px] font-semibold border border-red-200"
                  >
                    Fee Demand
                  </button>
                  <button
                    type="button"
                    onClick={() => loadPreset('scam_telegram')}
                    className="px-2.5 py-1 rounded-lg bg-amber-50 hover:bg-amber-100 text-amber-800 text-[11px] font-semibold border border-amber-200"
                  >
                    Telegram Only
                  </button>
                  <button
                    type="button"
                    onClick={() => loadPreset('scam_tech')}
                    className="px-2.5 py-1 rounded-lg bg-orange-50 hover:bg-orange-100 text-orange-800 text-[11px] font-semibold border border-orange-200"
                  >
                    12 Yrs Flutter
                  </button>
                  <button
                    type="button"
                    onClick={() => loadPreset('legit')}
                    className="px-2.5 py-1 rounded-lg bg-emerald-50 hover:bg-emerald-100 text-emerald-800 text-[11px] font-semibold border border-emerald-200"
                  >
                    Legitimate Job
                  </button>
                </div>
              </div>

              {/* Mode Selector */}
              <div className="flex border-b border-[#E4E4DA] mb-4">
                <button
                  type="button"
                  onClick={() => setMode('paste')}
                  className={`pb-2.5 px-3 text-xs font-semibold border-b-2 transition ${
                    mode === 'paste' ? 'border-[#163B32] text-[#163B32]' : 'border-transparent text-[#69756E]'
                  }`}
                >
                  Paste Description
                </button>
                <button
                  type="button"
                  onClick={() => setMode('form')}
                  className={`pb-2.5 px-3 text-xs font-semibold border-b-2 transition ${
                    mode === 'form' ? 'border-[#163B32] text-[#163B32]' : 'border-transparent text-[#69756E]'
                  }`}
                >
                  Structured Fields
                </button>
                <button
                  type="button"
                  onClick={() => setMode('url')}
                  className={`pb-2.5 px-3 text-xs font-semibold border-b-2 transition ${
                    mode === 'url' ? 'border-[#163B32] text-[#163B32]' : 'border-transparent text-[#69756E]'
                  }`}
                >
                  Safe URL Retrieval
                </button>
              </div>

              {mode === 'url' ? (
                <div className="space-y-4">
                  <div className="p-3.5 rounded-xl bg-blue-50 border border-blue-200 text-xs text-blue-900 leading-relaxed">
                    <strong>SSRF Defenses Active:</strong> Prohibits localhost, private RFC1918 subnets, and cloud metadata (169.254.169.254). Strict 8s timeout, 500KB cap.
                  </div>
                  <div>
                    <label className="text-xs font-bold text-[#163B32] block mb-1">Listing URL</label>
                    <input
                      type="url"
                      value={urlInput}
                      onChange={(e) => setUrlInput(e.target.value)}
                      placeholder="https://example-careers.com/job/123"
                      className="w-full px-3 py-2 text-xs rounded-xl bg-white border border-[#E4E4DA] focus:outline-none focus:ring-1 focus:ring-[#163B32]"
                    />
                  </div>
                  <button
                    type="button"
                    onClick={handleRetrieveUrl}
                    disabled={loading || !urlInput}
                    className="w-full py-2.5 px-4 rounded-xl bg-[#163B32] text-white text-xs font-semibold hover:bg-[#102C26] transition disabled:opacity-50"
                  >
                    {loading ? 'Retrieving Safely...' : 'Retrieve and Inspect'}
                  </button>
                </div>
              ) : (
                <form onSubmit={handleRunAssessment} className="space-y-3.5">
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="text-xs font-bold text-[#163B32] block mb-1">Job Title</label>
                      <input
                        type="text"
                        value={title}
                        onChange={(e) => setTitle(e.target.value)}
                        placeholder="e.g. Data Entry Clerk"
                        className="w-full px-3 py-2 text-xs rounded-xl bg-white border border-[#E4E4DA] focus:outline-none focus:ring-1 focus:ring-[#163B32]"
                      />
                    </div>
                    <div>
                      <label className="text-xs font-bold text-[#163B32] block mb-1">Stated Employer</label>
                      <input
                        type="text"
                        value={employer}
                        onChange={(e) => setEmployer(e.target.value)}
                        placeholder="e.g. Apex Global"
                        className="w-full px-3 py-2 text-xs rounded-xl bg-white border border-[#E4E4DA] focus:outline-none focus:ring-1 focus:ring-[#163B32]"
                      />
                    </div>
                  </div>

                  {mode === 'form' && (
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="text-xs font-bold text-[#163B32] block mb-1">Employer Domain</label>
                        <input
                          type="text"
                          value={employerDomain}
                          onChange={(e) => setEmployerDomain(e.target.value)}
                          placeholder="e.g. apex.site"
                          className="w-full px-3 py-2 text-xs rounded-xl bg-white border border-[#E4E4DA] focus:outline-none focus:ring-1 focus:ring-[#163B32]"
                        />
                      </div>
                      <div>
                        <label className="text-xs font-bold text-[#163B32] block mb-1">Contact Email</label>
                        <input
                          type="email"
                          value={contactEmail}
                          onChange={(e) => setContactEmail(e.target.value)}
                          placeholder="e.g. hr@gmail.com"
                          className="w-full px-3 py-2 text-xs rounded-xl bg-white border border-[#E4E4DA] focus:outline-none focus:ring-1 focus:ring-[#163B32]"
                        />
                      </div>
                    </div>
                  )}

                  <div>
                    <label className="text-xs font-bold text-[#163B32] block mb-1">
                      Job Description & Communications
                    </label>
                    <textarea
                      rows={6}
                      value={pastedText}
                      onChange={(e) => setPastedText(e.target.value)}
                      placeholder="Paste full job description, recruiter messages, or emails here..."
                      className="w-full p-3 text-xs rounded-xl bg-white border border-[#E4E4DA] focus:outline-none focus:ring-1 focus:ring-[#163B32] font-sans"
                    />
                  </div>

                  <button
                    type="submit"
                    disabled={evaluating}
                    className="w-full py-2.5 px-4 rounded-xl bg-[#163B32] text-white text-xs font-semibold hover:bg-[#102C26] transition flex items-center justify-center gap-2 shadow-sm disabled:opacity-50"
                  >
                    {evaluating ? (
                      <>
                        <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                        <span>Evaluating Signals...</span>
                      </>
                    ) : (
                      <>
                        <ShieldCheck className="w-4 h-4 text-[#79B9AC]" />
                        <span>Analyze Listing Risk</span>
                      </>
                    )}
                  </button>
                </form>
              )}
            </div>
          </div>

          {/* Right Column (7 cols): Assessment Results Breakdown */}
          <div className="lg:col-span-7">
            {result ? (
              <div className="glass-panel p-6 space-y-6">
                {/* Triage Tier Banner */}
                <div className={`p-5 rounded-2xl border flex flex-col sm:flex-row sm:items-center justify-between gap-4 ${
                  result.risk_tier === 'Elevated risk indicators'
                    ? 'bg-red-50/80 border-red-300 text-red-950'
                    : result.risk_tier === 'Needs verification'
                    ? 'bg-amber-50/80 border-amber-300 text-amber-950'
                    : 'bg-emerald-50/80 border-emerald-300 text-emerald-950'
                }`}>
                  <div>
                    <span className="text-[10px] font-bold uppercase tracking-wider block opacity-75">
                      Preliminary Risk Triage
                    </span>
                    <h3 className="text-xl font-bold mt-0.5">{result.risk_tier}</h3>
                    <p className="text-xs mt-1 leading-relaxed opacity-90">{result.summary}</p>
                  </div>
                  <div className="text-center sm:text-right flex-shrink-0">
                    <span className="text-3xl font-extrabold">{result.risk_score}</span>
                    <span className="text-xs font-semibold block opacity-75">/ 100 Risk Index</span>
                  </div>
                </div>

                {/* Warning Signals */}
                <div>
                  <h4 className="text-xs font-bold uppercase tracking-wider text-[#163B32] mb-3">
                    Observed Warning Signals ({result.signals?.length || 0})
                  </h4>
                  {result.signals && result.signals.length > 0 ? (
                    <div className="space-y-3">
                      {result.signals.map((sig: any, idx: number) => {
                        const isExpanded = !!expandedSignals[idx];
                        return (
                          <div 
                            key={idx} 
                            className="p-4 rounded-xl bg-white border border-[#E4E4DA] text-xs space-y-2 shadow-sm"
                          >
                            <div 
                              onClick={() => setExpandedSignals({ ...expandedSignals, [idx]: !isExpanded })}
                              className="flex items-center justify-between cursor-pointer"
                            >
                              <div className="flex items-center gap-2">
                                <span className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded-full ${
                                  sig.severity === 'critical' ? 'bg-red-100 text-red-800' : 'bg-amber-100 text-amber-800'
                                }`}>
                                  {sig.severity}
                                </span>
                                <span className="font-bold text-[#163B32]">{sig.title}</span>
                              </div>
                              {isExpanded ? <ChevronUp className="w-4 h-4 text-[#69756E]" /> : <ChevronDown className="w-4 h-4 text-[#69756E]" />}
                            </div>

                            {isExpanded && (
                              <div className="pt-2 border-t border-[#E4E4DA] space-y-2 text-[#202823]">
                                <p className="text-[#69756E]">{sig.description}</p>
                                
                                {sig.evidence_excerpt && (
                                  <div className="p-2.5 rounded-lg bg-black/5 font-mono text-[11px] border border-black/5">
                                    <span className="text-[10px] uppercase font-bold text-[#69756E] block mb-0.5 font-sans">
                                      Verbatim Evidence Excerpt:
                                    </span>
                                    "{sig.evidence_excerpt}"
                                  </div>
                                )}

                                <div className="p-2.5 rounded-lg bg-[#DCE9E0]/40 border border-[#79B9AC]/30">
                                  <span className="text-[10px] uppercase font-bold text-[#163B32] block mb-0.5">
                                    Recommended Candidate Next Action:
                                  </span>
                                  <p className="text-xs font-medium text-[#163B32]">{sig.recommended_action}</p>
                                </div>
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  ) : (
                    <div className="p-4 rounded-xl bg-emerald-50/60 border border-emerald-200 text-xs text-emerald-900 flex items-center gap-2">
                      <CheckCircle className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                      <span>No suspicious payment, domain, or timeline anomalies detected in this submission.</span>
                    </div>
                  )}
                </div>

                {/* Positive Signals */}
                {result.positive_signals && result.positive_signals.length > 0 && (
                  <div>
                    <h4 className="text-xs font-bold uppercase tracking-wider text-[#163B32] mb-2">
                      Reassuring Signals Observed
                    </h4>
                    <div className="space-y-1.5">
                      {result.positive_signals.map((p: any, i: number) => (
                        <div key={i} className="flex items-center gap-2 text-xs text-[#163B32]">
                          <CheckCircle className="w-3.5 h-3.5 text-emerald-600 flex-shrink-0" />
                          <span><strong>{p.title}:</strong> {p.description}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Unknown Signals */}
                {result.unknown_signals && result.unknown_signals.length > 0 && (
                  <div className="p-3.5 rounded-xl bg-gray-50 border border-gray-200 text-xs text-gray-700 space-y-1">
                    <span className="font-bold text-[#163B32] block mb-1">Information Requiring Independent Verification:</span>
                    {result.unknown_signals.map((u: string, i: number) => (
                      <p key={i} className="text-[11px]">• {u}</p>
                    ))}
                  </div>
                )}
              </div>
            ) : (
              <div className="glass-panel p-12 text-center text-[#69756E] space-y-3">
                <ShieldCheck className="w-12 h-12 text-[#79B9AC] mx-auto opacity-70" />
                <h3 className="text-base font-bold text-[#163B32]">Awaiting Listing Input</h3>
                <p className="text-xs max-w-sm mx-auto">
                  Paste a job listing description or choose a test preset on the left to inspect multi-signal scam indicators with verbatim evidence.
                </p>
              </div>
            )}
          </div>
        </div>
      ) : (
        /* Benchmark Evaluation Tab */
        <div className="glass-panel p-6 md:p-8 space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-[#E4E4DA]">
            <div>
              <h2 className="text-lg font-bold text-[#163B32]">
                Scam Evaluation Benchmark Model Performance
              </h2>
              <p className="text-xs text-[#69756E] mt-0.5">
                Evaluated against 42 labeled benchmark cases (25 suspicious / ambiguous scenarios and 17 verified legitimate postings).
              </p>
            </div>
            <button
              onClick={loadBenchmark}
              disabled={benchmarkLoading}
              className="px-4 py-2 rounded-xl bg-[#163B32] text-white text-xs font-semibold hover:bg-[#102C26] transition flex items-center gap-2 shadow-sm"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${benchmarkLoading ? 'animate-spin' : ''}`} />
              <span>Re-run Benchmark</span>
            </button>
          </div>

          {benchmarkData && (
            <div className="space-y-6">
              {/* Metrics Grid */}
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                <div className="p-4 rounded-xl bg-white border border-[#E4E4DA] text-center">
                  <span className="text-[10px] font-bold uppercase text-[#69756E] block mb-1">Accuracy</span>
                  <span className="text-2xl font-bold text-[#163B32]">{benchmarkData.metrics?.accuracy}%</span>
                </div>
                <div className="p-4 rounded-xl bg-white border border-[#E4E4DA] text-center">
                  <span className="text-[10px] font-bold uppercase text-[#69756E] block mb-1">Precision</span>
                  <span className="text-2xl font-bold text-[#163B32]">{benchmarkData.metrics?.precision}%</span>
                </div>
                <div className="p-4 rounded-xl bg-white border border-[#E4E4DA] text-center">
                  <span className="text-[10px] font-bold uppercase text-[#69756E] block mb-1">Recall</span>
                  <span className="text-2xl font-bold text-[#163B32]">{benchmarkData.metrics?.recall}%</span>
                </div>
                <div className="p-4 rounded-xl bg-white border border-[#E4E4DA] text-center">
                  <span className="text-[10px] font-bold uppercase text-[#69756E] block mb-1">False Positives</span>
                  <span className="text-2xl font-bold text-[#C47B54]">{benchmarkData.metrics?.false_positive_rate}%</span>
                </div>
                <div className="p-4 rounded-xl bg-white border border-[#E4E4DA] text-center">
                  <span className="text-[10px] font-bold uppercase text-[#69756E] block mb-1">F1-Score</span>
                  <span className="text-2xl font-bold text-[#163B32]">{benchmarkData.metrics?.f1_score}%</span>
                </div>
              </div>

              {/* 2x2 Confusion Matrix */}
              <div className="p-5 rounded-2xl bg-white border border-[#E4E4DA]">
                <h3 className="text-xs font-bold uppercase tracking-wider text-[#163B32] mb-3">
                  Binary Confusion Matrix (Suspicious vs Legitimate)
                </h3>
                <div className="grid grid-cols-2 gap-3 max-w-md">
                  <div className="p-3.5 rounded-xl bg-emerald-50 border border-emerald-200">
                    <span className="text-[10px] uppercase font-bold text-emerald-800 block">True Positives (TP)</span>
                    <span className="text-xl font-bold text-emerald-950">{benchmarkData.confusion_matrix?.true_positives}</span>
                    <p className="text-[10px] text-emerald-700 mt-0.5">Scams correctly flagged as elevated/needs verification</p>
                  </div>
                  <div className="p-3.5 rounded-xl bg-red-50 border border-red-200">
                    <span className="text-[10px] uppercase font-bold text-red-800 block">False Positives (FP)</span>
                    <span className="text-xl font-bold text-red-950">{benchmarkData.confusion_matrix?.false_positives}</span>
                    <p className="text-[10px] text-red-700 mt-0.5">Legitimate jobs flagged as suspicious</p>
                  </div>
                  <div className="p-3.5 rounded-xl bg-orange-50 border border-orange-200">
                    <span className="text-[10px] uppercase font-bold text-orange-800 block">False Negatives (FN)</span>
                    <span className="text-xl font-bold text-orange-950">{benchmarkData.confusion_matrix?.false_negatives}</span>
                    <p className="text-[10px] text-orange-700 mt-0.5">Scams missed as lower risk</p>
                  </div>
                  <div className="p-3.5 rounded-xl bg-emerald-50 border border-emerald-200">
                    <span className="text-[10px] uppercase font-bold text-emerald-800 block">True Negatives (TN)</span>
                    <span className="text-xl font-bold text-emerald-950">{benchmarkData.confusion_matrix?.true_negatives}</span>
                    <p className="text-[10px] text-emerald-700 mt-0.5">Legitimate postings correctly cleared</p>
                  </div>
                </div>
              </div>

              {/* Sample Case Runs */}
              <div>
                <h3 className="text-xs font-bold uppercase tracking-wider text-[#163B32] mb-3">
                  Individual Benchmark Evaluations (First 10 of {benchmarkData.dataset_size})
                </h3>
                <div className="space-y-2">
                  {benchmarkData.sample_evaluations?.slice(0, 10).map((c: any) => (
                    <div key={c.id} className="p-3 rounded-xl bg-white border border-[#E4E4DA] text-xs flex items-center justify-between">
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-[10px] px-1.5 py-0.5 rounded bg-gray-100 font-bold">{c.id}</span>
                          <span className="font-bold text-[#163B32]">{c.title}</span>
                          <span className="text-[#69756E]">· {c.employer}</span>
                        </div>
                        <div className="flex items-center gap-2 text-[10px] text-[#69756E] mt-0.5">
                          <span>Ground Truth: <strong>{c.true_label}</strong></span>
                          <span>→</span>
                          <span>Predicted: <strong>{c.predicted_tier}</strong></span>
                        </div>
                      </div>
                      <span className={`text-[10px] font-bold px-2.5 py-1 rounded-full ${
                        c.correct ? 'bg-emerald-100 text-emerald-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {c.correct ? 'CORRECT' : 'INCORRECT'}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
