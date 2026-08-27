const journeySteps = [
  'Discover your ideal career',
  'Identify skill gaps',
  'Generate your learning route',
  'Build real projects',
  'Reach your goal',
];

function AuthBrandPanel() {
  return (
    <aside className="rm-auth__brand">
      <div className="rm-auth__brand-top">
        <div className="rm-brand">RouteMaster</div>
        <p className="rm-auth__brand-subhead">Your Learning Route</p>
      </div>

      <div className="rm-auth__brand-main">
        <p className="rm-label rm-label--accent">AI Career PathFinder</p>
        <h1 className="rm-auth__headline">
          Mastering the
          <span>Sequence of Complex</span>
          <span>Educational Goals</span>
        </h1>
        <p className="rm-auth__support">
          Discover your ideal career. Identify your skill gaps. Follow an adaptive learning route built around your
          goals, skills, and available time.
        </p>

        <ol className="rm-step-list rm-step-list--auth">
          {journeySteps.map((step, index) => (
            <li key={step} className="rm-step">
              <div className="rm-step__rail" aria-hidden="true">
                <span className={`rm-step__dot ${index < 2 ? 'is-active' : ''}`} />
                {index < journeySteps.length - 1 && <span className="rm-step__line" />}
              </div>
              <div className="rm-step__content">
                <p className={`rm-step__title ${index < 2 ? 'is-active' : ''}`}>{step}</p>
              </div>
            </li>
          ))}
        </ol>
      </div>

      <p className="rm-auth__footer">© 2024 RouteMaster. All rights reserved.</p>
    </aside>
  );
}

export default function AuthLayout({ children, title, subtitle }) {
  return (
    <div className="rm-auth">
      <div className="rm-auth__shell">
        <AuthBrandPanel />

        <main className="rm-auth__main">
          <div className="rm-auth__form-wrap">
            <div className="rm-auth__mobile-brand">
              <div className="rm-brand">RouteMaster</div>
              <p className="rm-auth__brand-subhead">Your Learning Route</p>
            </div>

            <header className="rm-auth__heading">
              <h2>{title}</h2>
              {subtitle && <p>{subtitle}</p>}
            </header>

            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
