'use client';

export default function NavBar() {
  return (
    <nav className="h-16 bg-[#1e293b] border-b border-slate-700 flex items-center px-8">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center shadow-lg">
          <span className="text-white font-bold text-lg">H</span>
        </div>
        <div>
          <h1 className="text-xl font-bold text-slate-100">HealthMap</h1>
          <p className="text-xs text-slate-400">AI-Powered Global Health Intelligence</p>
        </div>
      </div>
    </nav>
  );
}