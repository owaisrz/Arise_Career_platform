import React, { useState, useEffect } from 'react';
import { 
  History, 
  ShieldCheck, 
  Clock, 
  RefreshCw,
  FileText
} from 'lucide-react';
import { api } from '../api/client';
import { useAuth } from '../context/AuthContext';

export const Audit: React.FC = () => {
  const { user } = useAuth();
  const [events, setEvents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchAuditHistory = async () => {
    try {
      setLoading(true);
      const res = await api.audit.history();
      setEvents(res);
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAuditHistory();
  }, [user]);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#DCE9E0] text-[#163B32] text-xs font-semibold mb-2 border border-[#79B9AC]/40">
            <History className="w-3.5 h-3.5 text-[#163B32]" />
            <span>Verifiable Accountability</span>
          </div>
          <h1 className="text-2xl md:text-3xl font-bold text-[#163B32] tracking-tight">
            Activity & Audit Ledger
          </h1>
          <p className="text-sm text-[#69756E] mt-1 max-w-2xl">
            A tamper-evident candidate log recording profile edits, document processing, evidence approvals, and consent revocations.
          </p>
        </div>

        <button
          onClick={fetchAuditHistory}
          disabled={loading}
          className="px-4 py-2 rounded-xl bg-white border border-[#E4E4DA] text-xs font-semibold text-[#163B32] hover:bg-gray-50 transition flex items-center gap-1.5 shadow-sm"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Ledger</span>
        </button>
      </div>

      <div className="glass-panel p-6">
        {loading ? (
          <div className="p-8 text-center text-xs text-[#69756E]">Loading audit events...</div>
        ) : events.length > 0 ? (
          <div className="space-y-3">
            {events.map((evt) => (
              <div
                key={evt.id}
                className="p-4 rounded-xl bg-white border border-[#E4E4DA] text-xs flex flex-col sm:flex-row sm:items-center justify-between gap-2 shadow-sm"
              >
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-[#163B32] capitalize">
                      {evt.event_type.replace(/_/g, ' ')}
                    </span>
                    <span className="text-[10px] text-[#69756E] font-mono">
                      (IP: {evt.ip_address})
                    </span>
                  </div>
                  {evt.details && Object.keys(evt.details).length > 0 && (
                    <div className="text-[11px] text-[#69756E] mt-1 font-mono">
                      {JSON.stringify(evt.details)}
                    </div>
                  )}
                </div>

                <div className="text-right text-[11px] text-[#69756E] flex-shrink-0 flex items-center gap-1">
                  <Clock className="w-3 h-3 text-[#79B9AC]" />
                  <span>{evt.created_at ? new Date(evt.created_at).toLocaleString() : 'N/A'}</span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="py-8 text-center text-xs text-[#69756E]">No audit events recorded yet.</div>
        )}
      </div>
    </div>
  );
};
