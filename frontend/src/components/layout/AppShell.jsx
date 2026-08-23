import { Outlet, useLocation } from 'react-router-dom';
import Sidebar from './Sidebar';
import MobileNav from './MobileNav';
import Topbar from './Topbar';

const PAGE_META = {
  '/home': { title: 'Learning Overview' },
  '/routes': { title: 'My Routes' },
  '/skills': { title: 'Skill Intelligence' },
  '/resources': { title: 'Learning Resources' },
  '/projects': { title: 'Projects' },
  '/progress': { title: 'Your Progress' },
  '/settings': { title: 'Personal Settings' },
  '/guide': { title: 'AI Guide' },
};

export default function AppShell() {
  const location = useLocation();
  const meta =
    PAGE_META[location.pathname] ||
    (location.pathname.startsWith('/routes/') ? { title: 'Route Details' } :
    location.pathname.startsWith('/resources/') ? { title: 'Resource Detail' } :
    location.pathname.startsWith('/projects/') ? { title: 'Project Detail' } :
    { title: 'RouteMaster' });

  return (
    // ✅ FIX: min-h-screen NOT h-screen overflow-hidden
    <div className="flex min-h-screen" style={{ backgroundColor: 'var(--bg)' }}>
      {/* Sidebar — sticky, scrolls independently */}
      <Sidebar />

      {/* Main area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Sticky topbar */}
        <Topbar title={meta.title} />

        {/* Scrollable main content — natural height */}
        <main className="flex-1 pb-20 lg:pb-12">
          <Outlet />
        </main>
      </div>

      {/* Mobile bottom nav */}
      <MobileNav />
    </div>
  );
}
