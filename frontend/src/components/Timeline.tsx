import { Link } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { getSpeeches, getLatestSnapshot, Speech, Snapshot } from '../utils/api';

export default function Timeline() {
  const [speeches, setSpeeches] = useState<Speech[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sourceFilter, setSourceFilter] = useState<string>('all');

  useEffect(() => {
    getSpeeches({ page_size: 100 })
      .then((data) => {
        setSpeeches(data.items || []);
        setError(null);
      })
      .catch((e) => {
        setError(e?.response?.data?.detail || e?.message || '无法连接后端服务');
      })
      .finally(() => setLoading(false));
  }, []);

  const filtered = sourceFilter === 'all'
    ? speeches
    : speeches.filter((s) => s.source_type === sourceFilter);

  // 按年份分组
  const grouped = filtered.reduce<Record<string, Speech[]>>((acc, s) => {
    const year = s.date?.slice(0, 4) || 'unknown';
    if (!acc[year]) acc[year] = [];
    acc[year].push(s);
    return acc;
  }, {});

  const sourceTypes = ['all', ...new Set(speeches.map((s) => s.source_type))];

  const icons: Record<string, string> = {
    keynote: '🎯',
    earnings: '📊',
    interview: '🎙️',
    conference: '🗣️',
    social: '🐦',
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">演讲时间线</h2>
          <p className="text-gray-400 mt-1">黄仁勋所有公开发言的时间分布</p>
        </div>

        {/* 筛选 */}
        <div className="flex gap-2">
          {sourceTypes.map((st) => (
            <button
              key={st}
              onClick={() => setSourceFilter(st)}
              className={`px-3 py-1.5 rounded-lg text-sm transition-colors ${
                sourceFilter === st
                  ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                  : 'text-gray-400 hover:text-white bg-gray-800/50 border border-transparent'
              }`}
            >
              {st === 'all' ? '全部' : st}
            </button>
          ))}
        </div>
      </div>

      {error ? (
        <div className="flex flex-col items-center justify-center h-64 space-y-4">
          <div className="text-red-400 text-lg">⚠️ 数据加载失败</div>
          <div className="text-gray-500 text-sm">{error}</div>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-emerald-500/10 border border-emerald-500/30 rounded-lg text-sm text-emerald-400 hover:bg-emerald-500/20 transition-colors"
          >
            重试
          </button>
        </div>
      ) : loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-400 animate-pulse">加载中...</div>
        </div>
      ) : (
        <div className="relative">
          {/* 时间线 */}
          <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-800" />

          {Object.entries(grouped)
            .sort(([a], [b]) => Number(b) - Number(a))
            .map(([year, items]) => (
              <div key={year} className="mb-8">
                {/* 年份标记 - 正常流布局避免被裁切 */}
                <div className="flex items-center gap-3 -ml-4">
                  <div className="w-3 h-3 bg-emerald-500 rounded-full ring-4 ring-gray-950 flex-shrink-0" />
                  <span className="text-lg font-bold text-white whitespace-nowrap">{year}</span>
                </div>

                <div className="ml-8 mt-6 space-y-3">
                  {items.map((speech) => (
                    <Link
                      key={speech.id}
                      to={`/speech/${speech.id}`}
                      className="stat-card block ml-4 hover:border-emerald-500/30"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex items-start gap-3 min-w-0">
                          <span className="text-lg mt-0.5">{icons[speech.source_type] || '📄'}</span>
                          <div className="min-w-0">
                            <p className="text-white font-medium truncate">{speech.title}</p>
                            <div className="flex items-center gap-3 mt-1">
                              <span className="text-xs text-gray-500">{speech.date?.slice(0, 10)}</span>
                              <span className="text-xs text-gray-600">·</span>
                              <span className="text-xs text-gray-500">{speech.event_name}</span>
                              {speech.word_count > 0 && (
                                <>
                                  <span className="text-xs text-gray-600">·</span>
                                  <span className="text-xs text-gray-500">{speech.word_count.toLocaleString()} 字</span>
                                </>
                              )}
                            </div>
                          </div>
                        </div>
                        {speech.source_url && (
                          <a
                            href={speech.source_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            onClick={(e) => e.stopPropagation()}
                            className="flex-shrink-0 p-2 text-gray-500 hover:text-emerald-400 hover:bg-gray-800 rounded-lg transition-colors"
                            title="查看原文"
                          >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                            </svg>
                          </a>
                        )}
                      </div>
                    </a>
                  ))}
                </div>
              </div>
            ))}
        </div>
      )}
    </div>
  );
}
