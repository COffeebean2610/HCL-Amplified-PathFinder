import { useState } from 'react';
import { Search, Bell } from 'lucide-react';
import { IconButton } from '../common/Button';

export default function Topbar({ title, subtitle, actions }) {
  const [searchOpen, setSearchOpen] = useState(false);
  const [searchValue, setSearchValue] = useState('');

  return (
    <header className="sticky top-0 z-30 bg-[#171714] border-b border-[#383832] px-6 py-3">
      <div className="flex items-center justify-between gap-4">
        {/* Title */}
        <div className="min-w-0">
          <div className="label">{title}</div>
          {subtitle && (
            <p className="text-xs text-[#77766F] mt-0.5 truncate">{subtitle}</p>
          )}
        </div>

        {/* Right controls */}
        <div className="flex items-center gap-2 flex-shrink-0">
          {/* Search */}
          {searchOpen ? (
            <div className="flex items-center gap-2 bg-[#22221E] border border-[#383832] rounded-lg px-3 py-1.5">
              <Search size={13} className="text-[#77766F]" />
              <input
                autoFocus
                value={searchValue}
                onChange={(e) => setSearchValue(e.target.value)}
                onBlur={() => { if (!searchValue) setSearchOpen(false); }}
                placeholder="Search..."
                className="bg-transparent border-none outline-none text-sm text-[#F3F0E8] placeholder-[#77766F] w-40 p-0"
              />
            </div>
          ) : (
            <IconButton
              icon={<Search size={16} />}
              onClick={() => setSearchOpen(true)}
              label="Search"
            />
          )}

          <IconButton icon={<Bell size={16} />} label="Notifications" />

          {/* Actions */}
          {actions}

          {/* Avatar */}
          <div className="w-7 h-7 rounded-full bg-[#C89B5B]/20 border border-[#C89B5B]/40 flex items-center justify-center cursor-pointer">
            <span className="text-[11px] font-semibold text-[#C89B5B]">A</span>
          </div>
        </div>
      </div>
    </header>
  );
}
