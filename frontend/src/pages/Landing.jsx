import { useNavigate } from 'react-router-dom';
import { ArrowRight, ChevronRight } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const ROUTE_STAGES = [
  { label: 'Current Skills', desc: 'Where you are today', state: 'active' },
  { label: 'Skill Gaps', desc: 'What you are missing', state: 'default' },
  { label: 'Learning Route', desc: 'Your personalized sequence', state: 'default' },
  { label: 'Projects', desc: 'Practical application', state: 'default' },
  { label: 'Career Goal', desc: 'Where you are going', state: 'default' },
];

const FEATURES = [
  { title: 'Adaptive routes', desc: 'Your path adjusts as your skills change.' },
  { title: 'Skill intelligence', desc: 'Know exactly what you are missing and why.' },
  { title: 'Project milestones', desc: 'Build real things at every stage.' },
  { title: 'Route continuity', desc: 'Multiple goals, one coherent journey.' },
];

const PREVIEW_STEPS = [
  { label: 'Python Fundamentals', state: 'done' },
  { label: 'Python & Data Handling', state: 'done' },
  { label: 'Statistics', state: 'done' },
  { label: 'Machine Learning', state: 'current' },
  { label: 'Deep Learning', state: 'upcoming' },
  { label: 'MLOps', state: 'upcoming' },
];

function RouteFlowCard({ stages }) {
  return (
    <article className="rm-route-card">
      <header className="rm-route-card__header">
        <div>
          <p className="rm-label">Journey</p>
          <h3 className="rm-route-card__title">RouteMaster flow</h3>
        </div>
        <span className="rm-badge">Active</span>
      </header>

      <ol className="rm-step-list">
        {stages.map((stage, index) => (
          <li key={stage.label} className="rm-step">
            <div className="rm-step__rail" aria-hidden="true">
              <span className={`rm-step__dot ${stage.state === 'active' ? 'is-active' : ''}`} />
              {index < stages.length - 1 && <span className="rm-step__line" />}
            </div>
            <div className="rm-step__content">
              <p className={`rm-step__title ${stage.state === 'active' ? 'is-active' : ''}`}>{stage.label}</p>
              <p className="rm-step__desc">{stage.desc}</p>
            </div>
          </li>
        ))}
      </ol>
    </article>
  );
}

function RoutePreviewCard() {
  return (
    <article className="rm-route-card rm-route-card--preview">
      <header className="rm-preview-header">
        <div>
          <p className="rm-label">Current route</p>
          <h3 className="rm-preview-title">AI / ML Engineer</h3>
        </div>
        <div className="rm-complete">
          <div className="rm-complete__value">68%</div>
          <div className="rm-complete__label">Complete</div>
        </div>
      </header>

      <ol className="rm-step-list">
        {PREVIEW_STEPS.map((step, index) => (
          <li key={step.label} className="rm-step">
            <div className="rm-step__rail" aria-hidden="true">
              <span
                className={`rm-step__dot ${
                  step.state === 'done' ? 'is-done' : step.state === 'current' ? 'is-active' : ''
                }`}
              />
              {index < PREVIEW_STEPS.length - 1 && <span className="rm-step__line" />}
            </div>
            <div className="rm-step__content">
              <p className={`rm-step__title ${step.state === 'done' ? 'is-done' : step.state === 'current' ? 'is-active' : ''}`}>
                {step.label}
                {step.state === 'current' && <span className="rm-current-tag">Current</span>}
              </p>
            </div>
          </li>
        ))}
      </ol>
    </article>
  );
}

function LandingHeader({ isAuthenticated, onStart, onSignIn, onHowItWorks, onBrandClick }) {
  return (
    <header className="rm-header">
      <div className="rm-container rm-header__inner">
        <button onClick={onBrandClick} className="rm-brand" type="button">
          RouteMaster
        </button>

        <nav className="rm-header__actions" aria-label="Primary">
          <button type="button" className="rm-link rm-link--muted rm-hide-mobile" onClick={onHowItWorks}>
            How it works
          </button>
          <button type="button" className="rm-link rm-link--muted" onClick={onSignIn}>
            Sign in
          </button>
          <button type="button" className="rm-btn rm-btn--primary rm-btn--sm" onClick={onStart}>
            {isAuthenticated ? 'Continue' : 'Get Started'}
          </button>
        </nav>
      </div>
    </header>
  );
}

export default function Landing() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  const handleStart = () => {
    navigate(isAuthenticated ? '/home' : '/register');
  };

  return (
    <div className="rm-landing">
      <LandingHeader
        isAuthenticated={isAuthenticated}
        onStart={handleStart}
        onSignIn={() => navigate('/login')}
        onHowItWorks={() => document.getElementById('how-it-works')?.scrollIntoView({ behavior: 'smooth' })}
        onBrandClick={() => navigate('/')}
      />

      <main>
        <section className="rm-container rm-hero">
          <div className="rm-hero__grid">
            <div className="rm-hero__content">
              <p className="rm-label rm-label--accent">AI Career PathFinder</p>
              <h1 className="rm-hero__title">
                Mastering the
                <span>Sequence of</span>
                <span>Complex</span>
                <span className="rm-accent">Educational Goals</span>
              </h1>
              <p className="rm-hero__copy">
                Discover your ideal career. Build your personalized learning roadmap.
              </p>

              <div className="rm-hero__actions">
                <button type="button" className="rm-btn rm-btn--primary" onClick={handleStart}>
                  {isAuthenticated ? 'Continue Your Journey' : 'Start Your Journey'}
                  <ArrowRight size={15} />
                </button>
                {!isAuthenticated && (
                  <button type="button" className="rm-link" onClick={() => navigate('/login')}>
                    Already have an account? <span className="rm-link__strong">Sign in</span> <ChevronRight size={14} />
                  </button>
                )}
              </div>
            </div>

            <div className="rm-hero__card-wrap">
              <RouteFlowCard stages={ROUTE_STAGES} />
            </div>
          </div>
        </section>

        <section id="how-it-works" className="rm-container rm-section rm-section--bordered">
          <p className="rm-label rm-label--accent rm-center">How it works</p>
          <div className="rm-feature-grid">
            {FEATURES.map((feature) => (
              <article key={feature.title} className="rm-feature-item">
                <h3>{feature.title}</h3>
                <p>{feature.desc}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="rm-container rm-section rm-section--bordered">
          <div className="rm-preview-grid">
            <div>
              <p className="rm-label rm-label--accent">Product preview</p>
              <h2 className="rm-section__title">Know exactly where you stand</h2>
              <p className="rm-section__copy">
                Your route shows every stage, current position, skill gaps, and what to build next — all in one view.
              </p>
              <button type="button" className="rm-link rm-link--accent" onClick={handleStart}>
                Build Your Route <ArrowRight size={14} />
              </button>
            </div>

            <RoutePreviewCard />
          </div>
        </section>

        <section className="rm-container rm-section rm-section--bordered rm-cta">
          <p className="rm-label rm-label--accent">Ready to start?</p>
          <h2 className="rm-section__title rm-cta__title">Your route begins here.</h2>
          <button type="button" className="rm-btn rm-btn--primary" onClick={handleStart}>
            Start Your Journey <ArrowRight size={15} />
          </button>
        </section>
      </main>

      <footer className="rm-footer">
        <div className="rm-container rm-footer__inner">
          <p>© 2024 RouteMaster. Mastering the sequence of complex educational goals.</p>
        </div>
      </footer>
    </div>
  );
}
