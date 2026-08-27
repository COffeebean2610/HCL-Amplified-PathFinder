import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, Brain, Check, ChevronRight, Circle, Code2, Database, MoreVertical, Plus, Sparkles } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { profileService } from '../services/profileService';
import { routeService } from '../services/routeService';
import './MyRoutes.css';

const routeIcons = [Code2, Brain, Database];
const progress = (route) => Math.round(Number(route?.progress) || 0);
const stageLabel = (route) => route?.current_stage || route?.currentStage || route?.next_checkpoint || route?.nextCheckpoint || 'Next milestone';
const stages = (route) => (route?.stages || []).slice(0, 5).map((stage) => ({
  label: stage.title || stage.name || 'Untitled stage',
  status: stage.status === 'completed' ? 'completed' : stage.status === 'current' ? 'current' : 'upcoming',
}));

function StageLine({ route }) {
  const items = stages(route);
  if (!items.length) return null;

  return (
    <div className="route-stage-progress">
      <div className="stage-line">
        {items.map((stage, index) => (
          <div className={`stage-item ${stage.status}`} key={stage.label}>
            <div className="stage-dot">{stage.status === 'completed' && <Check size={8} />}</div>
            <span>{stage.label}</span>
            {index < items.length - 1 && <div className={`stage-connector ${stage.status === 'completed' ? 'completed' : ''}`} />}
          </div>
        ))}
      </div>
    </div>
  );
}

function JourneyCard({ route, index, onOpen, onTogglePause, updating }) {
  const Icon = routeIcons[index % routeIcons.length];
  const paused = route.status === 'paused';
  const iconClass = ['route-icon-code', 'route-icon-ai', 'route-icon-data'][index % 3];

  return (
    <article className="journey-card">
      <div className={`journey-icon ${iconClass}`}><Icon size={16} /></div>
      <div className="journey-main">
        <div className="journey-title-row"><h3>{route.title || 'Untitled route'}</h3><span className="journey-progress-number">{progress(route)}%</span></div>
        <span className="journey-status">{paused ? 'PAUSED' : 'ACTIVE'}</span>
        <div className="journey-progress-bar"><div className="journey-progress-fill" style={{ width: `${progress(route)}%` }} /></div>
      </div>
      <div className="journey-stages"><StageLine route={route} /></div>
      <div className="journey-current"><span>CURRENT STAGE</span><strong>{stageLabel(route)}</strong><small>{route.estimated_weeks || route.estimatedWeeks || 'Flexible'} week route</small></div>
      <button type="button" className="journey-action" onClick={() => onOpen(route)}>{paused ? 'View Route' : 'Continue'} <ArrowRight size={12} /></button>
      <button type="button" className="more-button" onClick={() => onTogglePause(route)} disabled={updating} title={paused ? 'Resume route' : 'Pause route'} aria-label={paused ? 'Resume route' : 'Pause route'}><MoreVertical size={16} /></button>
    </article>
  );
}

function FocusCard({ route, onOpen }) {
  const items = stages(route);

  return (
    <section className="current-focus-card">
      <div className="focus-label">CURRENT FOCUS</div>
      <div className="focus-content">
        <div className="focus-left">
          <div className="focus-title">
            <div className="focus-icon"><Brain size={20} /></div>
            <div><h2>{route.title}</h2><span className="focus-progress-text">{progress(route)}% complete</span></div>
          </div>
          <div className="focus-progress">
            <div className="focus-progress-fill" style={{ width: `${progress(route)}%` }} />
            <div className="focus-stages">
              {items.map((stage) => (
                <div className={`focus-stage ${stage.status === 'current' ? 'active' : stage.status}`} key={stage.label}>
                  <div className="focus-stage-dot">{stage.status === 'completed' && <Check size={9} />}</div>
                  <span>{stage.label}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
        <div className="focus-divider" />
        <div className="focus-right">
          <div className="focus-detail"><span>CURRENT STAGE</span><strong>{stageLabel(route)}</strong><small>{route.estimated_weeks || route.estimatedWeeks || 'Flexible'} week route</small></div>
          <div className="next-checkpoint"><span>NEXT CHECKPOINT</span><div className="checkpoint-row"><div className="checkpoint-icon"><Circle size={13} /></div><div><strong>{route.next_checkpoint || route.nextCheckpoint || 'Continue learning'}</strong><small>Keep your momentum going</small></div></div></div>
          <button type="button" className="continue-route-button" onClick={onOpen}>Continue Route <ArrowRight size={13} /></button>
        </div>
      </div>
    </section>
  );
}

export default function MyRoutes() {
  const navigate = useNavigate();
  const { currentUser } = useAuth();
  const [routes, setRoutes] = useState([]);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [updating, setUpdating] = useState(null);
  const [error, setError] = useState('');

  const loadData = async () => {
    setLoading(true);
    try {
      const [routeData, profileData] = await Promise.all([routeService.getRoutes(), profileService.getProfile()]);
      setRoutes(Array.isArray(routeData) ? routeData : []);
      setProfile(profileData);
      setError('');
    } catch {
      setError('Unable to load your routes. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadData(); }, []);

  const createRoute = async () => {
    setCreating(true);
    try {
      const route = await routeService.generateRoute({ career_title: profile?.target_career || currentUser?.target_career });
      if (route?.id) navigate('/progress');
      else await loadData();
    } catch {
      setError('We could not build a route right now. Please try again.');
    } finally {
      setCreating(false);
    }
  };

  const togglePause = async (route) => {
    setUpdating(route.id);
    try {
      if (route.status === 'paused') await routeService.resumeRoute(route.id);
      else await routeService.pauseRoute(route.id);
      await loadData();
    } catch {
      setError('We could not update this route. Please try again.');
    } finally {
      setUpdating(null);
    }
  };

  const currentRoute = routes.find((route) => route.is_current || route.isCurrent) || routes.find((route) => route.status !== 'paused') || routes[0];
  const otherRoutes = routes.filter((route) => route.id !== currentRoute?.id);
  const sharedSkills = (profile?.skills || []).slice(0, 3);

  return (
    <main className="routes-page">
      <header className="routes-header">
        <div><span className="routes-eyebrow">YOUR LEARNING JOURNEYS</span><h1>My Routes</h1><p>Different goals. Different journeys. One place to keep moving forward.</p></div>
        <button type="button" className="create-route-button" onClick={createRoute} disabled={creating}><Plus size={15} /> {creating ? 'Building...' : 'Create New Route'}</button>
      </header>
      {error && <p className="summary-description" role="alert">{error}</p>}
      {loading ? <p className="summary-description">Loading your routes...</p> : routes.length === 0 ? (
        <section className="explore-card"><div className="explore-icon"><Sparkles size={20} /></div><div className="explore-content"><span>YOUR NEXT JOURNEY</span><h3>Build your first learning route</h3><p>RouteMaster will shape it around the career goal in your profile.</p></div><button type="button" className="create-route-button" onClick={createRoute} disabled={creating}><Plus size={15} /> Create Route</button></section>
      ) : (
        <>
          <section className="route-summary"><div className="summary-stat"><strong>{routes.filter((route) => route.status !== 'paused').length}</strong><span>ACTIVE ROUTES</span></div><div className="summary-divider" /><div className="summary-stat"><strong>{routes.length}</strong><span>TOTAL JOURNEYS</span></div><p className="summary-description">Your routes update as your skills, goals, and progress evolve.</p></section>
          <div className="routes-content">
            <div className="routes-main">
              {currentRoute && <FocusCard route={currentRoute} onOpen={() => navigate('/progress')} />}
              {otherRoutes.length > 0 && <><div className="other-journeys-title">OTHER JOURNEYS</div><div className="journeys-list">{otherRoutes.map((route, index) => <JourneyCard key={route.id} route={route} index={index} onOpen={() => navigate('/progress')} onTogglePause={togglePause} updating={updating === route.id} />)}</div></>}
              <section className="explore-card"><div className="explore-icon"><Sparkles size={20} /></div><div className="explore-content"><span>EXPLORE A NEW PATH</span><h3>Ready for another route?</h3><p>Build a new learning journey around your next career goal.</p></div><button type="button" className="create-route-button" onClick={createRoute} disabled={creating}><Plus size={15} /> Create Route</button></section>
            </div>
            <aside className="routes-right-sidebar"><section className="side-card"><h3>ROUTES AT A GLANCE</h3><div className="glance-list">{routes.map((route) => <div className="glance-item" key={route.id}><div><span>{route.title}</span><strong>{progress(route)}%</strong></div><div className="glance-bar"><div style={{ width: `${progress(route)}%` }} /></div></div>)}</div></section><section className="side-card"><h3>SHARED SKILLS</h3><div className="shared-skills">{sharedSkills.length ? sharedSkills.map((skill) => <div className="shared-skill" key={skill}><div className="shared-skill-icon">{skill.slice(0, 1)}</div><div><strong>{skill}</strong><span>From your profile</span></div></div>) : <p>Add skills to your profile to see them here.</p>}</div><button type="button" className="side-link" onClick={() => navigate('/skills')}>View skills <ChevronRight size={12} /></button></section><section className="side-card observation-card"><div className="observation-header"><Sparkles className="observation-icon" size={14} /><h3>ROUTEMASTER OBSERVATION</h3></div><p>Your route will adapt as you complete milestones and build new skills.</p></section></aside>
          </div>
        </>
      )}
    </main>
  );
}
