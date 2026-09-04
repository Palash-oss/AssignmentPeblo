import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { HomePage } from './pages/HomePage';
import { ShowDetailPage } from './pages/ShowDetailPage';
import { SearchPage } from './pages/SearchPage';
import { fetchPublishedCatalog } from './services/api';
import type { PublishedCatalog, PublishedShow } from './types';

export const App: React.FC = () => {
  const [currentView, setCurrentView] = useState<'home' | 'search' | 'show'>('home');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedShow, setSelectedShow] = useState<PublishedShow | null>(null);

  const [catalog, setCatalog] = useState<PublishedCatalog | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPublishedCatalog()
      .then((data) => setCatalog(data))
      .catch(() => setCatalog(null))
      .finally(() => setLoading(false));
  }, []);

  const handleSelectShow = (show: PublishedShow) => {
    setSelectedShow(show);
    setCurrentView('show');
  };

  const handleSelectShowById = (showId: string) => {
    if (!catalog?.sections) return;

    for (const shows of Object.values(catalog.sections)) {
      const match = shows.find((s) => s.id === showId);
      if (match) {
        setSelectedShow(match);
        setCurrentView('show');
        return;
      }
    }
  };

  const handleNavigateSearch = (query?: string) => {
    if (query !== undefined) setSearchQuery(query);
    setCurrentView('search');
  };

  return (
    <div className="viewer-app">
      <Navbar
        currentView={currentView}
        onNavigateHome={() => setCurrentView('home')}
        onNavigateSearch={handleNavigateSearch}
      />

      <main className="viewer-main-content">
        {currentView === 'home' && (
          <HomePage
            catalog={catalog}
            loading={loading}
            onSelectShow={handleSelectShow}
          />
        )}

        {currentView === 'show' && selectedShow && (
          <ShowDetailPage
            show={selectedShow}
            onBack={() => setCurrentView('home')}
          />
        )}

        {currentView === 'search' && (
          <SearchPage
            initialQuery={searchQuery}
            onSelectShowById={handleSelectShowById}
          />
        )}
      </main>
    </div>
  );
};

export default App;
