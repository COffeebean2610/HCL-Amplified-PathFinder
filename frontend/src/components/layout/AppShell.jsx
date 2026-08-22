import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import MobileNav from './MobileNav';
import Topbar from './Topbar';
import { useLocation } from 'react-router-dom';

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
  const meta = PAGE_META[location.pathname] ||
    (location.pathname.startsWith('/routes/') ? { title: 'Route Details' } :
    location.pathname.startsWith('/resources/') ? { title: 'Resource Detail' } :
    location.pathname.startsWith('/projects/') ? { title: 'Project Detail' } :
    { title: 'RouteMaster' });

  return (
    <div className="flex h-screen overflow-hidden" style={{ backgroundColor: 'var(--bg)' }}>
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <Topbar title={meta.title} />
        <main className="flex-1 overflow-y-auto pb-16 lg:pb-0">
          <Outlet />
        </main>
      </div>
      <MobileNav />
    </div>
  );
}
