import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Target,
  BarChart3,
  Sparkles,
  BookOpen,
  Clock3,
  Gauge,
  Lock,
  Mail,
  KeyRound,
  LogOut,
  Trash2,
  ArrowRight,
  Check,
} from 'lucide-react';

import './Settings.css';
import { useAuth } from '../context/AuthContext';
import { profileService } from '../services/profileService';

function SectionIntro({ eyebrow, title, description }) {
  return (
    <div className="section-intro">
      <div className="section-eyebrow">{eyebrow}</div>
      <h2>{title}</h2>
      <p>{description}</p>
    </div>
  );
}

function ChoiceButton({ selected, children, onClick }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`choice ${selected ? 'selected' : ''}`}
    >
      <span className="radio-dot" />
      {children}
    </button>
  );
}

function PreferenceOption({ selected, children, onClick }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`preference-option ${selected ? 'selected' : ''}`}
    >
      <span className="radio-dot" />
      {children}
    </button>
  );
}

function PersonalizationItem({ icon: Icon, label, value }) {
  return (
    <div className="personalization-item">
      <div className="personalization-icon">
        <Icon size={17} strokeWidth={1.5} />
      </div>
      <div>
        <div className="personalization-label">{label}</div>
        <div className="personalization-value">{value}</div>
      </div>
    </div>
  );
}

export default function Settings() {
  const navigate = useNavigate();
  const { currentUser, logout, updateUser } = useAuth();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [experience, setExperience] = useState('Intermediate');
  const [goal, setGoal] = useState('');

  const [learningStyle, setLearningStyle] = useState('Project-based');
  const [learningTime, setLearningTime] = useState('7 hrs / week');
  const [pace, setPace] = useState('Balanced');
  const [contentPreference, setContentPreference] = useState('Mixed');

  const [profileSaved, setProfileSaved] = useState(false);
  const [preferencesSaved, setPreferencesSaved] = useState(false);
  const [notice, setNotice] = useState('');

  useEffect(() => {
    const loadSettings = async () => {
      try {
        const [profile, preferences] = await Promise.all([
          profileService.getProfile(),
          profileService.getPreferences(),
        ]);
        setName(profile?.name || currentUser?.name || '');
        setEmail(profile?.email || currentUser?.email || '');
        setExperience(profile?.experience || 'Intermediate');
        setGoal(profile?.target_career || currentUser?.target_career || '');
        setLearningStyle(preferences?.style || 'Project-based');
        setLearningTime(`${preferences?.weekly_hours || profile?.weekly_learning_hours || 7} hrs / week`);
        setPace(preferences?.pace || 'Balanced');
        setContentPreference(preferences?.content || 'Mixed');
      } catch (err) {
        setNotice(err.message || 'Unable to load settings.');
      }
    };
    loadSettings();
  }, [currentUser]);

  const initials = useMemo(() => {
    return name
      .split(' ')
      .filter(Boolean)
      .map((word) => word[0])
      .join('')
      .slice(0, 2)
      .toUpperCase();
  }, [name]);

  const handleProfileSave = async () => {
    setNotice('');
    try {
      await profileService.updateProfile({ name, experience, target_career: goal });
      updateUser?.({ name, experience, target_career: goal });
      setProfileSaved(true);
      setTimeout(() => setProfileSaved(false), 2200);
    } catch (err) {
      setNotice(err.message || 'Unable to save profile.');
    }
  };

  const handlePreferencesSave = async () => {
    setNotice('');
    try {
      await profileService.updatePreferences({
        style: learningStyle,
        weekly_hours: Number.parseInt(learningTime, 10),
        pace,
        content: contentPreference,
      });
      setPreferencesSaved(true);
      setTimeout(() => setPreferencesSaved(false), 2200);
    } catch (err) {
      setNotice(err.message || 'Unable to save preferences.');
    }
  };

  const showUnavailable = () => setNotice('This account action is not available in the current RouteMaster API.');

  const handleSignOut = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <div className="settings-page">
      <div className="settings-container">
        
        {/* =========================================================
            HEADER
        ========================================================= */}
        <header className="settings-header">
          <div className="settings-eyebrow">PERSONAL SETTINGS</div>
          <h1>Settings</h1>
          <p>
            Manage your profile and the preferences RouteMaster uses to personalize your learning journey.
          </p>
        </header>

        {/* =========================================================
            MAIN LAYOUT
        ========================================================= */}
        <div className="settings-layout">
          
          <div className="settings-main">
            
            {/* =====================================================
                PROFILE
            ===================================================== */}
            <section className="settings-section">
              <SectionIntro
                eyebrow="PROFILE"
                title="About you"
                description="This information helps RouteMaster understand where you're starting from."
              />

              <div className="profile-content">
                <div className="profile-avatar-area">
                  <div className="profile-avatar">{initials || 'A'}</div>
                  <button type="button" className="change-photo" onClick={showUnavailable}>
                    Change photo
                  </button>
                </div>

                <div className="profile-form">
                  
                  <div className="form-row">
                    <div className="form-group">
                      <label>Full name</label>
                      <input
                        type="text"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                      />
                    </div>

                    <div className="form-group">
                      <label>Email</label>
                      <div className="input-with-icon">
                        <input type="text" value={email} readOnly />
                        <Lock size={13} />
                      </div>
                    </div>
                  </div>

                  <div className="form-group">
                    <label>Experience level <span>*</span></label>
                    <div className="choice-row">
                      {['Beginner', 'Intermediate', 'Advanced'].map((option) => (
                        <ChoiceButton
                          key={option}
                          selected={experience === option}
                          onClick={() => setExperience(option)}
                        >
                          {option}
                        </ChoiceButton>
                      ))}
                    </div>
                  </div>

                  <div className="form-group">
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                      <label style={{ margin: 0 }}>Current goal <span>*</span></label>
                      <button
                        type="button"
                        className="inline-action"
                        onClick={() => setGoal(goal === 'AI / ML Engineer' ? 'Software Development Engineer' : 'AI / ML Engineer')}
                      >
                        Edit goal <ArrowRight size={12} />
                      </button>
                    </div>
                    <input
                      type="text"
                      value={goal}
                      onChange={(e) => setGoal(e.target.value)}
                    />
                    <span className="field-help">Your current learning route is based on this goal.</span>
                  </div>

                  <div className="save-row" style={{ marginTop: '20px' }}>
                    <span>Last updated today</span>
                    <button type="button" className="primary-button" onClick={handleProfileSave}>
                      {profileSaved && <Check size={14} />}
                      {profileSaved ? 'Saved' : 'Save Changes'}
                    </button>
                  </div>

                </div>
              </div>
            </section>

            {/* =====================================================
                LEARNING PREFERENCES
            ===================================================== */}
            <section className="settings-section">
              <SectionIntro
                eyebrow="LEARNING PREFERENCES"
                title="How you learn"
                description="RouteMaster uses these preferences when sequencing your learning route."
              />

              <div className="preferences-content">
                
                <div className="preference-row">
                  <div className="preference-label">Preferred learning style</div>
                  <div className="preference-options">
                    {['Theory-first', 'Project-based', 'Balanced', 'Practice-first'].map((option) => (
                      <PreferenceOption
                        key={option}
                        selected={learningStyle === option}
                        onClick={() => setLearningStyle(option)}
                      >
                        {option}
                      </PreferenceOption>
                    ))}
                  </div>
                </div>

                <div className="preference-row">
                  <div className="preference-label">Available learning time</div>
                  <div className="preference-options">
                    {['2 hrs / week', '5 hrs / week', '7 hrs / week', '10 hrs / week', '15+ hrs / week'].map((option) => (
                      <PreferenceOption
                        key={option}
                        selected={learningTime === option}
                        onClick={() => setLearningTime(option)}
                      >
                        {option}
                      </PreferenceOption>
                    ))}
                  </div>
                </div>

                <div className="preference-row">
                  <div className="preference-label">Learning pace</div>
                  <div className="preference-options">
                    {['Relaxed', 'Balanced', 'Intensive'].map((option) => (
                      <PreferenceOption
                        key={option}
                        selected={pace === option}
                        onClick={() => setPace(option)}
                      >
                        {option}
                      </PreferenceOption>
                    ))}
                  </div>
                </div>

                <div className="preference-row">
                  <div className="preference-label">Content preference</div>
                  <div className="preference-options">
                    {['Short lessons', 'Mixed', 'Deep dives'].map((option) => (
                      <PreferenceOption
                        key={option}
                        selected={contentPreference === option}
                        onClick={() => setContentPreference(option)}
                      >
                        {option}
                      </PreferenceOption>
                    ))}
                  </div>
                </div>

                <div className="personalization-box">
                  <div>
                    <div className="panel-eyebrow">ROUTEMASTER PERSONALIZATION</div>
                    <p>
                      Your route adapts as your skills and progress change. These preferences help determine how quickly and in what format new checkpoints are introduced.
                    </p>
                  </div>
                  <button type="button" className="primary-button small" onClick={handlePreferencesSave}>
                    {preferencesSaved && <Check size={14} />}
                    {preferencesSaved ? 'Saved' : 'Save Preferences'}
                  </button>
                </div>

              </div>
            </section>

            {/* =====================================================
                ACCOUNT
            ===================================================== */}
            <section className="settings-section" style={{ borderBottom: 0 }}>
              <SectionIntro
                eyebrow="ACCOUNT"
                title="Account"
                description="Manage your account and security settings."
              />

              <div className="account-content">
                
                <div className="account-row">
                  <div className="account-left">
                    <Mail size={15} className="account-icon" />
                    <span>Email</span>
                  </div>
                  <div className="account-value">{email}</div>
                  <button type="button" className="account-action" onClick={showUnavailable}>
                    Change email <ArrowRight size={12} />
                  </button>
                </div>

                <div className="account-row">
                  <div className="account-left">
                    <KeyRound size={15} className="account-icon" />
                    <span>Password</span>
                  </div>
                  <div className="account-value" style={{ letterSpacing: '0.2em' }}>••••••••••••</div>
                  <button type="button" className="account-action" onClick={showUnavailable}>
                    Change password <ArrowRight size={12} />
                  </button>
                </div>

                <div className="account-row">
                  <div className="account-left">
                    <LogOut size={15} className="account-icon" />
                    <span>Sign out</span>
                  </div>
                  <div className="account-value"></div>
                  <button type="button" className="account-action" onClick={handleSignOut}>
                    Sign out <ArrowRight size={12} />
                  </button>
                </div>

                <div className="account-row danger">
                  <div className="account-left">
                    <Trash2 size={15} className="account-icon" />
                    <span>Delete account</span>
                  </div>
                  <div className="account-value"></div>
                  <button type="button" className="account-action" onClick={showUnavailable}>
                    Delete account <ArrowRight size={12} />
                  </button>
                </div>

              </div>
            </section>

          </div>

          {notice && <p className="panel-footer" role="status">{notice}</p>}

          {/* =======================================================
              RIGHT PERSONALIZATION PANEL
          ======================================================= */}
          <aside className="settings-sidebar">
            <div className="personalization-panel">
              
              <div className="personalization-title">CURRENT PERSONALIZATION</div>
              <p className="panel-footer" style={{ margin: '0 0 10px', padding: 0 }}>
                These preferences shape your route.
              </p>

              <PersonalizationItem icon={Target} label="Goal" value={goal} />
              <PersonalizationItem icon={BarChart3} label="Level" value={experience} />
              <PersonalizationItem icon={Sparkles} label="Interests" value={(currentUser?.interests || []).join(' · ') || 'Not set'} />
              <PersonalizationItem icon={BookOpen} label="Learning style" value={learningStyle} />
              <PersonalizationItem icon={Clock3} label="Time available" value={learningTime} />
              <PersonalizationItem icon={Gauge} label="Pace" value={pace} />

              <div className="panel-footer" style={{ borderTop: '1px solid var(--border)', marginTop: '5px' }}>
                These preferences shape your route.
              </div>

            </div>
          </aside>

        </div>
      </div>
    </div>
  );
}
