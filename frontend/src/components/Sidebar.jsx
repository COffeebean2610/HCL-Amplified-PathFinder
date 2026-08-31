import { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { BarChart3, BookOpen, ChevronDown, Folder, HelpCircle, Home, LogOut, Settings, User } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const NAV_ITEMS = [
  { to: '/home', label: 'Home', icon: Home },
  { to: '/my-routes', label: 'My Routes', icon: Folder },
  { to: '/projects', label: 'Projects', icon: Folder },
  { to: '/resources', label: 'Resources', icon: BookOpen },
  { to: '/skills', label: 'Skills', icon: BarChart3 },
  { to: '/progress', label: 'Progress', icon: BarChart3 },
  { to: '/settings', label: 'Settings', icon: Settings },
];

export default function Sidebar() {
  const navigate = useNavigate();
  const { currentUser, logout } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);
  const initials = currentUser?.name
    ? currentUser.name.split(' ').filter(Boolean).map((part) => part[0]).join('').slice(0, 2).toUpperCase()
    : 'U';

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <aside className="sidebar">
      <button type="button" className="brand" onClick={() => navigate('/home')}>
        <div className="brand-name">RouteMaster</div>
        <div className="brand-subtitle">YOUR LEARNING ROUTE</div>
      </button>

      <nav className="sidebar-nav" aria-label="Main navigation">
        {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
          <NavLink key={to} to={to} className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}>
            <Icon size={23} strokeWidth={1.6} />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-bottom">
        <button type="button" className="help-link" onClick={() => navigate('/guide')}>
          <HelpCircle size={22} strokeWidth={1.5} />
          <span>Help</span>
        </button>

        <div className="sidebar-user-wrap">
          <button type="button" className="sidebar-user" onClick={() => setMenuOpen((open) => !open)}>
            <div className="user-avatar">{initials}</div>
            <div className="user-details">
              <div className="user-name">{currentUser?.name || 'User'}</div>
              <div className="user-role">{currentUser?.target_career || 'Learner'}</div>
            </div>
            <ChevronDown size={18} strokeWidth={1.5} className="user-chevron" />
          </button>

          {menuOpen && (
            <div className="sidebar-user-menu">
              <button type="button" onClick={() => { setMenuOpen(false); navigate('/settings'); }}><User size={15} /> Profile & Settings</button>
              <button type="button" onClick={handleLogout}><LogOut size={15} /> Sign out</button>
            </div>
          )}
        </div>
      </div>
    </aside>
  );
}
