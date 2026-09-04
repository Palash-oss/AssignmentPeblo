import React, { useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { Plus, Search, Filter, Edit3 } from 'lucide-react';
import { fetchEpisodes, fetchShows } from '../services/api';
import type { Episode } from '../types';
import { EpisodeFormModal } from '../components/EpisodeFormModal';

export const EpisodesPage: React.FC = () => {
  const queryClient = useQueryClient();

  const [search, setSearch] = useState('');
  const [section, setSection] = useState('');
  const [status, setStatus] = useState('');
  const [language, setLanguage] = useState('');
  const [page, setPage] = useState(1);

  const [selectedEp, setSelectedEp] = useState<Episode | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const { data: showsData } = useQuery({
    queryKey: ['shows'],
    queryFn: () => fetchShows(),
  });

  const { data: episodesData, isLoading, isError, error } = useQuery({
    queryKey: ['episodes', search, section, status, language, page],
    queryFn: () =>
      fetchEpisodes({
        search,
        section,
        status,
        language,
        page,
        limit: 15,
      }),
  });

  const handleEdit = (ep: Episode) => {
    setSelectedEp(ep);
    setIsModalOpen(true);
  };

  const handleCreate = () => {
    setSelectedEp(null);
    setIsModalOpen(true);
  };

  const handleSaved = () => {
    setIsModalOpen(false);
    queryClient.invalidateQueries({ queryKey: ['episodes'] });
    queryClient.invalidateQueries({ queryKey: ['validation-report'] });
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h2>Episodes & Artwork Management</h2>
          <p className="page-desc">Upload artwork, edit episode details, and manage publication statuses.</p>
        </div>
        <button className="btn-primary" onClick={handleCreate}>
          <Plus size={16} />
          <span>New Episode</span>
        </button>
      </div>

      <div className="filter-bar">
        <div className="search-input-wrapper">
          <Search size={16} className="search-icon" />
          <input
            type="text"
            placeholder="Search by title, show, or content_group..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        <div className="filter-group">
          <Filter size={14} />
          <select value={section} onChange={(e) => setSection(e.target.value)}>
            <option value="">All Sections</option>
            <option value="featured">Featured</option>
            <option value="series">Series</option>
            <option value="minisodes">Minisodes</option>
            <option value="songs">Songs</option>
          </select>

          <select value={status} onChange={(e) => setStatus(e.target.value)}>
            <option value="">All Statuses</option>
            <option value="published">Published</option>
            <option value="draft">Draft</option>
          </select>

          <select value={language} onChange={(e) => setLanguage(e.target.value)}>
            <option value="">All Languages</option>
            <option value="en">English (en)</option>
            <option value="hi">Hindi (hi)</option>
          </select>
        </div>
      </div>

      {isLoading ? (
        <div className="state-box">Loading episodes...</div>
      ) : isError ? (
        <div className="state-box error">Error loading episodes: {(error as Error).message}</div>
      ) : !episodesData?.items || episodesData.items.length === 0 ? (
        <div className="state-box empty">No episodes found matching selected filters.</div>
      ) : (
        <div className="table-responsive">
          <table className="cms-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Show Title</th>
                <th>S / Ep</th>
                <th>Episode Title</th>
                <th>Lang</th>
                <th>Content Group</th>
                <th>Duration</th>
                <th>Artwork (P / B / T)</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {episodesData.items.map((ep) => {
                const artTypes = ep.artworks?.map((a) => a.artwork_type) || [];
                const hasPoster = artTypes.includes('poster');
                const hasBanner = artTypes.includes('banner');
                const hasThumb = artTypes.includes('thumbnail');

                return (
                  <tr key={ep.id}>
                    <td className="font-mono text-xs">{ep.id}</td>
                    <td className="font-medium">{ep.show_title}</td>
                    <td>S{ep.season_number} E{ep.episode_number}</td>
                    <td>{ep.episode_title}</td>
                    <td><span className="lang-tag">{ep.language.toUpperCase()}</span></td>
                    <td className="font-mono text-xs">{ep.content_group}</td>
                    <td>{ep.duration_seconds ? `${ep.duration_seconds}s` : <span className="text-warn">Missing</span>}</td>
                    <td>
                      <div className="art-indicators">
                        <span className={`art-dot ${hasPoster ? 'ok' : 'missing'}`} title="Poster">P</span>
                        <span className={`art-dot ${hasBanner ? 'ok' : 'missing'}`} title="Banner">B</span>
                        <span className={`art-dot ${hasThumb ? 'ok' : 'missing'}`} title="Thumbnail">T</span>
                      </div>
                    </td>
                    <td>
                      <span className={`status-pill ${ep.status}`}>
                        {ep.status}
                      </span>
                    </td>
                    <td>
                      <button className="btn-table-action" onClick={() => handleEdit(ep)}>
                        <Edit3 size={14} />
                        <span>Edit</span>
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {episodesData && episodesData.total > 15 && (
        <div className="pagination-bar">
          <span>Showing page {page} of {Math.ceil(episodesData.total / 15)} ({episodesData.total} items)</span>
          <div className="pag-buttons">
            <button disabled={page === 1} onClick={() => setPage((p) => p - 1)}>Previous</button>
            <button disabled={page * 15 >= episodesData.total} onClick={() => setPage((p) => p + 1)}>Next</button>
          </div>
        </div>
      )}

      {isModalOpen && (
        <EpisodeFormModal
          episode={selectedEp}
          shows={showsData || []}
          onClose={() => setIsModalOpen(false)}
          onSaved={handleSaved}
        />
      )}
    </div>
  );
};
