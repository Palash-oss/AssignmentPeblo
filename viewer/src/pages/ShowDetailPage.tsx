import React, { useState } from 'react';
import { ArrowLeft, Play, Globe, Film } from 'lucide-react';
import type { PublishedShow, CollapsedEpisode } from '../types';
import { ImageWithFallback } from '../components/ImageWithFallback';

interface ShowDetailPageProps {
  show: PublishedShow;
  onBack: () => void;
}

export const ShowDetailPage: React.FC<ShowDetailPageProps> = ({ show, onBack }) => {
  // Season 0 trailers are explicitly excluded from standard season selector
  const realSeasons = show.seasons ? show.seasons.filter((s) => s.season_number > 0) : [];
  const trailers = show.trailers || [];

  const [activeSeasonNum, setActiveSeasonNum] = useState<number>(realSeasons[0]?.season_number || 1);
  const [selectedLanguages, setSelectedLanguages] = useState<Record<string, string>>({});
  const [activeEpisode, setActiveEpisode] = useState<CollapsedEpisode | null>(null);

  const currentSeason = realSeasons.find((s) => s.season_number === activeSeasonNum) || realSeasons[0];

  const handleLanguageSelect = (contentGroup: string, lang: string) => {
    setSelectedLanguages((prev) => ({ ...prev, [contentGroup]: lang }));
  };

  return (
    <div className="show-detail-page">
      <button className="btn-back" onClick={onBack}>
        <ArrowLeft size={18} />
        <span>Back to Catalogue</span>
      </button>

      {/* Show Header */}
      <div className="show-header-banner">
        <div className="show-backdrop">
          <ImageWithFallback
            src={show.artwork?.banner || show.artwork?.poster}
            fallbackTitle={show.title}
            aspect="banner"
            className="show-banner-img"
          />
          <div className="show-header-overlay" />
        </div>

        <div className="show-header-info">
          <span className="section-pill">{show.section.toUpperCase()}</span>
          <h1 className="show-main-title">{show.title}</h1>
          <p className="show-description">{show.synopsis || 'No synopsis available.'}</p>
          <div className="show-category-list">
            {show.categories?.map((cat) => (
              <span key={cat} className="category-pill">{cat}</span>
            ))}
          </div>

          {trailers.length > 0 && (
            <div className="show-trailer-box">
              <span className="trailer-title"><Film size={16} /> Official Trailer</span>
              <button
                className="btn-trailer"
                onClick={() =>
                  setActiveEpisode({
                    content_group: trailers[0].episode_id,
                    episode_number: 0,
                    title: trailers[0].title,
                    duration_seconds: trailers[0].duration_seconds,
                    languages: [trailers[0].language],
                    artwork: trailers[0].artwork,
                    episode_ids: [trailers[0].episode_id],
                  })
                }
              >
                <Play size={14} /> Watch Trailer ({trailers[0].title})
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Active Video Player Mock Modal */}
      {activeEpisode && (
        <div className="player-modal">
          <div className="player-content">
            <div className="player-header">
              <h3>Playing: {activeEpisode.title}</h3>
              <button className="btn-close-player" onClick={() => setActiveEpisode(null)}>✕</button>
            </div>
            <div className="player-screen">
              <ImageWithFallback
                src={activeEpisode.artwork?.thumbnail || activeEpisode.artwork?.banner}
                fallbackTitle={activeEpisode.title}
                aspect="banner"
              />
              <div className="player-overlay">
                <Play size={48} className="pulse-play" />
                <span>Streaming Episode Content...</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Season Tabs (Excludes Season 0 Trailers) */}
      <div className="seasons-container">
        <div className="season-tabs-header">
          <h3>Seasons</h3>
          <div className="season-tabs">
            {realSeasons.map((s) => (
              <button
                key={s.season_number}
                className={`season-tab ${s.season_number === activeSeasonNum ? 'active' : ''}`}
                onClick={() => setActiveSeasonNum(s.season_number)}
              >
                Season {s.season_number}
              </button>
            ))}
          </div>
        </div>

        {/* Episode Cards Grid (uses THUMBNAIL artwork) */}
        <div className="episodes-grid">
          {currentSeason?.episodes?.map((ep) => {
            const activeLang = selectedLanguages[ep.content_group] || ep.languages[0] || 'en';

            return (
              <div key={ep.content_group} className="episode-card">
                <div className="ep-thumb-container" onClick={() => setActiveEpisode(ep)}>
                  <ImageWithFallback
                    src={ep.artwork?.thumbnail || ep.artwork?.banner}
                    fallbackTitle={ep.title}
                    aspect="thumbnail"
                    className="ep-thumb-img"
                  />
                  <div className="ep-play-hover">
                    <Play fill="#fff" size={24} />
                  </div>
                  {ep.duration_seconds && (
                    <span className="ep-duration">{Math.floor(ep.duration_seconds / 60)}m</span>
                  )}
                </div>

                <div className="ep-details">
                  <div className="ep-title-row">
                    <span className="ep-num">E{ep.episode_number}</span>
                    <h4 className="ep-title">{ep.title}</h4>
                  </div>

                  {/* Language Selector for Collapsed Episode Variants */}
                  <div className="ep-language-row">
                    <span className="lang-label"><Globe size={12} /> Languages:</span>
                    <div className="lang-pills">
                      {ep.languages.map((lang) => (
                        <button
                          key={lang}
                          className={`lang-pill ${lang === activeLang ? 'active' : ''}`}
                          onClick={() => handleLanguageSelect(ep.content_group, lang)}
                        >
                          {lang.toUpperCase()}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
