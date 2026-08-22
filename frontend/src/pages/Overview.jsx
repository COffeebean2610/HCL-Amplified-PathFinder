import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowRight, AlertTriangle, Clock, ChevronRight, MessageCircle, Sparkles } from 'lucide-react';
import { Button } from '../components/common/Button';
import { SkillIndicator } from '../components/common/ProgressBar';
import { LoadingState, ErrorState } from '../components/common/States';
import { routeService } from '../services/routeService';
import { skillService } from '../services/skillService';
import { mockProgress, mockSkillGaps, mockProjects } from '../data/mockData';
import { greetingByHour } from '../lib/utils';

function SectionLabel({ children }) {
  return <div className="label mb-4">{children}</div>;
}

function Divider() {
  return <div className="border-t border-[#383832] my-8" />;
}

// Route stage in overview
function MiniRouteStage({ stage, isLast }) {
  const statusColor = stage.status === 'completed' ? '#8C9A7A' : stage.status === 'current' ? '#C89B5B' : '#383832';
  const textColor = stage.status === 'completed' ? '#8C9A7A' : stage.status === 'current' ? '#C89B5B' : '#77766F';

  return (
    <div className="flex items-start gap-3">
      <div className="flex flex-col items-center flex-shrink-0">
        <div
          className="w-2.5 h-2.5 rounded-full border mt-1"
          style={{ borderColor: statusColor, backgroundColor: stage.status === 'completed' ? statusColor : 'transparent' }}
        />
        {!isLast && <div className="w-px flex-1 min-h-[44px]" style={{ backgroundColor: '#383832' }} />}
      </div>
      <div className="pb-3">
        <div className="text-sm font-medium" style={{ color: textColor }}>{stage.title}</div>
        {stage.status === 'current' && (
          <div className="text-xs text-[#77766F] mt-0.5">Current stage</div>
        )}
      </div>
    </div>
  );
}

export default function Overview() {
  const navigate = useNavigate();
  const [route, setRoute] = useState(null);
  const [skills, setSkills] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [aiExpanded, setAiExpanded] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        const [routes, skillsData] = await Promise.all([
          routeService.getRoutes(),
          skillService.getSkills(),
        ]);
        setRoute(routes.find((r) => r.isCurrent) || routes[0]);
        setSkills(skillsData);
      } catch (e) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  if (loading) return <LoadingState message="Loading your overview..." />;
  if (error) return <ErrorState message={error} onRetry={() => window.location.reload()} />;

  const strongSkills = skills.filter((s) => s.status === 'strong').slice(0, 3);
  const developingSkills = skills.filter((s) => s.status === 'developing').slice(0, 2);
  const weakSkills = skills.filter((s) => s.status === 'needs_attention').slice(0, 2);

  return (
    <div className="max-w-5xl mx-auto px-6 py-8">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="mb-10">
        <div className="label mb-3">Learning Overview</div>
        <h1 className="font-serif text-3xl text-[#F3F0E8] mb-2">
          {greetingByHour()}, {route ? 'Abhishek' : 'Learner'}.
        </h1>
        <p className="text-[#AAA89F]">Here's where your learning journey stands.</p>
      </motion.div>

      <div className="grid lg:grid-cols-3 gap-8">
        {/* Left column — Main */}
        <div className="lg:col-span-2 space-y-0">

          {/* Current Goal */}
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.1 }}>
            <div className="border border-[#383832] rounded-xl p-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <SectionLabel>Current Goal</SectionLabel>
                  <h2 className="text-xl font-semibold text-[#F3F0E8]">Become an {route?.title}</h2>
                  <p className="text-sm text-[#77766F] mt-1">Intermediate → Advanced · {route?.estimatedWeeks || 24} week journey · {route?.weeklyHours}hrs/week</p>
                </div>
                <div className="text-right">
                  <div className="text-3xl font-semibold text-[#C89B5B]">{route?.progress}%</div>
                  <div className="text-[10px] text-[#77766F] uppercase tracking-wide mt-1">Route Completed</div>
                </div>
              </div>
              <div className="progress-track mb-4">
                <motion.div
                  className="progress-fill"
                  initial={{ width: 0 }}
                  animate={{ width: `${route?.progress}%` }}
                  transition={{ duration: 1, delay: 0.3 }}
                  style={{ backgroundColor: '#C89B5B' }}
                />
              </div>
              <Button onClick={() => navigate(`/routes/${route?.id}`)} icon={<ArrowRight size={14} />}>
                Continue Route
              </Button>
            </div>
          </motion.div>

          <Divider />

          {/* Route visualization */}
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.15 }}>
            <div className="flex items-center justify-between mb-4">
              <SectionLabel>Your Route</SectionLabel>
              <button
                onClick={() => navigate(`/routes/${route?.id}`)}
                className="text-xs text-[#77766F] hover:text-[#C89B5B] flex items-center gap-1 transition-colors cursor-pointer"
              >
                View full route <ChevronRight size={12} />
              </button>
            </div>
            <div>
              {route?.stages.map((stage, i) => (
                <MiniRouteStage key={stage.id} stage={stage} isLast={i === route.stages.length - 1} />
              ))}
              {/* Destination */}
              <div className="flex items-center gap-3 mt-1">
                <div className="w-3 h-3 rounded-full border-2 border-[#C89B5B] flex items-center justify-center">
                  <div className="w-1 h-1 rounded-full bg-[#C89B5B]" />
                </div>
                <span className="text-sm font-semibold text-[#C89B5B] uppercase tracking-wide">{route?.title}</span>
              </div>
            </div>
          </motion.div>

          <Divider />

          {/* Next Step */}
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }}>
            <SectionLabel>Your Next Step</SectionLabel>
            <div className="border border-[#C89B5B]/20 bg-[#C89B5B]/5 rounded-xl p-5">
              <div className="flex items-start justify-between mb-3">
                <h3 className="text-base font-semibold text-[#F3F0E8]">Machine Learning Model Evaluation</h3>
                <span className="flex items-center gap-1 text-xs text-[#77766F] flex-shrink-0 ml-4">
                  <Clock size={12} /> ~45 min
                </span>
              </div>
              <p className="text-sm text-[#AAA89F] mb-4 leading-relaxed">
                RouteMaster recommends this because you've completed the required foundations
                and model evaluation is the next prerequisite for your advanced ML stage.
              </p>
              <div className="flex flex-wrap gap-2 mb-4">
                {['Intermediate', '2 skills'].map((t) => (
                  <span key={t} className="tag">{t}</span>
                ))}
              </div>
              <div className="flex gap-3">
                <Button size="sm" onClick={() => navigate('/resources/res-1')} icon={<ArrowRight size={13} />}>
                  Continue Learning
                </Button>
                <Button size="sm" variant="secondary">Why recommended?</Button>
              </div>
            </div>
          </motion.div>

          <Divider />

          {/* Skill Gaps */}
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.25 }}>
            <div className="flex items-center justify-between mb-4">
              <SectionLabel>Skill Gaps</SectionLabel>
              <button onClick={() => navigate('/skills')} className="text-xs text-[#77766F] hover:text-[#C89B5B] flex items-center gap-1 cursor-pointer transition-colors">
                View all <ChevronRight size={12} />
              </button>
            </div>
            <div className="text-sm text-[#AAA89F] mb-4">
              <span className="text-[#F3F0E8] font-medium">03</span> skills are currently blocking your next stage
            </div>
            <div className="space-y-3">
              {mockSkillGaps.map((gap) => (
                <div key={gap.skill} className="flex items-center justify-between py-3 border-b border-[#383832] last:border-0">
                  <div>
                    <div className="text-sm font-medium text-[#F3F0E8]">{gap.skill}</div>
                    <div className="text-xs text-[#77766F] mt-0.5">{gap.reason}</div>
                  </div>
                  <div className="flex items-center gap-3 flex-shrink-0 ml-4">
                    <span
                      className="text-[10px] font-semibold uppercase tracking-wider"
                      style={{ color: gap.priority === 'HIGH' ? '#A96A5F' : gap.priority === 'UPCOMING' ? '#C89B5B' : '#77766F' }}
                    >
                      {gap.priority}
                    </span>
                    <AlertTriangle size={13} className={gap.priority === 'HIGH' ? 'text-[#A96A5F]' : 'text-[#77766F]'} />
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        </div>

        {/* Right column */}
        <div className="space-y-6">

          {/* Momentum */}
          <motion.div initial={{ opacity: 0, x: 10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.2 }}>
            <SectionLabel>Learning Momentum</SectionLabel>
            <div className="border border-[#383832] rounded-xl p-5">
              <div className="grid grid-cols-2 gap-4 mb-5">
                {[
                  { label: 'This week', value: `${mockProgress.thisWeekHours}h` },
                  { label: 'Lessons done', value: mockProgress.lessonsCompleted },
                  { label: 'Skills improved', value: `+${mockProgress.skillsImproved}` },
                  { label: 'Streak', value: `${mockProgress.streak}d` },
                ].map((m) => (
                  <div key={m.label}>
                    <div className="text-xl font-semibold text-[#F3F0E8]">{m.value}</div>
                    <div className="text-[10px] text-[#77766F] mt-0.5 uppercase tracking-wide">{m.label}</div>
                  </div>
                ))}
              </div>
              {/* 7-day activity */}
              <div className="flex items-end gap-1 h-10">
                {mockProgress.weeklyActivity.map((d) => (
                  <div key={d.day} className="flex-1 flex flex-col items-center gap-1">
                    <div
                      className="w-full rounded-sm"
                      style={{
                        height: d.hours > 0 ? `${Math.max(4, d.hours * 20)}px` : '4px',
                        backgroundColor: d.hours > 0 ? '#C89B5B' : '#383832',
                      }}
                    />
                    <span className="text-[9px] text-[#77766F]">{d.day[0]}</span>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>

          {/* Skill Profile */}
          <motion.div initial={{ opacity: 0, x: 10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.25 }}>
            <div className="flex items-center justify-between mb-3">
              <SectionLabel>Your Skill Profile</SectionLabel>
              <button onClick={() => navigate('/skills')} className="text-xs text-[#77766F] hover:text-[#C89B5B] cursor-pointer transition-colors">View all</button>
            </div>
            <div className="border border-[#383832] rounded-xl p-5 space-y-5">
              {strongSkills.length > 0 && (
                <div>
                  <div className="text-[10px] text-[#8C9A7A] uppercase tracking-widest font-semibold mb-3">Strong</div>
                  <div className="space-y-3">
                    {strongSkills.map((s) => (
                      <SkillIndicator key={s.id} name={s.name} value={s.proficiency} color="#8C9A7A" />
                    ))}
                  </div>
                </div>
              )}
              {developingSkills.length > 0 && (
                <div>
                  <div className="text-[10px] text-[#C89B5B] uppercase tracking-widest font-semibold mb-3">Developing</div>
                  <div className="space-y-3">
                    {developingSkills.map((s) => (
                      <SkillIndicator key={s.id} name={s.name} value={s.proficiency} color="#C89B5B" />
                    ))}
                  </div>
                </div>
              )}
              {weakSkills.length > 0 && (
                <div>
                  <div className="text-[10px] text-[#A96A5F] uppercase tracking-widest font-semibold mb-3">Needs Attention</div>
                  <div className="space-y-3">
                    {weakSkills.map((s) => (
                      <SkillIndicator key={s.id} name={s.name} value={s.proficiency} color="#A96A5F" />
                    ))}
                  </div>
                </div>
              )}
            </div>
          </motion.div>

          {/* Projects */}
          <motion.div initial={{ opacity: 0, x: 10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.3 }}>
            <div className="flex items-center justify-between mb-3">
              <SectionLabel>Projects Along Your Route</SectionLabel>
              <button onClick={() => navigate('/projects')} className="text-xs text-[#77766F] hover:text-[#C89B5B] cursor-pointer transition-colors">View all</button>
            </div>
            <div className="border border-[#383832] rounded-xl divide-y divide-[#383832]">
              {mockProjects.filter((p) => p.status !== 'recommended').map((proj) => (
                <div key={proj.id} className="px-4 py-3 flex items-center justify-between">
                  <div>
                    <div className="text-sm text-[#F3F0E8]">{proj.title}</div>
                    <div className="text-[10px] text-[#77766F] mt-0.5 uppercase tracking-wide">{proj.status}</div>
                  </div>
                  <div
                    className="w-2 h-2 rounded-full flex-shrink-0"
                    style={{
                      backgroundColor: proj.status === 'completed' ? '#8C9A7A' : proj.status === 'current' ? '#C89B5B' : '#383832',
                    }}
                  />
                </div>
              ))}
            </div>
          </motion.div>

          {/* AI Guide */}
          <motion.div initial={{ opacity: 0, x: 10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.35 }}>
            <div className="border border-[#383832] rounded-xl p-5">
              <div className="flex items-center gap-2 mb-3">
                <Sparkles size={14} className="text-[#C89B5B]" />
                <div className="label">RouteMaster Guide</div>
              </div>
              <p className="text-sm text-[#AAA89F] leading-relaxed mb-4">
                You're ready to move into model evaluation. Ask RouteMaster about your current route, skill gaps or next step.
              </p>
              <Button
                variant="secondary"
                size="sm"
                fullWidth
                onClick={() => navigate('/guide')}
                icon={<MessageCircle size={13} />}
              >
                Ask RouteMaster
              </Button>
              <div className="mt-3 space-y-1.5">
                {['Why is this my next step?', 'Can I skip this module?', 'What should I practice today?'].map((q) => (
                  <button
                    key={q}
                    className="block w-full text-left text-xs text-[#77766F] hover:text-[#AAA89F] py-1 cursor-pointer transition-colors"
                  >
                    → {q}
                  </button>
                ))}
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
