import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
  ArrowLeft,
  ArrowRight,
  BarChart2,
  Bookmark,
  CheckCircle2,
  Clock,
  ExternalLink,
  Sparkles,
} from 'lucide-react';
import { motion } from 'framer-motion';

import { resourceService } from '../services/resourceService';
import './CourseDetail.css';

export default function CourseDetail() {
  const { resourceId } = useParams();
  const navigate = useNavigate();

  const [resource, setResource] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    let mounted = true;

    async function loadResource() {
      try {
        setLoading(true);
        setError('');

        const data =
          await resourceService.getResourceById(
            resourceId
          );

        if (!mounted) return;

        setResource(data);
      } catch (err) {
        if (!mounted) return;

        console.error(
          'Failed to load resource:',
          err
        );

        setError(
          err?.response?.data?.detail ||
            err?.message ||
            'Unable to load this resource.'
        );
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    }

    loadResource();

    return () => {
      mounted = false;
    };
  }, [resourceId]);

  function handleSave() {
    setSaved((current) => !current);
  }

  function handleStartLearning() {
    if (!resource?.url) return;

    window.open(
      resource.url,
      '_blank',
      'noopener,noreferrer'
    );
  }

  function getScore() {
    return (
      resource?.relevance ??
      resource?.score ??
      resource?.match_score ??
      resource?.route_relevance ??
      null
    );
  }

  function getSkills() {
    if (Array.isArray(resource?.skills)) {
      return resource.skills;
    }

    if (Array.isArray(resource?.skill_names)) {
      return resource.skill_names;
    }

    return [];
  }

  if (loading) {
    return (
      <div className="course-detail-state">
        <div className="course-detail-spinner" />
        <p>Loading resource...</p>
      </div>
    );
  }

  if (error || !resource) {
    return (
      <div className="course-detail-state">
        <h2>Resource unavailable</h2>

        <p>
          {error || 'Resource not found.'}
        </p>

        <button
          type="button"
          onClick={() => navigate('/resources')}
        >
          <ArrowLeft size={15} />
          Back to Resources
        </button>
      </div>
    );
  }

  const score = getScore();
  const skills = getSkills();

  return (
    <div className="course-detail-page">

      <main className="course-detail-container">

        {/* ================================= */}
        {/* BACK */}
        {/* ================================= */}

        <button
          type="button"
          className="course-back"
          onClick={() => navigate('/resources')}
        >
          <ArrowLeft size={16} />
          Back to Resources
        </button>

        {/* ================================= */}
        {/* HERO */}
        {/* ================================= */}

        <motion.section
          className="course-hero"
          initial={{
            opacity: 0,
            y: 15,
          }}
          animate={{
            opacity: 1,
            y: 0,
          }}
          transition={{
            duration: 0.35,
          }}
        >

          <div className="course-main">

            {/* Meta */}

            <div className="course-meta">

              <span className="course-type">
                {resource.type || 'COURSE'}
              </span>

              <span>
                <Clock size={14} />
                {resource.duration ||
                  'Self-paced'}
              </span>

              <span>
                <BarChart2 size={14} />
                {resource.level ||
                  'All levels'}
              </span>

            </div>

            {/* Title */}

            <h1>
              {resource.title}
            </h1>

            {/* Provider */}

            {resource.subtitle && (
              <div className="course-provider">
                {resource.subtitle}
              </div>
            )}

            {/* Description */}

            <section className="course-about">

              <div className="course-section-label">
                ABOUT THIS RESOURCE
              </div>

              <p>
                {resource.description ||
                  'This resource is designed to strengthen the skills required for your learning route.'}
              </p>

            </section>

            {/* Skills */}

            {skills.length > 0 && (
              <section className="course-skills">

                <div className="course-section-label">
                  SKILLS COVERED
                </div>

                <div className="course-skill-list">

                  {skills.map((skill) => (
                    <span key={skill}>
                      {skill}
                    </span>
                  ))}

                </div>

              </section>
            )}

          </div>

          {/* ================================= */}
          {/* SIDE PANEL */}
          {/* ================================= */}

          <aside className="course-sidebar">

            {score !== null && (
              <div className="relevance-card">

                <div className="course-section-label">
                  ROUTE RELEVANCE
                </div>

                <div className="relevance-score">
                  {Math.round(score)}%
                </div>

                <p>
                  This resource was matched to
                  your current learning route.
                </p>

                <div className="relevance-bar">
                  <span
                    style={{
                      width: `${Math.min(
                        100,
                        Math.max(0, score)
                      )}%`,
                    }}
                  />
                </div>

              </div>
            )}

            <div className="course-actions">

              <button
                type="button"
                className="course-primary-button"
                onClick={handleStartLearning}
                disabled={!resource.url}
              >
                <ArrowRight size={17} />
                Start Learning
                <ExternalLink size={14} />
              </button>

              <button
                type="button"
                className={
                  saved
                    ? 'course-save-button saved'
                    : 'course-save-button'
                }
                onClick={handleSave}
              >
                {saved ? (
                  <CheckCircle2 size={17} />
                ) : (
                  <Bookmark size={17} />
                )}

                {saved
                  ? 'Saved'
                  : 'Save Resource'}
              </button>

            </div>

            {/* Why this resource */}

            <div className="why-card">

              <div className="why-icon">
                <Sparkles size={17} />
              </div>

              <div>

                <strong>
                  Why this resource?
                </strong>

                <p>
                  It is selected using your
                  current skills, learning goals,
                  preferred difficulty, and route
                  requirements.
                </p>

              </div>

            </div>

          </aside>

        </motion.section>

      </main>
    </div>
  );
}