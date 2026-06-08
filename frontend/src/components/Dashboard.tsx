import { Link } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { getDashboardOverview, getKeywords, DashboardOverview, KeywordCloud } from '../utils/api';
import KeywordCloudChart from './charts/KeywordCloudChart';
import StatCard from './StatCard';

export default function Dashboard() {
  const [overview, setOverview] = useState<DashboardOverview | null>(null);
  const [keywords, setKeywords] = useState<KeywordCloud[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([getDashboardOverview(), getKeywords()])
      .then(([ov, kw]) => {
        setOverview(ov);
        setKeywords(kw);
        setError(null);
      })
      .catch((e) => {
        setError(e?.response?.data?.detail || e?.message || '无法连接后端服务');
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-400 animate-pulse">加载中...</div>
      </div>
    );
  }

  if (error) {
    return (
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
    );
  }

  return (
    <div className="space-y-6">
      {/* 标题区 */}
      <div>
        <h2 className="text-2xl font-bold text-white">研究概览</h2>
        <p className="text-gray-400 mt-1">黄仁勋所有公开发言的综合分析 Dashboard</p>
      </div>

      {/* 统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="演讲总数"
          value={overview?.total_speeches ?? 0}
          subtitle="篇"
          icon="🎤"
        />
        <StatCard
          title="总字数"
          value={overview ? (overview.total_words / 10000).toFixed(1) : '0'}
          subtitle="万字"
          icon="📝"
        />
        <StatCard
          title="时间跨度"
          value={
            overview?.time_range?.earliest
              ? `${overview.time_range.earliest.slice(0, 4)} - ${overview.time_range.latest.slice(0, 4)}`
              : '—'
          }
          subtitle="年"
          icon="📅"
        />
        <StatCard
          title="来源类型"
          value={overview?.source_distribution?.length ?? 0}
          subtitle="种"
          icon="📡"
        />
      </div>

      {/* 来源分布 & 词云 */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 来源分布 */}
        <div className="chart-container lg:col-span-1">
          <h3 className="text-sm font-medium text-gray-300 mb-4">演讲来源分布</h3>
          <div className="space-y-3">
            {overview?.source_distribution?.map((src) => {
              const total = overview.total_speeches || 1;
              const pct = ((src.count / total) * 100).toFixed(0);
              const icons: Record<string, string> = {
                keynote: '🎯',
                earnings: '📊',
                interview: '🎙️',
                conference: '🗣️',
                social: '🐦',
              };
              return (
                <div key={src.source}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-300">
                      {icons[src.source] || '📄'} {src.source === 'keynote' ? '主题演讲' :
                        src.source === 'earnings' ? '财报电话会' :
                        src.source === 'interview' ? '媒体采访' :
                        src.source === 'conference' ? '行业大会' : src.source}
                    </span>
                    <span className="text-gray-500">{src.count} ({pct}%)</span>
                  </div>
                  <div className="h-1.5 bg-gray-800 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-emerald-500 to-cyan-400 rounded-full transition-all duration-500"
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* 词云 */}
        <div className="chart-container lg:col-span-2">
          <h3 className="text-sm font-medium text-gray-300 mb-4">高频关键词</h3>
          <KeywordCloudChart keywords={keywords} />
        </div>
      </div>

      {/* 最近的演讲 */}
      <div className="chart-container">
        <h3 className="text-sm font-medium text-gray-300 mb-4">最近演讲</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-gray-500 border-b border-gray-800">
                <th className="text-left py-2 font-medium">标题</th>
                <th className="text-left py-2 font-medium">日期</th>
                <th className="text-left py-2 font-medium">类型</th>
              </tr>
            </thead>
            <tbody>
              {overview?.recent_speeches?.map((s) => (
                <tr key={s.id} className="border-b border-gray-800/50 hover:bg-gray-800/30">
                  <td className="py-2">
                    <Link to={`/speech/${s.id}`} className="text-emerald-400 hover:text-emerald-300">
                      {s.title}
                    </Link>
                  </td>
                  <td className="py-2 text-gray-400">{s.date?.slice(0, 10)}</td>
                  <td className="py-2">
                    <span className="px-2 py-0.5 bg-gray-800 rounded text-xs text-gray-400">
                      {s.source_type}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* 快照 */}
      {overview?.latest_snapshot && (
        <div className="stat-card flex items-center justify-between">
          <div>
            <span className="text-xs text-gray-500">最新快照</span>
            <p className="text-emerald-400 font-medium">{overview.latest_snapshot.name}</p>
            <p className="text-xs text-gray-500">{overview.latest_snapshot.created_at?.slice(0, 16)}</p>
          </div>
          <Link to="/snapshots" className="text-sm text-emerald-400 hover:text-emerald-300">
            查看全部 →
          </Link>
        </div>
      )}
    </div>
  );
}
