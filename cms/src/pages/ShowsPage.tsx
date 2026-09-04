import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchShows } from '../services/api';
import { Layers, Tags } from 'lucide-react';

export const ShowsPage: React.FC = () => {
  const { data: shows, isLoading, isError, error } = useQuery({
    queryKey: ['shows'],
    queryFn: () => fetchShows(),
  });

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h2>Shows & Sections Catalogue</h2>
          <p className="page-desc">Overview of shows, assigned sections, and category tags.</p>
        </div>
      </div>

      {isLoading ? (
        <div className="state-box">Loading shows...</div>
      ) : isError ? (
        <div className="state-box error">Error loading shows: {(error as Error).message}</div>
      ) : (
        <div className="shows-grid">
          {shows?.map((show) => (
            <div key={show.id} className="show-card">
              <div className="show-card-header">
                <div className="show-title-group">
                  <Layers className="text-primary" size={20} />
                  <h3>{show.title}</h3>
                </div>
                <span className={`section-badge ${show.section || 'none'}`}>
                  {show.section ? show.section.toUpperCase() : 'NO SECTION'}
                </span>
              </div>
              <p className="show-synopsis">{show.synopsis || 'No synopsis provided.'}</p>
              <div className="show-card-footer">
                <div className="cat-tags">
                  <Tags size={12} />
                  {show.categories?.map((cat) => (
                    <span key={cat} className="cat-pill">{cat}</span>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
