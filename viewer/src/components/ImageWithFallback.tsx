import React, { useState } from 'react';
import { Film } from 'lucide-react';

interface ImageWithFallbackProps extends React.ImgHTMLAttributes<HTMLImageElement> {
  src?: string;
  fallbackTitle?: string;
  aspect?: 'poster' | 'banner' | 'thumbnail';
}

export const ImageWithFallback: React.FC<ImageWithFallbackProps> = ({
  src,
  alt = 'Media image',
  fallbackTitle = 'Peblo TV',
  aspect = 'poster',
  className = '',
  ...props
}) => {
  const [error, setError] = useState(false);

  const fullUrl = src ? (src.startsWith('http') ? src : `http://localhost:8000${src}`) : null;

  if (!fullUrl || error) {
    return (
      <div className={`img-fallback-box aspect-${aspect} ${className}`}>
        <Film size={28} className="fallback-icon" />
        <span className="fallback-title">{fallbackTitle}</span>
      </div>
    );
  }

  return (
    <div className={`img-wrapper aspect-${aspect} ${className}`}>
      <img
        src={fullUrl}
        alt={alt}
        onError={() => setError(true)}
        className="img-element"
        {...props}
      />
    </div>
  );
};
