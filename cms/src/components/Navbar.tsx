import React from 'react';
import { Film, CheckSquare, Layers, Shield, UserCheck } from 'lucide-react';
import { setRole } from '../services/api';

interface NavbarProps {
  activeTab: 'episodes' | 'shows' | 'publish';
  setActiveTab: (tab: 'episodes' | 'shows' | 'publish') => void;
  role: 'admin' | 'editor';
  onRoleChange: (newRole: 'admin' | 'editor') => void;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab, role, onRoleChange }) => {
  const toggleRole = () => {
    const nextRole = role === 'admin' ? 'editor' : 'admin';
    setRole(nextRole);
    onRoleChange(nextRole);
  };

  return (
    <header className="cms-navbar">
      <div className="nav-brand">
        <Film className="brand-icon" size={24} />
        <div>
          <span className="brand-title">PEBLO TV</span>
          <span className="brand-subtitle">Editorial CMS</span>
        </div>
      </div>

      <nav className="nav-links">
        <button
          className={`nav-btn ${activeTab === 'episodes' ? 'active' : ''}`}
          onClick={() => setActiveTab('episodes')}
        >
          <Film size={16} />
          <span>Episodes & Artwork</span>
        </button>
        <button
          className={`nav-btn ${activeTab === 'shows' ? 'active' : ''}`}
          onClick={() => setActiveTab('shows')}
        >
          <Layers size={16} />
          <span>Shows & Sections</span>
        </button>
        <button
          className={`nav-btn ${activeTab === 'publish' ? 'active' : ''}`}
          onClick={() => setActiveTab('publish')}
        >
          <CheckSquare size={16} />
          <span>Validation & Publish</span>
        </button>
      </nav>

      <div className="nav-user">
        <button className={`role-badge ${role}`} onClick={toggleRole} title="Click to toggle Role for testing">
          {role === 'admin' ? <Shield size={14} /> : <UserCheck size={14} />}
          <span>Role: <strong>{role.toUpperCase()}</strong></span>
        </button>
      </div>
    </header>
  );
};
