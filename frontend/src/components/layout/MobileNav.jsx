import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Map, Zap, BookOpen, Wrench, TrendingUp } from 'lucide-react';

const items = [
  { to: '/home', label: 'Overview', icon: LayoutDashboard },
  { to: '/routes', label: 'Routes', icon: Map },
  { to: '/skills', label: 'Skills', icon: Zap },
  { to: '/resources', label: 'Resources', icon: BookOpen },
  { to: '/projects', label: 'Projects', icon: Wrench },
  { to: '/progress', label: 'Progress', icon: TrendingUp },
];

export default function MobileNav() {
  return (
    <nav className="lg:hidden fixed bottom-0 inset-x-0 z-30 bg-[#171714] border-t border-[#383832]">
      <ul className="flex">
        {items.map(({ to, label, icon: Icon }) => (
          <li key={to} className="flex-1">
            <NavLink
              to={to}
              className={({ isActive }) => `
                flex flex-col items-center gap-1 py-2.5 text-[10px] font-medium transition-colors
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
