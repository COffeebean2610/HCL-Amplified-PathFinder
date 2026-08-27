import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Sidebar from '../components/Sidebar';
import { resourceService } from '../services/resourceService';
import { projectService } from '../services/projectService';
import { routeService } from '../services/routeService';
import { skillService } from '../services/skillService';
import { ErrorState, LoadingState } from '../components/common/States';

import {
  ChevronRight,
  Bell,
  Target,
  BarChart3,
  Sun,
  Check,
  Play,
  Circle,
  Clock3,
  BookOpen,
  TrendingUp,
  CalendarDays,
  Code2,
  Paperclip,
  List,
  ArrowRight,
  FileText,
  Lightbulb,
  BookMarked,
  CircleCheck,
  Sparkles,
} from "lucide-react";

/* =========================================================
   TOP HEADER
========================================================= */

function Header() {
  return (
    <header className="top-header">

      <div className="studio-label">
        YOUR LEARNING STUDIO
      </div>

     

    </header>
  );
}


/* =========================================================
   HERO
========================================================= */

function Hero() {
  return (
    <section className="hero">

      <h1>
        What do you want
        <br />
        to become?
      </h1>

      <p className="hero-description">
        Tell RouteMaster where you want to go.
        <br />
        We'll help you figure out the sequence to get there.
      </p>

      <RouteInput />

      <div className="examples-label">
        Try these examples:
      </div>

      <div className="example-pills">

        <ExamplePill>
          Become an AI Engineer
        </ExamplePill>

        <ExamplePill>
          Data Scientist
        </ExamplePill>

        <ExamplePill>
          ML Engineer
        </ExamplePill>

        <ExamplePill>
          Full Stack Developer
        </ExamplePill>

        <ExamplePill>
          Cloud Engineer
        </ExamplePill>

      </div>

    </section>
  );
}


function RouteInput() {
  const navigate = useNavigate();

  return (
    <div className="route-input">
      <div className="route-input-content">
        <div className="route-placeholder">
          Tell RouteMaster what you're working toward...
        </div>

        <div className="route-example">
          Example: "I want to become an ML Engineer. I know Python and SQL,
          <br />
          but I need stronger foundations in statistics and machine learning."
        </div>
      </div>

      <div className="route-input-bottom">
        <div className="format-tools">
          <button type="button">
            <strong>B</strong>
          </button>

          <button type="button" className="italic">
            I
          </button>

          <button type="button">
            <List size={20} />
          </button>

          <button type="button">
            <Code2 size={19} />
          </button>

          <button type="button">
            <Paperclip size={19} />
          </button>
        </div>

        <button
          type="button"
          className="plan-button"
          onClick={() => navigate("/recommendation")}
        >
          Plan My Route
          <ArrowRight size={19} />
        </button>
      </div>
    </div>
  );
}

function ExamplePill({ children }) {
  return (
    <button className="example-pill">
      {children}
    </button>
  );
}


/* =========================================================
   RIGHT COLUMN
========================================================= */

/* =========================================================
   CURRENT STAGE
========================================================= */

function CurrentStage({ route }) {
  const navigate = useNavigate();

  return (
    <section className="dashboard-card current-stage-card">
      <div className="card-label">
        YOUR CURRENT STAGE
      </div>

      <div className="stage-row">
        <div className="stage-icon">
          <BarChart3 size={27} strokeWidth={1.6} />
        </div>

        <div className="stage-information">
          <div className="stage-title">
            {route?.current_stage || 'No active route'}
          </div>

          <div className="stage-subtitle">
            {route ? `Stage ${String((route.stages || []).findIndex((stage) => stage.status === 'current') + 1).padStart(2, '0')} of ${String((route.stages || []).length).padStart(2, '0')}` : 'Create a route to begin'}
          </div>
        </div>

        <button
          type="button"
          className="outline-button"
          onClick={() => navigate("/my-routes")}
        >
          View Stage
          <ArrowRight size={17} />
        </button>
      </div>
    </section>
  );
}

/* =========================================================
   DAILY FOCUS
========================================================= */

function DailyFocus({ resource }) {
  const navigate = useNavigate();

  return (
    <section className="dashboard-card daily-focus-card">
      <div className="card-label">
        DAILY FOCUS
      </div>

      <div className="daily-row">
        <div className="daily-icon">
          <Sun size={25} strokeWidth={1.6} />
        </div>

        <div className="daily-information">
          <div className="daily-title">
            {resource?.title || 'No resource recommended yet'}
          </div>

          <div className="daily-time">
            {resource?.duration || 'Choose a learning resource'}
          </div>
        </div>

        <button
          type="button"
          className="outline-button continue-button"
          onClick={async () => {
            if (resource?.id) navigate(`/resources/${resource.id}`);
          }}
        >
          Continue
          <ArrowRight size={17} />
        </button>
      </div>
    </section>
  );
}


/* =========================================================
   ROUTE OVERVIEW
========================================================= */

function RouteOverview({ route }) {
  const navigate = useNavigate();

  const stages = (route?.stages || []).map((stage) => ({
    number: stage.number,
    title: stage.title,
    status: stage.status === 'completed' ? 'Completed' : stage.status === 'current' ? 'Current Stage' : 'Upcoming',
    completed: stage.status === 'completed',
    current: stage.status === 'current',
  }));

  return (
    <section className="dashboard-card route-card">

      <div className="card-label">
        YOUR ROUTE OVERVIEW
      </div>

      <div className="timeline">

        {stages.map((stage) => (

          <div
            className={`timeline-item ${
              stage.current ? "current" : ""
            }`}
            key={stage.number}
          >

            <div
              className={`timeline-dot ${
                stage.completed
                  ? "completed"
                  : stage.current
                  ? "current-dot"
                  : "upcoming"
              }`}
            >

              {stage.completed && (
                <Check size={14} strokeWidth={2.5} />
              )}

              {!stage.completed && stage.current && (
                <span />
              )}

            </div>

            <div className="timeline-content">

              <div className="timeline-title">

                <span className="stage-number">
                  {stage.number}
                </span>

                <span>
                  {stage.title}
                </span>

              </div>

              <div className="timeline-status">
                {stage.status}
              </div>

            </div>

          </div>

        ))}

      </div>

      <button
  type="button"
  className="wide-outline-button"
  onClick={() => navigate("/my-routes")}
>
  View Full Route
  <ArrowRight size={17} />
</button>

    </section>
  );
}


/* =========================================================
   SKILLS
========================================================= */

function SkillsCard({ skills }) {
  const navigate = useNavigate();

  return (
    <section className="dashboard-card skills-card">

      <div className="card-label">
        SKILLS AT A GLANCE
      </div>

      <div className="skills-top">

        <div className="skills-donut">

          <div className="donut-inner">
            <strong>{skills.length}</strong>
            <span>Skills Tracked</span>
          </div>

        </div>

        <div className="skills-legend">

          <Legend
            className="strong"
            label="Strong"
            value={skills.filter((skill) => skill.status === 'strong').length}
          />

          <Legend
            className="developing"
            label="Developing"
            value={skills.filter((skill) => skill.status === 'developing').length}
          />

          <Legend
            className="attention"
            label="Need Attention"
            value={skills.filter((skill) => skill.status === 'needs_attention').length}
          />

        </div>

      </div>

      <div className="card-divider" />

      <div className="subsection-title">
        Top Developing
      </div>

      <SkillProgress
        label="Model Evaluation"
        percentage="48%"
        width="48%"
      />

      <SkillProgress
        label="Feature Engineering"
        percentage="61%"
        width="61%"
      />

      <SkillProgress
        label="Deep Learning"
        percentage="31%"
        width="31%"
      />

      <button
        type="button"
        className="wide-outline-button"
        onClick={() => navigate("/skills")}
      >
        View All Skills
        <ArrowRight size={17} />
      </button>

    </section>
  );
}


function Legend({ className, label, value }) {
  return (
    <div className="legend-row">

      <span className={`legend-dot ${className}`} />

      <span>{label}</span>

      <strong>{value}</strong>

    </div>
  );
}


function SkillProgress({
  label,
  percentage,
  width,
}) {
  return (
    <div className="skill-progress-row">

      <span className="skill-name">
        {label}
      </span>

      <div className="mini-progress">
        <div
          style={{ width }}
        />
      </div>

      <span className="skill-percent">
        {percentage}
      </span>

    </div>
  );
}


/* =========================================================
   PROJECTS
========================================================= */

function ProjectsCard({ apiProjects }) {
  const navigate = useNavigate();

  const projects = apiProjects.map((project) => ({
    ...project,
    status: project.status === 'completed' ? 'Completed' : project.status === 'current' ? 'In Progress' : 'Upcoming',
    percentage: project.status === 'completed' ? '100%' : project.status === 'current' ? `${project.progress || 0}%` : '',
    type: project.status === 'completed' ? 'completed' : project.status === 'current' ? 'progress' : 'upcoming',
  }));

  return (
    <section className="dashboard-card projects-card">

      <div className="card-label">
        PROJECTS ON YOUR ROUTE
      </div>

      <div className="projects-list">

        {projects.map((project, index) => (

          <button
            type="button"
            className="project-row"
            key={project.title}
            onClick={() => project.id && navigate(`/projects/${project.id}`)}
            style={{ width: "100%", border: 0, background: "transparent", padding: 0, textAlign: "left" }}
          >

            <div
              className={`project-icon ${project.type}`}
            >

              {project.type === "completed" && (
                <CircleCheck
                  size={21}
                  strokeWidth={1.7}
                />
              )}

              {project.type === "progress" && (
                <Play
                  size={18}
                  strokeWidth={1.7}
                />
              )}

              {project.type === "upcoming" && (
                <Circle
                  size={20}
                  strokeWidth={1.5}
                />
              )}

            </div>

            <div className="project-information">

              <div className="project-title">
                {project.title}
              </div>

              <div className="project-status">
                {project.status}
              </div>

            </div>

            {project.percentage && (
              <div
                className={`project-percentage ${project.type}`}
              >
                {project.percentage}
              </div>
            )}

          </button>

        ))}

      </div>

      <button
  type="button"
  className="wide-outline-button"
  onClick={() => navigate("/projects")}
>
  View All Projects
  <ArrowRight size={17} />
</button>

    </section>
  );
}


/* =========================================================
   WEEKLY PROGRESS
========================================================= */

function WeeklyProgress() {
  const navigate = useNavigate();

  const days = [
    { day: "Mon", value: 56 },
    { day: "Tue", value: 43 },
    { day: "Wed", value: 63 },
    { day: "Thu", value: 88, active: true },
    { day: "Fri", value: 43 },
    { day: "Sat", value: 44 },
    { day: "Sun", value: 48 },
  ];

  return (
    <section className="dashboard-card weekly-card">

      <div className="card-label">
        PROGRESS THIS WEEK
      </div>

      <div className="weekly-stats">

        <WeeklyStat
          icon={<Clock3 />}
          value="4h 32m"
          label="Time Learned"
        />

        <WeeklyStat
          icon={<BookOpen />}
          value="7"
          label="Lessons Completed"
        />

        <WeeklyStat
          icon={<TrendingUp />}
          value="+3"
          label="Skills Improved"
        />

        <WeeklyStat
          icon={<CalendarDays />}
          value="6"
          label="Day Streak"
        />

      </div>

      <div className="weekly-divider" />

      <div className="chart">
        {days.map((day) => (
          <div
            className={`chart-column ${
              day.active ? "active" : ""
            }`}
            key={day.day}
          >

            <div className="chart-bar-wrapper">
              <div
                className="chart-bar"
                style={{
                  height: `${day.value}%`,
                }}
              />
            </div>

            <span>
              {day.day}
            </span>

          </div>
        ))}
      </div>

      <button
        type="button"
        className="wide-outline-button"
        onClick={() => navigate("/progress")}
      >
        View Detailed Progress
        <ArrowRight size={17} />
      </button>

    </section>
  );
}

function WeeklyStat({
  icon,
  value,
  label,
}) {
  return (
    <div className="weekly-stat">

      <div className="weekly-stat-top">

        {React.cloneElement(icon, {
          size: 20,
          strokeWidth: 1.4,
        })}

        <strong>
          {value}
        </strong>

      </div>

      <span>
        {label}
      </span>

    </div>
  );
}


/* =========================================================
   RECOMMENDATIONS
========================================================= */

function Recommendations({ resources, projects }) {
  const navigate = useNavigate();

  const recommendations = [
    ...resources.slice(0, 3).map((resource) => ({ kind: 'resource', icon: <BookOpen />, title: resource.title, description: resource.description, id: resource.id })),
    ...projects.slice(0, 1).map((project) => ({ kind: 'project', icon: <Code2 />, title: project.title, description: project.description, id: project.id })),
  ];

  return (
    <section className="recommendations-card">

      <div className="recommendations-title">
        WHAT ROUTEMASTER RECOMMENDS YOU DO TODAY
      </div>

      <div className="recommendation-list">

        {recommendations.map((item) => (

          <button
            type="button"
            className="recommendation"
            key={item.title}
            onClick={() => item.id && navigate(item.kind === 'project' ? `/projects/${item.id}` : `/resources/${item.id}`)}
            style={{ width: "100%", border: 0, background: "transparent", padding: 0, textAlign: "left" }}
          >

            <div className="recommendation-icon">
              {React.cloneElement(item.icon, {
                size: 23,
                strokeWidth: 1.5,
              })}
            </div>

            <div className="recommendation-content">

              <div className="recommendation-heading">
                {item.title}
              </div>

              <div className="recommendation-description">
                {item.description}
              </div>

            </div>

            <ArrowRight
              className="recommendation-arrow"
              size={20}
              strokeWidth={1.5}
            />

          </button>

        ))}

      </div>

    </section>
  );
}


function GoalSnapshot({ route }) {
  return (
    <section className="dashboard-card goal-card">
      <div className="card-label">YOUR GOAL SNAPSHOT</div>
      <div className="goal-main">
        <div className="goal-icon"><Target size={25} strokeWidth={1.5} /></div>
        <div className="goal-name">{route?.title || 'Your learning goal'}</div>
        <div className="goal-percentage"><strong>{route?.progress || 0}%</strong><span>Complete</span></div>
      </div>
      <div className="progress-track"><div className="progress-fill" style={{ width: `${route?.progress || 0}%` }} /></div>
      <div className="goal-divider" />
      <div className="goal-dates">
        <div><span>Started</span><strong>12 Aug 2026</strong></div>
        <div className="date-divider" />
        <div><span>Target</span><strong>12 Feb 2027</strong></div>
      </div>
    </section>
  );
}

function RightColumn({ route }) {
  return (
    <aside className="right-column">
      <GoalSnapshot route={route} />
      <WeeklyProgress />
    </aside>
  );
}

function DashboardGrid({ route, resource, skills, projects }) {
  return (
    <section className="dashboard-grid">
      <CurrentStage route={route} />
      <DailyFocus resource={resource} />
      <RouteOverview route={route} />
      <SkillsCard skills={skills} />
      <ProjectsCard apiProjects={projects} />
    </section>
  );
}


/* =========================================================
   MAIN DASHBOARD
========================================================= */

export default function Dashboard() {

  const [data, setData] = useState({ routes: [], projects: [], resources: [], skills: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let mounted = true;

    (async () => {
      try {
        // The AI-backed project and resource endpoints perform synchronous
        // recommendation work. Running them together queues one request behind
        // the other in FastAPI and can exceed the client's 15s timeout even
        // though each endpoint completes normally on its own.
        const [routes, skills] = await Promise.all([
          routeService.getRoutes(),
          skillService.getSkills(),
        ]);
        const projects = await projectService.getRecommended();
        const resources = await resourceService.getRecommended();

        if (!mounted) return;
        setData({ routes: Array.isArray(routes) ? routes : [], projects: Array.isArray(projects) ? projects : [], resources: Array.isArray(resources) ? resources : [], skills: Array.isArray(skills) ? skills : [] });
      } catch (err) {
        if (mounted) setError(err.message || 'Unable to load your dashboard.');
      } finally {
        if (mounted) setLoading(false);
      }
    })();

    return () => { mounted = false; };
  }, []);

  if (loading) return <LoadingState message="Loading your dashboard..." />;
  if (error) return <ErrorState message={error} onRetry={() => window.location.reload()} />;
  const route = data.routes.find((item) => item.is_current) || data.routes[0] || null;

  return (
    <div className="dashboard-layout">

      <Sidebar />

      <main className="main-content">

        <Header />

        <div className="dashboard-container">

          <div className="top-section">

            <Hero />

            <RightColumn route={route} />

          </div>

          <DashboardGrid route={route} resource={data.resources[0] || null} skills={data.skills} projects={data.projects} />

          <Recommendations resources={data.resources} projects={data.projects} />

        </div>

      </main>

    </div>
  );
}
