import type { Episode, Show, ValidationReport, PublishRun } from '../types';

const API_BASE = 'http://localhost:8000';

let activeRole: 'admin' | 'editor' = 'admin';

export const setRole = (role: 'admin' | 'editor') => {
  activeRole = role;
};

export const getRole = (): 'admin' | 'editor' => activeRole;

const getHeaders = (extraHeaders: Record<string, string> = {}) => {
  return {
    'X-User-Role': activeRole,
    ...extraHeaders,
  };
};

export async function fetchShows(section?: string): Promise<Show[]> {
  const url = new URL(`${API_BASE}/admin/shows`);
  if (section) url.searchParams.append('section', section);
  const res = await fetch(url.toString(), { headers: getHeaders() });
  if (!res.ok) throw new Error('Failed to fetch shows');
  return res.json();
}

export async function fetchEpisodes(params: {
  show_id?: string;
  section?: string;
  status?: string;
  language?: string;
  search?: string;
  page?: number;
  limit?: number;
}): Promise<{ items: Episode[]; total: number; page: number; limit: number }> {
  const url = new URL(`${API_BASE}/admin/episodes`);
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== '') url.searchParams.append(k, String(v));
  });
  const res = await fetch(url.toString(), { headers: getHeaders() });
  if (!res.ok) throw new Error('Failed to fetch episodes');
  return res.json();
}

export async function createEpisode(payload: Partial<Episode>): Promise<Episode> {
  const res = await fetch(`${API_BASE}/admin/episodes`, {
    method: 'POST',
    headers: getHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify(payload),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || 'Failed to create episode');
  return data;
}

export async function updateEpisode(epId: string, payload: Partial<Episode>): Promise<Episode> {
  const res = await fetch(`${API_BASE}/admin/episodes/${epId}`, {
    method: 'PUT',
    headers: getHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify(payload),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || 'Failed to update episode');
  return data;
}

export async function uploadArtwork(
  epId: string,
  artworkType: 'poster' | 'banner' | 'thumbnail',
  file: File
): Promise<{ message: string; artwork: any }> {
  const formData = new FormData();
  formData.append('artwork_type', artworkType);
  formData.append('file', file);

  const res = await fetch(`${API_BASE}/admin/episodes/${epId}/artwork`, {
    method: 'POST',
    headers: getHeaders(),
    body: formData,
  });

  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || 'Artwork upload failed');
  }
  return data;
}

export async function fetchValidationReport(): Promise<ValidationReport> {
  const res = await fetch(`${API_BASE}/admin/validation-report`, {
    headers: getHeaders(),
  });
  if (!res.ok) throw new Error('Failed to fetch validation report');
  return res.json();
}

export async function triggerPublish(): Promise<{ status: string; message: string; run_id: string }> {
  const res = await fetch(`${API_BASE}/admin/catalog/publish`, {
    method: 'POST',
    headers: getHeaders(),
  });
  const data = await res.json();
  if (!res.ok) {
    const errorMsg = typeof data.detail === 'string' ? data.detail : data.detail?.message || 'Publish failed';
    throw new Error(errorMsg);
  }
  return data;
}

export async function fetchPublishRuns(): Promise<PublishRun[]> {
  const res = await fetch(`${API_BASE}/admin/publish-runs`, {
    headers: getHeaders(),
  });
  if (!res.ok) throw new Error('Failed to fetch publish runs');
  return res.json();
}
