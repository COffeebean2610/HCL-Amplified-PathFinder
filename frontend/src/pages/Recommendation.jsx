import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowRight, Check, ChevronRight } from 'lucide-react';
import { Button } from '../components/common/Button';
import { profileService } from '../services/profileService';
import { routeService } from '../services/routeService';
import { LoadingState } from '../components/common/States';
import { useAuth } from '../context/AuthContext';

function RecommendationReason({ children }) {
  return (
    <div className="rm-rec-reason">
      <span className="rm-rec-reason__icon">
        <Check size={13} />
      </span>
      <span>{children}</span>
    </div>
  );
}

function BreakdownRow({ label, value }) {
  return (
    <div className="rm-rec-breakdown-row">
      <div className="rm-rec-breakdown-row__head">
        <span>{label}</span>
        <span>{value}%</span>
      </div>
      <div className="rm-rec-breakdown-row__track">
        <div className="rm-rec-breakdown-row__fill" style={{ width: `${value}%` }} />
      </div>
    </div>
  );
}

function ProfileBlock({ label, value, list = false }) {
  const empty = list ? !value?.length : !value;

  return (
    <div className="rm-rec-profile-item">
      <div className="rm-rec-profile-item__label">{label}</div>
      {empty ? (
        <div className="rm-rec-profile-item__value is-muted">Not provided</div>
      ) : list ? (
        <div className="rm-rec-profile-tags">
          {value.map((item) => (
            <span key={item} className="rm-rec-profile-tag">
              {item}
            </span>
          ))}
        </div>
      ) : (
        <div className="rm-rec-profile-item__value">{value}</div>
      )}
    </div>
  );
}

export default function Recommendation() {
  const navigate = useNavigate();
  const { currentUser } = useAuth();
  const [loading, setLoading] = useState(true);
  const [recommendations, setRecommendations] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [profile, setProfile] = useState(currentUser);
  const [buildingRoute, setBuildingRoute] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    let mounted = true;

    (async () => {
      try {
        const [recommendationData, profileData] = await Promise.all([
          profileService.getCareerRecommendation({}),
          profileService.getProfile(),
        ]);

        if (!mounted) return;

        setRecommendations(recommendationData || []);
        setProfile(profileData || currentUser);

        const primaryId =
          recommendationData?.find((item) => item.is_primary || item.isPrimary)?.id ||
          recommendationData?.[0]?.id ||
          null;
        setSelectedId(primaryId);
        setError('');
      } catch (err) {
        if (mounted) setError(err.message || 'Unable to load recommendations.');
      } finally {
        if (mounted) setLoading(false);
      }
    })();

    return () => {
      mounted = false;
    };
  }, [currentUser]);

  const selectedRecommendation = useMemo(() => {
    if (!recommendations.length) return null;
    return (
      recommendations.find((item) => item.id === selectedId) ||
      recommendations.find((item) => item.is_primary || item.isPrimary) ||
      recommendations[0]
    );
  }, [recommendations, selectedId]);

  const alternativeRecommendations = useMemo(() => {
    if (!selectedRecommendation) return [];
    return recommendations.filter((item) => item.id !== selectedRecommendation.id);
  }, [recommendations, selectedRecommendation]);

  const derivedBreakdown = useMemo(() => {
    const base = selectedRecommendation?.match ?? 0;
    const skills = profile?.skills?.length ? Math.min(96, base + 5) : Math.max(60, base - 6);
    const interests = profile?.interests?.length ? Math.min(94, base + 1) : Math.max(56, base - 10);
    const experience = profile?.experience ? Math.min(92, base - 3) : Math.max(52, base - 14);
    const careerGoal = profile?.target_career ? Math.min(98, base + 3) : Math.max(58, base - 8);

    return [
      { label: 'Skills', value: skills },
      { label: 'Interests', value: interests },
      { label: 'Experience', value: experience },
      { label: 'Career Goal', value: careerGoal },
    ];
  }, [profile, selectedRecommendation]);

  const profileSummary = useMemo(() => {
    const weeklyHours =
      profile?.weekly_learning_hours ??
      profile?.weeklyHours ??
      null;
    const targetCareer =
      profile?.target_career ??
      profile?.currentGoal ??
      null;

    return {
      experience: profile?.experience || null,
      skills: profile?.skills || [],
      interests: profile?.interests || [],
      targetCareer,
      weeklyHours: weeklyHours ? `${weeklyHours} hrs / week` : null,
    };
  }, [profile]);

  const handleBuildRoute = async () => {
    if (!selectedRecommendation) return;
    setBuildingRoute(true);
    try {
      await routeService.generateRoute({ career_title: selectedRecommendation.title });
      navigate('/progress');
    } catch (err) {
      setError(err.message || 'Unable to build a route.');
    } finally {
      setBuildingRoute(false);
    }
  };

  if (loading) {
    return (
      <div className="rm-rec-shell rm-rec-shell--loading">
        <motion.div
          animate={{ opacity: [0.4, 1, 0.4] }}
          transition={{ duration: 2, repeat: Infinity }}
          className="rm-rec-loading-note"
        >
          Analyzing your profile...
        </motion.div>
        <LoadingState message="Building your career recommendation" />
      </div>
    );
  }

  if (!selectedRecommendation) {
    return (
      <div className="rm-rec-shell rm-rec-shell--loading">
        <p className="rm-rec-loading-note">{error || 'No recommendation data is available right now.'}</p>
      </div>
    );
  }

  return (
    <div className="rm-rec-shell">
      <div className="rm-rec-backdrop rm-rec-backdrop--left" aria-hidden="true" />
      <div className="rm-rec-backdrop rm-rec-backdrop--right" aria-hidden="true" />

      <div className="rm-rec-container">
        <motion.div
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          className="rm-rec-page"
        >
          <header className="rm-rec-header">
            <div className="rm-rec-header__brand-group">
              <div className="rm-rec-brand">RouteMaster</div>
              <div className="rm-rec-context">Career Recommendation</div>
            </div>
            <div className="rm-rec-status">Profile analyzed ✓</div>
          </header>

          <section className="rm-rec-hero">
            <div className="rm-rec-hero__eyebrow">Your Career Path</div>
            <h1 className="rm-rec-hero__title">Find the direction that best matches your profile.</h1>
            <p className="rm-rec-hero__copy">
              RouteMaster compares your skills, interests, experience, and goals to recommend the strongest learning direction.
            </p>
          </section>

          <section className="rm-rec-main-grid">
            <article className="rm-rec-primary-card">
              <div className="rm-rec-primary-card__top">
                <div>
                  <div className="rm-rec-section-label">Your Top Recommendation</div>
                  <h2 className="rm-rec-primary-card__title">{selectedRecommendation.title}</h2>
                  <p className="rm-rec-primary-card__description">{selectedRecommendation.description}</p>
                </div>

                <div className="rm-rec-match">
                  <div className="rm-rec-match__value">{selectedRecommendation.match}%</div>
                  <div className="rm-rec-match__label">Match</div>
                </div>
              </div>

              <div className="rm-rec-reasons-block">
                <div className="rm-rec-section-label">Why This Fits You</div>
                <div className="rm-rec-reasons-list">
                  {selectedRecommendation.reasons?.map((reason) => (
                    <RecommendationReason key={reason}>{reason}</RecommendationReason>
                  ))}
                </div>
              </div>

              <div className="rm-rec-cta-block">
                <Button
                  fullWidth
                  size="lg"
                  className="rm-rec-cta"
                  onClick={handleBuildRoute}
                  loading={buildingRoute}
                  icon={<ArrowRight size={16} />}
                >
                  Build My Learning Route
                </Button>
                <p className="rm-rec-cta__note">Turn this recommendation into a personalized learning path.</p>
              </div>
            </article>

            <aside className="rm-rec-side-column">
              <section className="rm-rec-panel">
                <div className="rm-rec-section-label">Match Breakdown</div>
                <div className="rm-rec-breakdown-list">
                  {derivedBreakdown.map((item) => (
                    <BreakdownRow key={item.label} label={item.label} value={item.value} />
                  ))}
                </div>
              </section>

              <section className="rm-rec-panel">
                <div className="rm-rec-section-label">Based On Your Profile</div>
                <div className="rm-rec-profile-grid">
                  <ProfileBlock label="Experience" value={profileSummary.experience} />
                  <ProfileBlock label="Target Career" value={profileSummary.targetCareer} />
                  <ProfileBlock label="Skills" value={profileSummary.skills} list />
                  <ProfileBlock label="Interests" value={profileSummary.interests} list />
                  <ProfileBlock label="Learning Time" value={profileSummary.weeklyHours} />
                </div>
              </section>
            </aside>
          </section>

          <section className="rm-rec-alternatives">
            <div className="rm-rec-section-label">Other Strong Matches</div>
            <div className="rm-rec-alternative-list">
              {alternativeRecommendations.map((career) => (
                <motion.button
                  key={career.id}
                  type="button"
                  whileTap={{ scale: 0.99 }}
                  onClick={() => setSelectedId(career.id)}
                  className={`rm-rec-alt-card ${selectedRecommendation.id === career.id ? 'is-selected' : ''}`}
                >
                  <div className="rm-rec-alt-card__body">
                    <div>
                      <div className="rm-rec-alt-card__title">{career.title}</div>
                      <div className="rm-rec-alt-card__meta">{career.match}% match</div>
                      <p className="rm-rec-alt-card__description">
                        {career.description || career.reasons?.[0] || 'A strong route based on your current profile signals.'}
                      </p>
                    </div>
                    <div className="rm-rec-alt-card__tail">
                      <span className="rm-rec-alt-card__percent">{career.match}%</span>
                      <ChevronRight size={16} />
                    </div>
                  </div>
                </motion.button>
              ))}
            </div>
          </section>

          <footer className="rm-rec-footer">
            RouteMaster analyzes your profile to recommend a learning direction that fits where you are - and where you want to go.
          </footer>
        </motion.div>
      </div>
    </div>
  );
}
