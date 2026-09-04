import React, { useState } from 'react';
import { Upload, CheckCircle2, AlertCircle, Image as ImageIcon } from 'lucide-react';
import { uploadArtwork } from '../services/api';
import type { Artwork } from '../types';

interface ArtworkSlotProps {
  episodeId: string;
  artworkType: 'poster' | 'banner' | 'thumbnail';
  existingArtwork?: Artwork;
  specText: string;
  aspectDesc: string;
  onUploaded: () => void;
}

export const ArtworkSlot: React.FC<ArtworkSlotProps> = ({
  episodeId,
  artworkType,
  existingArtwork,
  specText,
  aspectDesc,
  onUploaded,
}) => {
  const [preview, setPreview] = useState<string | null>(existingArtwork?.url ? `http://localhost:8000${existingArtwork.url}` : null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const localUrl = URL.createObjectURL(file);
    setPreview(localUrl);
    setError(null);
    setSuccess(false);
    setUploading(true);

    try {
      await uploadArtwork(episodeId, artworkType, file);
      setSuccess(true);
      setError(null);
      onUploaded();
    } catch (err: any) {
      setError(err.message || 'Upload failed');
      setSuccess(false);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="artwork-slot-card">
      <div className="slot-header">
        <span className="slot-title">{artworkType.toUpperCase()}</span>
        <span className="slot-spec">{specText}</span>
      </div>
      <div className="slot-aspect">{aspectDesc}</div>

      <div className="slot-preview-area">
        {preview ? (
          <img src={preview} alt={`${artworkType} preview`} className="slot-img-preview" />
        ) : (
          <div className="slot-placeholder">
            <ImageIcon size={32} />
            <span>No image</span>
          </div>
        )}
      </div>

      <div className="slot-actions">
        <label className="upload-btn">
          <Upload size={14} />
          <span>{uploading ? 'Uploading...' : existingArtwork || preview ? 'Replace' : 'Upload'}</span>
          <input
            type="file"
            accept="image/jpeg,image/png,image/webp"
            disabled={uploading}
            onChange={handleFileChange}
            style={{ display: 'none' }}
          />
        </label>
        {success && (
          <span className="status-badge success">
            <CheckCircle2 size={14} /> Validated
          </span>
        )}
      </div>

      {error && (
        <div className="slot-error-msg">
          <AlertCircle size={14} />
          <span>{error}</span>
        </div>
      )}
    </div>
  );
};
