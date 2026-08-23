import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowRight, ChevronRight } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const ROUTE_STAGES = [
  { label: 'Current Skills', desc: 'Where you are today', done: true },
  { label: 'Skill Gaps', desc: 'What you are missing', done: false },
  { label: 'Learning Route', desc: 'Your personalized sequence', done: false },
  { label: 'Projects', desc: 'Practical application', done: false },
  { label: 'Career Goal', desc: 'Where you are going', done: false },
];

const FEATURES = [
  { label: 'Adaptive routes', desc: 'Your path adjusts as your skills change.' },
  { label: 'Skill intelligence', desc: 'Know exactly what you are missing and why.' },
  { label: 'Project milestones', desc: 'Build real things at every stage.' },
  { label: 'Route continuity', desc: 'Multiple goals, one coherent journey.' },
];

export default function Landing() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  const handleStartJourney = () => {
    navigate(isAuthenticated ? '/home' : '/register');
  };

  return (
    <div className="min-h-screen bg-[#171714] text-[#F3F0E8]">
      {/* Nav */}
      <header className="fixed top-0 inset-x-0 z-20 flex items-center justify-between px-8 py-4 border-b border-[#383832]/60 bg-[#171714]/90 backdrop-blur-sm">
        <span className="text-sm font-semibold tracking-[0.12em] uppercase text-[#C89B5B]">RouteMaster</span>
        <div className="flex items-center gap-6">
          <button
            onClick={() => {
              const el = document.getElementById('how-it-works');
              el?.scrollIntoView({ behavior: 'smooth' });
            }}
            className="text-sm text-[#AAA89F] hover:text-[#F3F0E8] transition-colors cursor-pointer hidden md:block"
          >
            How it works
          </button>
          <button
            onClick={() => navigate('/login')}
            className="text-sm text-[#AAA89F] hover:text-[#F3F0E8] transition-colors cursor-pointer"
          >
            Sign in
          </button>
          <button
            onClick={handleStartJourney}
            className="px-4 py-2 text-sm font-medium bg-[#C89B5B] text-[#171714] rounded-lg hover:bg-[#D4AA6C] transition-colors cursor-pointer"
          >
            {isAuthenticated ? 'Continue' : 'Get Started'}
          </button>
        </div>
      </header>

      {/* Hero */}
      <section className="pt-36 pb-24 px-8 max-w-6xl mx-auto">
        <div className="grid lg:grid-cols-2 gap-16 items-center">
          {/* Left */}
          <div>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <div className="label mb-4 text-[#C89B5B]">AI Career PathFinder</div>
              <h1 className="font-serif text-5xl lg:text-6xl leading-tight text-[#F3F0E8] mb-6" style={{ fontFamily: 'DM Serif Display, Georgia, serif' }}>
                Mastering the Sequence of Complex
                <span className="text-[#C89B5B]"> Educational Goals</span>
              </h1>
              <p className="text-lg text-[#AAA89F] leading-relaxed mb-10 max-w-lg">
                Discover your ideal career. Build your personalized learning roadmap.
              </p>

              <div className="flex flex-wrap items-center gap-4">
                <button
                  onClick={handleStartJourney}
                  className="inline-flex items-center gap-2 px-6 py-3 bg-[#C89B5B] text-[#171714] text-sm font-semibold rounded-lg hover:bg-[#D4AA6C] transition-colors cursor-pointer"
                >
                  {isAuthenticated ? 'Continue Your Journey' : 'Start Your Journey'}
                  <ArrowRight size={16} />
                </button>
                {!isAuthenticated && (
                  <button
                    onClick={() => navigate('/login')}
                    className="inline-flex items-center gap-1 text-sm text-[#AAA89F] hover:text-[#F3F0E8] transition-colors cursor-pointer"
                  >
                    Already have an account? Sign in
                    <ChevronRight size={14} />
                  </button>
                )}
              </div>
            </motion.div>
          </div>

          {/* Right — Route visualization */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="hidden lg:flex flex-col items-center"
          >
            <div className="relative">
              {ROUTE_STAGES.map((stage, i) => (
                <motion.div
                  key={stage.label}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.4 + i * 0.12 }}
                  className="flex items-start gap-4"
                >
                  <div className="flex flex-col items-center">
                    <div
                      className="w-3 h-3 rounded-full border-2 flex-shrink-0 mt-1"
                      style={{
                        borderColor: i === 0 ? '#C89B5B' : i === 4 ? '#C89B5B' : '#383832',
                        backgroundColor: i === 0 ? '#C89B5B' : 'transparent',
                      }}
                    />
                    {i < ROUTE_STAGES.length - 1 && (
                      <div className="w-px flex-1 min-h-[52px]" style={{ backgroundColor: '#383832' }} />
                    )}
                  </div>
                  <div className="pb-8">
                    <div className="text-sm font-semibold" style={{ color: i === 0 || i === 4 ? '#C89B5B' : '#F3F0E8' }}>
                      {stage.label}
                    </div>
                    <div className="text-xs text-[#77766F] mt-0.5">{stage.desc}</div>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>
      </section>

      {/* Divider */}
      <div className="border-t border-[#383832]/60 max-w-6xl mx-auto" />

      {/* Features */}
      <section id="how-it-works" className="py-20 px-8 max-w-6xl mx-auto">
        <div className="label mb-10 text-center">How It Works</div>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-px bg-[#383832]">
          {FEATURES.map((f, i) => (
            <motion.div
              key={f.label}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.6 + i * 0.1 }}
              className="bg-[#171714] p-8"
            >
              <div className="text-base font-semibold text-[#F3F0E8] mb-2">{f.label}</div>
              <div className="text-sm text-[#77766F] leading-relaxed">{f.desc}</div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Route preview */}
      <section className="py-16 px-8 max-w-6xl mx-auto border-t border-[#383832]/60">
        <div className="grid lg:grid-cols-3 gap-8 items-center">
          <div className="lg:col-span-1">
            <div className="label mb-4">Product Preview</div>
            <h2 className="font-serif text-3xl text-[#F3F0E8] mb-4" style={{ fontFamily: 'DM Serif Display, Georgia, serif' }}>Know exactly where you stand</h2>
            <p className="text-sm text-[#AAA89F] leading-relaxed mb-6">
              Your route shows every stage, current position, skill gaps, and what to build next — all in one view.
            </p>
            <button
              onClick={handleStartJourney}
              className="inline-flex items-center gap-2 text-sm text-[#C89B5B] hover:text-[#D4AA6C] font-medium cursor-pointer transition-colors"
            >
              Build Your Route <ArrowRight size={14} />
            </button>
          </div>

          <div className="lg:col-span-2 bg-[#22221E] border border-[#383832] rounded-xl p-6">
            <div className="flex items-center justify-between mb-6">
              <div>
                <div className="label mb-1">Current Route</div>
                <div className="text-base font-semibold">AI / ML Engineer</div>
              </div>
              <div className="text-right">
                <div className="text-2xl font-semibold text-[#C89B5B]">68%</div>
                <div className="text-xs text-[#77766F]">Complete</div>
              </div>
            </div>
            <div className="space-y-0">
              {[
                { label: 'Python Fundamentals', status: 'completed' },
                { label: 'Python & Data Handling', status: 'completed' },
                { label: 'Statistics', status: 'completed' },
                { label: 'Machine Learning', status: 'current' },
                { label: 'Deep Learning', status: 'upcoming' },
                { label: 'MLOps', status: 'upcoming' },
              ].map((s, i) => (
                <div key={s.label} className="flex items-start gap-3">
                  <div className="flex flex-col items-center">
                    <div
                      className={`w-2 h-2 rounded-full mt-1 flex-shrink-0 ${
                        s.status === 'completed' ? 'bg-[#8C9A7A]' :
                        s.status === 'current' ? 'bg-[#C89B5B]' : 'border border-[#383832]'
                      }`}
                    />
                    {i < 5 && <div className="w-px h-7" style={{ backgroundColor: '#383832' }} />}
                  </div>
                  <div className="pb-0 pt-0.5">
                    <span
                      className="text-sm"
                      style={{
                        color: s.status === 'completed' ? '#8C9A7A' :
                               s.status === 'current' ? '#C89B5B' : '#77766F'
                      }}
                    >
                      {s.label}
                    </span>
                    {s.status === 'current' && (
                      <span className="ml-2 text-[10px] font-medium tracking-wider uppercase text-[#C89B5B]/70">Current</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-8 max-w-6xl mx-auto border-t border-[#383832]/60 text-center">
        <div className="label mb-6">Ready to start?</div>
        <h2 className="font-serif text-4xl text-[#F3F0E8] mb-6" style={{ fontFamily: 'DM Serif Display, Georgia, serif' }}>Your route begins here.</h2>
        <button
          onClick={handleStartJourney}
          className="inline-flex items-center gap-2 px-8 py-4 bg-[#C89B5B] text-[#171714] font-semibold rounded-lg hover:bg-[#D4AA6C] transition-colors cursor-pointer"
        >
          Start Your Journey <ArrowRight size={16} />
        </button>
      </section>

      {/* Footer */}
      <footer className="border-t border-[#383832]/60 px-8 py-6 text-center">
        <span className="text-xs text-[#77766F]">© 2024 RouteMaster. Mastering the sequence of complex educational goals.</span>
      </footer>
    </div>
  );
}
