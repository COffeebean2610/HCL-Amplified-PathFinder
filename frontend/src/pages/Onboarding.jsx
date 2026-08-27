import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronRight, ChevronLeft, Plus, X, Check, ArrowRight } from 'lucide-react';
import { Button } from '../components/common/Button';
import { useAuth } from '../context/AuthContext';
import client from '../services/api';

const STEPS = ['About You', 'Skills & Background', 'Your Goal'];

const SKILL_SUGGESTIONS = ['Python', 'JavaScript', 'SQL', 'React', 'Machine Learning', 'Data Analysis', 'Statistics', 'Docker', 'NumPy', 'Pandas'];
const INTEREST_OPTIONS = ['AI', 'ML', 'GenAI', 'Web Development', 'Data Science', 'Cloud Computing', 'DevOps', 'Cybersecurity', 'LLMs', 'NLP'];
const EXPERIENCE_LEVELS = ['Beginner', 'Intermediate', 'Advanced'];
const WEEKLY_HOURS = ['2 hrs / week', '5 hrs / week', '7 hrs / week', '10 hrs / week', '15+ hrs / week'];
const STEP_COPY = [
  {
    heading: "Tell us where you're starting.",
    description: 'We use this to tailor your route around your background, pace, and direction.',
  },
  {
    heading: 'Map your skills and background.',
    description: 'Add what you already know so RouteMaster can identify the strongest next steps.',
  },
  {
    heading: 'Define the goal you want to reach.',
    description: 'Your target career and weekly time help shape the depth and pacing of your route.',
  },
];

function TagInput({ tags, setTags, placeholder, suggestions }) {
  const [input, setInput] = useState('');

  const addTag = (val) => {
    const v = val.trim();
    if (v && !tags.includes(v)) setTags([...tags, v]);
    setInput('');
  };

  return (
    <div className="rm-onboard-field">
      <div className="rm-onboard-tags">
        {tags.map((t) => (
          <span key={t} className="rm-onboard-tag rm-onboard-tag--selected">
            {t}
            <button
              type="button"
              onClick={() => setTags(tags.filter((x) => x !== t))}
              className="rm-onboard-tag__remove"
            >
              <X size={12} />
            </button>
          </span>
        ))}
      </div>

      <div className="rm-onboard-tag-input">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              e.preventDefault();
              addTag(input);
            }
          }}
          placeholder={placeholder}
          className="rm-onboard-control rm-onboard-control--input"
        />
        <button type="button" onClick={() => addTag(input)} className="rm-onboard-add-btn">
          <Plus size={16} />
        </button>
      </div>

      {suggestions && (
        <div className="rm-onboard-chip-grid">
          {suggestions.filter((s) => !tags.includes(s)).map((s) => (
            <button key={s} type="button" onClick={() => addTag(s)} className="rm-onboard-chip">
              {s}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

function SelectOption({ options, value, onChange, prominent = false }) {
  return (
    <div className={`rm-onboard-option-grid ${prominent ? 'is-prominent' : ''}`}>
      {options.map((opt) => (
        <button
          key={opt}
          type="button"
          onClick={() => onChange(opt)}
          className={`rm-onboard-option ${prominent ? 'is-prominent' : ''} ${value === opt ? 'is-selected' : ''}`}
        >
          {value === opt && <Check size={14} className="rm-onboard-option__check" />}
          {opt}
        </button>
      ))}
    </div>
  );
}

export default function Onboarding() {
  const navigate = useNavigate();
  const { currentUser, updateUser } = useAuth();
  const [step, setStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const [form, setForm] = useState({
    name: currentUser?.name || '',
    education: '',
    branch: '',
    experience: 'Intermediate',
    skills: [],
    interests: [],
    projects: '',
    certifications: '',
    target_career: '',
    weekly_learning_hours: 7,
  });

  const update = (field, value) => setForm((f) => ({ ...f, [field]: value }));

  const handleSubmit = async () => {
    setLoading(true);
    setError('');
    try {
      await client.put('/users/me', {
        ...form,
        onboarding_completed: true,
      });

      updateUser({ onboarding_completed: true, target_career: form.target_career });
      navigate('/recommendation');
    } catch (err) {
      setError(err.message || 'Could not save your profile. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const canProceed = () => {
    if (step === 0) return form.name.trim().length > 0;
    if (step === 1) return true;
    if (step === 2) return form.target_career.trim().length > 0;
    return true;
  };

  const progressValue = ((step + 1) / STEPS.length) * 100;

  return (
    <div className="rm-onboard-shell">
      <div className="rm-onboard-bg-orb rm-onboard-bg-orb--left" aria-hidden="true" />
      <div className="rm-onboard-bg-orb rm-onboard-bg-orb--right" aria-hidden="true" />

      <div className="rm-onboard-container">
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="rm-onboard-header"
        >
          <div className="rm-onboard-brand">RouteMaster</div>
          <div className="rm-onboard-step-row">
            <div className="rm-onboard-step-pill">Step {step + 1} of {STEPS.length}</div>
            <div className="rm-onboard-step-name">{STEPS[step]}</div>
          </div>
          <h1 className="rm-onboard-title">{STEP_COPY[step].heading}</h1>
          <p className="rm-onboard-copy">{STEP_COPY[step].description}</p>

          <div className="rm-onboard-progress" aria-label={`Progress: step ${step + 1} of ${STEPS.length}`}>
            <div className="rm-onboard-progress__track">
              <div className="rm-onboard-progress__fill" style={{ width: `${progressValue}%` }} />
            </div>
            <div className="rm-onboard-progress__steps">
              {STEPS.map((label, index) => (
                <div
                  key={label}
                  className={`rm-onboard-progress__item ${index === step ? 'is-active' : index < step ? 'is-complete' : ''}`}
                >
                  <span className="rm-onboard-progress__index">0{index + 1}</span>
                  <span className="rm-onboard-progress__label">{label}</span>
                </div>
              ))}
            </div>
          </div>
        </motion.div>

        <AnimatePresence mode="wait">
          <motion.div
            key={step}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.2 }}
            className="rm-onboard-panel"
          >
            {step === 0 && (
              <div className="rm-onboard-fields">
                <div className="rm-onboard-field">
                  <label className="rm-onboard-label">Full Name</label>
                  <input
                    className="rm-onboard-control rm-onboard-control--input"
                    value={form.name}
                    onChange={(e) => update('name', e.target.value)}
                    placeholder="Your name"
                  />
                </div>

                <div className="rm-onboard-grid rm-onboard-grid--two">
                  <div className="rm-onboard-field">
                    <label className="rm-onboard-label">Education</label>
                    <input
                      className="rm-onboard-control rm-onboard-control--input"
                      value={form.education}
                      onChange={(e) => update('education', e.target.value)}
                      placeholder="e.g. B.Tech Computer Science"
                    />
                  </div>

                  <div className="rm-onboard-field">
                    <label className="rm-onboard-label">Branch / Specialization</label>
                    <input
                      className="rm-onboard-control rm-onboard-control--input"
                      value={form.branch}
                      onChange={(e) => update('branch', e.target.value)}
                      placeholder="e.g. Computer Science"
                    />
                  </div>
                </div>

                <div className="rm-onboard-field">
                  <label className="rm-onboard-label">Experience Level</label>
                  <SelectOption options={EXPERIENCE_LEVELS} value={form.experience} onChange={(v) => update('experience', v)} />
                </div>
              </div>
            )}

            {step === 1 && (
              <div className="rm-onboard-grid rm-onboard-grid--two rm-onboard-grid--balanced">
                <div className="rm-onboard-field">
                  <label className="rm-onboard-label">Current Skills</label>
                  <TagInput
                    tags={form.skills}
                    setTags={(v) => update('skills', v)}
                    placeholder="Add a skill..."
                    suggestions={SKILL_SUGGESTIONS}
                  />
                </div>

                <div className="rm-onboard-field">
                  <label className="rm-onboard-label">Interests</label>
                  <TagInput
                    tags={form.interests}
                    setTags={(v) => update('interests', v)}
                    placeholder="Add an interest..."
                    suggestions={INTEREST_OPTIONS}
                  />
                </div>

                <div className="rm-onboard-field">
                  <label className="rm-onboard-label">
                    Notable Projects <span className="rm-onboard-optional">(optional)</span>
                  </label>
                  <textarea
                    className="rm-onboard-control rm-onboard-control--textarea"
                    value={form.projects}
                    onChange={(e) => update('projects', e.target.value)}
                    placeholder="Describe any projects you've built..."
                    rows={5}
                  />
                </div>

                <div className="rm-onboard-field">
                  <label className="rm-onboard-label">
                    Certifications <span className="rm-onboard-optional">(optional)</span>
                  </label>
                  <input
                    className="rm-onboard-control rm-onboard-control--input"
                    value={form.certifications}
                    onChange={(e) => update('certifications', e.target.value)}
                    placeholder="e.g. AWS Cloud Practitioner, Python for DS"
                  />
                </div>
              </div>
            )}

            {step === 2 && (
              <div className="rm-onboard-fields">
                <div className="rm-onboard-field rm-onboard-field--hero">
                  <label className="rm-onboard-label">Target Career</label>
                  <input
                    className="rm-onboard-control rm-onboard-control--input rm-onboard-control--hero"
                    value={form.target_career}
                    onChange={(e) => update('target_career', e.target.value)}
                    placeholder="e.g. AI / ML Engineer"
                  />
                  <p className="rm-onboard-helper">
                    Don&apos;t worry - RouteMaster will also recommend careers based on your profile.
                  </p>
                </div>

                <div className="rm-onboard-field">
                  <label className="rm-onboard-label">Weekly Learning Time</label>
                  <SelectOption
                    options={WEEKLY_HOURS}
                    value={`${form.weekly_learning_hours} hrs / week`}
                    onChange={(v) => update('weekly_learning_hours', parseInt(v))}
                    prominent
                  />
                </div>
              </div>
            )}
          </motion.div>
        </AnimatePresence>

        {error && <p className="rm-onboard-error">{error}</p>}

        <div className="rm-onboard-actions">
          {step > 0 ? (
            <Button
              variant="secondary"
              size="lg"
              className="rm-onboard-action-btn rm-onboard-action-btn--back"
              onClick={() => setStep((s) => s - 1)}
              icon={<ChevronLeft size={16} />}
            >
              Back
            </Button>
          ) : (
            <div className="rm-onboard-actions__spacer" />
          )}

          {step < STEPS.length - 1 ? (
            <Button
              size="lg"
              className="rm-onboard-action-btn"
              onClick={() => setStep((s) => s + 1)}
              disabled={!canProceed()}
              icon={<ChevronRight size={16} />}
            >
              Continue
            </Button>
          ) : (
            <Button
              size="lg"
              className="rm-onboard-action-btn rm-onboard-action-btn--final"
              onClick={handleSubmit}
              loading={loading}
              disabled={!canProceed()}
              icon={!loading && <ArrowRight size={16} />}
            >
              {loading ? 'Building your route...' : 'Build My Route'}
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
