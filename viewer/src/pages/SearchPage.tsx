import React, { useState, useEffect } from 'react';
import { Search, Filter, Play } from 'lucide-react';
import { searchCatalog } from '../services/api';
import type { SearchResponse, SearchResultItem } from '../types';
import { ImageWithFallback } from '../components/ImageWithFallback';

interface SearchPageProps {
  initialQuery?: string;
  onSelectShowById: (showId: string) => void;
}

export const SearchPage: React.FC<SearchPageProps> = ({ initialQuery = '', onSelectShowById }) => {
  const [q, setQ] = useState(initialQuery);
  const [category, setCategory] = useState('');
  const [language, setLanguage] = useState('');
  const [section, setSection] = useState('');

  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<SearchResponse | null>(null);

  useEffect(() => {
    let isMounted = true;
    setLoading(true);

    searchCatalog({ q, category, language, section })
      .then((res) => {
        if (isMounted) setData(res);
      })
      .catch(() => {
        if (isMounted) setData({ query: {}, total_results: 0, results: [] });
      })
      .finally(() => {
        if (isMounted) setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [q, category, language, section]);

  return (
    <div className="search-page">
      <div className="search-header-container">
        <h2>Browse & Search Catalogue</h2>

        <div className="search-controls-bar">
          <div className="search-main-input">
            <Search size={18} className="search-icon" />
            <input
              type="text"
              placeholder="Search by title, show, category..."
              value={q}
              onChange={(e) => setQ(e.target.value)}
            />
          </div>

          <div className="search-filters">
            <Filter size={16} />
            <select value={section} onChange={(e) => setSection(e.target.value)}>
              <option value="">All Sections</option>
              <option value="featured">Featured</option>
              <option value="series">Series</option>
              <option value="minisodes">Minisodes</option>
              <option value="songs">Songs</option>
            </select>

            <select value={category} onChange={(e) => setCategory(e.target.value)}>
              <option value="">All Categories</option>
              <option value="adventure">Adventure</option>
              <option value="india">India</option>
              <option value="friendship">Friendship</option>
              <option value="learning">Learning</option>
              <option value="maths">Maths</option>
              <option value="music">Music</option>
            </select>

            <select value={language} onChange={(e) => setLanguage(e.target.value)}>
              <option value="">All Languages</option>
              <option value="en">English (en)</option>
              <option value="hi">Hindi (hi)</option>
            </select>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="state-screen">
          <div className="spinner" />
          <span>Searching catalog...</span>
        </div>
      ) : !data || data.total_results === 0 ? (
        <div className="state-screen empty">
          <h3>No Results Found</h3>
          <p>
            {q || category || language || section
              ? `No catalog matches found for criteria: ${[q, category, language, section].filter(Boolean).join(', ')}. Try broadening your filters.`
              : 'Type a search term or select filters to browse the catalogue.'}
          </p>
        </div>
      ) : (
        <div className="search-results-grid">
          {data.results.map((item: SearchResultItem) => (
            <div
              key={item.content_group}
              className="search-card"
              onClick={() => onSelectShowById(item.show_id)}
            >
              <div className="search-card-thumb">
                <ImageWithFallback
                  src={item.artwork?.thumbnail || item.show_artwork?.poster}
                  fallbackTitle={item.show_title}
                  aspect="thumbnail"
                />
                <div className="hover-play">
                  <Play fill="#fff" size={20} />
                </div>
              </div>
              <div className="search-card-info">
                <span className="search-show-name">{item.show_title}</span>
                <h4 className="search-ep-name">{item.episode_title}</h4>
                <div className="search-meta">
                  <span>S{item.season_number} E{item.episode_number}</span>
                  <span className="search-langs">
                    {item.languages.map((l) => l.toUpperCase()).join(', ')}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
