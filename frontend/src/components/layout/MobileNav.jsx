import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Map, Zap, BookOpen, Wrench, TrendingUp, Bot, Settings } from 'lucide-react';

const items = [
  { to: '/home', label: 'Overview', icon: LayoutDashboard },
  { to: '/my-routes', label: 'Routes', icon: Map },
  { to: '/skills', label: 'Skills', icon: Zap },
  { to: '/resources', label: 'Resources', icon: BookOpen },
  { to: '/projects', label: 'Projects', icon: Wrench },
  { to: '/progress', label: 'Progress', icon: TrendingUp },
  { to: '/guide', label: 'AI Guide', icon: Bot },
  { to: '/settings', label: 'Settings', icon: Settings },
];

export default function MobileNav() {
  return (
    <nav className="lg:hidden fixed bottom-0 inset-x-0 z-30 bg-[#171714] border-t border-[#383832]">
      <ul className="grid grid-cols-4 sm:flex">
        {items.map(({ to, label, icon: Icon }) => (
          <li key={to} className="sm:flex-1">
            <NavLink
              to={to}
              className={({ isActive }) => `
                flex flex-col items-center gap-1 py-2 text-[9px] sm:text-[10px] font-medium transition-colors
                ${isActive ? 'text-[#C89B5B]' : 'text-[#77766F]'}
              `}
            >
              {({ isActive }) => (
                <>
                  <Icon size={18} strokeWidth={isActive ? 2 : 1.5} />
                  <span>{label}</span>
                </>
              )}
            </NavLink>
          </li>
        ))}
      </ul>
    </nav>
  );
}
