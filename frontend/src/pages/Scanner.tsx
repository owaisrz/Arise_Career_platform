import React, { useState, useEffect } from 'react';
import { 
  UploadCloud, 
  FileText, 
  CheckCircle, 
  XCircle, 
  AlertTriangle, 
  Trash2, 
  RefreshCw, 
  Eye, 
  ShieldAlert, 
  ChevronRight,
  Info,
  Check,
  FileSearch
} from 'lucide-react';
import { api } from '../api/client';

export const Scanner: React.FC = () => {
  const [documents, setDocuments] = useState<any[]>([]);
  const [selectedDoc, setSelectedDoc] = useState<any | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadStage, setUploadStage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);

  const fetchDocuments = async () => {
    try {
      const docs = await api.documents.list();
      setDocuments(docs);
      if (docs.length > 0 && !selectedDoc) {
        loadDocDetails(docs[0].id);
      }
    } catch (err: any) {
      console.error(err);
    }
  };

  const loadDocDetails = async (id: string) => {
    try {
      const details = await api.documents.get(id);
      setSelectedDoc(details);
    } catch (err: any) {
      setError(err.message || 'Failed to load document details');
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const handleFileUpload = async (file: File) => {
    try {
      setUploading(true);
      setError(null);
      setUploadStage('VALIDATING (Size & Signatures)...');
      await new Promise((r) => setTimeout(r, 400));
      
      setUploadStage('EXTRACTING (Parsing Machine Text)...');
      await new Promise((r) => setTimeout(r, 400));
      
      setUploadStage('STRUCTURING (Attributing Claims & Sources)...');
      const uploaded = await api.documents.upload(file);
      
      setUploadStage('REVIEW REQUIRED');
      setSelectedDoc(uploaded);
      await fetchDocuments();
    } catch (err: any) {
      setError(err.message || 'Document processing failed.');
    } finally {
      setUploading(false);
      setUploadStage(null);
    }
  };

  const handleClaimAction = async (claimId: string, action: 'approve' | 'reject') => {
    try {
      await api.profile.claimAction(claimId, action);
      if (selectedDoc) {
        setSelectedDoc({
          ...selectedDoc,
          claims: selectedDoc.claims.map((c: any) =>
            c.id === claimId ? { ...c, status: action === 'approve' ? 'approved' : 'rejected' } : c
          ),
        });
      }
    } catch (err: any) {
      alert(err.message || 'Failed to update claim');
    }
  };

  const handleDeleteDoc = async (id: string) => {
    if (!confirm('Are you sure you want to permanently delete this document and its claims?')) return;
    try {
      await api.documents.delete(id);
      if (selectedDoc?.id === id) {
        setSelectedDoc(null);
      }
      await fetchDocuments();
    } catch (err: any) {
      alert(err.message || 'Failed to delete document');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#DCE9E0] text-[#163B32] text-xs font-semibold mb-2 border border-[#79B9AC]/40">
          <FileText className="w-3.5 h-3.5 text-[#163B32]" />
          <span>Evidence Extraction Pipeline</span>
        </div>
        <h1 className="text-2xl md:text-3xl font-bold text-[#163B32] tracking-tight">
          Document Scanner & Claim Verification
        </h1>
        <p className="text-sm text-[#69756E] mt-1">
          Upload resumes, transcripts, or project certificates. Every extracted skill is preserved with its original page number and verbatim excerpt.
        </p>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-red-800 text-xs flex items-center gap-3">
          <AlertTriangle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Two Column Workspace */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column (5 cols): Upload Zone & Past Documents */}
        <div className="lg:col-span-5 space-y-6">
          {/* Upload Drop Zone */}
          <div
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={(e) => {
              e.preventDefault();
              setDragOver(false);
              if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                handleFileUpload(e.dataTransfer.files[0]);
              }
            }}
            className={`glass-panel p-6 border-2 border-dashed transition-all text-center rounded-2xl ${
              dragOver ? 'border-[#163B32] bg-[#DCE9E0]/40' : 'border-[#79B9AC]/50 hover:border-[#163B32]'
            }`}
          >
            <div className="w-12 h-12 rounded-full bg-[#DCE9E0] mx-auto flex items-center justify-center text-[#163B32] mb-3">
              <UploadCloud className="w-6 h-6" />
            </div>
            <h3 className="text-sm font-bold text-[#163B32]">Drop your career document here</h3>
            <p className="text-xs text-[#69756E] mt-1 mb-4">
              Supports PDF, DOCX, TXT, PNG, JPG up to 15 MB
            </p>

            <label className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-[#163B32] text-white text-xs font-semibold hover:bg-[#102C26] cursor-pointer transition shadow-sm">
              <span>Browse Files</span>
              <input
                type="file"
                className="hidden"
                accept=".pdf,.docx,.txt,.png,.jpg,.jpeg"
                onChange={(e) => {
                  if (e.target.files && e.target.files[0]) {
                    handleFileUpload(e.target.files[0]);
                  }
                }}
              />
            </label>

            {uploading && (
              <div className="mt-4 p-3 rounded-xl bg-white/80 border border-[#E4E4DA]">
                <div className="flex items-center justify-center gap-2 text-xs font-medium text-[#163B32]">
                  <RefreshCw className="w-3.5 h-3.5 animate-spin text-[#79B9AC]" />
                  <span>{uploadStage || 'Processing document...'}</span>
                </div>
              </div>
            )}
          </div>

          {/* Uploaded Documents List */}
          <div className="glass-panel p-5">
            <h3 className="text-xs font-bold uppercase tracking-wider text-[#163B32] mb-3">
              Uploaded Documents ({documents.length})
            </h3>
            {documents.length > 0 ? (
              <div className="space-y-2 max-h-[350px] overflow-y-auto pr-1">
                {documents.map((doc) => (
                  <div
                    key={doc.id}
                    onClick={() => loadDocDetails(doc.id)}
                    className={`p-3 rounded-xl border text-xs cursor-pointer transition flex items-center justify-between ${
                      selectedDoc?.id === doc.id
                        ? 'bg-white border-[#163B32] shadow-sm'
                        : 'bg-white/60 hover:bg-white/90 border-[#E4E4DA]'
                    }`}
                  >
                    <div className="truncate pr-2">
                      <p className="font-semibold text-[#163B32] truncate">{doc.filename}</p>
                      <div className="flex items-center gap-2 text-[10px] text-[#69756E] mt-0.5">
                        <span className="uppercase">{doc.file_type}</span>
                        <span>·</span>
                        <span>{(doc.file_size / 1024).toFixed(0)} KB</span>
                        <span>·</span>
                        <span className="capitalize">{doc.extraction_quality}</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-1.5 flex-shrink-0">
                      <button
                        onClick={(e) => { e.stopPropagation(); handleDeleteDoc(doc.id); }}
                        className="p-1 text-[#69756E] hover:text-red-700 rounded transition"
                        title="Delete document"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-[#69756E] text-center py-4">No documents uploaded yet.</p>
            )}
          </div>
        </div>

        {/* Right Column (7 cols): Extracted Evidence & Claims Inspection */}
        <div className="lg:col-span-7">
          {selectedDoc ? (
            <div className="glass-panel p-6 space-y-6">
              {/* Document Header & Quality Badge */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-[#E4E4DA]">
                <div>
                  <h2 className="text-lg font-bold text-[#163B32] break-all">{selectedDoc.filename}</h2>
                  <div className="flex flex-wrap items-center gap-2 text-xs text-[#69756E] mt-1">
                    <span className="capitalize font-medium">Type: {selectedDoc.document_type}</span>
                    <span>·</span>
                    <span>{selectedDoc.page_count} page(s)</span>
                    <span>·</span>
                    <span>Status: {selectedDoc.status.replace(/_/g, ' ')}</span>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <span className={`text-xs font-bold px-3 py-1 rounded-full border ${
                    selectedDoc.extraction_quality === 'High'
                      ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
                      : selectedDoc.extraction_quality === 'Moderate'
                      ? 'bg-amber-50 text-amber-800 border-amber-200'
                      : 'bg-red-50 text-red-800 border-red-200'
                  }`}>
                    Quality: {selectedDoc.extraction_quality}
                  </span>
                </div>
              </div>

              {/* Extraction Warnings if any */}
              {selectedDoc.warnings && selectedDoc.warnings.length > 0 && (
                <div className="p-3.5 rounded-xl bg-amber-50 border border-amber-200 text-xs text-amber-900 space-y-1">
                  <div className="flex items-center gap-2 font-bold">
                    <ShieldAlert className="w-4 h-4 text-amber-700" />
                    <span>Extraction Warnings & Defensive Checks</span>
                  </div>
                  {selectedDoc.warnings.map((w: string, i: number) => (
                    <p key={i} className="text-[11px] pl-6">• {w}</p>
                  ))}
                </div>
              )}

              {/* Extracted Claims Section */}
              <div>
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-sm font-bold text-[#163B32]">
                    Extracted Claims with Verbatim Evidence ({selectedDoc.claims?.length || 0})
                  </h3>
                  <span className="text-[11px] text-[#69756E]">Review and approve into profile</span>
                </div>

                <div className="space-y-3">
                  {selectedDoc.claims && selectedDoc.claims.length > 0 ? (
                    selectedDoc.claims.map((claim: any) => (
                      <div
                        key={claim.id}
                        className={`p-4 rounded-xl border text-xs transition ${
                          claim.status === 'approved'
                            ? 'bg-emerald-50/70 border-emerald-300'
                            : claim.status === 'rejected'
                            ? 'bg-red-50/50 border-red-200 opacity-60'
                            : 'bg-white/80 border-[#E4E4DA]'
                        }`}
                      >
                        <div className="flex items-start justify-between gap-3">
                          <div>
                            <div className="flex items-center gap-2 mb-1">
                              <span className="uppercase text-[9px] font-bold tracking-wider px-2 py-0.5 rounded bg-[#DCE9E0] text-[#163B32]">
                                {claim.claim_type}
                              </span>
                              <span className="text-xs font-bold text-[#163B32]">
                                {claim.field_name}: {claim.raw_value}
                              </span>
                            </div>

                            {/* Source reference attribution */}
                            <div className="p-2.5 rounded-lg bg-black/5 text-[#202823] mt-2 font-mono text-[11px] leading-relaxed border border-black/5">
                              <span className="text-[10px] uppercase font-bold text-[#69756E] block mb-0.5 font-sans">
                                Verbatim Source Excerpt (Page {claim.page_number} · {claim.section_heading || 'Section'})
                              </span>
                              "{claim.text_excerpt || claim.raw_value}"
                            </div>
                          </div>

                          {/* Approval Actions */}
                          <div className="flex items-center gap-1.5 flex-shrink-0">
                            {claim.status === 'approved' ? (
                              <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-emerald-100 text-emerald-800 text-[11px] font-bold">
                                <Check className="w-3 h-3" />
                                <span>Approved</span>
                              </span>
                            ) : claim.status === 'rejected' ? (
                              <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-red-100 text-red-800 text-[11px] font-medium">
                                <span>Rejected</span>
                              </span>
                            ) : (
                              <>
                                <button
                                  onClick={() => handleClaimAction(claim.id, 'approve')}
                                  className="px-3 py-1.5 rounded-lg bg-[#163B32] text-white font-semibold hover:bg-[#102C26] transition flex items-center gap-1 text-[11px] shadow-sm"
                                >
                                  <Check className="w-3 h-3" />
                                  <span>Approve</span>
                                </button>
                                <button
                                  onClick={() => handleClaimAction(claim.id, 'reject')}
                                  className="px-2.5 py-1.5 rounded-lg bg-black/5 text-[#69756E] hover:text-red-700 hover:bg-red-50 transition text-[11px]"
                                >
                                  Reject
                                </button>
                              </>
                            )}
                          </div>
                        </div>
                      </div>
                    ))
                  ) : (
                    <p className="text-xs text-[#69756E] text-center py-6">
                      No claims extracted from this document. Ensure the file contains machine-readable text.
                    </p>
                  )}
                </div>
              </div>
            </div>
          ) : (
            <div className="glass-panel p-12 text-center text-[#69756E] space-y-3">
              <FileSearch className="w-12 h-12 text-[#79B9AC] mx-auto opacity-70" />
              <h3 className="text-base font-bold text-[#163B32]">No Document Selected</h3>
              <p className="text-xs max-w-sm mx-auto">
                Upload a resume or select an existing document on the left to inspect machine-extracted claims and approve verified evidence.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
