import { useEffect, useState } from 'react';
import { getSnapshots, createSnapshot, Snapshot } from '../utils/api';

export default function Snapshots() {
  const [snapshots, setSnapshots] = useState<Snapshot[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);

  const load = () => {
    setLoading(true);
    getSnapshots()
      .then(setSnapshots)
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  const handleCreate = async () => {
    setCreating(true);
    try {
      await createSnapshot();
      await load();
    } finally {
      setCreating(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-400 animate-pulse">加载中...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">分析快照</h2>
          <p className="text-gray-400 mt-1">定期保存的阶段性分析状态，支持回溯对比</p>
        </div>
        <button
          onClick={handleCreate}
          disabled={creating}
          className="px-4 py-2 bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 rounded-lg text-sm hover:bg-emerald-500/20 transition-colors disabled:opacity-50"
        >
          {creating ? '生成中...' : '生成新快照'}
        </button>
      </div>

      {snapshots.length === 0 ? (
        <div className="chart-container text-center py-12">
          <p className="text-gray-500">暂无快照</p>
          <p className="text-gray-600 text-sm mt-1">点击"生成新快照"创建第一个分析快照</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {snapshots.map((snap) => (
            <div key={snap.id} className="stat-card">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-white font-medium">{snap.name}</h3>
                  <p className="text-xs text-gray-500 mt-1">
                    {snap.created_at?.slice(0, 16).replace('T', ' ')}
                  </p>
                </div>
                <div className="w-8 h-8 bg-emerald-500/10 rounded-lg flex items-center justify-center text-emerald-400 text-xs font-bold">
                  {snap.speech_count}
                </div>
              </div>
              <div className="mt-3 pt-3 border-t border-gray-800">
                <div className="flex justify-between text-xs text-gray-500">
                  <span>演讲数</span>
                  <span className="text-white">{snap.speech_count}</span>
                </div>
                {snap.analysis_data?.top_topics && (
                  <div className="mt-2">
                    <p className="text-xs text-gray-500 mb-1">Top 主题</p>
                    <div className="flex flex-wrap gap-1">
                      {snap.analysis_data.top_topics.slice(0, 5).map((t: any) => (
                        <span key={t.topic} className="px-2 py-0.5 bg-gray-800 rounded text-xs text-gray-400">
                          {t.topic}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
