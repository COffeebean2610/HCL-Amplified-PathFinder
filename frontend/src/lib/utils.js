export function cn(...classes) {
  return classes.filter(Boolean).join(' ');
}

export function formatDuration(minutes) {
  if (minutes < 60) return `${minutes} min`;
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  return m ? `${h}h ${m}min` : `${h}h`;
}

export function getStatusColor(status) {
  switch (status) {
    case 'completed': return '#8C9A7A';
    case 'current': return '#C89B5B';
    case 'upcoming': return '#77766F';
    case 'recommended': return '#C89B5B';
    default: return '#77766F';
  }
}

export function getPriorityColor(priority) {
  switch (priority) {
    case 'HIGH': return '#A96A5F';
    case 'MEDIUM': return '#C89B5B';
    case 'UPCOMING': return '#77766F';
    case 'FUTURE': return '#77766F';
    default: return '#77766F';
  }
}

export function getTypeLabel(type) {
  const map = {
    course: 'Course',
    video: 'Video',
    article: 'Article',
    documentation: 'Documentation',
    book: 'Book',
    practice: 'Practice',
    project: 'Project',
  };
  return map[type] || type;
}

export function getTypeColor(type) {
  const map = {
    course: '#C89B5B',
    video: '#8C9A7A',
    article: '#AAA89F',
    documentation: '#77766F',
    book: '#AAA89F',
    practice: '#8C9A7A',
    project: '#C89B5B',
  };
  return map[type] || '#77766F';
}

export function greetingByHour() {
  const h = new Date().getHours();
  if (h < 12) return 'Good morning';
  if (h < 17) return 'Good afternoon';
  return 'Good evening';
}
