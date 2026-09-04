import type { PublishedCatalog, SearchResponse } from '../types';

const API_BASE = 'http://localhost:8000';

export async function fetchPublishedCatalog(): Promise<PublishedCatalog> {
  const res = await fetch(`${API_BASE}/catalog`);
  if (!res.ok) throw new Error('Failed to load catalog');
  return res.json();
}

export async function searchCatalog(params: {
  q?: string;
  category?: string;
  language?: string;
  section?: string;
}): Promise<SearchResponse> {
  const url = new URL(`${API_BASE}/catalog/search`);
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== '') url.searchParams.append(k, v);
  });

  const res = await fetch(url.toString());
  if (!res.ok) throw new Error('Search failed');
  return res.json();
}
