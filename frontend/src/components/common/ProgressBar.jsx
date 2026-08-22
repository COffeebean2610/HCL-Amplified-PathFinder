export function ProgressBar({ value = 0, color = '#C89B5B', className = '' }) {
  const pct = Math.min(100, Math.max(0, value));
  return (
    <div
      className={`progress-track relative ${className}`}
      role="progressbar"
      aria-valuenow={pct}
      aria-valuemin={0}
      aria-valuemax={100}
    >
      <div
        className="progress-fill"
        style={{ width: `${pct}%`, backgroundColor: color }}
      />
    </div>
  );
}

export function SkillIndicator({ name, value, target, color = '#C89B5B', showTarget = false }) {
  return (
    <div className="space-y-1.5">
      {name && (
        <div className="flex items-center justify-between">
          <span className="text-sm text-[#F3F0E8]">{name}</span>
          <div className="flex items-center gap-3">
            {showTarget && <span className="text-xs text-[#77766F]">→ {target}%</span>}
            <span className="text-sm font-medium" style={{ color }}>{value}%</span>
          </div>
        </div>
      )}
      <div className="relative">
        <ProgressBar value={value} color={color} />
        {showTarget && (
          <div
            className="absolute top-0 w-px h-full"
            style={{ left: `${target}%`, backgroundColor: '#C89B5B', opacity: 0.6 }}
          />
        )}
      </div>
    </div>
  );
}
