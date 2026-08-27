import { Outlet, useLocation } from 'react-router-dom';
import Sidebar from './Sidebar';
import MobileNav from './MobileNav';
import Topbar from './Topbar';

const PAGE_META = {
  '/home': { title: 'Learning Overview' },
  '/my-routes': { title: 'My Routes' },
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
    (location.pathname.startsWith('/resources/') ? { title: 'Resource Detail' } :
    location.pathname.startsWith('/projects/') ? { title: 'Project Detail' } :
    { title: 'RouteMaster' });

  return (
    // ✅ FIX: min-h-screen NOT h-screen overflow-hidden
    <div className="app-shell flex min-h-screen" style={{ backgroundColor: 'var(--bg)' }}>
      <Sidebar />

      <div className="app-shell-content flex flex-col min-w-0">
        <Topbar title={meta.title} />

        <main className="flex-1 min-w-0 pb-20 lg:pb-12">
          <div className="w-full">
            <Outlet />
          </div>
        </main>
      </div>

      <MobileNav />
    </div>
  );
}
