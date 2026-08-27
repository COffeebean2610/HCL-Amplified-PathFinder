import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import {
  ArrowRight,
  Target,
  TrendingUp,
  BookOpen,
  Code2,
  FileText,
  BarChart3,
  Calendar,
  Clock,
  Award,
  Bell,
  Home,
  Folder,
  Settings,
  CircleHelp,
  Check,
  Play,
  Circle,
} from "lucide-react";

import { useAuth } from "../context/AuthContext";


// ============================================================
// REUSABLE COMPONENTS
// ============================================================

function Card({ children, className = "" }) {
  return (
    <div
      className={`
        rounded-lg
        border
        p-5
        ${className}
      `}
      style={{
        backgroundColor: 'var(--surface)',
        borderColor: 'var(--border)',
      }}
    >
      {children}
    </div>
  );
}


function SectionLabel({ children }) {
  return (
    <div className="mb-4 text-[10px] font-semibold uppercase tracking-[0.16em] text-accent">
      {children}
    </div>
  );
}


function ProgressBar({ percentage }) {
  return (
    <div className="h-1.5 w-full overflow-hidden rounded-full" style={{ backgroundColor: 'var(--border)' }}>
      <motion.div
        initial={{ width: 0 }}
        animate={{ width: `${percentage}%` }}
        transition={{ duration: 1 }}
        className="h-full rounded-full"
        style={{ backgroundColor: 'var(--accent)' }}
      />
    </div>
  );
}


// ============================================================
// SIDEBAR
// ============================================================

function Sidebar({ navigate }) {
  const menu = [
    {
      label: "Home",
      icon: Home,
      path: "/",
    },
    {
      label: "Projects",
      icon: Folder,
      path: "/projects",
    },
    {
      label: "Settings",
      icon: Settings,
      path: "/settings",
    },
  ];

  return (
    <aside className="fixed left-0 top-0 z-40 hidden h-screen w-[220px] lg:flex lg:flex-col" style={{ backgroundColor: 'var(--bg)', borderRight: '1px solid var(--border)' }}>

      {/* Logo */}
      <div className="px-5 py-6" style={{ borderBottom: '1px solid var(--border)' }}>
        <div className="font-serif text-[27px] leading-none text-text-primary">
          RouteMaster
        </div>

        <div className="mt-2 text-[10px] uppercase tracking-[0.15em] text-accent">
          Your Learning Route
        </div>
      </div>


      {/* Navigation */}
      <nav className="flex-1 px-3 py-5">

        {menu.map((item, index) => {
          const Icon = item.icon;
          const active = index === 0;

          return (
            <button
              key={item.label}
              onClick={() => navigate(item.path)}
              className={`
                mb-2 flex w-full items-center gap-4 rounded-lg px-4 py-3
                text-left text-sm transition-all
                ${
                  active
                    ? "text-accent"
                    : "text-text-secondary hover:text-text-primary"
                }
              `}
              style={{
                backgroundColor: active ? 'var(--accent)15' : 'transparent',
              }}
              onMouseEnter={(e) => {
                if (!active) e.currentTarget.style.backgroundColor = 'var(--surface)';
              }}
              onMouseLeave={(e) => {
                if (!active) e.currentTarget.style.backgroundColor = 'transparent';
              }}
            >
              <Icon size={20} strokeWidth={1.5} />

              <span>{item.label}</span>
            </button>
          );
        })}

      </nav>


      {/* Help */}
      <div className="px-4 py-5" style={{ borderTop: '1px solid var(--border)' }}>
        <button
          onClick={() => navigate("/help")}
          className="flex items-center gap-4 px-2 text-sm text-text-muted hover:text-text-primary"
        >
          <CircleHelp size={19} strokeWidth={1.5} />
          Help
        </button>
      </div>


      {/* User */}
      <div className="p-4" style={{ borderTop: '1px solid var(--border)' }}>

        <div className="flex items-center gap-3">

          <div className="flex h-10 w-10 items-center justify-center rounded-full font-serif text-lg" style={{ backgroundColor: 'var(--accent)', color: 'var(--bg)' }}>
            A
          </div>

          <div className="min-w-0">
            <div className="truncate text-sm font-medium text-text-primary">
              Abhishek
            </div>

            <div className="truncate text-xs text-text-muted">
              AI / ML Engineer
            </div>
          </div>

        </div>

      </div>

    </aside>
  );
}


// ============================================================
// HEADER
// ============================================================

function Header() {
  return (
    <header className="flex h-[72px] items-center justify-end px-5 lg:px-8" style={{ borderBottom: '1px solid var(--border)' }}>

      <div className="flex items-center gap-5">

        <button className="text-accent hover:text-accent-hover">
          <Bell size={21} strokeWidth={1.5} />
        </button>

        <div className="flex h-9 w-9 items-center justify-center rounded-full font-serif text-lg" style={{ backgroundColor: 'var(--accent)', color: 'var(--bg)' }}>
          A
        </div>

      </div>

    </header>
  );
}


// ============================================================
// GOAL SNAPSHOT
// ============================================================

function GoalSnapshot({ userData }) {
  return (
    <Card>

      <div className="flex items-start justify-between">

        <div>

          <SectionLabel>
            Your Goal Snapshot
          </SectionLabel>

          <div className="flex items-center gap-3">

            <div className="flex h-11 w-11 items-center justify-center rounded-full" style={{ backgroundColor: 'var(--accent)18' }}>
              <Target
                size={21}
                className="text-accent"
                strokeWidth={1.5}
              />
            </div>

            <h2 className="font-serif text-xl text-text-primary">
              {userData.targetCareer}
            </h2>

          </div>

        </div>


        <div className="text-right">

          <div className="font-serif text-2xl text-accent">
            {userData.progress}%
          </div>

          <div className="text-[10px] text-text-secondary">
            Complete
          </div>

        </div>

      </div>


      <div className="mt-5">
        <ProgressBar percentage={userData.progress} />
      </div>


      <div className="mt-5 flex items-center justify-between pt-4" style={{ borderTop: '1px solid var(--border)' }}>

        <div>
          <div className="text-[10px] text-text-muted">
            Started
          </div>

          <div className="mt-1 text-xs text-text-primary">
            {userData.startDate}
          </div>
        </div>


        <div className="h-8 w-px" style={{ backgroundColor: 'var(--border)' }} />


        <div className="text-right">
          <div className="text-[10px] text-text-muted">
            Target
          </div>

          <div className="mt-1 text-xs text-text-primary">
            {userData.targetDate}
          </div>
        </div>

      </div>

    </Card>
  );
}


// ============================================================
// CURRENT STAGE
// ============================================================

function CurrentStage({ userData, navigate }) {
  return (
    <Card>

      <SectionLabel>
        Your Current Stage
      </SectionLabel>

      <div className="flex items-center justify-between">

        <div className="flex items-center gap-3">

          <div className="flex h-11 w-11 items-center justify-center rounded-lg" style={{ backgroundColor: 'var(--accent)18' }}>
            <BarChart3
              size={21}
              className="text-accent"
              strokeWidth={1.5}
            />
          </div>

          <div>

            <h3 className="font-serif text-lg text-text-primary">
              {userData.currentStage}
            </h3>

            <div className="text-xs text-text-muted">
              Stage {userData.currentStageNumber} of{" "}
              {userData.totalStages}
            </div>

          </div>

        </div>


        <button
          onClick={() => navigate("/routes")}
          className="flex items-center gap-1 rounded-lg px-3 py-2 text-xs text-accent transition"
          style={{ border: '1px solid var(--border)' }}
          onMouseEnter={(e) => { e.currentTarget.style.borderColor = 'var(--accent)'; }}
          onMouseLeave={(e) => { e.currentTarget.style.borderColor = 'var(--border)'; }}
        >
          View Stage
          <ArrowRight size={13} />
        </button>

      </div>

    </Card>
  );
}


// ============================================================
// DAILY FOCUS
// ============================================================

function DailyFocus({ dailyFocus, navigate }) {
  return (
    <Card>

      <SectionLabel>
        Daily Focus
      </SectionLabel>

      <div className="flex items-center justify-between">

        <div className="flex items-center gap-3">

          <div className="flex h-11 w-11 items-center justify-center rounded-lg" style={{ backgroundColor: 'var(--accent)18' }}>
            <Target
              size={19}
              className="text-accent"
            />
          </div>

          <div>

            <h4 className="text-sm font-medium text-text-primary">
              {dailyFocus.title}
            </h4>

            <div className="mt-1 flex items-center gap-1 text-xs text-text-muted">
              <Clock size={11} />
              {dailyFocus.duration}
            </div>

          </div>

        </div>


        <button
          onClick={() => navigate("/resources")}
          className="flex items-center gap-1 rounded-lg px-3 py-2 text-xs text-accent transition"
          style={{ border: '1px solid var(--border)' }}
          onMouseEnter={(e) => { e.currentTarget.style.borderColor = 'var(--accent)'; }}
          onMouseLeave={(e) => { e.currentTarget.style.borderColor = 'var(--border)'; }}
        >
          Continue
          <ArrowRight size={13} />
        </button>

      </div>

    </Card>
  );
}


// ============================================================
// ROUTE OVERVIEW
// ============================================================

function RouteOverview({ routeStages, navigate }) {
  return (
    <Card>

      <div className="mb-5 flex items-center justify-between">

        <SectionLabel>
          Your Route Overview
        </SectionLabel>

        <button
          onClick={() => navigate("/routes")}
          className="flex items-center gap-1 text-xs text-accent hover:text-accent-hover"
        >
          View Full Route
          <ArrowRight size={12} />
        </button>

      </div>


      <div className="space-y-3">

        {routeStages.map((stage, index) => {

          const completed = stage.status === "completed";
          const current = stage.status === "current";

          return (
            <div
              key={stage.number}
              className="flex items-start gap-3"
            >

              {/* Timeline */}
              <div className="flex flex-col items-center">

                {completed ? (
                  <div className="flex h-6 w-6 items-center justify-center rounded-full" style={{ backgroundColor: 'var(--completed)' }}>
                    <Check
                      size={13}
                      style={{ color: 'var(--bg)' }}
                    />
                  </div>
                ) : current ? (
                  <div className="flex h-6 w-6 items-center justify-center rounded-full" style={{ backgroundColor: 'var(--accent)' }}>
                    <div className="h-2 w-2 rounded-full" style={{ backgroundColor: 'var(--bg)' }} />
                  </div>
                ) : (
                  <div className="h-6 w-6 rounded-full" style={{ border: '2px solid var(--border)' }} />
                )}

                {index !== routeStages.length - 1 && (
                  <div className="h-7 w-px" style={{ backgroundColor: 'var(--border)' }} />
                )}

              </div>


              <div className="pt-0.5">

                <div className="flex items-center gap-2">

                  <span className="text-[10px] text-text-muted">
                    0{stage.number}
                  </span>

                  <span className="text-sm text-text-primary">
                    {stage.title}
                  </span>

                </div>

                <div
                  className={`
                    mt-0.5 text-[11px]
                    ${
                      completed
                        ? "text-completed"
                        : current
                        ? "text-accent"
                        : "text-text-muted"
                    }
                  `}
                >
                  {completed
                    ? "Completed"
                    : current
                    ? "Current Stage"
                    : "Upcoming"}
                </div>

              </div>

            </div>
          );
        })}

      </div>

    </Card>
  );
}


// ============================================================
// SKILLS
// ============================================================

function SkillsCard({ skillsData, navigate }) {
  return (
    <Card>

      <div className="flex items-center justify-between">

        <SectionLabel>
          Skills at a Glance
        </SectionLabel>

        <button
          onClick={() => navigate("/skills")}
          className="flex items-center gap-1 text-xs text-accent hover:text-accent-hover"
        >
          View All Skills
          <ArrowRight size={12} />
        </button>

      </div>


      <div className="flex items-center gap-6">

        {/* Circle */}
        <div className="relative h-[105px] w-[105px] flex-shrink-0">

          <svg
            viewBox="0 0 120 120"
            className="-rotate-90"
          >

            <circle
              cx="60"
              cy="60"
              r="49"
              fill="none"
              stroke="var(--border)"
              strokeWidth="8"
            />

            <circle
              cx="60"
              cy="60"
              r="49"
              fill="none"
              stroke="var(--accent)"
              strokeWidth="8"
              strokeLinecap="round"
              strokeDasharray="308"
              strokeDashoffset={
                308 -
                (skillsData.strong / skillsData.total) *
                  308
              }
            />

          </svg>


          <div className="absolute inset-0 flex flex-col items-center justify-center">

            <div className="font-serif text-2xl text-text-primary">
              {skillsData.total}
            </div>

            <div className="text-[8px] uppercase tracking-wider text-text-muted">
              Skills
            </div>

          </div>

        </div>


        {/* Breakdown */}
        <div className="flex-1 space-y-3">

          <div className="flex justify-between">
            <span className="text-xs text-text-secondary">
              <span className="mr-2 inline-block h-2 w-2 rounded-full" style={{ backgroundColor: 'var(--completed)' }} />
              Strong
            </span>

            <span className="text-xs text-text-primary">
              {skillsData.strong}
            </span>
          </div>


          <div className="flex justify-between">
            <span className="text-xs text-text-secondary">
              <span className="mr-2 inline-block h-2 w-2 rounded-full" style={{ backgroundColor: 'var(--accent)' }} />
              Developing
            </span>

            <span className="text-xs text-text-primary">
              {skillsData.developing}
            </span>
          </div>


          <div className="flex justify-between">
            <span className="text-xs text-text-secondary">
              <span className="mr-2 inline-block h-2 w-2 rounded-full" style={{ backgroundColor: 'var(--danger)' }} />
              Need Attention
            </span>

            <span className="text-xs text-text-primary">
              {skillsData.needsAttention}
            </span>
          </div>

        </div>

      </div>


      {/* Developing */}
      <div className="mt-5 pt-5" style={{ borderTop: '1px solid var(--border)' }}>

        <div className="mb-3 text-[10px] font-semibold uppercase tracking-wider text-accent">
          Top Developing
        </div>

        <div className="space-y-3">

          {skillsData.topDeveloping.map((skill) => (
            <div key={skill.name}>

              <div className="mb-1 flex justify-between">

                <span className="text-xs text-text-primary">
                  {skill.name}
                </span>

                <span className="text-xs text-accent">
                  {skill.progress}%
                </span>

              </div>

              <ProgressBar
                percentage={skill.progress}
              />

            </div>
          ))}

        </div>

      </div>

    </Card>
  );
}


// ============================================================
// PROJECTS
// ============================================================

function ProjectsCard({ projectsData, navigate }) {
  return (
    <Card>

      <div className="mb-3 flex items-center justify-between">

        <SectionLabel>
          Projects on Your Route
        </SectionLabel>

        <button
          onClick={() => navigate("/projects")}
          className="flex items-center gap-1 text-xs text-accent hover:text-accent-hover"
        >
          View All Projects
          <ArrowRight size={12} />
        </button>

      </div>


      <div>

        {projectsData.map((project) => {

          const completed =
            project.status === "completed";

          const inProgress =
            project.status === "in_progress";

          return (
            <div
              key={project.title}
              className="flex items-center gap-3 py-3 last:border-0"
              style={{ borderBottom: '1px solid var(--border)' }}
            >

              {completed ? (
                <div className="flex h-5 w-5 items-center justify-center rounded" style={{ backgroundColor: 'var(--completed)' }}>
                  <Check
                    size={11}
                    style={{ color: 'var(--bg)' }}
                  />
                </div>
              ) : inProgress ? (
                <div className="flex h-5 w-5 items-center justify-center rounded border" style={{ borderColor: 'var(--accent)' }}>
                  <Play
                    size={9}
                    fill="var(--accent)"
                    style={{ color: 'var(--accent)' }}
                  />
                </div>
              ) : (
                <Circle
                  size={19}
                  style={{ color: 'var(--border)' }}
                />
              )}

              <div className="flex-1">

                <div className="text-sm text-text-primary">
                  {project.title}
                </div>

                <div className="text-[11px] text-text-muted">
                  {completed
                    ? "Completed"
                    : inProgress
                    ? "In Progress"
                    : "Upcoming"}
                </div>

              </div>


              {inProgress && (
                <span className="text-sm font-semibold text-accent">
                  {project.progress}%
                </span>
              )}

              {completed && (
                <span className="text-sm text-completed">
                  100%
                </span>
              )}

            </div>
          );
        })}

      </div>

    </Card>
  );
}


// ============================================================
// WEEKLY PROGRESS
// ============================================================

function WeeklyProgress({ progressThisWeek, navigate }) {
  return (
    <Card>

      <SectionLabel>
        Progress This Week
      </SectionLabel>


      <div className="grid grid-cols-4 gap-3">

        <Stat
          icon={Clock}
          value={progressThisWeek.timeSpent}
          label="Time Learned"
        />

        <Stat
          icon={BookOpen}
          value={progressThisWeek.lessonsCompleted}
          label="Lessons Completed"
        />

        <Stat
          icon={TrendingUp}
          value={`+${progressThisWeek.skillsImproved}`}
          label="Skills Improved"
        />

        <Stat
          icon={Calendar}
          value={progressThisWeek.dayStreak}
          label="Day Streak"
        />

      </div>


      <div className="mt-6 pt-5" style={{ borderTop: '1px solid var(--border)' }}>

        <div className="flex h-[100px] items-end gap-3">

          {progressThisWeek.weeklyActivity.map(
            (day) => {

              const height =
                day.hours === 0
                  ? 8
                  : Math.max(
                      15,
                      (day.hours / 2) * 100
                    );

              return (
                <div
                  key={day.day}
                  className="flex flex-1 flex-col items-center gap-2"
                >

                  <div className="flex h-[75px] w-full items-end">

                    <div
                      className={`
                        w-full rounded-t
                        ${
                          day.day === "Thu"
                            ? ""
                            : day.hours > 0
                            ? ""
                            : ""
                        }
                      `}
                      style={{
                        height: `${height}%`,
                        backgroundColor: day.day === "Thu" ? 'var(--accent)' : day.hours > 0 ? 'var(--text-secondary)' : 'var(--border)',
                      }}
                    />

                  </div>

                  <span className="text-[10px] text-text-muted">
                    {day.day}
                  </span>

                </div>
              );
            }
          )}

        </div>

      </div>


      <button
        onClick={() => navigate("/progress")}
        className="mt-5 flex w-full items-center justify-center gap-1 rounded-lg border border-[#45443D] py-2.5 text-xs text-[#C89B5B] hover:border-[#C89B5B]"
      >
        View Detailed Progress
        <ArrowRight size={12} />
      </button>

    </Card>
  );
}


function Stat({ icon: Icon, value, label }) {
  return (
    <div>

      <div className="flex items-center gap-1.5">

        <Icon
          size={13}
          className="text-[#C89B5B]"
        />

        <span className="text-base font-semibold text-[#F3F0E8]">
          {value}
        </span>

      </div>

      <div className="mt-1 text-[8px] uppercase tracking-wider text-[#77766F]">
        {label}
      </div>

    </div>
  );
}


// ============================================================
// RECOMMENDATIONS
// ============================================================

function Recommendations({ recommendations, navigate }) {
  return (
    <div>

      <SectionLabel>
        What RouteMaster Recommends You Do Today
      </SectionLabel>


      <div className="grid grid-cols-4 gap-3">

        {recommendations.map((item) => {

          const Icon = item.icon;

          return (
            <button
              key={item.title}
              onClick={() => navigate("/resources")}
              className="group rounded-xl border border-[#2C2C28] bg-[#111110] p-4 text-left transition hover:border-[#665033]"
            >

              <div className="mb-4 flex h-9 w-9 items-center justify-center rounded-lg bg-[#292818]">
                <Icon
                  size={17}
                  className="text-[#C89B5B]"
                />
              </div>

              <h4 className="mb-1 text-xs font-semibold text-[#F3F0E8]">
                {item.title}
              </h4>

              <p className="text-[10px] leading-relaxed text-[#77766F]">
                {item.description}
              </p>

              <div className="mt-4 flex justify-end">
                <ArrowRight
                  size={14}
                  className="text-[#C89B5B] transition group-hover:translate-x-1"
                />
              </div>

            </button>
          );
        })}

      </div>

    </div>
  );
}


// ============================================================
// MAIN DASHBOARD
// ============================================================

export default function Overview() {

  const navigate = useNavigate();
  const { currentUser } = useAuth();

  const [loading] = useState(false);
  const [error] = useState(null);


  // ----------------------------------------------------------
  // DATA
  // ----------------------------------------------------------

  const userData = {
    targetCareer: "AI / ML Engineer",
    progress: 68,
    startDate: "12 Aug 2026",
    targetDate: "12 Feb 2027",
    currentStage: "Machine Learning",
    currentStageNumber: "04",
    totalStages: "06",
  };


  const routeStages = [
    {
      number: 1,
      title: "Foundations",
      status: "completed",
    },
    {
      number: 2,
      title: "Python & Data Handling",
      status: "completed",
    },
    {
      number: 3,
      title: "Statistics & Probability",
      status: "completed",
    },
    {
      number: 4,
      title: "Machine Learning",
      status: "current",
    },
    {
      number: 5,
      title: "Deep Learning",
      status: "upcoming",
    },
    {
      number: 6,
      title: "MLOps & Deployment",
      status: "upcoming",
    },
  ];


  const skillsData = {
    total: 18,
    strong: 7,
    developing: 6,
    needsAttention: 5,

    topDeveloping: [
      {
        name: "Model Evaluation",
        progress: 48,
      },
      {
        name: "Feature Engineering",
        progress: 61,
      },
      {
        name: "Deep Learning",
        progress: 31,
      },
    ],
  };


  const projectsData = [
    {
      title: "Spam Detection Model",
      status: "completed",
      progress: 100,
    },
    {
      title: "Customer Churn Predictor",
      status: "in_progress",
      progress: 64,
    },
    {
      title: "Image Classification System",
      status: "upcoming",
      progress: 0,
    },
    {
      title: "AI Recommendation Engine",
      status: "upcoming",
      progress: 0,
    },
  ];


  const progressThisWeek = {
    timeSpent: "4h 32m",
    lessonsCompleted: 7,
    skillsImproved: 3,
    dayStreak: 6,

    weeklyActivity: [
      { day: "Mon", hours: 0.8 },
      { day: "Tue", hours: 1.2 },
      { day: "Wed", hours: 0.9 },
      { day: "Thu", hours: 1.5 },
      { day: "Fri", hours: 0 },
      { day: "Sat", hours: 0 },
      { day: "Sun", hours: 0 },
    ],
  };


  const dailyFocus = {
    title: "Complete Model Evaluation",
    duration: "~45 min",
  };


  const recommendations = [
    {
      icon: BookOpen,
      title: "Continue Model Evaluation",
      description:
        "This is your next priority in Machine Learning stage.",
    },
    {
      icon: Code2,
      title: "Practice Classification Metrics",
      description:
        "Strengthen your evaluation skills with hands-on practice.",
    },
    {
      icon: FileText,
      title: "Read Cross Validation Guide",
      description:
        "Understand why validation is critical before moving ahead.",
    },
    {
      icon: Award,
      title: "Work on Project Milestone",
      description:
        "Complete model training for your Customer Churn project.",
    },
  ];


  // ----------------------------------------------------------
  // STATES
  // ----------------------------------------------------------

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#0D0D0C] text-[#C89B5B]">
        Loading your overview...
      </div>
    );
  }


  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#0D0D0C] text-red-400">
        {error}
      </div>
    );
  }


  // ----------------------------------------------------------
  // UI
  // ----------------------------------------------------------

  return (
    <div className="min-h-screen bg-[#0D0D0C] text-[#F3F0E8]">

      <Sidebar navigate={navigate} />

      <div className="lg:ml-[220px]">

        <Header />


        <main className="px-5 py-7 lg:px-8">

          {/* ================================================
              TOP AREA
          ================================================= */}

          <div className="mb-7 flex flex-col justify-between gap-6 xl:flex-row">

            <div>

              <div className="mb-2 text-[11px] uppercase tracking-[0.18em] text-[#C89B5B]">
                Your Learning Studio
              </div>

              <h1 className="max-w-xl font-serif text-4xl leading-[1.05] text-[#F3F0E8] xl:text-5xl">
                What do you want
                <br />
                to become?
              </h1>

              <p className="mt-4 max-w-xl text-sm leading-6 text-[#AAA89F]">
                Tell RouteMaster where you want to go.
                <br />
                We'll help you figure out the sequence to get there.
              </p>

            </div>


            {/* Goal input */}
            <div className="w-full max-w-[760px]">

              <div className="rounded-xl border border-[#45443D] bg-[#111110] p-5 transition hover:border-[#8B6738]">

                <textarea
                  rows={3}
                  placeholder="Tell RouteMaster what you're working toward..."
                  className="w-full resize-none border-none bg-transparent text-sm text-[#F3F0E8] outline-none placeholder:text-[#62615A]"
                />

                <p className="mb-4 text-[11px] leading-5 text-[#77766F]">
                  Example: "I want to become an ML Engineer. I know
                  Python and SQL, but I need stronger foundations in
                  statistics and machine learning."
                </p>


                <div className="flex items-center justify-between">

                  <div className="flex items-center gap-1">

                    <button className="h-8 w-8 rounded text-sm font-bold text-[#AAA89F] hover:bg-[#292925]">
                      B
                    </button>

                    <button className="h-8 w-8 rounded font-serif italic text-[#AAA89F] hover:bg-[#292925]">
                      I
                    </button>

                    <button className="h-8 w-8 rounded text-[#AAA89F] hover:bg-[#292925]">
                      ≡
                    </button>

                    <button className="h-8 w-8 rounded text-xs text-[#AAA89F] hover:bg-[#292925]">
                      {"</>"}
                    </button>

                    <button className="h-8 w-8 rounded text-[#AAA89F] hover:bg-[#292925]">
                      📎
                    </button>

                  </div>


                  <button
                    onClick={() =>
                      navigate("/recommendation")
                    }
                    className="flex items-center gap-2 rounded-lg bg-[#D49A37] px-5 py-2.5 text-xs font-semibold text-[#171714] transition hover:bg-[#E2AA4A]"
                  >
                    Plan My Route
                    <ArrowRight size={14} />
                  </button>

                </div>

              </div>


              {/* Example pills */}
              <div className="mt-4">

                <div className="mb-2 text-[10px] text-[#77766F]">
                  Try these examples:
                </div>

                <div className="flex flex-wrap gap-2">

                  {[
                    "Become an AI Engineer",
                    "Data Scientist",
                    "ML Engineer",
                    "Full Stack Developer",
                    "Cloud Engineer",
                  ].map((example) => (

                    <button
                      key={example}
                      className="rounded-full border border-[#353530] bg-[#151514] px-3.5 py-1.5 text-[10px] text-[#AAA89F] transition hover:border-[#C89B5B] hover:text-[#C89B5B]"
                    >
                      {example}
                    </button>

                  ))}

                </div>

              </div>

            </div>

          </div>


          {/* ================================================
              MAIN DASHBOARD
          ================================================= */}

          <div className="grid grid-cols-1 gap-5 xl:grid-cols-12">


            {/* ============================================
                LEFT / MAIN COLUMN
            ============================================= */}

            <div className="space-y-5 xl:col-span-8">

              <GoalSnapshot
                userData={userData}
              />


              <div className="grid grid-cols-1 gap-5 md:grid-cols-2">

                <CurrentStage
                  userData={userData}
                  navigate={navigate}
                />

                <DailyFocus
                  dailyFocus={dailyFocus}
                  navigate={navigate}
                />

              </div>


              <div className="grid grid-cols-1 gap-5 md:grid-cols-2">

                <RouteOverview
                  routeStages={routeStages}
                  navigate={navigate}
                />

                <SkillsCard
                  skillsData={skillsData}
                  navigate={navigate}
                />

              </div>


              <ProjectsCard
                projectsData={projectsData}
                navigate={navigate}
              />

            </div>


            {/* ============================================
                RIGHT COLUMN
            ============================================= */}

            <div className="space-y-5 xl:col-span-4">

              <WeeklyProgress
                progressThisWeek={progressThisWeek}
                navigate={navigate}
              />


              {/* Current focus summary */}
              <Card>

                <SectionLabel>
                  Continue Learning
                </SectionLabel>

                <div className="flex items-center gap-4">

                  <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-[#292818]">
                    <BookOpen
                      size={20}
                      className="text-[#C89B5B]"
                    />
                  </div>

                  <div>

                    <div className="text-sm font-medium text-[#F3F0E8]">
                      {dailyFocus.title}
                    </div>

                    <div className="mt-1 text-xs text-[#77766F]">
                      {dailyFocus.duration}
                    </div>

                  </div>

                </div>


                <button
                  onClick={() => navigate("/resources")}
                  className="mt-4 flex w-full items-center justify-center gap-2 rounded-lg bg-[#D49A37] py-2.5 text-xs font-semibold text-[#171714] hover:bg-[#E2AA4A]"
                >
                  Continue
                  <ArrowRight size={13} />
                </button>

              </Card>

            </div>

          </div>


          {/* ================================================
              RECOMMENDATIONS
          ================================================= */}

          <div className="mt-7">

            <Recommendations
              recommendations={recommendations}
              navigate={navigate}
            />

          </div>

        </main>

      </div>

    </div>
  );
}