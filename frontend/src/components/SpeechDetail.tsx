import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { getSpeech, Speech } from '../utils/api';

export default function SpeechDetail() {
  const { id } = useParams<{ id: string }>();
  const [speech, setSpeech] = useState<Speech | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) {
      getSpeech(id)
        .then(setSpeech)
        .finally(() => setLoading(false));
    }
  }, [id]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-400 animate-pulse">加载中...</div>
      </div>
    );
  }

  if (!speech) {
    return <div className="text-gray-400">未找到该演讲</div>;
  }

  return (
    <div className="space-y-6">
      {/* 头部 */}
      <div>
        <a href="/timeline" className="text-sm text-gray-500 hover:text-gray-300 mb-2 block">← 返回时间线</a>
        <h2 className="text-2xl font-bold text-white">{speech.title}</h2>
        <div className="flex items-center gap-4 mt-2 text-sm text-gray-500">
          <span>{speech.date?.slice(0, 10)}</span>
          <span className="px-2 py-0.5 bg-gray-800 rounded">{speech.source_type}</span>
          {speech.event_name && <span>{speech.event_name}</span>}
          {speech.word_count > 0 && <span>{speech.word_count.toLocaleString()} 字</span>}
        </div>
        {/* 信源链接 */}
        {speech.source_url && (
          <a
            href={speech.source_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 mt-3 px-4 py-2 bg-emerald-500/10 border border-emerald-500/30 rounded-lg text-sm text-emerald-400 hover:bg-emerald-500/20 transition-colors"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
            查看原文信源
          </a>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 正文 */}
        <div className="chart-container lg:col-span-2">
          <div className="prose prose-invert max-w-none">
            <pre className="whitespace-pre-wrap text-sm text-gray-300 font-sans leading-relaxed">
              {speech.raw_text?.slice(0, 5000)}
              {(speech.raw_text?.length ?? 0) > 5000 && (
                <span className="text-gray-600">... (内容过长，仅显示前 5000 字)</span>
              )}
            </pre>
          </div>
        </div>

        {/* 分析侧边栏 */}
        <div className="space-y-4">
          {/* 主题 */}
          <div className="chart-container">
            <h3 className="text-sm font-medium text-gray-300 mb-3">主题分析</h3>
            {speech.topics?.map((t) => (
              <div key={t.topic_name} className="mb-3 last:mb-0">
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-300">{t.topic_name}</span>
                  <span className="text-gray-500">{(t.relevance_score * 100).toFixed(0)}%</span>
                </div>
                <div className="h-1 bg-gray-800 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-emerald-400 rounded-full"
                    style={{ width: `${t.relevance_score * 100}%` }}
                  />
                </div>
                {t.keywords?.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-1">
                    {t.keywords.slice(0, 5).map((kw) => (
                      <span key={kw} className="text-xs text-gray-500">#{kw}</span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* 情感 */}
          <div className="chart-container">
            <h3 className="text-sm font-medium text-gray-300 mb-3">情感分析</h3>
            {speech.sentiments?.map((s, i) => (
              <div key={i} className="flex items-center gap-2 mb-2 text-sm">
                <span className={`px-1.5 py-0.5 rounded text-xs ${
                  s.label === 'positive' || s.label === 'excited' ? 'bg-emerald-500/10 text-emerald-400' :
                  s.label === 'negative' ? 'bg-red-500/10 text-red-400' :
                  'bg-gray-500/10 text-gray-400'
                }`}>
                  {s.label}
                </span>
                <span className="text-gray-500">{(s.confidence * 100).toFixed(0)}%</span>
              </div>
            ))}
          </div>

          {/* 叙事 */}
          <div className="chart-container">
            <h3 className="text-sm font-medium text-gray-300 mb-3">叙事框架</h3>
            {speech.narratives?.map((n, i) => (
              <div key={i} className="flex items-center gap-2 mb-2 text-sm">
                <span className={`px-1.5 py-0.5 rounded text-xs ${
                  n.category === 'metaphor' ? 'bg-purple-500/10 text-purple-400' :
                  n.category === 'prediction' ? 'bg-blue-500/10 text-blue-400' :
                  n.category === 'principle' ? 'bg-amber-500/10 text-amber-400' :
                  'bg-gray-500/10 text-gray-400'
                }`}>
                  {n.name.slice(0, 20)}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
