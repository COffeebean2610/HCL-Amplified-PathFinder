import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Home,
  FolderOpen,
  Settings,
  CircleHelp,
  Search,
  Bell,
  Clock3,
  Layers3,
  BookOpen,
  Box,
  Target,
  Pencil,
  ArrowRight,
  Check,
  BarChart3,
  BriefcaseBusiness,
  FileText,
  FlaskConical,
  Circle,
  Trophy,
  Star,
  ChevronRight,
  Database,
  Code2,
} from "lucide-react";

import "./Progress.css";
import { resourceService } from '../services/resourceService';
import { projectService } from '../services/projectService';
import { progressService } from '../services/progressService';
import { ErrorState, LoadingState } from '../components/common/States';

const stages = [
  {
    number: "01",
    title: "Foundations",
    status: "completed",
    progress: 100,
    skills: "Python · SQL · Git",
    duration: "24 hrs",
  },
  {
    number: "02",
    title: "Data Handling",
    status: "completed",
    progress: 100,
    skills: "NumPy · Pandas · Data Cleaning",
    duration: "18 hrs",
  },
  {
    number: "03",
    title: "Statistics",
    status: "completed",
    progress: 100,
    skills: "Probability · Statistics · Distributions",
    duration: "20 hrs",
  },
  {
    number: "04",
    title: "Machine Learning",
    status: "current",
    progress: 64,
    skills: "Supervised Learning · Classification · Regression · Model Evaluation",
    duration: "32 hrs",
  },
  {
    number: "05",
    title: "Deep Learning",
    status: "upcoming",
    progress: 0,
    skills: "Neural Networks · CNNs · RNNs · Transformers · Transfer Learning",
    duration: "36 hrs",
  },
  {
    number: "06",
    title: "MLOps & Deployment",
    status: "upcoming",
    progress: 0,
    skills: "Docker · APIs · Deployment · Monitoring · CI/CD",
    duration: "24 hrs",
  },
];

const stats = [
  {
    label: "PROGRESS",
    value: "68%",
    sub: "",
    icon: Clock3,
    progress: 68,
  },
  {
    label: "STAGES",
    value: "4 / 6",
    sub: "completed",
    icon: Layers3,
  },
  {
    label: "SKILLS",
    value: "18",
    sub: "skills",
    icon: BookOpen,
  },
  {
    label: "PROJECTS",
    value: "3",
    sub: "projects",
    icon: Box,
  },
  {
    label: "ESTIMATED TIME",
    value: "142 hrs",
    sub: "remaining",
    icon: Clock3,
  },
];

const prerequisites = [
  {
    name: "Python Fundamentals",
    completed: true,
  },
  {
    name: "Data Handling",
    completed: true,
  },
  {
    name: "Statistics & Probability",
    completed: true,
  },
];

function Progress() {
  const navigate = useNavigate();
  const [currentResource, setCurrentResource] = useState(null);
  const [currentProject, setCurrentProject] = useState(null);
  const [progressData, setProgressData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    (async () => {
      try {
        const progress = await progressService.getProgress();
        // These two endpoints are AI-backed and synchronous in the current
        // FastAPI service, so they must not contend with one another.
        const resources = await resourceService.getRecommended();
        const projects = await projectService.getProjects();
        setProgressData(progress);
        setCurrentResource(Array.isArray(resources) ? resources[0] || null : null);
        setCurrentProject(Array.isArray(projects) ? projects.find((project) => project.title === "Customer Churn Predictor") || null : null);
      } catch (err) {
        setError(err.message || 'Unable to load progress.');
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const displayStats = progressData ? [
    { ...stats[0], value: `${progressData.overall ?? 0}%`, progress: progressData.overall ?? 0 },
    { ...stats[1], value: `${progressData.skills_completed ?? 0} / ${progressData.total_skills ?? 0}` },
    { ...stats[2], value: `${progressData.total_skills ?? 0}` },
    { ...stats[3], value: `${progressData.projects_completed ?? 0}` },
    stats[4],
  ] : stats;

  if (loading) return <LoadingState message="Loading progress..." />;
  if (error) return <ErrorState message={error} onRetry={() => window.location.reload()} />;

  const handleNavigation = (path) => {
    navigate(path);
  };

  return (
    <div className="progress-page">

      {/* =========================================================
          MAIN CONTENT
      ========================================================== */}
      <main className="progress-main">
        {/* TOP BAR */}
        <header className="progress-topbar">
          <div className="progress-breadcrumb">
            <span>Home</span>
            <span className="breadcrumb-separator">/</span>
            <span>Learning Routes</span>
            <span className="breadcrumb-separator">/</span>
            <span className="breadcrumb-current">AI / ML Engineer</span>
          </div>

          <div className="progress-top-actions">
            

            
          </div>
        </header>

        <div className="progress-content">
          {/* =====================================================
              HERO
          ====================================================== */}
          <section className="progress-hero">
            <div>
              <div className="hero-eyebrow">YOUR LEARNING ROUTE</div>

              <h1>AI / ML Engineer</h1>

              <p>
                A personalized sequence from your current skill level to
                professional AI / ML engineering.
              </p>
            </div>
          </section>

          {/* =====================================================
              CONTENT GRID
          ====================================================== */}
          <div className="progress-layout">
            {/* ===================================================
                LEFT / CENTER CONTENT
            ==================================================== */}
            <section className="progress-primary">
              {/* STATS */}
              <div className="progress-stats">
                {displayStats.map((stat, index) => {
                  const Icon = stat.icon;

                  return (
                    <div
                      className={`progress-stat ${
                        index === stats.length - 1 ? "last-stat" : ""
                      }`}
                      key={stat.label}
                    >
                      <div className="stat-icon">
                        <Icon size={20} strokeWidth={1.35} />
                      </div>

                      <div className="stat-content">
                        <span className="stat-label">{stat.label}</span>

                        <span className="stat-value">{stat.value}</span>

                        {stat.sub && (
                          <span className="stat-sub">{stat.sub}</span>
                        )}

                        {stat.progress !== undefined && (
                          <div className="stat-progress-track">
                            <div
                              className="stat-progress-fill"
                              style={{
                                width: `${stat.progress}%`,
                              }}
                            />
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* JOURNEY HEADER */}
              <div className="journey-heading">
                <span>YOUR LEARNING JOURNEY</span>
              </div>

              {/* TIMELINE */}
              <div className="journey">
                {stages.map((stage, index) => (
                  <div className="journey-item" key={stage.number}>
                    <div className="timeline-column">
                      <div
                        className={`timeline-node ${stage.status}`}
                      >
                        {stage.status === "completed" ? (
                          <Check size={16} strokeWidth={2.2} />
                        ) : stage.status === "current" ? (
                          <span className="current-node-dot" />
                        ) : (
                          <Circle size={13} strokeWidth={1.2} />
                        )}
                      </div>

                      {index !== stages.length - 1 && (
                        <div
                          className={`timeline-line ${
                            stage.status === "completed"
                              ? "completed-line"
                              : ""
                          }`}
                        />
                      )}
                    </div>

                    <div
                      className={`stage-card ${
                        stage.status === "current" ? "current-stage" : ""
                      }`}
                    >
                      <div className="stage-number">
                        {stage.number}
                      </div>

                      <div className="stage-main">
                        <div className="stage-title-row">
                          <h3>{stage.title}</h3>

                          {stage.status === "completed" && (
                            <span className="stage-status completed">
                              COMPLETED
                            </span>
                          )}

                          {stage.status === "current" && (
                            <span className="stage-status current">
                              CURRENT STAGE
                            </span>
                          )}

                          {stage.status === "upcoming" && (
                            <span className="stage-status upcoming">
                              UPCOMING
                            </span>
                          )}

                          <span
                            className={`stage-percentage ${
                              stage.status === "current"
                                ? "highlight"
                                : ""
                            }`}
                          >
                            {stage.progress}%
                          </span>
                        </div>

                        <div className="stage-skills">
                          <span className="stage-column-label">
                            Skills
                          </span>

                          <span className="stage-skills-text">
                            {stage.skills}
                          </span>
                        </div>
                      </div>

                      <div className="stage-duration">
                        <span>Duration</span>
                        <strong>{stage.duration}</strong>
                      </div>

                      <div className="stage-action">
                        {stage.status === "current" ? (
                          <button
                            className="continue-button"
                            onClick={() => handleNavigation("/resources")}
                          >
                            Continue Learning
                            <ArrowRight size={15} />
                          </button>
                        ) : (
                          <button
                            className="view-details-button"
                            onClick={() => handleNavigation("/my-routes")}
                          >
                            <span>View Details</span>
                            <ArrowRight size={15} />
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                ))}

                {/* DESTINATION */}
                <div className="destination-wrapper">
                  <div className="destination-node">
                    <Trophy size={18} strokeWidth={1.4} />
                  </div>

                  <div className="destination-card">
                    <div className="destination-content">
                      <span className="destination-label">
                        DESTINATION
                      </span>

                      <h3>AI / ML Engineer</h3>

                      <p>Your ultimate learning goal</p>
                    </div>

                    <div className="destination-divider" />

                    <div className="destination-message">
                      <Trophy size={22} strokeWidth={1.4} />

                      <span>
                        Complete all stages and projects
                        <br />
                        to achieve your target skill profile.
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </section>

            {/* ===================================================
                RIGHT SIDEBAR
            ==================================================== */}
            <aside className="progress-right-column">
              {/* TARGET CARD */}
              <div className="side-card target-card">
                <span className="side-card-label">TARGET</span>

                <div className="target-title">
                  <Target size={30} strokeWidth={1.3} />

                  <h3>AI / ML Engineer</h3>
                </div>

                <div className="target-dates">
                  <div>
                    <span>Started</span>
                    <strong>12 Aug 2026</strong>
                  </div>

                  <div>
                    <span>Target</span>
                    <strong>12 Feb 2027</strong>
                  </div>
                </div>

                <button
                  className="edit-route-button"
                  onClick={() => handleNavigation("/my-routes")}
                >
                  <span>Edit Route</span>
                  <Pencil size={14} />
                </button>
              </div>

              {/* CURRENT STAGE */}
              <div className="side-card">
                <span className="side-card-label">
                  CURRENT STAGE OVERVIEW
                </span>

                <div className="current-stage-heading">
                  <div className="stage-overview-icon">
                    <BarChart3 size={26} strokeWidth={1.3} />
                  </div>

                  <div>
                    <h3>Machine Learning</h3>
                    <span>Stage 04 of 06</span>
                  </div>
                </div>

                <p className="stage-description">
                  You are learning how to build, evaluate and improve
                  predictive machine learning models.
                </p>

                <div className="side-progress">
                  <div className="side-progress-track">
                    <div
                      className="side-progress-fill"
                      style={{ width: "64%" }}
                    />
                  </div>

                  <span>64% complete</span>
                </div>

                <div className="stage-overview-list">
                  <button onClick={() => handleNavigation("/my-routes")}>
                    <span>
                      <BriefcaseBusiness size={15} />
                      Modules
                    </span>
                    <strong>
                      5 <ChevronRight size={14} />
                    </strong>
                  </button>

                  <button onClick={() => handleNavigation("/skills")}>
                    <span>
                      <BookOpen size={15} />
                      Skills
                    </span>
                    <strong>
                      9 <ChevronRight size={14} />
                    </strong>
                  </button>

                  <button onClick={() => currentResource?.id && handleNavigation(`/resources/${currentResource.id}`)}>
                    <span>
                      <FileText size={15} />
                      Resources
                    </span>
                    <strong>
                      14 <ChevronRight size={14} />
                    </strong>
                  </button>

                  <button onClick={() => currentResource?.id && handleNavigation(`/resources/${currentResource.id}`)}>
                    <span>
                      <FlaskConical size={15} />
                      Practice Labs
                    </span>
                    <strong>
                      6 <ChevronRight size={14} />
                    </strong>
                  </button>

                  <button>
                    <span>
                      <Clock3 size={15} />
                      Est. Time Left
                    </span>
                    <strong>~11 hrs</strong>
                  </button>
                </div>
              </div>

              {/* PROJECT */}
              <div className="side-card project-stage-card">
                <span className="side-card-label">
                  PROJECT IN THIS STAGE
                </span>

                <button
                  className="stage-project"
                  onClick={() => currentProject?.id && handleNavigation(`/projects/${currentProject.id}`)}
                >
                  <div className="project-icon">
                    <FolderOpen size={19} strokeWidth={1.4} />
                  </div>

                  <div className="project-info">
                    <strong>Customer Churn Predictor</strong>

                    <span>64% complete</span>
                  </div>

                  <ChevronRight size={16} />
                </button>
              </div>

              {/* PREREQUISITES */}
              <div className="side-card prerequisites-card">
                <span className="side-card-label">PREREQUISITES</span>

                <div className="prerequisites-list">
                  {prerequisites.map((item) => (
                    <div
                      className="prerequisite-item"
                      key={item.name}
                    >
                      <span className="prerequisite-check">
                        <Check size={11} strokeWidth={2.3} />
                      </span>

                      <span>{item.name}</span>
                    </div>
                  ))}
                </div>

                <div className="all-prerequisites">
                  <Check size={14} strokeWidth={1.8} />
                  <span>All prerequisites met</span>
                </div>
              </div>
            </aside>
          </div>
        </div>
      </main>
    </div>
  );
}

export default Progress;
