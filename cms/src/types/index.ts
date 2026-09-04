export interface Artwork {
  id: string;
  episode_id: string;
  artwork_type: 'poster' | 'banner' | 'thumbnail';
  url: string;
  width: number;
  height: number;
  file_size_kb: number;
}

export interface Episode {
  id: string;
  show_id: string;
  show_title: string;
  section: string | null;
  season_number: number;
  episode_number: number;
  episode_title: string;
  duration_seconds: number | null;
  language: string;
  content_group: string;
  status: 'published' | 'draft';
  artworks: Artwork[];
}

export interface Show {
  id: string;
  title: string;
  slug: string;
  section: string | null;
  categories: string[];
  synopsis: string | null;
  created_at: string;
  episodes?: Episode[];
}

export interface ValidationIssue {
  episode_id?: string;
  show_id?: string;
  show_title?: string;
  episode_title?: string;
  missing_artwork?: string[];
  section?: string | null;
  content_group?: string;
  language?: string;
  episode_ids?: string[];
  message: string;
}

export interface ValidationReport {
  is_publishable: boolean;
  total_issues: number;
  issues_by_category: {
    missing_artwork: ValidationIssue[];
    missing_duration: ValidationIssue[];
    missing_section: ValidationIssue[];
    duplicate_content_group_language: ValidationIssue[];
  };
}

export interface PublishRun {
  id: string;
  published_at: string;
  published_by: string;
  status: 'success' | 'failed';
  item_counts: Record<string, number>;
  error_summary: string | null;
}
