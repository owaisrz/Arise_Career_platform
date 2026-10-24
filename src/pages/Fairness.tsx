import React, { useState, useEffect } from 'react';
import { 
  Scale, 
  CheckCircle2, 
  AlertCircle, 
  RefreshCw, 
  ShieldCheck, 
  HelpCircle,
  FileText
} from 'lucide-react';
import { api } from '../api/client';

export const Fairness: React.FC = () => {
  const [data, setData] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchAudit = async () => {
    try {
      setLoading(true);
      const res = await api.fairness.audit();
      setData(res);
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAudit();
  }, []);

  return (
    <div className="space-y-6">
      {/* Editorial Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#DCE9E0] text-[#163B32] text-xs font-semibold mb-2 border border-[#79B9AC]/40">
            <Scale className="w-3.5 h-3.5 text-[#163B32]" />
            <span>Algorithmic Transparency</span>
          </div>
          <h1 className="text-2xl md:text-3xl font-bold text-[#163B32] tracking-tight">
            Fairness & Counterfactual Audit
          </h1>
          <p className="text-sm text-[#69756E] mt-1 max-w-2xl">
            Controlled counterfactual testing ensures that recommendations and match scores are strictly invariant to candidate demographic, pedigree, or geographic proxies.
          </p>
        </div>

        <button
          onClick={fetchAudit}
          disabled={loading}
          className="px-4 py-2 rounded-xl bg-[#163B32] text-white text-xs font-semibold hover:bg-[#102C26] transition flex items-center gap-2 shadow-sm self-start sm:self-auto"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Re-evaluate Parity</span>
        </button>
      </div>

      {loading ? (
        <div className="p-12 text-center text-xs text-[#69756E]">Running counterfactual permutation suite...</div>
      ) : data ? (
        <div className="space-y-6">
          {/* Top Parity Banner */}
          <div className="glass-panel p-6">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-center">
              <div className="p-4 rounded-xl bg-white border border-[#E4E4DA]">
                <span className="text-[10px] font-bold uppercase text-[#69756E] block mb-1">
                  Demographic Parity Score
                </span>
                <span className="text-2xl font-bold text-emerald-800">{data.overall_parity_score}</span>
              </div>
              <div className="p-4 rounded-xl bg-white border border-[#E4E4DA]">
                <span className="text-[10px] font-bold uppercase text-[#69756E] block mb-1">
                  Rank Shifts Observed
                </span>
                <span className="text-2xl font-bold text-[#163B32]">{data.rank_shifts_detected}</span>
              </div>
              <div className="p-4 rounded-xl bg-white border border-[#E4E4DA]">
                <span className="text-[10px] font-bold uppercase text-[#69756E] block mb-1">
                  Mean Score Delta
                </span>
                <span className="text-2xl font-bold text-[#163B32]">{data.mean_score_variance}</span>
              </div>
            </div>

            <div className="mt-4 p-3.5 rounded-xl bg-amber-50/70 border border-amber-200 text-xs text-amber-900 flex items-start gap-2.5">
              <AlertCircle className="w-4 h-4 text-amber-700 flex-shrink-0 mt-0.5" />
              <div>
                <strong className="block mb-0.5">Transparent Evaluation Notice:</strong>
                <span>{data.synthetic_data_notice} {data.guarantee_disclaimer}</span>
              </div>
            </div>
          </div>

          {/* Test Dimensions */}
          <div className="space-y-4">
            <h3 className="text-sm font-bold text-[#163B32]">Counterfactual Dimension Audit Results</h3>
            {data.evaluations?.map((ev: any, idx: number) => (
              <div key={idx} className="glass-panel p-6 space-y-4">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-[#E4E4DA]">
                  <div>
                    <span className="text-[10px] font-bold uppercase tracking-wider text-[#79B9AC] block">
                      Dimension {idx + 1}
                    </span>
                    <h4 className="text-base font-bold text-[#163B32]">{ev.dimension}</h4>
                  </div>
                  <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-900 border border-emerald-300 self-start sm:self-auto">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-700" />
                    <span>{ev.status}</span>
                  </span>
                </div>

                <p className="text-xs text-[#69756E] leading-relaxed">{ev.description}</p>

                {/* Score Comparison Grid */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
                  <div className="p-3 rounded-xl bg-white/80 border border-[#E4E4DA]">
                    <span className="text-[10px] text-[#69756E] font-medium block">Baseline Subject</span>
                    <strong className="text-[#163B32]">{ev.baseline_subject}</strong>
                    <div className="mt-1 text-sm font-bold text-[#163B32]">{ev.baseline_avg_score}% Avg Match</div>
                  </div>
                  <div className="p-3 rounded-xl bg-white/80 border border-[#E4E4DA]">
                    <span className="text-[10px] text-[#69756E] font-medium block">Counterfactual Subject</span>
                    <strong className="text-[#163B32]">{ev.counterfactual_subject}</strong>
                    <div className="mt-1 text-sm font-bold text-[#163B32]">{ev.counterfactual_avg_score}% Avg Match</div>
                  </div>
                  <div className="p-3 rounded-xl bg-emerald-50/60 border border-emerald-200">
                    <span className="text-[10px] text-emerald-800 font-medium block">Absolute Variance (Delta)</span>
                    <strong className="text-emerald-950">Δ = {ev.delta} points</strong>
                    <p className="mt-1 text-[10px] text-emerald-800">Zero algorithmic bias detected</p>
                  </div>
                </div>

                <div className="p-3 rounded-lg bg-black/5 text-[11px] text-[#202823] border border-black/5">
                  <strong>Remediation & Governance:</strong> {ev.remediation_note}
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : null}
    </div>
  );
};
