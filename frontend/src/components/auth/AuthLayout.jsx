import { motion } from 'framer-motion';

/**
 * Two-column auth layout: left branding, right form.
 * Adapts to single-column on mobile.
 */
export default function AuthLayout({ children, title, subtitle }) {
  return (
    <div className="min-h-screen bg-[#171714] flex">
      {/* Left — Branding */}
      <div className="hidden lg:flex flex-col justify-between w-[45%] border-r border-[#383832] p-12 bg-[#171714]">
        {/* Logo */}
        <div>
          <div className="text-[11px] font-semibold tracking-[0.15em] uppercase text-[#C89B5B] mb-1">
            RouteMaster
          </div>
          <div className="text-[10px] tracking-[0.1em] uppercase text-[#77766F]">
            Your Learning Route
          </div>
        </div>

        {/* Center content */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div className="label mb-6 text-[#C89B5B]">AI Career PathFinder</div>
          <h1
            className="font-serif text-4xl leading-tight text-[#F3F0E8] mb-6"
            style={{ fontFamily: 'DM Serif Display, Georgia, serif' }}
          >
            Mastering the Sequence of Complex Educational Goals
          </h1>
          <p className="text-[#AAA89F] leading-relaxed text-sm">
            Discover your ideal career. Identify your skill gaps. Follow an adaptive learning
            route built around your goals, skills, and available time.
          </p>

          {/* Mini route visual */}
          <div className="mt-10 space-y-0">
            {[
              { label: 'Discover your ideal career', done: true },
              { label: 'Identify skill gaps', done: true },
              { label: 'Generate your learning route', done: false },
              { label: 'Build real projects', done: false },
              { label: 'Reach your goal', done: false },
            ].map((step, i) => (
              <div key={step.label} className="flex items-start gap-3">
                <div className="flex flex-col items-center flex-shrink-0">
                  <div
                    className="w-2 h-2 rounded-full mt-1"
                    style={{
                      backgroundColor: step.done ? '#C89B5B' : 'transparent',
                      borderWidth: 2,
                      borderStyle: 'solid',
                      borderColor: step.done ? '#C89B5B' : '#383832',
                    }}
                  />
                  {i < 4 && <div className="w-px h-7" style={{ backgroundColor: '#383832' }} />}
                </div>
                <div className="pb-0 pt-0.5">
                  <span
                    className="text-sm"
                    style={{ color: step.done ? '#C89B5B' : '#77766F' }}
                  >
                    {step.label}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Footer */}
        <p className="text-xs text-[#77766F]">
          © 2024 RouteMaster. All rights reserved.
        </p>
      </div>

      {/* Right — Form */}
      <div className="flex-1 flex items-center justify-center p-8 lg:p-16">
        <div className="w-full max-w-md">
          {/* Mobile logo */}
          <div className="lg:hidden mb-8">
            <div className="text-[11px] font-semibold tracking-[0.15em] uppercase text-[#C89B5B] mb-0.5">
              RouteMaster
            </div>
            <div className="text-[10px] tracking-[0.1em] uppercase text-[#77766F]">
              Your Learning Route
            </div>
          </div>

          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
          >
            {title && (
              <div className="mb-8">
                <h2
                  className="font-serif text-3xl text-[#F3F0E8] mb-2"
                  style={{ fontFamily: 'DM Serif Display, Georgia, serif' }}
                >
                  {title}
                </h2>
                {subtitle && <p className="text-[#AAA89F] text-sm">{subtitle}</p>}
              </div>
            )}
            {children}
          </motion.div>
        </div>
      </div>
    </div>
  );
}
