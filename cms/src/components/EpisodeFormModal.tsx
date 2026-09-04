import React, { useState } from 'react';
import { X, Save, AlertCircle } from 'lucide-react';
import type { Episode, Show } from '../types';
import { createEpisode, updateEpisode } from '../services/api';
import { ArtworkSlot } from './ArtworkSlot';

interface EpisodeFormModalProps {
  episode?: Episode | null;
  shows: Show[];
  onClose: () => void;
  onSaved: () => void;
}

export const EpisodeFormModal: React.FC<EpisodeFormModalProps> = ({
  episode,
  shows,
  onClose,
  onSaved,
}) => {
  const isEdit = !!episode;

  const [showId, setShowId] = useState(episode?.show_id || shows[0]?.id || '');
  const [seasonNumber, setSeasonNumber] = useState(episode?.season_number || 1);
  const [episodeNumber, setEpisodeNumber] = useState(episode?.episode_number || 1);
  const [episodeTitle, setEpisodeTitle] = useState(episode?.episode_title || '');
  const [durationSeconds, setDurationSeconds] = useState<string>(episode?.duration_seconds?.toString() || '300');
  const [language, setLanguage] = useState(episode?.language || 'en');
  const [contentGroup, setContentGroup] = useState(episode?.content_group || '');
  const [status, setStatus] = useState<'published' | 'draft'>(episode?.status || 'draft');

  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSaving(true);

    const dur = durationSeconds ? parseInt(durationSeconds, 10) : null;

    try {
      if (isEdit) {
        await updateEpisode(episode.id, {
          episode_title: episodeTitle,
          season_number: seasonNumber,
          duration_seconds: dur,
          language,
          content_group: contentGroup,
          status,
        });
      } else {
        await createEpisode({
          show_id: showId,
          season_number: seasonNumber,
          episode_number: episodeNumber,
          episode_title: episodeTitle,
          duration_seconds: dur,
          language,
          content_group: contentGroup,
          status,
        });
      }
      onSaved();
    } catch (err: any) {
      setError(err.message || 'Operation failed');
    } finally {
      setSaving(false);
    }
  };

  const getArt = (type: 'poster' | 'banner' | 'thumbnail') => {
    return episode?.artworks?.find((a) => a.artwork_type === type);
  };

  return (
    <div className="modal-backdrop">
      <div className="modal-container">
        <div className="modal-header">
          <h3>{isEdit ? `Edit Episode (${episode.id})` : 'Create New Episode'}</h3>
          <button className="icon-close-btn" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="modal-body">
          {error && (
            <div className="form-error-banner">
              <AlertCircle size={16} />
              <span>{error}</span>
            </div>
          )}

          <div className="form-grid">
            <div className="form-group">
              <label>Show</label>
              <select
                disabled={isEdit}
                value={showId}
                onChange={(e) => setShowId(e.target.value)}
                required
              >
                {shows.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.title}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Season Number (0 = Trailer)</label>
              <input
                type="number"
                min="0"
                value={seasonNumber}
                onChange={(e) => setSeasonNumber(parseInt(e.target.value) || 0)}
                required
              />
            </div>

            <div className="form-group">
              <label>Episode Number</label>
              <input
                type="number"
                min="1"
                value={episodeNumber}
                onChange={(e) => setEpisodeNumber(parseInt(e.target.value) || 1)}
                required
              />
            </div>

            <div className="form-group">
              <label>Episode Title</label>
              <input
                type="text"
                value={episodeTitle}
                onChange={(e) => setEpisodeTitle(e.target.value)}
                placeholder="e.g. The Lost Kite"
                required
              />
            </div>

            <div className="form-group">
              <label>Duration (Seconds)</label>
              <input
                type="number"
                min="1"
                value={durationSeconds}
                onChange={(e) => setDurationSeconds(e.target.value)}
                placeholder="e.g. 510"
              />
            </div>

            <div className="form-group">
              <label>Language</label>
              <select value={language} onChange={(e) => setLanguage(e.target.value)}>
                <option value="en">English (en)</option>
                <option value="hi">Hindi (hi)</option>
              </select>
            </div>

            <div className="form-group">
              <label>Content Group (collapses language variants)</label>
              <input
                type="text"
                value={contentGroup}
                onChange={(e) => setContentGroup(e.target.value)}
                placeholder="e.g. motis-many-lives-s01e01"
                required
              />
            </div>

            <div className="form-group">
              <label>Status</label>
              <select
                value={status}
                onChange={(e) => setStatus(e.target.value as 'published' | 'draft')}
              >
                <option value="draft">Draft</option>
                <option value="published">Published</option>
              </select>
            </div>
          </div>

          {isEdit ? (
            <div className="artwork-slots-section">
              <h4 className="section-subtitle">Episode Artwork Slots (All 3 required for publishing)</h4>
              <div className="artwork-slots-grid">
                <ArtworkSlot
                  episodeId={episode.id}
                  artworkType="poster"
                  existingArtwork={getArt('poster')}
                  specText="600×900 • 200KB Max"
                  aspectDesc="2:3 Portrait"
                  onUploaded={onSaved}
                />
                <ArtworkSlot
                  episodeId={episode.id}
                  artworkType="banner"
                  existingArtwork={getArt('banner')}
                  specText="1280×720 • 200KB Max"
                  aspectDesc="16:9 Landscape"
                  onUploaded={onSaved}
                />
                <ArtworkSlot
                  episodeId={episode.id}
                  artworkType="thumbnail"
                  existingArtwork={getArt('thumbnail')}
                  specText="640×360 • 200KB Max"
                  aspectDesc="16:9 Landscape"
                  onUploaded={onSaved}
                />
              </div>
            </div>
          ) : (
            <div className="info-banner">
              Save episode details first to unlock Artwork Upload slots.
            </div>
          )}

          <div className="modal-footer">
            <button type="button" className="btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn-primary" disabled={saving}>
              <Save size={16} />
              <span>{saving ? 'Saving...' : 'Save Episode'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
