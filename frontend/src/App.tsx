import { useEffect } from 'react';
import { BrowserRouter, Routes, Route, NavLink, useNavigate, useLocation } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import Timeline from './components/Timeline';
import TopicAnalysis from './components/TopicAnalysis';
import Snapshots from './components/Snapshots';
import SpeechDetail from './components/SpeechDetail';

function AppContent() {
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    // 处理 GitHub Pages 刷新/直接访问 SPA 路由
    const redirect = sessionStorage.getItem('redirect');
    if (redirect) {
      sessionStorage.removeItem('redirect');
      const base = '/huang-research-platform';
      const target = redirect.replace(base, '') || '/';
      navigate(target, { replace: true });
    }
  }, []);

  return (
    <div className="min-h-screen bg-gray-950">
      {/* Header */}
      <header className="border-b border-gray-800 bg-gray-950/90 backdrop-blur sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          <NavLink to="/" className="flex items-center gap-3">
            <div className="w-8 h-8 bg-gradient-to-br from-emerald-400 to-cyan-400 rounded-lg flex items-center justify-center text-sm font-bold text-black">
              JH
            </div>
            <div>
              <h1 className="text-lg font-semibold text-white">黄仁勋深度研究</h1>
              <p className="text-xs text-gray-500">Jensen Huang Research Platform</p>
            </div>
          </NavLink>
          <nav className="flex items-center gap-1">
            <NavLink
              to="/"
              end
              className={({ isActive }) =>
                `px-3 py-2 rounded-lg text-sm transition-colors ${
                  isActive ? 'bg-emerald-500/10 text-emerald-400' : 'text-gray-400 hover:text-white hover:bg-gray-800'
                }`
              }
            >
              概览
            </NavLink>
            <NavLink
              to="/timeline"
              className={({ isActive }) =>
                `px-3 py-2 rounded-lg text-sm transition-colors ${
                  isActive ? 'bg-emerald-500/10 text-emerald-400' : 'text-gray-400 hover:text-white hover:bg-gray-800'
                }`
              }
            >
              时间线
            </NavLink>
            <NavLink
              to="/topics"
              className={({ isActive }) =>
                `px-3 py-2 rounded-lg text-sm transition-colors ${
                  isActive ? 'bg-emerald-500/10 text-emerald-400' : 'text-gray-400 hover:text-white hover:bg-gray-800'
                }`
              }
            >
              主题分析
            </NavLink>
            <NavLink
              to="/snapshots"
              className={({ isActive }) =>
                `px-3 py-2 rounded-lg text-sm transition-colors ${
                  isActive ? 'bg-emerald-500/10 text-emerald-400' : 'text-gray-400 hover:text-white hover:bg-gray-800'
                }`
              }
            >
              快照
            </NavLink>
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/timeline" element={<Timeline />} />
          <Route path="/topics" element={<TopicAnalysis />} />
          <Route path="/snapshots" element={<Snapshots />} />
          <Route path="/speech/:id" element={<SpeechDetail />} />
        </Routes>
      </main>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter basename="/huang-research-platform">
      <AppContent />
    </BrowserRouter>
  );
}

export default App;
