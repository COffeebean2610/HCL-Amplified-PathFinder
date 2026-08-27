import React, { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Search,
  ArrowUpRight,
  ArrowRight,
  BookOpen,
  Play,
  FileText,
  Code2,
  BookMarked,
  FolderKanban,
  Clock3,
  Sparkles,
  Target,
  ExternalLink,
  ChevronRight,
} from "lucide-react";

import "./Resources.css";
import { resourceService } from "../services/resourceService";
import { ErrorState, LoadingState } from '../components/common/States';


// --------------------------------------------------
// RESOURCE DATA
// --------------------------------------------------

const resources = [
  {
    id: 1,
    title: "Cross Validation Explained",
    type: "Article",
    icon: FileText,
    duration: "12 min",
    difficulty: "Intermediate",
    description:
      "Understand cross-validation techniques and how they improve model evaluation.",
    skills: ["Model Evaluation", "Machine Learning"],
    relevance: 94,
  },
  {
    id: 2,
    title: "Classification Metrics Deep Dive",
    type: "Video",
    icon: Play,
    duration: "28 min",
    difficulty: "Intermediate",
    description:
      "Learn precision, recall, F1-score, ROC-AUC and when to use each metric.",
    skills: ["Classification", "Model Evaluation"],
    relevance: 91,
  },
  {
    id: 3,
    title: "Hands-on Model Evaluation",
    type: "Practice",
    icon: Code2,
    duration: "40 min",
    difficulty: "Intermediate",
    description:
      "Apply model evaluation techniques using real datasets and Python.",
    skills: ["Python", "Model Evaluation"],
    relevance: 89,
  },
  {
    id: 4,
    title: "Feature Engineering for ML",
    type: "Course",
    icon: BookOpen,
    duration: "90 min",
    difficulty: "Intermediate",
    description:
      "Build stronger machine learning models through effective feature engineering.",
    skills: ["Feature Engineering", "Machine Learning"],
    relevance: 86,
  },
  {
    id: 5,
    title: "Ensemble Methods Explained",
    type: "Video",
    icon: Play,
    duration: "35 min",
    difficulty: "Intermediate",
    description:
      "Explore bagging, boosting and ensemble learning with practical examples.",
    skills: ["Machine Learning", "Ensemble Methods"],
    relevance: 83,
  },
  {
    id: 6,
    title: "Introduction to Deep Learning",
    type: "Course",
    icon: BookOpen,
    duration: "120 min",
    difficulty: "Advanced",
    description:
      "A practical introduction to neural networks and modern deep learning.",
    skills: ["Deep Learning", "Neural Networks"],
    relevance: 79,
  },
  {
    id: 7,
    title: "Statistics for Machine Learning",
    type: "Book",
    icon: BookMarked,
    duration: "3 hrs",
    difficulty: "Intermediate",
    description:
      "Build the statistical foundation required for machine learning.",
    skills: ["Statistics", "Machine Learning"],
    relevance: 76,
  },
  {
    id: 8,
    title: "Docker for ML Engineers",
    type: "Documentation",
    icon: Code2,
    duration: "60 min",
    difficulty: "Advanced",
    description:
      "Learn how to containerize and deploy machine learning applications.",
    skills: ["Docker", "MLOps"],
    relevance: 68,
  },
];


// --------------------------------------------------
// RESOURCE TYPE DATA
// --------------------------------------------------

const resourceTypes = [
  {
    title: "Courses",
    subtitle: "Structured learning",
    count: 12,
    icon: BookOpen,
    className: "course",
  },
  {
    title: "Videos",
    subtitle: "Visual explanations",
    count: 18,
    icon: Play,
    className: "video",
  },
  {
    title: "Articles",
    subtitle: "Focused concepts",
    count: 24,
    icon: FileText,
    className: "article",
  },
  {
    title: "Documentation",
    subtitle: "Deep references",
    count: 9,
    icon: Code2,
    className: "documentation",
  },
  {
    title: "Practice",
    subtitle: "Hands-on learning",
    count: 14,
    icon: Target,
    className: "practice",
  },
  {
    title: "Projects",
    subtitle: "Build real things",
    count: 6,
    icon: FolderKanban,
    className: "projects",
  },
];


// --------------------------------------------------
// FILTERS
// --------------------------------------------------

const filters = [
  "All Types",
  "Course",
  "Video",
  "Article",
  "Documentation",
  "Book",
  "Practice",
];

const resourceIcons = { course: BookOpen, video: Play, article: FileText, documentation: Code2, practice: Code2, book: BookMarked };
const normalizeResource = (resource) => ({
  ...resource,
  type: `${resource.type || "Article"}`.replace(/^./, (letter) => letter.toUpperCase()),
  difficulty: resource.difficulty || resource.level || "Intermediate",
  skills: Array.isArray(resource.skills) ? resource.skills : [],
  icon: resourceIcons[`${resource.type || "article"}`.toLowerCase()] || FileText,
});


// --------------------------------------------------
// RESOURCE CARD
// --------------------------------------------------

function ResourceCard({ resource, onOpen }) {
  const Icon = resource.icon;

  return (
    <article className="resource-card">
      <div className="resource-card-left">
        <div className={`resource-icon ${resource.type.toLowerCase()}`}>
          <Icon size={18} strokeWidth={1.8} />
        </div>

        <div className="resource-card-content">
          <div className="resource-meta">
            <span className={`resource-type ${resource.type.toLowerCase()}`}>
              {resource.type}
            </span>

            <span className="resource-duration">
              <Clock3 size={13} />
              {resource.duration}
            </span>

            <span className="resource-dot">•</span>

            <span className="resource-difficulty">
              {resource.difficulty}
            </span>
          </div>

          <h3>{resource.title}</h3>

          <p>{resource.description}</p>

          <div className="resource-tags">
            {resource.skills.map((skill) => (
              <span key={skill}>{skill}</span>
            ))}
          </div>
        </div>
      </div>

      <div className="resource-card-right">
        <div className="relevance">
          <strong>{resource.relevance}%</strong>
          <span>Route relevance</span>
        </div>

        <button className="resource-action" type="button" onClick={() => onOpen(resource.id)}>
          <ArrowUpRight size={17} />
        </button>
      </div>
    </article>
  );
}


// --------------------------------------------------
// MAIN PAGE
// --------------------------------------------------

export default function Resources() {
  const navigate = useNavigate();
  const [activeFilter, setActiveFilter] = useState("All Types");
  const [searchQuery, setSearchQuery] = useState("");
  const [resourceData, setResourceData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    (async () => {
      try {
        const data = await resourceService.getResources();
        setResourceData((Array.isArray(data) ? data : []).map(normalizeResource));
        setError('');
      } catch (err) {
        setError(err.message || 'Unable to load resources.');
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const filteredResources = useMemo(() => {
    return resourceData.filter((resource) => {
      const matchesFilter =
        activeFilter === "All Types" ||
        resource.type === activeFilter;

      const query = searchQuery.toLowerCase().trim();

      const matchesSearch =
        !query ||
        resource.title.toLowerCase().includes(query) ||
        resource.description.toLowerCase().includes(query) ||
        resource.skills.some((skill) =>
          skill.toLowerCase().includes(query)
        );

      return matchesFilter && matchesSearch;
    });
  }, [activeFilter, resourceData, searchQuery]);
  const recommendedResource = resourceData.find((resource) => resource.is_current) || resourceData[0] || null;

  if (loading) return <LoadingState message="Loading resources..." />;
  if (error) return <ErrorState message={error} onRetry={() => window.location.reload()} />;


  return (
    <div className="resources-page">

        {/* -------------------------------- */}
        {/* HEADER */}
        {/* -------------------------------- */}

        <header className="resources-header">
          <div>
            <span className="page-eyebrow">LEARNING RESOURCES</span>

            <h1>Resources</h1>

            <p>
              Discover the right resources to strengthen your skills
              and move forward on your learning route.
            </p>
          </div>

          <div className="resources-header-stat">
            <span>PERSONALIZED FOR YOU</span>
            <strong>{recommendedResource?.relevance || 0}%</strong>
            <small>average route relevance</small>
          </div>
        </header>


        {/* -------------------------------- */}
        {/* SEARCH + FILTERS */}
        {/* -------------------------------- */}

        <section className="resource-controls">

          <div className="resource-search">
            <Search size={19} />

            <input
              type="text"
              placeholder="Search resources, skills or topics..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />

            {searchQuery && (
              <button
                className="clear-search"
                onClick={() => setSearchQuery("")}
                type="button"
              >
                ×
              </button>
            )}
          </div>


          <div className="resource-filters">
            {filters.map((filter) => (
              <button
                key={filter}
                type="button"
                className={
                  activeFilter === filter
                    ? "filter-btn active"
                    : "filter-btn"
                }
                onClick={() => setActiveFilter(filter)}
              >
                {filter}
              </button>
            ))}
          </div>

        </section>


        {/* -------------------------------- */}
        {/* PERSONALIZED RECOMMENDATION */}
        {/* -------------------------------- */}

        <section className="recommended-resource">

          <div className="recommended-glow" />

          <div className="recommended-icon">
            <Sparkles size={21} />
          </div>

          <div className="recommended-content">

            <div className="recommended-label">
              <span>PERSONALIZED FOR YOU</span>

              <span className="recommended-score">
                {recommendedResource?.relevance || 0}% ROUTE MATCH
              </span>
            </div>

            <h2>{recommendedResource?.title || 'No recommended resource yet'}</h2>

            <p>
              {recommendedResource?.description || 'Resources tailored to your current route will appear here.'}
            </p>

            <div className="recommended-tags">
              {(recommendedResource?.skills || []).slice(0, 2).map((skill) => <span key={skill}>{skill}</span>)}
              <span>{recommendedResource?.duration || '—'}</span>
              <span>{recommendedResource?.difficulty || '—'}</span>
            </div>

            <div className="recommended-actions">

              <button className="primary-resource-btn" type="button" onClick={() => recommendedResource?.id && navigate(`/resources/${recommendedResource.id}`)}>
                <Play size={16} />
                Start Learning
                <ArrowRight size={16} />
              </button>

              <button className="secondary-resource-btn" type="button" onClick={() => recommendedResource?.id && navigate(`/resources/${recommendedResource.id}`)}>
                Why recommended?
                <ChevronRight size={15} />
              </button>

            </div>

          </div>

          <div className="recommended-progress">

            <div className="progress-ring">
              <svg viewBox="0 0 100 100">
                <circle
                  className="progress-ring-bg"
                  cx="50"
                  cy="50"
                  r="42"
                />

                <circle
                  className="progress-ring-value"
                  cx="50"
                  cy="50"
                  r="42"
                />
              </svg>

              <div>
                <strong>48%</strong>
                <span>Current</span>
              </div>
            </div>

            <div className="target-info">
              <span>REQUIRED</span>
              <strong>75%</strong>
            </div>

          </div>

        </section>


        {/* -------------------------------- */}
        {/* ALL RESOURCES */}
        {/* -------------------------------- */}

        <section className="all-resources-section">

          <div className="section-heading">
            <div>
              <span className="section-eyebrow">EXPLORE</span>
              <h2>All Resources</h2>
            </div>

            <span className="resource-count">
              {filteredResources.length} resources
            </span>
          </div>


          <div className="resources-grid">

            {filteredResources.map((resource) => (
              <ResourceCard
                key={resource.id}
                resource={resource}
                onOpen={(resourceId) => navigate(`/resources/${resourceId}`)}
              />
            ))}

          </div>


          {filteredResources.length === 0 && (
            <div className="empty-resources">
              <Search size={30} />
              <h3>No resources found</h3>
              <p>
                Try searching for another skill or resource type.
              </p>

              <button
                type="button"
                onClick={() => {
                  setSearchQuery("");
                  setActiveFilter("All Types");
                }}
              >
                Clear filters
              </button>
            </div>
          )}

        </section>


        {/* -------------------------------- */}
        {/* RESOURCE TYPES */}
        {/* -------------------------------- */}

        <section className="resource-types-section">

          <div className="section-heading">
            <div>
              <span className="section-eyebrow">BROWSE BY TYPE</span>
              <h2>Resource Library</h2>
            </div>
          </div>


          <div className="resource-types-grid">

            {resourceTypes.map((item) => {
              const Icon = item.icon;

              return (
                <button
                  key={item.title}
                  className={`resource-type-card ${item.className}`}
                  type="button"
                  onClick={() => {
                    if (filters.includes(item.title.slice(0, -1))) {
                      setActiveFilter(item.title.slice(0, -1));
                    }
                  }}
                >

                  <div className="type-card-icon">
                    <Icon size={20} />
                  </div>

                  <div className="type-card-content">
                    <h3>{item.title}</h3>
                    <p>{item.subtitle}</p>
                  </div>

                  <div className="type-card-count">
                    {item.count}
                  </div>

                  <ArrowRight
                    className="type-card-arrow"
                    size={17}
                  />

                </button>
              );
            })}

          </div>

        </section>

    </div>
  );
}
