export interface CollapsedEpisode {
  content_group: string;
  episode_number: number;
  title: string;
  duration_seconds: number | null;
  languages: string[];
  artwork: Record<string, string>;
  episode_ids: string[];
}

export interface SeasonGroup {
  season_number: number;
  episodes: CollapsedEpisode[];
}

export interface Trailer {
  episode_id: string;
  title: string;
  duration_seconds: number | null;
  language: string;
  artwork: Record<string, string>;
}

export interface PublishedShow {
  id: string;
  title: string;
  slug: string;
  section: string;
  categories: string[];
  synopsis: string | null;
  artwork: Record<string, string>; // poster, banner
  seasons: SeasonGroup[];
  trailers: Trailer[];
}

export interface PublishedCatalog {
  published_at: string | null;
  total_shows: number;
  total_episodes: number;
  sections: Record<string, PublishedShow[]>;
}

export interface SearchResultItem {
  content_group: string;
  episode_id: string;
  episode_title: string;
  show_id: string;
  show_title: string;
  show_slug: string;
  section: string;
  categories: string[];
  synopsis: string | null;
  season_number: number;
  episode_number: number;
  duration_seconds: number | null;
  languages: string[];
  artwork: Record<string, string>;
  show_artwork: Record<string, string>;
}

export interface SearchResponse {
  query: Record<string, string | null>;
  total_results: number;
  results: SearchResultItem[];
}
