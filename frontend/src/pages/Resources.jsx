import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Search,
  SlidersHorizontal,
  Sparkles,
  ArrowRight,
  Play,
  Bookmark,
  Clock,
  BarChart3,
  BookOpen,
  Video,
  FileText,
  BookMarked,
  Dumbbell,
  ExternalLink,
} from 'lucide-react';

import { resourceService } from '../services/resourceService';
import './Resources.css';

const RESOURCE_TYPES = [
  { label: 'All Types', value: 'all' },
  { label: 'Course', value: 'course' },
  { label: 'Video', value: 'video' },
  { label: 'Article', value: 'article' },
  { label: 'Documentation', value: 'documentation' },
  { label: 'Book', value: 'book' },
  { label: 'Practice', value: 'practice' },
];

const TYPE_ICONS = {
  course: BookOpen,
  video: Video,
  article: FileText,
  documentation: BookMarked,
  book: BookOpen,
  practice: Dumbbell,
};

function normalizeType(type) {
  if (!type) return 'course';

  return String(type)
    .toLowerCase()
    .replace(/[\s_-]+/g, '');
}

function getTypeIcon(type) {
  const normalized = normalizeType(type);

  if (normalized === 'documentation') return BookMarked;
  if (normalized === 'practice') return Dumbbell;

  return (
    TYPE_ICONS[normalized] ||
    BookOpen
  );
}

function normalizeResources(data) {
  if (Array.isArray(data)) return data;

  if (Array.isArray(data?.resources)) {
    return data.resources;
  }

  if (Array.isArray(data?.items)) {
    return data.items;
  }

  if (Array.isArray(data?.data)) {
    return data.data;
  }

  return [];
}

function getResourceId(resource) {
  return (
    resource?.id ??
    resource?.resource_id ??
    resource?.resourceId ??
    resource?.course_id
  );
}

function getResourceSkills(resource) {
  if (Array.isArray(resource?.skills)) {
    return resource.skills;
  }

  if (Array.isArray(resource?.skill_names)) {
    return resource.skill_names;
  }

  return [];
}

function getRelevance(resource) {
  const value =
    resource?.relevance ??
    resource?.route_relevance ??
    resource?.match ??
    resource?.match_score ??
    resource?.route_match;

  if (value === null || value === undefined || value === '') {
    return null;
  }

  const number = Number(value);

  if (Number.isNaN(number)) {
    return null;
  }

  // Handle APIs returning 0.38 instead of 38.
  if (number > 0 && number <= 1) {
    return Math.round(number * 100);
  }

  return Math.round(number);
}

function getAverageRelevance(resources) {
  const values = resources
    .map(getRelevance)
    .filter(
      (value) =>
        value !== null &&
        !Number.isNaN(value)
    );

  if (!values.length) return 0;

  return Math.round(
    values.reduce((sum, value) => sum + value, 0) /
      values.length
  );
}

export default function Resources() {
  const navigate = useNavigate();

  const [resources, setResources] = useState([]);
  const [recommended, setRecommended] = useState(null);

  const [loading, setLoading] = useState(true);
  const [recommendedLoading, setRecommendedLoading] =
    useState(true);

  const [error, setError] = useState('');
  const [search, setSearch] = useState('');
  const [activeType, setActiveType] = useState('all');
  const [savedResources, setSavedResources] = useState(
    []
  );

  useEffect(() => {
    const saved =
      JSON.parse(
        localStorage.getItem('routemaster_saved_resources') ||
          '[]'
      ) || [];

    setSavedResources(saved);
  }, []);

  useEffect(() => {
    let mounted = true;

    async function loadResources() {
      try {
        setLoading(true);
        setError('');

        const [resourceResponse, recommendedResponse] =
          await Promise.all([
            resourceService.getResources(),
            resourceService.getRecommended(),
          ]);

        if (!mounted) return;

        const resourceList =
          normalizeResources(resourceResponse);

        const recommendedList =
          normalizeResources(recommendedResponse);

        setResources(resourceList);

        /*
         * The recommendation endpoint should normally return
         * the personalized resource(s) for the current user.
         *
         * We use the first recommendation as the featured
         * resource instead of hardcoding a specific course.
         */
        setRecommended(
          recommendedList.length
            ? recommendedList[0]
            : null
        );
      } catch (err) {
        if (!mounted) return;

        setError(
          err?.response?.data?.detail ||
            err?.message ||
            'Unable to load learning resources.'
        );
      } finally {
        if (mounted) {
          setLoading(false);
          setRecommendedLoading(false);
        }
      }
    }

    loadResources();

    return () => {
      mounted = false;
    };
  }, []);

  const filteredResources = useMemo(() => {
    const query = search.trim().toLowerCase();

    return resources.filter((resource) => {
      const type = normalizeType(resource?.type);

      const matchesType =
        activeType === 'all' ||
        type === normalizeType(activeType);

      if (!matchesType) return false;

      if (!query) return true;

      const searchableText = [
        resource?.title,
        resource?.subtitle,
        resource?.description,
        resource?.provider,
        ...(getResourceSkills(resource) || []),
      ]
        .filter(Boolean)
        .join(' ')
        .toLowerCase();

      return searchableText.includes(query);
    });
  }, [resources, search, activeType]);

  const averageRelevance = useMemo(
    () => getAverageRelevance(resources),
    [resources]
  );

  const recommendedRelevance = recommended
    ? getRelevance(recommended)
    : null;

  const toggleSave = (resource) => {
    const id = getResourceId(resource);

    if (!id) return;

    setSavedResources((current) => {
      const exists = current.includes(id);

      const next = exists
        ? current.filter((item) => item !== id)
        : [...current, id];

      localStorage.setItem(
        'routemaster_saved_resources',
        JSON.stringify(next)
      );

      return next;
    });
  };

  const isSaved = (resource) => {
    const id = getResourceId(resource);

    return id
      ? savedResources.includes(id)
      : false;
  };

  const openResource = (resource) => {
    const id = getResourceId(resource);

    if (id) {
      navigate(`/resources/${id}`);
      return;
    }

    if (resource?.url) {
      window.open(
        resource.url,
        '_blank',
        'noopener,noreferrer'
      );
    }
  };

  const handleStartLearning = (event, resource) => {
    event.stopPropagation();

    if (resource?.url) {
      window.open(
        resource.url,
        '_blank',
        'noopener,noreferrer'
      );
      return;
    }

    openResource(resource);
  };

  if (loading) {
    return (
      <div className="resources-page">
        <div className="resources-loading">
          <div className="resources-loading-spinner" />

          <p>Loading your learning resources...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="resources-page">
      <div className="resources-container">

        {/* =====================================================
            PAGE HEADER
        ====================================================== */}

        <header className="resources-header">
          <div className="resources-header-main">
            <div className="resources-eyebrow">
              LEARNING RESOURCES
            </div>

            <h1>Resources</h1>

            <p>
              Discover the right resources to strengthen
              your skills and move forward on your learning
              route.
            </p>
          </div>

          <div className="resources-header-stat">
            <span>PERSONALIZED FOR YOU</span>

            <strong>
              {averageRelevance}%
            </strong>

            <small>
              average route relevance
            </small>
          </div>
        </header>

        {/* =====================================================
            SEARCH
        ====================================================== */}

        <section className="resources-controls">
          <div className="resources-search">
            <Search size={19} />

            <input
              type="text"
              value={search}
              onChange={(event) =>
                setSearch(event.target.value)
              }
              placeholder="Search resources, skills or topics..."
            />

            {search && (
              <button
                type="button"
                className="search-clear"
                onClick={() => setSearch('')}
              >
                Clear
              </button>
            )}
          </div>

          <div className="resources-filters">
            <div className="filter-label">
              <SlidersHorizontal size={15} />
              <span>FILTER BY TYPE</span>
            </div>

            <div className="filter-buttons">
              {RESOURCE_TYPES.map((type) => (
                <button
                  key={type.value}
                  type="button"
                  className={
                    activeType === type.value
                      ? 'filter-button active'
                      : 'filter-button'
                  }
                  onClick={() =>
                    setActiveType(type.value)
                  }
                >
                  {type.label}
                </button>
              ))}
            </div>
          </div>
        </section>

        {/* =====================================================
            ERROR
        ====================================================== */}

        {error && (
          <div className="resources-error">
            <div>
              <strong>
                Unable to load some resources
              </strong>

              <p>{error}</p>
            </div>

            <button
              type="button"
              onClick={() => window.location.reload()}
            >
              Retry
            </button>
          </div>
        )}

        {/* =====================================================
            PERSONALIZED RECOMMENDATION
        ====================================================== */}

        <section className="recommended-section">
          <div className="section-heading-row">
            <div>
              <span className="section-eyebrow">
                YOUR NEXT STEP
              </span>

              <h2>
                Recommended for your route
              </h2>
            </div>

            {recommendedRelevance !== null && (
              <div className="section-match">
                <span>ROUTE MATCH</span>

                <strong>
                  {recommendedRelevance}%
                </strong>
              </div>
            )}
          </div>

          {recommendedLoading ? (
            <div className="recommendation-skeleton">
              <div />
              <div />
              <div />
            </div>
          ) : recommended ? (
            <RecommendedResource
              resource={recommended}
              saved={isSaved(recommended)}
              onSave={() =>
                toggleSave(recommended)
              }
              onOpen={() =>
                openResource(recommended)
              }
              onStart={(event) =>
                handleStartLearning(
                  event,
                  recommended
                )
              }
            />
          ) : (
            <div className="empty-recommendation">
              <Sparkles size={22} />

              <div>
                <strong>
                  No personalized recommendation yet
                </strong>

                <p>
                  Complete your profile and skill
                  preferences to receive a resource
                  recommendation tailored to your route.
                </p>
              </div>
            </div>
          )}
        </section>

        {/* =====================================================
            ALL RESOURCES
        ====================================================== */}

        <section className="all-resources-section">
          <div className="section-heading-row">
            <div>
              <span className="section-eyebrow">
                EXPLORE
              </span>

              <h2>All Resources</h2>
            </div>

            <span className="resource-count">
              {filteredResources.length}{' '}
              {filteredResources.length === 1
                ? 'resource'
                : 'resources'}
            </span>
          </div>

          {filteredResources.length === 0 ? (
            <div className="resources-empty">
              <Search size={26} />

              <h3>No resources found</h3>

              <p>
                Try another search term or choose a
                different resource type.
              </p>

              <button
                type="button"
                onClick={() => {
                  setSearch('');
                  setActiveType('all');
                }}
              >
                Clear filters
              </button>
            </div>
          ) : (
            <div className="resources-grid">
              {filteredResources.map(
                (resource, index) => (
                  <ResourceCard
                    key={
                      getResourceId(resource) ||
                      `${resource?.title}-${index}`
                    }
                    resource={resource}
                    saved={isSaved(resource)}
                    onSave={() =>
                      toggleSave(resource)
                    }
                    onOpen={() =>
                      openResource(resource)
                    }
                  />
                )
              )}
            </div>
          )}
        </section>

      </div>
    </div>
  );
}


/* =============================================================
   RECOMMENDED RESOURCE
============================================================= */

function RecommendedResource({
  resource,
  saved,
  onSave,
  onOpen,
  onStart,
}) {
  const TypeIcon = getTypeIcon(resource?.type);

  const skills = getResourceSkills(resource);

  const relevance = getRelevance(resource);

  return (
    <motion.article
      className="featured-resource"
      initial={{
        opacity: 0,
        y: 16,
      }}
      animate={{
        opacity: 1,
        y: 0,
      }}
      transition={{
        duration: 0.4,
      }}
      onClick={onOpen}
    >
      <div className="featured-glow" />

      <div className="featured-icon">
        <Sparkles size={23} />
      </div>

      <div className="featured-content">

        <div className="featured-topline">
          <span className="personalized-badge">
            <Sparkles size={13} />
            PERSONALIZED FOR YOU
          </span>

          {relevance !== null && (
            <span className="match-badge">
              {relevance}% ROUTE MATCH
            </span>
          )}
        </div>

        <h3>
          {resource?.title ||
            'Recommended learning resource'}
        </h3>

        {resource?.subtitle && (
          <div className="featured-provider">
            {resource.subtitle}
          </div>
        )}

        {resource?.description && (
          <p className="featured-description">
            {resource.description}
          </p>
        )}

        <div className="resource-meta">
          {resource?.duration && (
            <span>
              <Clock size={14} />
              {resource.duration}
            </span>
          )}

          {resource?.level && (
            <span>
              <BarChart3 size={14} />
              {resource.level}
            </span>
          )}

          <span>
            <BookOpen size={14} />
            {String(
              resource?.type || 'Course'
            ).toUpperCase()}
          </span>
        </div>

        {skills.length > 0 && (
          <div className="resource-skills">
            {skills.slice(0, 5).map(
              (skill, index) => (
                <span key={`${skill}-${index}`}>
                  {skill}
                </span>
              )
            )}
          </div>
        )}

        <div className="featured-actions">
          <button
            type="button"
            className="primary-resource-button"
            onClick={onStart}
          >
            <Play size={15} />
            Start Learning
            <ArrowRight size={16} />
          </button>

          <button
            type="button"
            className={
              saved
                ? 'secondary-resource-button saved'
                : 'secondary-resource-button'
            }
            onClick={(event) => {
              event.stopPropagation();
              onSave();
            }}
          >
            <Bookmark
              size={16}
              fill={saved ? 'currentColor' : 'none'}
            />

            {saved ? 'Saved' : 'Save'}
          </button>

          {resource?.url && (
            <button
              type="button"
              className="external-resource-button"
              onClick={onStart}
            >
              <ExternalLink size={15} />
              Open resource
            </button>
          )}
        </div>
      </div>

      <div className="featured-score">
        <div
          className="score-ring"
          style={{
            '--score':
              relevance !== null
                ? `${relevance * 3.6}deg`
                : '0deg',
          }}
        >
          <div className="score-ring-inner">
            <strong>
              {relevance !== null
                ? `${relevance}%`
                : '—'}
            </strong>

            <span>MATCH</span>
          </div>
        </div>
      </div>
    </motion.article>
  );
}


/* =============================================================
   RESOURCE CARD
============================================================= */

function ResourceCard({
  resource,
  saved,
  onSave,
  onOpen,
}) {
  const TypeIcon = getTypeIcon(resource?.type);

  const relevance = getRelevance(resource);

  const skills = getResourceSkills(resource);

  return (
    <motion.article
      className="resource-card"
      initial={{
        opacity: 0,
        y: 12,
      }}
      animate={{
        opacity: 1,
        y: 0,
      }}
      transition={{
        duration: 0.25,
      }}
      whileHover={{
        y: -4,
      }}
      onClick={onOpen}
    >
      <div className="resource-card-top">
        <div className="resource-type">
          <TypeIcon size={15} />

          <span>
            {resource?.type || 'Course'}
          </span>
        </div>

        <button
          type="button"
          className={
            saved
              ? 'card-bookmark active'
              : 'card-bookmark'
          }
          onClick={(event) => {
            event.stopPropagation();
            onSave();
          }}
          aria-label={
            saved
              ? 'Remove bookmark'
              : 'Save resource'
          }
        >
          <Bookmark
            size={16}
            fill={saved ? 'currentColor' : 'none'}
          />
        </button>
      </div>

      <div className="resource-card-body">
        <h3>
          {resource?.title ||
            'Learning resource'}
        </h3>

        {resource?.subtitle && (
          <p className="resource-provider">
            {resource.subtitle}
          </p>
        )}

        {resource?.description && (
          <p className="resource-card-description">
            {resource.description}
          </p>
        )}

        <div className="resource-card-meta">
          {resource?.duration && (
            <span>
              <Clock size={13} />
              {resource.duration}
            </span>
          )}

          {resource?.level && (
            <span>
              <BarChart3 size={13} />
              {resource.level}
            </span>
          )}
        </div>

        {skills.length > 0 && (
          <div className="resource-card-skills">
            {skills.slice(0, 3).map(
              (skill, index) => (
                <span key={`${skill}-${index}`}>
                  {skill}
                </span>
              )
            )}

            {skills.length > 3 && (
              <span>
                +{skills.length - 3}
              </span>
            )}
          </div>
        )}
      </div>

      <div className="resource-card-footer">
        <button
          type="button"
          onClick={(event) => {
            event.stopPropagation();
            onOpen();
          }}
          className="view-resource-button"
        >
          View resource
          <ArrowRight size={15} />
        </button>

        {relevance !== null && (
          <div className="card-relevance">
            <span>{relevance}%</span>
            <small>match</small>
          </div>
        )}
      </div>
    </motion.article>
  );
}