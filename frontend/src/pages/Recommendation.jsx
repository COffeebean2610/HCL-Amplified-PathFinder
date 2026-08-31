import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowRight, Check, ChevronRight } from 'lucide-react';
import { Button } from '../components/common/Button';
import { profileService } from '../services/profileService';
import { LoadingState } from '../components/common/States';

export default function Recommendation() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [recommendations, setRecommendations] = useState([]);
  const [selected, setSelected] = useState(null);

  useEffect(() => {
    (async () => {
      const data = await profileService.getCareerRecommendation({});
      setRecommendations(data);
      setSelected(data[0]);
      setLoading(false);
    })();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-[#171714] flex flex-col items-center justify-center">
        <motion.div
          animate={{ opacity: [0.4, 1, 0.4] }}
          transition={{ duration: 2, repeat: Infinity }}
          className="text-sm text-[#77766F] mb-4"
        >
          Analyzing your profile...
        </motion.div>
        <LoadingState message="Building your career recommendation" />
      </div>
    );
  }

  const primary = recommendations.find((r) => r.isPrimary) || recommendations[0];
  const others = recommendations.filter((r) => !r.isPrimary);

  return (
    <div className="min-h-screen bg-[#171714] flex items-center justify-center p-6">
      <div className="w-full max-w-2xl">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <div className="label text-center mb-10">Your Recommended Career</div>

          {/* Primary recommendation */}
          <div className="bg-[#22221E] border border-[#C89B5B]/30 rounded-xl p-8 mb-6">
            <div className="flex items-start justify-between mb-6">
              <div>
                <h1 className="font-serif text-3xl text-[#F3F0E8] mb-1">{primary?.title}</h1>
                <p className="text-sm text-[#AAA89F] leading-relaxed max-w-sm">{primary?.description}</p>
              </div>
              <div className="text-right flex-shrink-0 ml-6">
                <div className="text-3xl font-semibold text-[#C89B5B]">{primary?.match}%</div>
                <div className="text-xs text-[#77766F] mt-1">Match</div>
              </div>
            </div>

            <div className="space-y-2 mb-8">
              {primary?.reasons.map((r) => (
                <div key={r} className="flex items-center gap-3">
                  <Check size={13} className="text-[#8C9A7A] flex-shrink-0" />
                  <span className="text-sm text-[#AAA89F]">{r}</span>
                </div>
              ))}
            </div>

            <Button fullWidth onClick={() => navigate('/home')} icon={<ArrowRight size={15} />}>
              Build My Route
            </Button>
          </div>

          {/* Alternatives */}
          <div className="label mb-4">Alternatives for You</div>
          <div className="space-y-2">
            {others.map((career) => (
              <motion.div
                key={career.id}
                whileTap={{ scale: 0.99 }}
                onClick={() => setSelected(career)}
                className={`flex items-center justify-between px-5 py-4 rounded-lg border cursor-pointer transition-all ${
                  selected?.id === career.id
                    ? 'bg-[#22221E] border-[#C89B5B]/30'
                    : 'bg-[#22221E]/50 border-[#383832] hover:border-[#383832]/80'
                }`}
              >
                <div>
                  <div className="text-sm font-medium text-[#F3F0E8]">{career.title}</div>
                  <div className="text-xs text-[#77766F] mt-0.5">{career.reasons[0]}</div>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-sm font-medium text-[#C89B5B]">{career.match}%</span>
                  <ChevronRight size={14} className="text-[#77766F]" />
                </div>
              </motion.div>
            ))}
          </div>

          <p className="text-center text-xs text-[#77766F] mt-8">
            RouteMaster analyzes your skills, interests, and experience to recommend the right path.
          </p>
        </motion.div>
      </div>
    </div>
  );
}
