import React from 'react';
import { Play, Info, ChevronRight } from 'lucide-react';
import type { PublishedCatalog, PublishedShow } from '../types';
import { ImageWithFallback } from '../components/ImageWithFallback';

interface HomePageProps {
  catalog: PublishedCatalog | null;
  loading: boolean;
  onSelectShow: (show: PublishedShow) => void;
}

export const HomePage: React.FC<HomePageProps> = ({ catalog, loading, onSelectShow }) => {
  if (loading) {
    return (
      <div className="viewer-loading-screen">
        <div className="spinner" />
        <span>Loading Peblo TV Catalogue...</span>
      </div>
    );
  }

  if (!catalog || Object.keys(catalog.sections || {}).length === 0) {
    return (
      <div className="viewer-empty-screen">
        <h2>Catalogue Updating</h2>
        <p>Check back shortly! The editorial team is preparing new shows.</p>
      </div>
    );
  }

  // Pick first show from 'featured' or first section as Hero
  const sections = catalog.sections;
  const sectionKeys = Object.keys(sections);
  const featuredSection = sections['featured'] || sections[sectionKeys[0]] || [];
  const heroShow: PublishedShow | undefined = featuredSection[0];

  return (
    <div className="home-page">
      {/* Featured Hero (uses BANNER artwork) */}
      {heroShow && (
        <section className="hero-banner">
          <div className="hero-backdrop-container">
            <ImageWithFallback
              src={heroShow.artwork?.banner}
              fallbackTitle={heroShow.title}
              aspect="banner"
              className="hero-img"
            />
            <div className="hero-gradient-overlay" />
          </div>

          <div className="hero-content">
            <span className="hero-badge">FEATURED STREAMING</span>
            <h1 className="hero-title">{heroShow.title}</h1>
            <p className="hero-synopsis">{heroShow.synopsis || 'Explore exciting new adventures!'}</p>
            <div className="hero-tags">
              {heroShow.categories?.map((c) => (
                <span key={c} className="hero-tag">#{c}</span>
              ))}
            </div>

            <div className="hero-actions">
              <button className="btn-hero-primary" onClick={() => onSelectShow(heroShow)}>
                <Play fill="currentColor" size={18} />
                <span>Watch Now</span>
              </button>
              <button className="btn-hero-secondary" onClick={() => onSelectShow(heroShow)}>
                <Info size={18} />
                <span>More Info</span>
              </button>
            </div>
          </div>
        </section>
      )}

      {/* Horizontal Rows Grouped by Section (uses POSTER artwork) */}
      <div className="section-rows-container">
        {Object.entries(sections).map(([sectionName, shows]) => {
          if (!shows || shows.length === 0) return null;

          return (
            <section key={sectionName} className="row-section">
              <div className="row-header">
                <h2 className="row-title">
                  {sectionName.toUpperCase()}
                  <ChevronRight size={18} className="row-icon" />
                </h2>
              </div>

              <div className="horizontal-row">
                {shows.map((show) => (
                  <div
                    key={show.id}
                    className="show-poster-card"
                    onClick={() => onSelectShow(show)}
                  >
                    <ImageWithFallback
                      src={show.artwork?.poster}
                      fallbackTitle={show.title}
                      aspect="poster"
                      className="poster-img"
                    />
                    <div className="poster-card-overlay">
                      <h4 className="poster-title">{show.title}</h4>
                      <span className="poster-seasons">{show.seasons?.length || 0} Season(s)</span>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          );
        })}
      </div>
    </div>
  );
};
