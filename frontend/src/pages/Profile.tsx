import React, { useState, useEffect } from 'react';
import { 
  User as UserIcon, 
  Briefcase, 
  GraduationCap, 
  FolderGit2, 
  Award, 
  Plus, 
  Trash2, 
  CheckCircle2, 
  ExternalLink,
  Edit3,
  Save,
  X
} from 'lucide-react';
import { api } from '../api/client';
import { useAuth } from '../context/AuthContext';

export const Profile: React.FC = () => {
  const { user } = useAuth();
  const [profile, setProfile] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const [editingInfo, setEditingInfo] = useState(false);

  // Form states
  const [headline, setHeadline] = useState('');
  const [summary, setSummary] = useState('');
  const [preferredRole, setPreferredRole] = useState('');
  const [preferredLocation, setPreferredLocation] = useState('');
  const [workArrangement, setWorkArrangement] = useState('remote');
  const [phone, setPhone] = useState('');
  const [portfolioUrl, setPortfolioUrl] = useState('');
  const [githubUrl, setGithubUrl] = useState('');

  // Add Skill Modal
  const [showSkillModal, setShowSkillModal] = useState(false);
  const [newSkillName, setNewSkillName] = useState('');
  const [newSkillProficiency, setNewSkillProficiency] = useState('Intermediate');

  // Add Project Modal
  const [showProjectModal, setShowProjectModal] = useState(false);
  const [projTitle, setProjTitle] = useState('');
  const [projDesc, setProjDesc] = useState('');
  const [projSkills, setProjSkills] = useState('');
  const [projRepo, setProjRepo] = useState('');
  const [projDemo, setProjDemo] = useState('');

  const fetchProfile = async () => {
    try {
      setLoading(true);
      const data = await api.profile.get();
      setProfile(data);
      setHeadline(data.headline || '');
      setSummary(data.summary || '');
      setPreferredRole(data.preferred_role || '');
      setPreferredLocation(data.preferred_location || '');
      setWorkArrangement(data.work_arrangement || 'remote');
      setPhone(data.phone || '');
      setPortfolioUrl(data.portfolio_url || '');
      setGithubUrl(data.github_url || '');
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProfile();
  }, [user]);

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.profile.update({
        headline,
        summary,
        preferred_role: preferredRole,
        preferred_location: preferredLocation,
        work_arrangement: workArrangement,
        phone,
        portfolio_url: portfolioUrl,
        github_url: githubUrl,
      });
      setEditingInfo(false);
      await fetchProfile();
    } catch (err: any) {
      alert(err.message || 'Failed to update profile');
    }
  };

  const handleAddSkill = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newSkillName) return;
    try {
      await api.profile.addSkill({
        skill_name: newSkillName,
        proficiency_level: newSkillProficiency,
        category: 'Technical',
      });
      setShowSkillModal(false);
      setNewSkillName('');
      await fetchProfile();
    } catch (err: any) {
      alert(err.message || 'Failed to add skill');
    }
  };

  const handleDeleteSkill = async (id: string) => {
    try {
      await api.profile.deleteSkill(id);
      await fetchProfile();
    } catch (err: any) {
      alert(err.message || 'Failed to delete skill');
    }
  };

  const handleAddProject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!projTitle || !projDesc) return;
    try {
      const skillsArr = projSkills.split(',').map((s) => s.trim()).filter(Boolean);
      await api.profile.addProject({
        title: projTitle,
        description: projDesc,
        skills_used: skillsArr,
        repo_url: projRepo,
        demo_url: projDemo,
      });
      setShowProjectModal(false);
      setProjTitle('');
      setProjDesc('');
      setProjSkills('');
      setProjRepo('');
      setProjDemo('');
      await fetchProfile();
    } catch (err: any) {
      alert(err.message || 'Failed to add project');
    }
  };

  const handleDeleteProject = async (id: string) => {
    try {
      await api.profile.deleteProject(id);
      await fetchProfile();
    } catch (err: any) {
      alert(err.message || 'Failed to delete project');
    }
  };

  if (loading) {
    return <div className="p-8 text-center text-xs text-[#69756E]">Loading candidate profile...</div>;
  }

  return (
    <div className="space-y-8">
      {/* Editorial Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#DCE9E0] text-[#163B32] text-xs font-semibold mb-2 border border-[#79B9AC]/40">
            <UserIcon className="w-3.5 h-3.5 text-[#163B32]" />
            <span>Candidate Dossier</span>
          </div>
          <h1 className="text-2xl md:text-3xl font-bold text-[#163B32] tracking-tight">
            My Profile & Evidence Vault
          </h1>
          <p className="text-sm text-[#69756E] mt-1">
            Every skill claim is backed by projects or document source records. Manually add, edit, or remove claims at any time.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="p-3 rounded-xl bg-white border border-[#E4E4DA] text-right">
            <span className="text-[10px] font-bold uppercase text-[#69756E] block">Completeness</span>
            <span className="text-base font-bold text-[#163B32]">{profile?.completeness_percentage}%</span>
          </div>
          <button
            onClick={() => setEditingInfo(!editingInfo)}
            className="px-4 py-2 rounded-xl bg-[#163B32] text-white text-xs font-semibold hover:bg-[#102C26] transition flex items-center gap-1.5 shadow-sm"
          >
            <Edit3 className="w-3.5 h-3.5" />
            <span>{editingInfo ? 'Cancel' : 'Edit Bio'}</span>
          </button>
        </div>
      </div>

      {/* Main Profile Info Card */}
      <div className="glass-panel p-6">
        {editingInfo ? (
          <form onSubmit={handleSaveProfile} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="text-xs font-bold text-[#163B32] block mb-1">Headline</label>
                <input
                  type="text"
                  value={headline}
                  onChange={(e) => setHeadline(e.target.value)}
                  className="w-full px-3 py-2 text-xs rounded-xl bg-white border border-[#E4E4DA]"
                />
              </div>
              <div>
                <label className="text-xs font-bold text-[#163B32] block mb-1">Target Role</label>
                <input
                  type="text"
                  value={preferredRole}
                  onChange={(e) => setPreferredRole(e.target.value)}
                  className="w-full px-3 py-2 text-xs rounded-xl bg-white border border-[#E4E4DA]"
                />
              </div>
              <div>
                <label className="text-xs font-bold text-[#163B32] block mb-1">Preferred Location</label>
                <input
                  type="text"
                  value={preferredLocation}
                  onChange={(e) => setPreferredLocation(e.target.value)}
                  className="w-full px-3 py-2 text-xs rounded-xl bg-white border border-[#E4E4DA]"
                />
              </div>
              <div>
                <label className="text-xs font-bold text-[#163B32] block mb-1">Work Arrangement</label>
                <select
                  value={workArrangement}
                  onChange={(e) => setWorkArrangement(e.target.value)}
                  className="w-full px-3 py-2 text-xs rounded-xl bg-white border border-[#E4E4DA]"
                >
                  <option value="remote">Remote</option>
                  <option value="hybrid">Hybrid</option>
                  <option value="onsite">Onsite</option>
                </select>
              </div>
              <div>
                <label className="text-xs font-bold text-[#163B32] block mb-1">GitHub URL</label>
                <input
                  type="url"
                  value={githubUrl}
                  onChange={(e) => setGithubUrl(e.target.value)}
                  className="w-full px-3 py-2 text-xs rounded-xl bg-white border border-[#E4E4DA]"
                />
              </div>
              <div>
                <label className="text-xs font-bold text-[#163B32] block mb-1">Portfolio Website</label>
                <input
                  type="url"
                  value={portfolioUrl}
                  onChange={(e) => setPortfolioUrl(e.target.value)}
                  className="w-full px-3 py-2 text-xs rounded-xl bg-white border border-[#E4E4DA]"
                />
              </div>
            </div>

            <div>
              <label className="text-xs font-bold text-[#163B32] block mb-1">Executive Summary</label>
              <textarea
                rows={3}
                value={summary}
                onChange={(e) => setSummary(e.target.value)}
                className="w-full p-3 text-xs rounded-xl bg-white border border-[#E4E4DA]"
              />
            </div>

            <div className="flex justify-end gap-2">
              <button
                type="button"
                onClick={() => setEditingInfo(false)}
                className="px-4 py-2 rounded-xl bg-black/5 text-[#202823] text-xs font-semibold"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-5 py-2 rounded-xl bg-[#163B32] text-white text-xs font-semibold hover:bg-[#102C26]"
              >
                Save Changes
              </button>
            </div>
          </form>
        ) : (
          <div className="space-y-4">
            <div>
              <h2 className="text-xl font-bold text-[#163B32]">{profile?.full_name}</h2>
              <p className="text-xs font-semibold text-[#79B9AC] mt-0.5">{profile?.headline}</p>
              <p className="text-xs text-[#69756E] mt-2 leading-relaxed">{profile?.summary}</p>
            </div>

            <div className="flex flex-wrap gap-4 pt-3 border-t border-[#E4E4DA] text-xs text-[#202823]">
              <div>
                <span className="text-[#69756E] text-[10px] block uppercase font-bold">Email</span>
                <span className="font-medium">{profile?.email}</span>
              </div>
              <div>
                <span className="text-[#69756E] text-[10px] block uppercase font-bold">Target Arrangement</span>
                <span className="font-medium capitalize">{profile?.work_arrangement}</span>
              </div>
              <div>
                <span className="text-[#69756E] text-[10px] block uppercase font-bold">Target Location</span>
                <span className="font-medium">{profile?.preferred_location || 'Flexible'}</span>
              </div>
              {profile?.github_url && (
                <div>
                  <span className="text-[#69756E] text-[10px] block uppercase font-bold">GitHub</span>
                  <a href={profile.github_url} target="_blank" rel="noreferrer" className="text-[#163B32] underline font-medium">
                    {profile.github_url.replace('https://', '')}
                  </a>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Skills Section */}
      <div className="glass-panel p-6 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-base font-bold text-[#163B32]">Skills & Verifiable Evidence</h3>
            <p className="text-xs text-[#69756E]">Distinguishes project-backed skills from self-reported claims</p>
          </div>
          <button
            onClick={() => setShowSkillModal(true)}
            className="px-3 py-1.5 rounded-lg bg-[#DCE9E0] text-[#163B32] text-xs font-semibold hover:bg-[#cbe0d0] flex items-center gap-1 transition"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Add Skill</span>
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
          {profile?.skills?.map((s: any) => (
            <div key={s.id} className="p-3 rounded-xl bg-white border border-[#E4E4DA] text-xs flex items-center justify-between">
              <div>
                <span className="font-bold text-[#163B32]">{s.canonical_name}</span>
                <div className="flex items-center gap-1.5 text-[10px] text-[#69756E] mt-0.5">
                  <span>{s.proficiency_level}</span>
                  <span>·</span>
                  <span className={`font-semibold ${s.verified_status === 'project_verified' ? 'text-emerald-700' : 'text-gray-600'}`}>
                    {s.verified_status === 'project_verified' ? '✓ Project Evidence' : 'Self-Reported'}
                  </span>
                </div>
              </div>
              <button
                onClick={() => handleDeleteSkill(s.id)}
                className="text-[#69756E] hover:text-red-700 p-1"
                title="Remove Skill"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Projects Section */}
      <div className="glass-panel p-6 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-base font-bold text-[#163B32]">Substantiated Projects</h3>
            <p className="text-xs text-[#69756E]">Tangible proof of execution backing your skill claims</p>
          </div>
          <button
            onClick={() => setShowProjectModal(true)}
            className="px-3 py-1.5 rounded-lg bg-[#163B32] text-white text-xs font-semibold hover:bg-[#102C26] flex items-center gap-1 transition"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Add Project</span>
          </button>
        </div>

        <div className="space-y-4">
          {profile?.projects?.map((p: any) => (
            <div key={p.id} className="p-4 rounded-xl bg-white border border-[#E4E4DA] text-xs space-y-2">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h4 className="font-bold text-sm text-[#163B32]">{p.title}</h4>
                  <p className="text-[#69756E] mt-1 leading-relaxed">{p.description}</p>
                </div>
                <button
                  onClick={() => handleDeleteProject(p.id)}
                  className="text-[#69756E] hover:text-red-700 p-1"
                  title="Remove Project"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>

              <div className="flex flex-wrap gap-1.5 pt-1">
                {p.skills_used?.map((sk: string) => (
                  <span key={sk} className="text-[10px] font-semibold px-2 py-0.5 rounded bg-[#DCE9E0] text-[#163B32]">
                    {sk}
                  </span>
                ))}
              </div>

              {(p.repo_url || p.demo_url) && (
                <div className="pt-2 border-t border-[#E4E4DA] flex items-center gap-3 text-[11px]">
                  {p.repo_url && (
                    <a href={p.repo_url} target="_blank" rel="noreferrer" className="text-[#163B32] font-semibold flex items-center gap-1 hover:underline">
                      <FolderGit2 className="w-3.5 h-3.5 text-[#79B9AC]" />
                      <span>Repository Code</span>
                    </a>
                  )}
                  {p.demo_url && (
                    <a href={p.demo_url} target="_blank" rel="noreferrer" className="text-[#163B32] font-semibold flex items-center gap-1 hover:underline">
                      <ExternalLink className="w-3.5 h-3.5 text-[#C47B54]" />
                      <span>Live Demo</span>
                    </a>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Add Skill Modal */}
      {showSkillModal && (
        <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass-modal max-w-sm w-full p-6 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-sm text-[#163B32]">Add Verified Skill</h3>
              <button onClick={() => setShowSkillModal(false)}><X className="w-4 h-4 text-[#69756E]" /></button>
            </div>
            <form onSubmit={handleAddSkill} className="space-y-3">
              <div>
                <label className="text-xs font-bold text-[#163B32] block mb-1">Skill Name</label>
                <input
                  type="text"
                  value={newSkillName}
                  onChange={(e) => setNewSkillName(e.target.value)}
                  placeholder="e.g. Kubernetes, React, Python"
                  className="w-full px-3 py-2 text-xs rounded-xl bg-white border border-[#E4E4DA]"
                  required
                />
              </div>
              <div>
                <label className="text-xs font-bold text-[#163B32] block mb-1">Proficiency Level</label>
                <select
                  value={newSkillProficiency}
                  onChange={(e) => setNewSkillProficiency(e.target.value)}
                  className="w-full px-3 py-2 text-xs rounded-xl bg-white border border-[#E4E4DA]"
                >
                  <option value="Beginner">Beginner</option>
                  <option value="Intermediate">Intermediate</option>
                  <option value="Advanced">Advanced</option>
                  <option value="Expert">Expert</option>
                </select>
              </div>
              <button
                type="submit"
                className="w-full py-2 rounded-xl bg-[#163B32] text-white text-xs font-semibold hover:bg-[#102C26]"
              >
                Add Skill
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Add Project Modal */}
      {showProjectModal && (
        <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass-modal max-w-md w-full p-6 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-sm text-[#163B32]">Add Project Evidence</h3>
              <button onClick={() => setShowProjectModal(false)}><X className="w-4 h-4 text-[#69756E]" /></button>
            </div>
            <form onSubmit={handleAddProject} className="space-y-3">
              <div>
                <label className="text-xs font-bold text-[#163B32] block mb-1">Project Title</label>
                <input
                  type="text"
                  value={projTitle}
                  onChange={(e) => setProjTitle(e.target.value)}
                  placeholder="e.g. Real-Time Telemetry Dashboard"
                  className="w-full px-3 py-2 text-xs rounded-xl bg-white border border-[#E4E4DA]"
                  required
                />
              </div>
              <div>
                <label className="text-xs font-bold text-[#163B32] block mb-1">Description</label>
                <textarea
                  rows={3}
                  value={projDesc}
                  onChange={(e) => setProjDesc(e.target.value)}
                  placeholder="What problem did you solve and what was the quantifiable outcome?"
                  className="w-full p-2.5 text-xs rounded-xl bg-white border border-[#E4E4DA]"
                  required
                />
              </div>
              <div>
                <label className="text-xs font-bold text-[#163B32] block mb-1">Skills Used (comma-separated)</label>
                <input
                  type="text"
                  value={projSkills}
                  onChange={(e) => setProjSkills(e.target.value)}
                  placeholder="e.g. Python, FastAPI, Docker, SQL"
                  className="w-full px-3 py-2 text-xs rounded-xl bg-white border border-[#E4E4DA]"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-bold text-[#163B32] block mb-1">GitHub Repo URL</label>
                  <input
                    type="url"
                    value={projRepo}
                    onChange={(e) => setProjRepo(e.target.value)}
                    placeholder="https://github.com/..."
                    className="w-full px-3 py-2 text-xs rounded-xl bg-white border border-[#E4E4DA]"
                  />
                </div>
                <div>
                  <label className="text-xs font-bold text-[#163B32] block mb-1">Live Demo URL</label>
                  <input
                    type="url"
                    value={projDemo}
                    onChange={(e) => setProjDemo(e.target.value)}
                    placeholder="https://..."
                    className="w-full px-3 py-2 text-xs rounded-xl bg-white border border-[#E4E4DA]"
                  />
                </div>
              </div>
              <button
                type="submit"
                className="w-full py-2 rounded-xl bg-[#163B32] text-white text-xs font-semibold hover:bg-[#102C26]"
              >
                Save Project
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
