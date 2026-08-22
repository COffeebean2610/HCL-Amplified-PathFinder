export function Badge({ children, color = '#77766F', bg }) {
  return (
    <span
      className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-semibold uppercase tracking-widest"
      style={{
        color: color,
        backgroundColor: bg || `${color}15`,
        border: `1px solid ${color}30`,
      }}
    >
      {children}
    </span>
  );
}

export function StatusBadge({ status }) {
  const map = {
    completed: { label: 'Completed', color: '#8C9A7A' },
    current: { label: 'Current', color: '#C89B5B' },
    upcoming: { label: 'Upcoming', color: '#77766F' },
    recommended: { label: 'Recommended', color: '#C89B5B' },
    active: { label: 'Active', color: '#8C9A7A' },
    paused: { label: 'Paused', color: '#77766F' },
  };
  const s = map[status] || { label: status, color: '#77766F' };
  return <Badge color={s.color}>{s.label}</Badge>;
}

export function TypeBadge({ type }) {
  const map = {
    course: { label: 'Course', color: '#C89B5B' },
    video: { label: 'Video', color: '#8C9A7A' },
    article: { label: 'Article', color: '#AAA89F' },
    documentation: { label: 'Docs', color: '#77766F' },
    book: { label: 'Book', color: '#AAA89F' },
    practice: { label: 'Practice', color: '#8C9A7A' },
    project: { label: 'Project', color: '#C89B5B' },
  };
  const t = map[type] || { label: type, color: '#77766F' };
  return <Badge color={t.color}>{t.label}</Badge>;
}
