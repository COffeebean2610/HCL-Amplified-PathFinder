import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  ArrowRight,
  ArrowLeft,
  Clock,
  BarChart2,
  Bookmark,
} from 'lucide-react';

import { TypeBadge } from '../components/common/Badge';
import { Button } from '../components/common/Button';
import { ErrorState, LoadingState } from '../components/common/States';
import { resourceService } from '../services/resourceService';

export default function CourseDetail() {
  const { resourceId } = useParams();
  const navigate = useNavigate();

  const [resource, setResource] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    let mounted = true;

    const loadResource = async () => {
      try {
        setLoading(true);

        const data = await resourceService.getResourceById(resourceId);

        if (mounted) {
          setResource(data);
          setError('');
        }
      } catch (err) {
        if (mounted) {
          setError(
            err?.message || 'Unable to load this resource.'
          );
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    };

    loadResource();

    return () => {
      mounted = false;
    };
  }, [resourceId]);

  const handleSave = () => {
    setSaved((current) => !current);
  };

  const handleStartLearning = () => {
    if (resource?.url) {
      window.open(resource.url, '_blank', 'noopener,noreferrer');
    }
  };

  if (loading) {
    return <LoadingState message="Loading resource..." />;
  }

  if (error || !resource) {
    return (
      <ErrorState
        message={error || 'Resource not found.'}
        onRetry={() => navigate('/resources')}
      />
    );
  }

  return (
    <div className="min-h-full bg-[#0A0A0A] text-[#F3F0E8]">
      <div className="page">

        {/* Back navigation */}
        <button
          type="button"
          onClick={() => navigate('/resources')}
          className="
            flex items-center gap-2
            text-sm text-[#77766F]
            hover:text-[#F3F0E8]
            mb-8
            cursor-pointer
            transition-colors
          "
        >
          <ArrowLeft size={14} />
          Back to Resources
        </button>

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.35 }}
          className="max-w-5xl"
        >

          {/* Meta */}
          <div className="flex items-center gap-4 mb-4 flex-wrap">
            <TypeBadge type={resource.type} />

            <span className="flex items-center gap-1.5 text-xs text-[#77766F]">
              <Clock size={12} />
              {resource.duration || 'Self-paced'}
            </span>

            <span className="flex items-center gap-1.5 text-xs text-[#77766F]">
              <BarChart2 size={12} />
              {resource.level || 'All levels'}
            </span>
          </div>

          {/* Title */}
          <h1 className="
            font-serif
            text-4xl
            md:text-5xl
            leading-tight
            text-[#F3F0E8]
            mb-3
          ">
            {resource.title}
          </h1>

          {/* Provider / subtitle */}
          {resource.subtitle && (
            <p className="text-base text-[#AAA89F] mb-6">
              {resource.subtitle}
            </p>
          )}

          {/* Description */}
          {resource.description && (
            <div className="
              border-l-2
              border-[#C89B5B]/40
              pl-4
              mb-7
            ">
              <p className="
                text-sm
                text-[#AAA89F]
                leading-relaxed
                max-w-4xl
              ">
                {resource.description}
              </p>
            </div>
          )}

          {/* Skills */}
          {resource.skills?.length > 0 && (
            <div className="flex flex-wrap gap-2 mb-8">
              {resource.skills.map((skill) => (
                <span
                  key={skill}
                  className="
                    inline-flex
                    items-center
                    px-3
                    py-1.5
                    rounded-full
                    text-xs
                    bg-[#181713]
                    border
                    border-[#C89B5B]/20
                    text-[#AAA89F]
                  "
                >
                  {skill}
                </span>
              ))}
            </div>
          )}

          {/* Route relevance */}
          {resource.relevance != null && (
            <div className="
              border
              border-[#C89B5B]/20
              rounded-xl
              p-5
              mb-8
              flex
              items-center
              justify-between
              gap-6
              bg-[#0E0E0D]
            ">
              <div>
                <div className="
                  text-[11px]
                  uppercase
                  tracking-[0.18em]
                  text-[#C89B5B]
                  mb-1
                ">
                  Route Relevance
                </div>

                <div className="text-sm text-[#AAA89F]">
                  Directly addresses your current skill gap
                </div>
              </div>

              <div className="
                text-3xl
                font-semibold
                text-[#C89B5B]
                shrink-0
              ">
                {resource.relevance}%
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="flex items-center gap-3 flex-wrap">

            <Button
              icon={<ArrowRight size={14} />}
              onClick={handleStartLearning}
            >
              Start Learning
            </Button>

            <Button
              variant="secondary"
              icon={<Bookmark size={14} />}
              onClick={handleSave}
            >
              {saved ? 'Saved' : 'Save'}
            </Button>

            <Button
              variant="ghost"
              onClick={() => navigate(-1)}
            >
              Back
            </Button>

          </div>

        </motion.div>
      </div>
    </div>
  );
}