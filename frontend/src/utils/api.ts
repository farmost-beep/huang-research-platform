import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
});

export interface DashboardOverview {
  total_speeches: number;
  total_words: number;
  time_range: { earliest: string; latest: string };
  source_distribution: { source: string; count: number }[];
  recent_speeches: { id: string; title: string; date: string; source_type: string }[];
  latest_snapshot: { id: string; name: string; created_at: string } | null;
}

export interface Speech {
  id: string;
  title: string;
  date: string;
  source_type: string;
  event_name: string;
  word_count: number;
  source_url?: string;
  topics?: { topic_name: string; relevance_score: number; keywords: string[] }[];
  sentiments?: { segment: string; label: string; confidence: number }[];
  narratives?: { name: string; category: string; significance: number }[];
}

export interface TopicItem {
  topic: string;
  count: number;
  avg_relevance: number;
}

export interface TopicEvolution {
  period: string;
  topic: string;
  intensity: number;
  mentions: number;
}

export interface SentimentTrend {
  period: string;
  label: string;
  count: number;
}

export interface KeywordCloud {
  word: string;
  count: number;
}

export interface NarrativeItem {
  name: string;
  category: string;
  occurrences: number;
  significance: number;
}

export interface Snapshot {
  id: string;
  name: string;
  speech_count: number;
  summary: string;
  analysis_data: any;
  created_at: string;
}

export async function getDashboardOverview() {
  const { data } = await api.get<DashboardOverview>('/dashboard/overview');
  return data;
}

export async function getSpeeches(params?: { source_type?: string; year?: number; page?: number }) {
  const { data } = await api.get('/speeches/', { params });
  return data;
}

export async function getSpeech(id: string) {
  const { data } = await api.get<Speech>(`/speeches/${id}`);
  return data;
}

export async function getTopics(limit = 50) {
  const { data } = await api.get<TopicItem[]>('/analysis/topics', { params: { limit } });
  return data;
}

export async function getTopicEvolution(topic?: string) {
  const { data } = await api.get<TopicEvolution[]>('/analysis/topics/evolution', { params: { topic } });
  return data;
}

export async function getSentimentTrend() {
  const { data } = await api.get<SentimentTrend[]>('/analysis/sentiment/trend');
  return data;
}

export async function getNarratives(category?: string) {
  const { data } = await api.get<NarrativeItem[]>('/analysis/narratives', { params: { category } });
  return data;
}

export async function getKeywords() {
  const { data } = await api.get<KeywordCloud[]>('/analysis/keywords');
  return data;
}

export async function getSnapshots(limit = 10) {
  const { data } = await api.get<Snapshot[]>('/snapshots/', { params: { limit } });
  return data;
}

export async function getLatestSnapshot() {
  const { data } = await api.get('/snapshots/latest');
  return data;
}

export async function createSnapshot() {
  const { data } = await api.post('/snapshots/create');
  return data;
}

export default api;
