import React, { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Search,
  Bell,
  ChevronDown,
  ChevronRight,
  Check,
  ArrowRight,
  Folder,
  BarChart3,
  BookOpen,
  Sparkles,
  Clock3,
  Code2,
  CircleHelp,
  Image as ImageIcon,
} from "lucide-react";

import { projectService } from "../services/projectService";
import { ErrorState, LoadingState } from '../components/common/States';
import "./projects.css";

const categories = [
  "ALL",
  "AI / ML",
  "DATA SCIENCE",
  "GENAI",
  "NLP",
  "COMPUTER VISION",
  "MLOPS",
];

const statusLabels = {
  all: "All",
  "not-started": "Not Started",
  "in-progress": "In Progress",
  completed: "Completed",
};

function projectDomain(project) {
  const text = `${project.title || ''} ${project.stage || ''} ${(project.skills || []).join(' ')}`.toLowerCase();
  if (text.includes('vision') || text.includes('image') || text.includes('cnn')) return 'COMPUTER VISION';
  if (text.includes('generative') || text.includes('rag') || text.includes('embedding')) return 'GENAI';
  if (text.includes('nlp') || text.includes('language')) return 'NLP';
  if (text.includes('deploy') || text.includes('docker') || text.includes('ci/cd')) return 'MLOPS';
  if (text.includes('data') || text.includes('analytics')) return 'DATA SCIENCE';
  return 'AI / ML';
}

function normalizeProject(project) {
  const status = project.status === 'current' ? 'in-progress' : project.status === 'recommended' ? 'upcoming' : project.status || 'upcoming';
  return {
    ...project,
    description: project.description || 'A practical project tailored to your current learning route.',
    domain: project.domain || projectDomain(project),
    progress: Number(project.progress) || (status === 'completed' ? 100 : 0),
    route: project.route || project.stage || 'Learning route',
    stage: project.stage || 'Current stage',
    status,
    skills: Array.isArray(project.skills) ? project.skills : [],
  };
}

function ProjectStatus({ status, progress }) {
  if (status === "completed") {
    return (
      <span className="project-status completed">
        <span className="status-dot">
          <Check size={12} />
        </span>
        COMPLETED
      </span>
    );
  }

  if (status === "in-progress") {
    return (
      <div className="progress-status">
        <span className="progress-label">{progress}% COMPLETE</span>

        <div className="progress-track">
          <div
            className="progress-fill"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>
    );
  }

  return (
    <span className="project-status upcoming">
      UPCOMING
    </span>
  );
}

function ProjectIcon({ status }) {
  if (status === "completed") {
    return (
      <div className="project-circle completed-circle">
        <Check size={18} />
      </div>
    );
  }

  if (status === "in-progress") {
    return (
      <div className="project-circle progress-circle">
        <ArrowRight size={18} />
      </div>
    );
  }

  return <div className="project-circle empty-circle" />;
}

export default function Projects() {
  const navigate = useNavigate();
  const [projects, setProjects] = useState([]);
  const [recommendedProject, setRecommendedProject] = useState(null);
  const [activeCategory, setActiveCategory] = useState("ALL");
  const [statusFilter, setStatusFilter] = useState("all");
  const [search, setSearch] = useState("");
  const [showStatusMenu, setShowStatusMenu] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadProjects = async () => {
      try {
        // The backend's project catalog is already personalized. Avoid issuing
        // two identical CPU-bound recommendation requests on page mount.
        const projectData = await projectService.getProjects();
        const recommendedData = projectData;
        const normalized = (Array.isArray(projectData) ? projectData : []).map(normalizeProject);
        const recommendedProjectData = Array.isArray(recommendedData) ? recommendedData[0] : recommendedData;
        const recommendation = recommendedProjectData ? normalizeProject(recommendedProjectData) : null;
        setProjects(recommendation && !normalized.some((project) => project.id === recommendation.id) ? [...normalized, recommendation] : normalized);
        setRecommendedProject(recommendation);
        setError('');
      } catch (err) {
        setError(err.message || 'Unable to load projects.');
      } finally {
        setLoading(false);
      }
    };
    loadProjects();
  }, []);

  if (loading) return <LoadingState message="Loading projects..." />;
  if (error) return <ErrorState message={error} onRetry={() => window.location.reload()} />;

  const filteredProjects = useMemo(() => {
    return projects.filter((project) => {
      const categoryMatch =
        activeCategory === "ALL" ||
        project.domain.toLowerCase() === activeCategory.toLowerCase();

      const statusMatch =
        statusFilter === "all" ||
        statusFilter === 'not-started'
          ? project.status === 'upcoming'
          : project.status === statusFilter;

      const searchMatch =
        project.title.toLowerCase().includes(search.toLowerCase()) ||
        project.domain.toLowerCase().includes(search.toLowerCase()) ||
        project.description.toLowerCase().includes(search.toLowerCase()) ||
        project.skills.some((skill) =>
          skill.toLowerCase().includes(search.toLowerCase())
        );

      return categoryMatch && statusMatch && searchMatch;
    });
  }, [activeCategory, statusFilter, search]);

  const completedCount = projects.filter(
    (project) => project.status === "completed"
  ).length;

  const inProgressCount = projects.filter(
    (project) => project.status === "in-progress"
  ).length;

  const upcomingCount = projects.filter(
    (project) => project.status === "upcoming"
  ).length;

  return (
    <div className="projects-page">
      {/* =====================================================
          HEADER
      ====================================================== */}
      <header className="projects-header">
        <div>
          <div className="eyebrow">PRACTICAL LEARNING</div>

          <h1>Projects</h1>

          <p>
            Build what you learn. Every project strengthens a skill
            on your route.
          </p>
        </div>

        <div className="projects-header-right">
          <div className="projects-total">
            <span>{projects.length} PROJECTS</span>

            <div className="project-stat-row">
              <div>
                <strong>{completedCount}</strong>
                <small>completed</small>
              </div>

              <div>
                <strong>{inProgressCount}</strong>
                <small>in progress</small>
              </div>

              <div>
                <strong>{upcomingCount}</strong>
                <small>upcoming</small>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* =====================================================
          FILTER BAR
      ====================================================== */}
      <section className="project-panel">
        <div className="project-toolbar">
          <div className="category-tabs">
            {categories.map((category) => (
              <button
                key={category}
                className={
                  activeCategory === category
                    ? "category-tab active"
                    : "category-tab"
                }
                onClick={() => setActiveCategory(category)}
              >
                {category}
              </button>
            ))}
          </div>

          <div className="filter-actions">
            <div className="status-dropdown-wrapper">
              <button
                className="status-filter"
                onClick={() =>
                  setShowStatusMenu((previous) => !previous)
                }
              >
                <span>Status</span>
                <ChevronDown size={15} />
              </button>

              {showStatusMenu && (
                <div className="status-menu">
                  {Object.entries(statusLabels).map(
                    ([value, label]) => (
                      <button
                        key={value}
                        className={
                          statusFilter === value
                            ? "status-option active"
                            : "status-option"
                        }
                        onClick={() => {
                          setStatusFilter(value);
                          setShowStatusMenu(false);
                        }}
                      >
                        {label}
                        {statusFilter === value && (
                          <Check size={14} />
                        )}
                      </button>
                    )
                  )}
                </div>
              )}
            </div>

            <div className="project-search">
              <Search size={16} />

              <input
                type="text"
                placeholder="Search projects..."
                value={search}
                onChange={(event) => setSearch(event.target.value)}
              />
            </div>
          </div>
        </div>

        {/* ===================================================
            TABLE HEADER
        ==================================================== */}
        <div className="project-table-header">
          <span>PROJECT</span>
          <span>DOMAIN</span>
          <span>DESCRIPTION</span>
          <span>SKILLS</span>
          <span>ROUTE STAGE</span>
          <span>STATUS</span>
          <span>ACTION</span>
        </div>

        {/* ===================================================
            PROJECT ROWS
        ==================================================== */}
        <div className="project-list">
          {filteredProjects.length === 0 ? (
            <div className="empty-projects">
              <Folder size={30} />
              <h3>No projects found</h3>
              <p>
                Try changing your search or filter.
              </p>
            </div>
          ) : (
            filteredProjects.map((project) => (
              <div
                className="project-row"
                key={project.id}
              >
                {/* PROJECT */}
                <div className="project-name-cell">
                  <ProjectIcon status={project.status} />

                  <span>{project.title}</span>
                </div>

                {/* DOMAIN */}
                <div
                  className={`project-domain ${project.domain
                    .toLowerCase()
                    .replaceAll(" ", "-")
                    .replace("/", "-")}`}
                >
                  {project.domain}
                </div>

                {/* DESCRIPTION */}
                <div className="project-description">
                  {project.description}
                </div>

                {/* SKILLS */}
                <div className="project-skills">
                  {project.skills.map((skill, index) => (
                    <React.Fragment key={skill}>
                      <span>{skill}</span>

                      {index !== project.skills.length - 1 && (
                        <b>•</b>
                      )}
                    </React.Fragment>
                  ))}
                </div>

                {/* ROUTE */}
                <div className="route-stage">
                  <span>Route:</span>
                  <strong>{project.route}</strong>
                  <small>— {project.stage}</small>
                </div>

                {/* STATUS */}
                <div className="project-status-cell">
                  <ProjectStatus
                    status={project.status}
                    progress={project.progress}
                  />
                </div>

                {/* ACTION */}
                <div className="project-action">
                  {project.status === "completed" ? (
                    <button className="action-button" type="button" onClick={() => navigate(`/projects/${project.id}`)}>
                      View Project
                      <ArrowRight size={15} />
                    </button>
                  ) : project.status === "in-progress" ? (
                    <button className="action-button" type="button" onClick={() => navigate(`/projects/${project.id}`)}>
                      Continue
                      <ArrowRight size={15} />
                    </button>
                  ) : (
                    <button className="action-button" type="button" onClick={() => navigate(`/projects/${project.id}`)}>
                      View Details
                      <ArrowRight size={15} />
                    </button>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </section>

      {/* =====================================================
          BOTTOM CARDS
      ====================================================== */}
      <section className="project-insights">
        {/* PROJECT IMPACT */}
        <div className="insight-card">
          <div className="insight-header">
            <div className="insight-icon">
              <BarChart3 size={18} />
            </div>

            <div>
              <h3>PROJECT IMPACT</h3>
              <p>
                Projects strengthen your learning by applying
                concepts in real-world scenarios.
              </p>
            </div>
          </div>

          <div className="impact-list">
            <div>
              <span>
                <Sparkles size={15} />
                Skills applied
              </span>
              <strong>18</strong>
            </div>

            <div>
              <span>
                <Clock3 size={15} />
                Hours spent
              </span>
              <strong>42h 15m</strong>
            </div>

            <div>
              <span>
                <Code2 size={15} />
                Lines of code
              </span>
              <strong>12.7k+</strong>
            </div>
          </div>
        </div>

        {/* LEARNING */}
        <div className="insight-card">
          <div className="insight-header">
            <div className="insight-icon">
              <BookOpen size={18} />
            </div>

            <div>
              <h3>LEARNING THROUGH PROJECTS</h3>
              <p>
                Projects help you retain more, think deeper and
                build practical confidence.
              </p>
            </div>
          </div>

          <div className="learning-list">
            <div>
              <Check size={15} />
              <span>Better concept retention</span>
              <strong>High</strong>
            </div>

            <div>
              <Check size={15} />
              <span>Hands-on learning</span>
              <strong>Very High</strong>
            </div>

            <div>
              <Check size={15} />
              <span>Career impact</span>
              <strong>High</strong>
            </div>
          </div>
        </div>

        {/* RECOMMENDATION */}
        <div className="insight-card recommendation-card">
          <div className="insight-header">
            <div className="insight-icon">
              <Sparkles size={18} />
            </div>

            <div>
              <h3>NEXT PROJECT RECOMMENDATION</h3>
              <p>
                Based on your current progress and skill gaps.
              </p>
            </div>
          </div>

          <div className="recommendation-project">
            <div className="recommendation-icon">
              <ImageIcon size={19} />
            </div>

            <div className="recommendation-info">
              <h4>{recommendedProject?.title || 'Your next project'}</h4>
              <p>
                {recommendedProject?.description || 'Your next project recommendation will appear as your route develops.'}
              </p>
            </div>

            <button className="preview-button" type="button" onClick={() => recommendedProject && navigate(`/projects/${recommendedProject.id}`)} disabled={!recommendedProject}>
              Preview
              <ArrowRight size={15} />
            </button>
          </div>
        </div>
      </section>
    </div>
  );
}
