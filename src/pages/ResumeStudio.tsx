import React, { useState, useEffect } from 'react';
import { 
  FileText, 
  ShieldCheck, 
  Eye, 
  Share2, 
  Lock, 
  Unlock, 
  Copy, 
  Check, 
  Plus, 
  Ban, 
  AlertCircle,
  ExternalLink
} from 'lucide-react';
import { api } from '../api/client';
import { useAuth } from '../context/AuthContext';

export const ResumeStudio: React.FC = () => {
  const { user } = useAuth();
  const [versions, setVersions] = useState<any[]>([]);
  const [sharedRecords, setSharedRecords] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // Active preview
  const [selectedResumeId, setSelectedResumeId] = useState<string | null>(null);
  const [previewContent, setPreviewContent] = useState<any | null>(null);

  // New Version Modal
  const [showModal, setShowModal] = useState(false);
  const [versionName, setVersionName] = useState('');
  const [targetEmployer, setTargetEmployer] = useState('');
  const [isRedacted, setIsRedacted] = useState(false);

  // Share Modal
  const [showShareModal, setShowShareModal] = useState(false);
  const [shareEmployerName, setShareEmployerName] = useState('');
  const [contactVisibility, setContactVisibility] = useState('redacted');
  const [sharingResumeId, setSharingResumeId] = useState<string | null>(null);

  const fetchResumes = async () => {
    try {
      setLoading(true);
      const res = await api.resumes.list();
      setVersions(res.versions || []);
      setSharedRecords(res.shared_records || []);
      if (res.versions?.length > 0 && !selectedResumeId) {
        loadContent(res.versions[0].id);
      }
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const loadContent = async (id: string) => {
    try {
      setSelectedResumeId(id);
      const content = await api.resumes.getContent(id);
      setPreviewContent(content);
    } catch (err: any) {
      alert(err.message || 'Failed to load resume content');
    }
  };

  useEffect(() => {
    fetchResumes();
  }, [user]);

  const handleCreateVersion = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!versionName) return;
    try {
      await api.resumes.generate({
        version_name: versionName,
        target_employer: targetEmployer,
        is_redacted: isRedacted,
        redacted_fields: isRedacted ? ['phone', 'email', 'full_name'] : [],
      });
      setShowModal(false);
      setVersionName('');
      setTargetEmployer('');
      setIsRedacted(false);
      await fetchResumes();
    } catch (err: any) {
      alert(err.message || 'Failed to create resume version');
    }
  };

  const handleShareSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!sharingResumeId || !shareEmployerName) return;
    try {
      const res = await api.resumes.share(sharingResumeId, shareEmployerName, contactVisibility);
      alert(`Consent-based share created! Share token: ${res.share_token}`);
      setShowShareModal(false);
      setShareEmployerName('');
      setSharingResumeId(null);
      await fetchResumes();
    } catch (err: any) {
      alert(err.message || 'Failed to share resume');
    }
  };

  const handleRevoke = async (shareId: string) => {
    if (!confirm('Are you sure you want to revoke employer access to this resume version?')) return;
    try {
      const res = await api.resumes.revoke(shareId);
      alert(res.message);
      await fetchResumes();
    } catch (err: any) {
      alert(err.message || 'Failed to revoke access');
    }
  };

  return (
    <div className="space-y-6">
      {/* Editorial Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#DCE9E0] text-[#163B32] text-xs font-semibold mb-2 border border-[#79B9AC]/40">
            <ShieldCheck className="w-3.5 h-3.5 text-[#163B32]" />
            <span>Candidate Data Sovereignty</span>
          </div>
          <h1 className="text-2xl md:text-3xl font-bold text-[#163B32] tracking-tight">
            Resume Studio & Consent-Based Sharing
          </h1>
          <p className="text-sm text-[#69756E] mt-1 max-w-2xl">
            Tailor employer-specific resume drafts, toggle candidate privacy redactions, and maintain an immutable ledger of third-party access with instant revocation.
          </p>
        </div>

        <button
          onClick={() => setShowModal(true)}
          className="px-4 py-2 rounded-xl bg-[#163B32] text-white text-xs font-semibold hover:bg-[#102C26] transition flex items-center gap-2 shadow-sm self-start sm:self-auto"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>New Tailored Version</span>
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column (5 cols): Versions List & Sharing Ledger */}
        <div className="lg:col-span-5 space-y-6">
          {/* Versions List */}
          <div className="glass-panel p-5 space-y-3">
            <h3 className="text-xs font-bold uppercase tracking-wider text-[#163B32]">
              Resume Versions ({versions.length})
            </h3>
            {versions.length > 0 ? (
              <div className="space-y-2">
                {versions.map((ver) => (
                  <div
                    key={ver.id}
                    onClick={() => loadContent(ver.id)}
                    className={`p-3.5 rounded-xl border text-xs cursor-pointer transition flex items-center justify-between ${
                      selectedResumeId === ver.id
                        ? 'bg-white border-[#163B32] shadow-sm'
                        : 'bg-white/60 hover:bg-white/90 border-[#E4E4DA]'
                    }`}
                  >
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-[#163B32]">{ver.version_name}</span>
                        {ver.is_redacted && (
                          <span className="text-[9px] font-bold px-1.5 py-0.2 rounded bg-purple-100 text-purple-800">
                            Redacted
                          </span>
                        )}
                      </div>
                      <p className="text-[10px] text-[#69756E] mt-0.5">
                        {ver.target_employer ? `Target: ${ver.target_employer}` : 'General Purpose'}
                      </p>
                    </div>

                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setSharingResumeId(ver.id);
                        setShowShareModal(true);
                      }}
                      className="px-2.5 py-1 rounded-lg bg-[#DCE9E0] text-[#163B32] hover:bg-[#cbe0d0] text-[11px] font-semibold flex items-center gap-1 transition"
                    >
                      <Share2 className="w-3 h-3" />
                      <span>Share</span>
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <div className="py-6 text-center text-xs text-[#69756E]">
                No customized resume versions yet. Click "New Tailored Version" above.
              </div>
            )}
          </div>

          {/* Access Ledger */}
          <div className="glass-panel p-5 space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold uppercase tracking-wider text-[#163B32]">
                Employer Access Ledger ({sharedRecords.length})
              </h3>
              <span className="text-[10px] text-[#69756E]">Revocable at any time</span>
            </div>

            {sharedRecords.length > 0 ? (
              <div className="space-y-2.5">
                {sharedRecords.map((sr) => (
                  <div key={sr.id} className="p-3 rounded-xl bg-white border border-[#E4E4DA] text-xs space-y-1.5 shadow-sm">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-[#163B32]">{sr.employer_name}</span>
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                        sr.status === 'active' ? 'bg-emerald-100 text-emerald-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {sr.status}
                      </span>
                    </div>

                    <div className="flex items-center justify-between text-[10px] text-[#69756E]">
                      <span>Visibility: <strong className="capitalize">{sr.contact_visibility}</strong></span>
                      <span>Shared: {sr.shared_at ? new Date(sr.shared_at).toLocaleDateString() : 'N/A'}</span>
                    </div>

                    {sr.status === 'active' && (
                      <div className="pt-2 border-t border-[#E4E4DA] flex items-center justify-between">
                        <span className="text-[10px] font-mono text-gray-500 truncate max-w-[150px]">
                          Token: {sr.share_token}
                        </span>
                        <button
                          onClick={() => handleRevoke(sr.id)}
                          className="text-[11px] font-semibold text-red-700 hover:text-red-900 flex items-center gap-1"
                        >
                          <Ban className="w-3 h-3" />
                          <span>Revoke Access</span>
                        </button>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-[#69756E] text-center py-4">
                No active external shares. Your profile and resumes remain 100% private.
              </p>
            )}
          </div>
        </div>

        {/* Right Column (7 cols): Clean Document Preview */}
        <div className="lg:col-span-7">
          {previewContent ? (
            <div className="glass-panel p-8 bg-white border border-[#E4E4DA] space-y-6 shadow-sm">
              {/* Header */}
              <div className="border-b border-[#E4E4DA] pb-5">
                <div className="flex items-start justify-between">
                  <div>
                    <h2 className="text-2xl font-bold text-[#163B32] font-editorial">
                      {previewContent.content?.header?.name}
                    </h2>
                    <p className="text-xs font-semibold text-[#79B9AC] mt-0.5">
                      {previewContent.content?.header?.headline}
                    </p>
                  </div>
                  {previewContent.content?.header?.is_redacted && (
                    <span className="text-[10px] font-bold px-2 py-1 rounded bg-purple-100 text-purple-900 border border-purple-200">
                      Anonymized Preview Mode
                    </span>
                  )}
                </div>

                <div className="flex flex-wrap gap-3 text-xs text-[#69756E] mt-2">
                  <span>{previewContent.content?.header?.email}</span>
                  <span>·</span>
                  <span>{previewContent.content?.header?.phone}</span>
                </div>
              </div>

              {/* Summary */}
              {previewContent.content?.summary && (
                <div>
                  <h4 className="text-xs font-bold uppercase tracking-wider text-[#163B32] mb-1.5">Professional Summary</h4>
                  <p className="text-xs text-[#202823] leading-relaxed">
                    {previewContent.content.summary}
                  </p>
                </div>
              )}

              {/* Verified Projects */}
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-[#163B32] mb-2.5">
                  Demonstrated Project Evidence
                </h4>
                <div className="space-y-3">
                  {previewContent.content?.projects?.map((proj: any) => (
                    <div key={proj.id} className="text-xs space-y-1">
                      <div className="flex items-center justify-between">
                        <strong className="text-[#163B32]">{proj.title}</strong>
                        <span className="text-[10px] text-[#69756E]">{proj.role}</span>
                      </div>
                      <p className="text-[#69756E] leading-relaxed">{proj.description}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Skills */}
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-[#163B32] mb-2">Verified Skillset</h4>
                <div className="flex flex-wrap gap-1.5">
                  {previewContent.content?.skills?.map((sk: any, i: number) => (
                    <span key={i} className="text-[10px] font-semibold px-2 py-0.5 rounded bg-[#DCE9E0] text-[#163B32]">
                      {sk.canonical_name} ({sk.proficiency_level})
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="glass-panel p-12 text-center text-[#69756E]">
              <FileText className="w-12 h-12 text-[#79B9AC] mx-auto opacity-70 mb-2" />
              <p className="text-xs">Select a resume version to preview layout</p>
            </div>
          )}
        </div>
      </div>

      {/* New Version Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass-modal max-w-md w-full p-6 space-y-4">
            <h3 className="font-bold text-sm text-[#163B32]">Create Tailored Resume Version</h3>
            <form onSubmit={handleCreateVersion} className="space-y-3">
              <div>
                <label className="text-xs font-bold text-[#163B32] block mb-1">Version Label</label>
                <input
                  type="text"
                  value={versionName}
                  onChange={(e) => setVersionName(e.target.value)}
                  placeholder="e.g. Meridian Health — Full Stack Version"
                  className="w-full px-3 py-2 text-xs rounded-xl bg-white border border-[#E4E4DA]"
                  required
                />
              </div>
              <div>
                <label className="text-xs font-bold text-[#163B32] block mb-1">Target Employer (Optional)</label>
                <input
                  type="text"
                  value={targetEmployer}
                  onChange={(e) => setTargetEmployer(e.target.value)}
                  placeholder="e.g. Meridian Health Technologies"
                  className="w-full px-3 py-2 text-xs rounded-xl bg-white border border-[#E4E4DA]"
                />
              </div>
              <div className="p-3 rounded-xl bg-[#F6F3EC] border border-[#E4E4DA] space-y-1.5">
                <label className="flex items-center gap-2 text-xs font-semibold text-[#163B32] cursor-pointer">
                  <input
                    type="checkbox"
                    checked={isRedacted}
                    onChange={(e) => setIsRedacted(e.target.checked)}
                    className="w-4 h-4 rounded text-[#163B32]"
                  />
                  <span>Enable Privacy Redaction (Anonymized)</span>
                </label>
                <p className="text-[10px] text-[#69756E] pl-6">
                  Masks phone, email, and full name. Employer communicates through Careerloom secure relay.
                </p>
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-3.5 py-1.5 rounded-lg text-xs font-medium text-[#69756E]"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-1.5 rounded-lg bg-[#163B32] text-white text-xs font-semibold hover:bg-[#102C26]"
                >
                  Save Draft Version
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Share Modal */}
      {showShareModal && (
        <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass-modal max-w-md w-full p-6 space-y-4">
            <h3 className="font-bold text-sm text-[#163B32]">Grant Employer Access</h3>
            <p className="text-xs text-[#69756E]">
              Create a revocable access token tied to a specific employer identity.
            </p>
            <form onSubmit={handleShareSubmit} className="space-y-3">
              <div>
                <label className="text-xs font-bold text-[#163B32] block mb-1">Employer / Organization Name</label>
                <input
                  type="text"
                  value={shareEmployerName}
                  onChange={(e) => setShareEmployerName(e.target.value)}
                  placeholder="e.g. Meridian Health Technologies"
                  className="w-full px-3 py-2 text-xs rounded-xl bg-white border border-[#E4E4DA]"
                  required
                />
              </div>
              <div>
                <label className="text-xs font-bold text-[#163B32] block mb-1">Contact Visibility Level</label>
                <select
                  value={contactVisibility}
                  onChange={(e) => setContactVisibility(e.target.value)}
                  className="w-full px-3 py-2 text-xs rounded-xl bg-white border border-[#E4E4DA]"
                >
                  <option value="redacted">Redacted (Contact via Platform Relay)</option>
                  <option value="email_only">Email Only</option>
                  <option value="full">Full Contact (Name, Phone & Email)</option>
                </select>
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowShareModal(false)}
                  className="px-3.5 py-1.5 rounded-lg text-xs font-medium text-[#69756E]"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-1.5 rounded-lg bg-[#163B32] text-white text-xs font-semibold hover:bg-[#102C26]"
                >
                  Confirm & Generate Share Token
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
