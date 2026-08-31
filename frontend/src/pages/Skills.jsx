import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowRight } from 'lucide-react';
import { SkillIndicator } from '../components/common/ProgressBar';
import { Button } from '../components/common/Button';
import { LoadingState, ErrorState } from '../components/common/States';
import { skillService } from '../services/skillService';
import { mockSkillGaps } from '../data/mockData';

const SKILL_CATEGORIES = ['Programming', 'Data', 'Machine Learning', 'AI / Deep Learning', 'MLOps'];

const TARGET_SKILLS = [
  { name: 'Python', current: 92, target: 90 },
  { name: 'Statistics', current: 78, target: 80 },
  { name: 'Machine Learning', current: 64, target: 85 },
  { name: 'Model Evaluation', current: 48, target: 75 },
  { name: 'Deep Learning', current: 31, target: 70 },
  { name: 'MLOps', current: 18, target: 60 },
];

const PRIORITY_COLOR = { HIGH: '#A96A5F', UPCOMING: '#C89B5B', FUTURE: '#77766F' };

export default function Skills() {
  const navigate = useNavigate();
  const [skills, setSkills] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeCategory, setActiveCategory] = useState('all');

  useEffect(() => {
    (async () => {
      try {
        const data = await skillService.getSkills();
        setSkills(data);
      } catch (e) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  if (loading) return <LoadingState message="Loading your skills..." />;
  if (error) return <ErrorState message={error} onRetry={() => window.location.reload()} />;

  const filtered = activeCategory === 'all'
    ? skills
    : skills.filter((s) => s.category === activeCategory);

  const grouped = SKILL_CATEGORIES.reduce((acc, cat) => {
    acc[cat] = filtered.filter((s) => s.category === cat);
    return acc;
  }, {});

  const strong = skills.filter((s) => s.status === 'strong');
  const developing = skills.filter((s) => s.status === 'developing');
  const needsAttention = skills.filter((s) => s.status === 'needs_attention');

  return (
    <div className="max-w-5xl mx-auto px-6 py-8">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="mb-10">
        <div className="label mb-3">Skill Intelligence</div>
        <h1 className="font-serif text-3xl text-[#F3F0E8] mb-2">Your Skills</h1>
        <p className="text-[#AAA89F]">Understand your strengths, identify gaps, and see what your goal requires next.</p>
      </motion.div>

      <div className="grid lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-8">
          {/* Profile summary */}
          <div className="border border-[#383832] rounded-xl p-6">
            <div className="label mb-3">Your Current Profile</div>
            <p className="text-sm text-[#AAA89F] leading-relaxed mb-4">
              Your strongest skills are <span className="text-[#F3F0E8]">Python, SQL and data handling</span>.
              You're building the machine learning capabilities required for your AI / ML Engineer goal.
            </p>
            <div className="grid grid-cols-4 gap-4 pt-4 border-t border-[#383832]">
              {[
                { label: 'Skills Tracked', value: skills.length, color: '#F3F0E8' },
                { label: 'Strong', value: strong.length, color: '#8C9A7A' },
                { label: 'Developing', value: developing.length, color: '#C89B5B' },
                { label: 'Need Attention', value: needsAttention.length, color: '#A96A5F' },
              ].map((m) => (
                <div key={m.label}>
                  <div className="text-2xl font-semibold" style={{ color: m.color }}>{m.value}</div>
                  <div className="text-[10px] text-[#77766F] mt-1 uppercase tracking-wide">{m.label}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Skill Landscape */}
          <div>
            <div className="label mb-4">Skill Landscape</div>
            {/* Category filter */}
            <div className="flex flex-wrap gap-2 mb-6">
              <button
                onClick={() => setActiveCategory('all')}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all cursor-pointer ${activeCategory === 'all' ? 'bg-[#C89B5B] text-[#171714]' : 'bg-[#22221E] border border-[#383832] text-[#77766F] hover:text-[#F3F0E8]'}`}
              >
                All
              </button>
              {SKILL_CATEGORIES.map((cat) => (
                <button
                  key={cat}
                  onClick={() => setActiveCategory(cat)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all cursor-pointer ${activeCategory === cat ? 'bg-[#C89B5B] text-[#171714]' : 'bg-[#22221E] border border-[#383832] text-[#77766F] hover:text-[#F3F0E8]'}`}
                >
                  {cat}
                </button>
              ))}
            </div>

            <div className="space-y-6">
              {Object.entries(grouped).map(([cat, catSkills]) => (
                catSkills.length > 0 && (
                  <div key={cat}>
                    <div className="text-[10px] font-semibold uppercase tracking-widest text-[#77766F] mb-3">{cat}</div>
                    <div className="space-y-3">
                      {catSkills.map((skill) => (
                        <SkillIndicator
                          key={skill.id}
                          name={skill.name}
                          value={skill.proficiency}
                          color={skill.status === 'strong' ? '#8C9A7A' : skill.status === 'developing' ? '#C89B5B' : '#A96A5F'}
                        />
                      ))}
                    </div>
                  </div>
                )
              ))}
            </div>
          </div>

          {/* Current vs Target */}
          <div>
            <div className="label mb-4">Current vs Target</div>
            <div className="border border-[#383832] rounded-xl overflow-hidden">
              <div className="grid grid-cols-3 px-5 py-2.5 border-b border-[#383832] bg-[#22221E]">
                <span className="text-[10px] text-[#77766F] uppercase tracking-wide">Skill</span>
                <span className="text-[10px] text-[#77766F] uppercase tracking-wide text-center">Current</span>
                <span className="text-[10px] text-[#77766F] uppercase tracking-wide text-center">Target</span>
              </div>
              {TARGET_SKILLS.map((s) => (
                <div key={s.name} className="px-5 py-3 border-b border-[#383832] last:border-0">
                  <div className="grid grid-cols-3 items-center mb-1.5">
                    <span className="text-sm text-[#F3F0E8]">{s.name}</span>
                    <span className="text-sm font-medium text-center" style={{ color: s.current >= s.target ? '#8C9A7A' : '#C89B5B' }}>{s.current}%</span>
                    <span className="text-sm text-[#77766F] text-center">{s.target}%</span>
                  </div>
                  <SkillIndicator
                    name=""
                    value={s.current}
                    target={s.target}
                    showTarget
                    color={s.current >= s.target ? '#8C9A7A' : s.current >= s.target * 0.7 ? '#C89B5B' : '#A96A5F'}
                  />
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right column: Skill Gaps */}
        <div>
          <div className="label mb-4">Skill Gaps</div>
          <div className="space-y-4">
            {mockSkillGaps.map((gap) => (
              <motion.div
                key={gap.skill}
                initial={{ opacity: 0, x: 10 }}
                animate={{ opacity: 1, x: 0 }}
                className="border border-[#383832] rounded-xl p-5"
                style={{ borderLeftColor: PRIORITY_COLOR[gap.priority], borderLeftWidth: 2 }}
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="text-sm font-semibold text-[#F3F0E8]">{gap.skill}</div>
                  <span
                    className="text-[9px] font-bold uppercase tracking-widest ml-2"
                    style={{ color: PRIORITY_COLOR[gap.priority] }}
                  >
                    {gap.priority}
                  </span>
                </div>

                <div className="space-y-2 mb-3">
                  <div className="flex justify-between text-xs">
                    <span className="text-[#77766F]">Current</span>
                    <span className="text-[#AAA89F]">{gap.current}%</span>
                  </div>
                  <div className="progress-track">
                    <div className="progress-fill" style={{ width: `${gap.current}%`, backgroundColor: '#C89B5B' }} />
                    <div
                      className="absolute top-0 w-px h-full bg-[#A96A5F]/60"
                      style={{ left: `${gap.required}%` }}
                    />
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-[#77766F]">Required</span>
                    <span className="text-[#AAA89F]">{gap.required}%</span>
                  </div>
                </div>

                <div className="text-xs text-[#77766F] mb-3 leading-relaxed">{gap.reason}</div>
                <Button
                  size="sm"
                  variant="secondary"
                  fullWidth
                  onClick={() => navigate('/resources')}
                  icon={<ArrowRight size={12} />}
                >
                  Find Resources
                </Button>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
