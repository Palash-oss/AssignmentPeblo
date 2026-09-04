import React, { useState } from 'react';
import { Tv, Search, Home } from 'lucide-react';

interface NavbarProps {
  currentView: 'home' | 'search' | 'show';
  onNavigateHome: () => void;
  onNavigateSearch: (query?: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentView,
  onNavigateHome,
  onNavigateSearch,
}) => {
  const [q, setQ] = useState('');

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (q.trim()) {
      onNavigateSearch(q.trim());
    }
  };

  return (
    <header className="viewer-navbar">
      <div className="nav-left">
        <div className="nav-logo" onClick={onNavigateHome}>
          <Tv className="logo-icon" size={28} />
          <span className="logo-text">PEBLO<span className="logo-accent">TV</span></span>
        </div>

        <nav className="viewer-nav-links">
          <button
            className={`nav-link ${currentView === 'home' ? 'active' : ''}`}
            onClick={onNavigateHome}
          >
            <Home size={16} /> Home
          </button>
          <button
            className={`nav-link ${currentView === 'search' ? 'active' : ''}`}
            onClick={() => onNavigateSearch()}
          >
            <Search size={16} /> Search & Browse
          </button>
        </nav>
      </div>

      <form onSubmit={handleSearchSubmit} className="nav-search-form">
        <div className="nav-search-input">
          <Search size={16} className="search-icon" />
          <input
            type="text"
            placeholder="Search shows, episodes, categories..."
            value={q}
            onChange={(e) => setQ(e.target.value)}
          />
        </div>
      </form>
    </header>
  );
};
