import React, { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Navbar } from './components/Navbar';
import { EpisodesPage } from './pages/EpisodesPage';
import { ShowsPage } from './pages/ShowsPage';
import { PublishPage } from './pages/PublishPage';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'episodes' | 'shows' | 'publish'>('episodes');
  const [role, setRole] = useState<'admin' | 'editor'>('admin');

  return (
    <QueryClientProvider client={queryClient}>
      <div className="cms-app">
        <Navbar
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          role={role}
          onRoleChange={setRole}
        />
        <main className="main-content">
          {activeTab === 'episodes' && <EpisodesPage />}
          {activeTab === 'shows' && <ShowsPage />}
          {activeTab === 'publish' && <PublishPage role={role} />}
        </main>
      </div>
    </QueryClientProvider>
  );
};

export default App;
