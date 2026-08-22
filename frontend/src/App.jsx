import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';

// Layout
import AppShell from './components/layout/AppShell';

// Pages
import Landing from './pages/Landing';
import Profile from './pages/Profile';
import Recommendation from './pages/Recommendation';
import Overview from './pages/Overview';
import MyRoutes from './pages/MyRoutes';
import RouteDetails from './pages/RouteDetails';
import Skills from './pages/Skills';
import Resources from './pages/Resources';
import CourseDetail from './pages/CourseDetail';
import Projects from './pages/Projects';
import ProjectDetail from './pages/ProjectDetail';
import Progress from './pages/Progress';
import Settings from './pages/Settings';
import Guide from './pages/Guide';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public routes */}
        <Route path="/" element={<Landing />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/recommendation" element={<Recommendation />} />

        {/* Authenticated shell */}
        <Route element={<AppShell />}>
          <Route path="/home" element={<Overview />} />
          <Route path="/routes" element={<MyRoutes />} />
          <Route path="/routes/:routeId" element={<RouteDetails />} />
          <Route path="/skills" element={<Skills />} />
          <Route path="/resources" element={<Resources />} />
          <Route path="/resources/:resourceId" element={<CourseDetail />} />
          <Route path="/projects" element={<Projects />} />
          <Route path="/projects/:projectId" element={<ProjectDetail />} />
          <Route path="/progress" element={<Progress />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/guide" element={<Guide />} />
        </Route>

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
