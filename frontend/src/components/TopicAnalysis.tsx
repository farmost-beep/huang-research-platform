import { useEffect, useState } from 'react';
import { getTopics, getTopicEvolution, getKeywords, getSentimentTrend, getNarratives, TopicItem, TopicEvolution, KeywordCloud, SentimentTrend, NarrativeItem } from '../utils/api';
import KeywordCloudChart from './charts/KeywordCloudChart';
import RiverChart from './charts/RiverChart';
import SentimentChart from './charts/SentimentChart';

export default function TopicAnalysis() {
  const [topics, setTopics] = useState<TopicItem[]>([]);
  const [evolution, setEvolution] = useState<TopicEvolution[]>([]);
  const [keywords, setKeywords] = useState<KeywordCloud[]>([]);
  const [sentiments, setSentiments] = useState<SentimentTrend[]>([]);
  const [narratives, setNarratives] = useState<NarrativeItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'topics' | 'evolution' | 'keywords' | 'narratives'>('topics');

  useEffect(() => {
    Promise.all([
      getTopics(),
      getTopicEvolution(),
      getKeywords(),
      getSentimentTrend(),
      getNarratives(),
    ])
      .then(([t, e, kw, se, n]) => {
        setTopics(t);
        setEvolution(e);
        setKeywords(kw);
        setSentiments(se);
        setNarratives(n);
        setError(null);
      })
      .catch((e) => {
        setError(e?.response?.data?.detail || e?.message || '无法连接后端服务');
      })
      .finally(() => setLoading(false));
  }, []);

  const topTopics = topics.slice(0, 20);

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
      <div>
        <h2 className="text-2xl font-bold text-white">主题分析</h2>
        <p className="text-gray-400 mt-1">黄仁勋演讲主题的多维度分析</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-gray-900 rounded-lg p-1 w-fit">
        {[
          { key: 'topics' as const, label: '主题排名' },
          { key: 'evolution' as const, label: '主题演化' },
          { key: 'keywords' as const, label: '词云' },
          { key: 'narratives' as const, label: '叙事框架' },
        ].map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`px-4 py-2 rounded-md text-sm transition-colors ${
              activeTab === tab.key
                ? 'bg-emerald-500/10 text-emerald-400'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* 主题排名 */}
      {activeTab === 'topics' && (
        <div className="chart-container">
          <h3 className="text-sm font-medium text-gray-300 mb-4">Top 20 主题</h3>
          <div className="space-y-2">
            {topTopics.map((t, i) => (
              <div key={t.topic} className="flex items-center gap-4">
                <span className="text-xs text-gray-600 w-6 text-right">{i + 1}</span>
                <span className="text-sm text-gray-200 w-48 truncate">{t.topic}</span>
                <div className="flex-1 h-2 bg-gray-800 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-emerald-500 to-cyan-400 rounded-full"
                    style={{ width: `${Math.min(t.avg_relevance * 100, 100)}%` }}
                  />
                </div>
                <span className="text-xs text-gray-500 w-16 text-right">{t.count}次</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 主题演化 */}
      {activeTab === 'evolution' && (
        <div className="chart-container">
          <h3 className="text-sm font-medium text-gray-300 mb-4">主题随时间演化</h3>
          <RiverChart data={evolution} />
        </div>
      )}

      {/* 词云 */}
      {activeTab === 'keywords' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="chart-container lg:col-span-2">
            <h3 className="text-sm font-medium text-gray-300 mb-4">高频关键词</h3>
            <KeywordCloudChart keywords={keywords} />
          </div>
          <div className="chart-container lg:col-span-1">
            <h3 className="text-sm font-medium text-gray-300 mb-4">情感趋势</h3>
            <SentimentChart data={sentiments} />
          </div>
        </div>
      )}

      {/* 叙事框架 */}
      {activeTab === 'narratives' && (
        <div className="grid grid-cols-1 gap-6">
          {/* 叙事清单 */}
          <div className="chart-container">
            <h3 className="text-sm font-medium text-gray-300 mb-4">识别到的叙事模式</h3>
            <div className="space-y-3">
              {narratives.map((n) => (
                <div key={n.name} className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <span className={`px-2 py-0.5 rounded text-xs ${
                      n.category === 'metaphor' ? 'bg-purple-500/10 text-purple-400' :
                      n.category === 'prediction' ? 'bg-blue-500/10 text-blue-400' :
                      n.category === 'principle' ? 'bg-amber-500/10 text-amber-400' :
                      n.category === 'strategy' ? 'bg-green-500/10 text-green-400' :
                      'bg-gray-500/10 text-gray-400'
                    }`}>
                      {n.category === 'metaphor' ? '比喻' :
                       n.category === 'prediction' ? '预测' :
                       n.category === 'principle' ? '原则' :
                       n.category === 'strategy' ? '战略' : '观点'}
                    </span>
                    <span className="text-sm text-gray-200">{n.name}</span>
                  </div>
                  <div className="flex items-center gap-4 text-xs text-gray-500">
                    <span>出现 {n.occurrences} 次</span>
                    <div className="w-16 h-1.5 bg-gray-700 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-emerald-400 rounded-full"
                        style={{ width: `${n.significance * 100}%` }}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* 情感趋势 */}
          <div className="chart-container">
            <h3 className="text-sm font-medium text-gray-300 mb-4">情感时序趋势</h3>
            <SentimentChart data={sentiments} />
          </div>
        </div>
      )}
    </div>
  );
}
