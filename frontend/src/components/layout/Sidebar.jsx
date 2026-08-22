import { NavLink, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  LayoutDashboard, Map, Zap, BookOpen, Wrench,
  TrendingUp, Bot, Settings, HelpCircle, ChevronRight
} from 'lucide-react';

const NAV_ITEMS = [
  { to: '/home', label: 'Overview', icon: LayoutDashboard },
  { to: '/routes', label: 'My Routes', icon: Map },
  { to: '/skills', label: 'Skills', icon: Zap },
  { to: '/resources', label: 'Resources', icon: BookOpen },
  { to: '/projects', label: 'Projects', icon: Wrench },
  { to: '/progress', label: 'Progress', icon: TrendingUp },
  { to: '/guide', label: 'AI Guide', icon: Bot },
];

const BOTTOM_ITEMS = [
  { to: '/settings', label: 'Settings', icon: Settings },
  { to: '/help', label: 'Help', icon: HelpCircle },
];

export default function Sidebar() {
  const navigate = useNavigate();

  return (
    <aside
      className="hidden lg:flex flex-col h-screen sticky top-0 bg-[#171714] border-r border-[#383832]"
      style={{ width: 230, flexShrink: 0 }}
    >
      {/* Logo */}
      <div className="px-5 py-5 border-b border-[#383832]">
        <button
          onClick={() => navigate('/')}
          className="block cursor-pointer"
        >
          <div className="text-[11px] font-semibold tracking-[0.15em] uppercase text-[#C89B5B] mb-1">RouteMaster</div>
          <div className="text-[10px] tracking-[0.1em] uppercase text-[#77766F]">Your Learning Route</div>
        </button>
      </div>

      {/* Nav */}
      <nav className="flex-1 py-4 px-3 overflow-y-auto">
        <ul className="space-y-0.5">
          {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
            <li key={to}>
              <NavLink
                to={to}
                className={({ isActive }) => `
                  flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150
                  ${isActive
                    ? 'bg-[#C89B5B]/10 text-[#C89B5B]'
                    : 'text-[#AAA89F] hover:text-[#F3F0E8] hover:bg-[#22221E]'
                  }
                `}
              >
                {({ isActive }) => (
                  <>
                    <Icon size={16} strokeWidth={isActive ? 2 : 1.5} className="flex-shrink-0" />
                    <span>{label}</span>
                    {isActive && (
                      <motion.div
                        layoutId="nav-indicator"
                        className="ml-auto w-1 h-1 rounded-full bg-[#C89B5B]"
                      />
                    )}
                  </>
                )}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>

      {/* Bottom */}
      <div className="border-t border-[#383832] px-3 py-3">
        <ul className="space-y-0.5 mb-3">
          {BOTTOM_ITEMS.map(({ to, label, icon: Icon }) => (
            <li key={to}>
              <NavLink
                to={to}
                className={({ isActive }) => `
                  flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all duration-150
                  ${isActive ? 'text-[#C89B5B]' : 'text-[#77766F] hover:text-[#AAA89F] hover:bg-[#22221E]'}
                `}
              >
                <Icon size={15} strokeWidth={1.5} className="flex-shrink-0" />
                <span>{label}</span>
              </NavLink>
            </li>
          ))}
        </ul>

        {/* User */}
        <div className="flex items-center gap-3 px-3 py-2.5 mt-1 rounded-lg hover:bg-[#22221E] cursor-pointer transition-colors">
          <div className="w-7 h-7 rounded-full bg-[#C89B5B]/20 border border-[#C89B5B]/40 flex items-center justify-center flex-shrink-0">
            <span className="text-[11px] font-semibold text-[#C89B5B]">A</span>
          </div>
          <div className="min-w-0">
            <div className="text-xs font-medium text-[#F3F0E8] truncate">Abhishek</div>
            <div className="text-[10px] text-[#77766F] truncate">AI / ML Engineer</div>
          </div>
          <ChevronRight size={13} className="text-[#77766F] ml-auto flex-shrink-0" />
        </div>
      </div>
    </aside>
  );
}
