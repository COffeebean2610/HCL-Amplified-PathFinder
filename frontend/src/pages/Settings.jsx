import { useState } from 'react';
import { motion } from 'framer-motion';
import { Check, User, BookOpen, Shield, ChevronRight } from 'lucide-react';
import { Button } from '../components/common/Button';
import { mockProfile } from '../data/mockData';

const LEARNING_STYLES = ['Theory-first', 'Project-based', 'Balanced', 'Practice-first'];
const WEEKLY_HOURS = ['2 hrs / week', '5 hrs / week', '7 hrs / week', '10 hrs / week', '15+ hrs / week'];
const PACES = ['Relaxed', 'Balanced', 'Intensive'];
const CONTENT_PREFS = ['Short lessons', 'Mixed', 'Deep dives'];

function SelectGroup({ options, value, onChange }) {
  return (
    <div className="flex flex-wrap gap-2">
      {options.map((opt) => (
        <button
          key={opt}
          onClick={() => onChange(opt)}
          className={`px-4 py-2 text-sm rounded-lg border transition-all cursor-pointer ${
            value === opt
              ? 'bg-[#C89B5B]/10 border-[#C89B5B]/60 text-[#C89B5B]'
              : 'bg-transparent border-[#383832] text-[#AAA89F] hover:text-[#F3F0E8] hover:border-[#383832]/80'
          }`}
        >
          {value === opt && <Check size={11} className="inline mr-1.5" />}
          {opt}
        </button>
      ))}
    </div>
  );
}

function SectionHeader({ icon: Icon, label }) {
  return (
    <div className="flex items-center gap-2 mb-6 pb-3 border-b border-[#383832]">
      <Icon size={14} className="text-[#77766F]" />
      <span className="label">{label}</span>
    </div>
  );
}

export default function Settings() {
  const [profile, setProfile] = useState({
    ...mockProfile,
    learningStyle: 'Project-based',
    weeklyHours: '7 hrs / week',
    pace: 'Balanced',
    contentPreference: 'Mixed',
  });
  const [saved, setSaved] = useState(false);

  const update = (field, value) => setProfile((p) => ({ ...p, [field]: value }));

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="max-w-5xl mx-auto px-6 py-8">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="mb-10">
        <div className="label mb-3">Personal Settings</div>
        <h1 className="font-serif text-3xl text-[#F3F0E8] mb-2">Settings</h1>
        <p className="text-[#AAA89F]">Manage your profile and the preferences RouteMaster uses to personalize your learning journey.</p>
      </motion.div>

      <div className="grid lg:grid-cols-3 gap-8">
        {/* Left: Form */}
        <div className="lg:col-span-2 space-y-10">
          {/* Profile */}
          <section>
            <SectionHeader icon={User} label="Profile" />
            <div className="space-y-5">
              <div>
                <label className="label block mb-2">Full Name</label>
                <input value={profile.name} onChange={(e) => update('name', e.target.value)} />
              </div>
              <div>
                <label className="label block mb-2">Email</label>
                <input value={profile.email} onChange={(e) => update('email', e.target.value)} type="email" />
              </div>
              <div>
                <label className="label block mb-2">Experience Level</label>
                <SelectGroup
                  options={['Beginner', 'Intermediate', 'Advanced']}
                  value={profile.experience}
                  onChange={(v) => update('experience', v)}
                />
              </div>
              <div>
                <label className="label block mb-2">Current Goal</label>
                <input value={profile.currentGoal} onChange={(e) => update('currentGoal', e.target.value)} />
              </div>
            </div>
          </section>

          {/* Learning Preferences */}
          <section>
            <SectionHeader icon={BookOpen} label="Learning Preferences" />
            <div className="space-y-6">
              <div>
                <label className="label block mb-3">Learning Style</label>
                <SelectGroup options={LEARNING_STYLES} value={profile.learningStyle} onChange={(v) => update('learningStyle', v)} />
              </div>
              <div>
                <label className="label block mb-3">Available Time</label>
                <SelectGroup options={WEEKLY_HOURS} value={profile.weeklyHours} onChange={(v) => update('weeklyHours', v)} />
              </div>
              <div>
                <label className="label block mb-3">Learning Pace</label>
                <SelectGroup options={PACES} value={profile.pace} onChange={(v) => update('pace', v)} />
              </div>
              <div>
                <label className="label block mb-3">Content Preference</label>
                <SelectGroup options={CONTENT_PREFS} value={profile.contentPreference} onChange={(v) => update('contentPreference', v)} />
              </div>
            </div>

            <div className="mt-6 border border-[#383832] rounded-xl p-5">
              <div className="label text-[#C89B5B] mb-2">RouteMaster Personalization</div>
              <p className="text-sm text-[#77766F] leading-relaxed">
                Your route adapts as your skills and progress change. These preferences help determine how quickly and in what format new checkpoints are introduced.
              </p>
            </div>
          </section>

          {/* Account */}
          <section>
            <SectionHeader icon={Shield} label="Account" />
            <div className="space-y-2">
              {['Change email', 'Change password', 'Sign out'].map((action) => (
                <button
                  key={action}
                  className="w-full flex items-center justify-between px-4 py-3 border border-[#383832] rounded-lg text-sm text-[#AAA89F] hover:text-[#F3F0E8] hover:border-[#C89B5B]/30 transition-colors cursor-pointer text-left"
                >
                  {action}
                  <ChevronRight size={13} className="text-[#77766F]" />
                </button>
              ))}
              <button className="w-full flex items-center justify-between px-4 py-3 border border-[#A96A5F]/30 rounded-lg text-sm text-[#A96A5F] hover:bg-[#A96A5F]/5 transition-colors cursor-pointer">
                Delete account
                <ChevronRight size={13} />
              </button>
            </div>
          </section>

          <Button onClick={handleSave} loading={false}>
            {saved ? '✓ Saved' : 'Save Changes'}
          </Button>
        </div>

        {/* Right: Current personalization summary */}
        <div>
          <div className="sticky top-20">
            <div className="label mb-4 text-[#C89B5B]">Current Personalization</div>
            <div className="border border-[#383832] rounded-xl divide-y divide-[#383832]">
              {[
                { label: 'Goal', value: profile.currentGoal },
                { label: 'Level', value: profile.experience },
                { label: 'Interests', value: profile.interests?.join(' · ') },
                { label: 'Learning style', value: profile.learningStyle },
                { label: 'Time available', value: profile.weeklyHours },
                { label: 'Pace', value: profile.pace },
              ].map((item) => (
                <div key={item.label} className="px-5 py-3">
                  <div className="text-[10px] text-[#77766F] uppercase tracking-wide mb-0.5">{item.label}</div>
                  <div className="text-sm text-[#F3F0E8]">{item.value}</div>
                </div>
              ))}
            </div>
            <p className="text-xs text-[#77766F] mt-4 leading-relaxed">
              These preferences shape your route.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
