import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Search,
  Bell,
  LogOut,
  Settings,
} from 'lucide-react';
import { IconButton } from '../common/Button';
import { AnimatePresence, motion } from 'framer-motion';
import { useAuth } from '../../context/AuthContext';

export default function Topbar({
  title = 'RouteMaster',
  subtitle,
  actions,
}) {
  const navigate = useNavigate();
  const { currentUser, logout } = useAuth();

  const [searchOpen, setSearchOpen] = useState(false);
  const [searchValue, setSearchValue] = useState('');
  const [avatarOpen, setAvatarOpen] = useState(false);

  const initials = currentUser?.name
    ? currentUser.name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .slice(0, 2)
      .toUpperCase()
    : 'U';

  const handleLogout = async () => {
    setAvatarOpen(false);
    await logout();
    navigate('/login');
  };

  return (
    <header
      className="
        sticky
        top-0
        z-30
        px-6
        py-3
      "
      style={{
        backgroundColor: 'var(--bg)',
        borderBottom: '1px solid var(--border)',
      }}
    >
      <div className="flex items-center justify-between gap-4">

        {/* =====================================================
            LEFT — PAGE TITLE
        ====================================================== */}
        <div className="min-w-0">
          <div className="label">
            {title}
          </div>

          {subtitle && (
            <p className="text-xs text-text-muted mt-0.5 truncate">
              {subtitle}
            </p>
          )}
        </div>

        {/* =====================================================
            RIGHT — CONTROLS
        ====================================================== */}
        <div className="flex items-center gap-2 flex-shrink-0">

          {/* -------------------------------------------------
              SEARCH
          -------------------------------------------------- */}
          {searchOpen ? (
            <div
              className="
                flex
                items-center
                gap-2
                rounded-lg
                px-3
                py-1.5
              "
              style={{
                backgroundColor: 'var(--surface)',
                border: '1px solid var(--border)',
              }}
            >
              <Search
                size={13}
                className="text-text-muted"
              />

              <input
                autoFocus
                value={searchValue}
                onChange={(e) =>
                  setSearchValue(e.target.value)
                }
                onKeyDown={(e) => {
                  if (e.key === 'Escape') {
                    setSearchValue('');
                    setSearchOpen(false);
                  }
                }}
                onBlur={() => {
                  if (!searchValue) {
                    setSearchOpen(false);
                  }
                }}
                placeholder="Search..."
                className="
                  bg-transparent
                  border-none
                  outline-none
                  text-sm
                  text-text-primary
                  placeholder-text-muted
                  w-40
                  p-0
                "
              />
            </div>
          ) : (
            <IconButton
              icon={<Search size={16} />}
              onClick={() => setSearchOpen(true)}
              label="Search"
            />
          )}

          {/* -------------------------------------------------
              NOTIFICATIONS
          -------------------------------------------------- */}
          <IconButton
            icon={<Bell size={16} />}
            label="Notifications"
          />

          {/* -------------------------------------------------
              PAGE ACTIONS
          -------------------------------------------------- */}
          {actions}

          {/* =================================================
              AVATAR
          ================================================== */}
          <div className="relative">

            <button
              onClick={() =>
                setAvatarOpen((v) => !v)
              }
              aria-label="Open user menu"
              className="
                w-8
                h-8
                rounded-full
                flex
                items-center
                justify-center
                cursor-pointer
                transition-colors
              "
              style={{
                backgroundColor: 'var(--accent)25',
                border: '1px solid var(--accent)50',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor =
                  'var(--accent)35';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor =
                  'var(--accent)25';
              }}
            >
              <span
                className="
                  text-[11px]
                  font-semibold
                  text-accent
                "
              >
                {initials}
              </span>
            </button>

            {/* =================================================
                AVATAR DROPDOWN
            ================================================== */}
            <AnimatePresence>
              {avatarOpen && (
                <motion.div
                  initial={{
                    opacity: 0,
                    y: 6,
                    scale: 0.97,
                  }}
                  animate={{
                    opacity: 1,
                    y: 0,
                    scale: 1,
                  }}
                  exit={{
                    opacity: 0,
                    y: 4,
                    scale: 0.97,
                  }}
                  transition={{
                    duration: 0.12,
                  }}
                  className="
                    absolute
                    right-0
                    top-full
                    mt-2
                    w-52
                    rounded-lg
                    overflow-hidden
                    shadow-xl
                    z-50
                  "
                  style={{
                    backgroundColor: 'var(--surface)',
                    border: '1px solid var(--border)',
                  }}
                >

                  {/* User information */}
                  <div
                    className="px-4 py-3"
                    style={{
                      borderBottom:
                        '1px solid var(--border)',
                    }}
                  >
                    <div
                      className="
                        text-xs
                        font-medium
                        text-text-primary
                        truncate
                      "
                    >
                      {currentUser?.name || 'User'}
                    </div>

                    <div
                      className="
                        text-[10px]
                        text-text-muted
                        truncate
                        mt-0.5
                      "
                    >
                      {currentUser?.email || ''}
                    </div>

                    <div
                      className="
                        text-[10px]
                        text-text-muted
                        truncate
                        mt-0.5
                      "
                    >
                      {currentUser?.target_career || 'Learner'}
                    </div>
                  </div>

                  {/* Settings */}
                  <button
                    onClick={() => {
                      navigate('/settings');
                      setAvatarOpen(false);
                    }}
                    className="
                      w-full
                      flex
                      items-center
                      gap-2.5
                      px-4
                      py-2.5
                      text-xs
                      cursor-pointer
                      text-left
                      transition-colors
                    "
                    style={{
                      backgroundColor: 'transparent',
                      color: 'var(--text-secondary)',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.backgroundColor =
                        'var(--surface-elevated)';

                      e.currentTarget.style.color =
                        'var(--text-primary)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.backgroundColor =
                        'transparent';

                      e.currentTarget.style.color =
                        'var(--text-secondary)';
                    }}
                  >
                    <Settings size={13} />

                    Settings
                  </button>

                  {/* Divider */}
                  <div
                    style={{
                      borderTop:
                        '1px solid var(--border)',
                    }}
                  />

                  <button
                    onClick={handleLogout}
                    className="
                      w-full
                      flex
                      items-center
                      gap-2.5
                      px-4
                      py-2.5
                      text-xs
                      cursor-pointer
                      text-left
                      transition-colors
                    "
                    style={{
                      backgroundColor: 'transparent',
                      color: 'var(--text-muted)',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.backgroundColor =
                        'var(--surface-elevated)';

                      e.currentTarget.style.color =
                        'var(--text-primary)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.backgroundColor =
                        'transparent';

                      e.currentTarget.style.color =
                        'var(--text-muted)';
                    }}
                  >
                    <LogOut size={13} />

                    Sign out
                  </button>

                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </header>
  );
}
