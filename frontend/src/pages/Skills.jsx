import React, { useEffect, useMemo, useState } from "react";
import {
  BarChart3,
  ShieldCheck,
  Target,
  Code2,
  Database,
  Brain,
  Network,
  Infinity,
  Server,
  Sigma,
  Cloud,
  TrendingUp,
  Star,
  Crosshair,
  Rocket,
  Search,
  Bell,
} from "lucide-react";

import "./Skills.css";
import { ErrorState, LoadingState } from '../components/common/States';
import { skillService } from '../services/skillService';

/* =========================================================
   SKILL DATA
========================================================= */

const skillCategories = [
  {
    id: "programming",
    title: "Programming",
    icon: Code2,
    value: 84,
    status: "Strong",
    color: "#8BAE4F",
    shades: ["#A8C76A", "#8BAE4F", "#6F913C"],
    skills: [
      { name: "Python", value: 92 },
      { name: "SQL", value: 88 },
      { name: "JavaScript", value: 72 },
    ],
  },

  {
    id: "data",
    title: "Data",
    icon: Database,
    value: 76,
    status: "Strong",
    color: "#36A7A8",
    shades: ["#54C2C1", "#36A7A8", "#238789"],
    skills: [
      { name: "Pandas", value: 84 },
      { name: "NumPy", value: 82 },
      { name: "Data Cleaning", value: 79 },
    ],
  },

  {
    id: "machine-learning",
    title: "Machine Learning",
    icon: Brain,
    value: 62,
    status: "Developing",
    color: "#D49A37",
    shades: ["#E6B45B", "#D49A37", "#B57920"],
    skills: [
      { name: "Supervised Learning", value: 70 },
      { name: "Classification", value: 68 },
      { name: "Regression", value: 65 },
    ],
  },

  {
    id: "deep-learning",
    title: "AI / Deep Learning",
    icon: Network,
    value: 41,
    status: "Needs Focus",
    color: "#D95B48",
    shades: ["#ED755F", "#D95B48", "#B94435"],
    skills: [
      { name: "Neural Networks", value: 34 },
      { name: "Deep Learning", value: 31 },
      { name: "Transformers", value: 14 },
    ],
  },

  {
    id: "mlops",
    title: "MLOps",
    icon: Infinity,
    value: 28,
    status: "Needs Focus",
    color: "#8652B8",
    shades: ["#9E6DCE", "#8652B8", "#68409A"],
    skills: [
      { name: "Docker", value: 22 },
      { name: "Deployment", value: 19 },
      { name: "Monitoring", value: 18 },
    ],
  },

  {
    id: "data-engineering",
    title: "Data Engineering",
    icon: Server,
    value: 45,
    status: "Developing",
    color: "#299A9A",
    shades: ["#46B9B8", "#299A9A", "#217A7B"],
    skills: [
      { name: "SQL", value: 60 },
      { name: "ETL Pipelines", value: 45 },
      { name: "Data Warehousing", value: 30 },
    ],
  },

  {
    id: "statistics",
    title: "Statistics",
    icon: Sigma,
    value: 70,
    status: "Strong",
    color: "#C9B83E",
    shades: ["#E0D05A", "#C9B83E", "#A6962D"],
    skills: [
      { name: "Statistics", value: 78 },
      { name: "Probability", value: 70 },
      { name: "Hypothesis Testing", value: 62 },
    ],
  },

  {
    id: "cloud",
    title: "Cloud",
    icon: Cloud,
    value: 30,
    status: "Needs Focus",
    color: "#2780C5",
    shades: ["#4B9BDD", "#2780C5", "#1B6098"],
    skills: [
      { name: "AWS", value: 35 },
      { name: "GCP", value: 25 },
      { name: "Azure", value: 20 },
    ],
  },
];

/* =========================================================
   CURRENT VS TARGET
========================================================= */

const currentVsTarget = [
  {
    skill: "Python",
    current: 92,
    target: 90,
    color: "#8BAE4F",
  },
  {
    skill: "Statistics",
    current: 78,
    target: 80,
    color: "#C9B83E",
  },
  {
    skill: "Machine Learning",
    current: 64,
    target: 85,
    color: "#D49A37",
  },
  {
    skill: "Model Evaluation",
    current: 48,
    target: 75,
    color: "#D95B48",
  },
  {
    skill: "Deep Learning",
    current: 31,
    target: 70,
    color: "#D95B48",
  },
  {
    skill: "MLOps",
    current: 18,
    target: 60,
    color: "#8652B8",
  },
];

/* =========================================================
   SKILL GAPS
========================================================= */

const skillGaps = [
  {
    title: "Model Evaluation",
    current: 48,
    required: 75,
    label: "HIGH",
    icon: BarChart3,
    color: "#D95B48",
    description: "Currently blocking your next route stage",
  },
  {
    title: "Deep Learning",
    current: 31,
    required: 70,
    label: "UPCOMING",
    icon: Network,
    color: "#D49A37",
    description:
      "Required for the next route stage after Machine Learning",
  },
  {
    title: "MLOps",
    current: 18,
    required: 60,
    label: "FUTURE",
    icon: Server,
    color: "#6AA5D8",
    description:
      "Required for final production-ready AI systems",
  },
];

/* =========================================================
   INSIGHTS
========================================================= */

const insights = [
  {
    title: "Great progress in Python",
    description: "You're ahead of your target by 2%",
    icon: TrendingUp,
    color: "#8BAE4F",
  },
  {
    title: "Focus on Model Evaluation",
    description: "Improve by 27% to reach next stage",
    icon: Star,
    color: "#D49A37",
  },
  {
    title: "Deep Learning needs attention",
    description: "Essential for your AI / ML goal",
    icon: Crosshair,
    color: "#D95B48",
  },
  {
    title: "MLOps is your next frontier",
    description: "Start building for deployment readiness",
    icon: Rocket,
    color: "#6AA5D8",
  },
];

const categoryMeta = {
  Programming: { icon: Code2, color: '#8BAE4F', shades: ['#A8C76A', '#8BAE4F', '#6F913C'] },
  Data: { icon: Database, color: '#36A7A8', shades: ['#54C2C1', '#36A7A8', '#238789'] },
  'Machine Learning': { icon: Brain, color: '#D49A37', shades: ['#E6B45B', '#D49A37', '#B57920'] },
  'AI / Deep Learning': { icon: Network, color: '#D95B48', shades: ['#ED755F', '#D95B48', '#B94435'] },
  MLOps: { icon: Infinity, color: '#8652B8', shades: ['#9E6DCE', '#8652B8', '#68409A'] },
};

function apiCategories(skills) {
  const grouped = skills.reduce((groups, skill) => {
    const category = skill.category || 'Other';
    (groups[category] ||= []).push(skill);
    return groups;
  }, {});
  return Object.entries(grouped).map(([title, items]) => {
    const meta = categoryMeta[title] || { icon: ShieldCheck, color: '#6AA5D8', shades: ['#8CC0EA', '#6AA5D8', '#4B86B6'] };
    const value = Math.round(items.reduce((total, item) => total + (Number(item.proficiency) || 0), 0) / items.length);
    return { id: title.toLowerCase().replace(/[^a-z0-9]+/g, '-'), title, value, status: value >= 70 ? 'Strong' : value >= 45 ? 'Developing' : 'Needs Focus', ...meta, skills: items.map((item) => ({ name: item.name, value: Number(item.proficiency) || 0 })) };
  });
}

/* =========================================================
   RING COMPONENT
========================================================= */

function SkillRing({
  value,
  color,
  size = 108,
}) {
  const radius = 43;
  const circumference = 2 * Math.PI * radius;

  const offset =
    circumference -
    (value / 100) * circumference;

  return (
    <div
      className="skill-ring"
      style={{
        width: size,
        height: size,
      }}
    >
      <svg
        width={size}
        height={size}
        viewBox="0 0 100 100"
      >
        <circle
          className="ring-background"
          cx="50"
          cy="50"
          r={radius}
        />

        <circle
          className="ring-progress"
          cx="50"
          cy="50"
          r={radius}
          style={{
            stroke: color,
            strokeDasharray: circumference,
            strokeDashoffset: offset,
          }}
        />
      </svg>

      <div className="ring-content">
        <strong>{value}%</strong>
        <span>
          {value >= 70
            ? "Strong"
            : value >= 45
              ? "Developing"
              : "Needs Focus"}
        </span>
      </div>
    </div>
  );
}

/* =========================================================
   SKILL CATEGORY CARD
========================================================= */

function SkillCategoryCard({ category }) {
  const Icon = category.icon;

  return (
    <div
      className="skill-category-card"
      style={{
        "--category-color": category.color,
      }}
    >
      <div className="skill-card-header">

        <div
          className="skill-category-icon"
          style={{
            color: category.color,
            background: `${category.color}18`,
          }}
        >
          <Icon size={20} />
        </div>

        <h3>{category.title}</h3>

      </div>

      <div className="skill-ring-wrapper">
        <SkillRing
          value={category.value}
          color={category.color}
        />
      </div>

      <div className="skill-status">
        <span
          style={{
            background: category.color,
          }}
        />

        {category.status}
      </div>

      <div className="sub-skills">

        {category.skills.map((skill, index) => (
          <div
            className="sub-skill"
            key={skill.name}
          >

            <div className="sub-skill-name">
              <span
                style={{
                  background:
                    category.shades[
                    index % category.shades.length
                    ],
                }}
              />

              {skill.name}
            </div>

            <strong>{skill.value}%</strong>

          </div>
        ))}

      </div>
    </div>
  );
}

/* =========================================================
   GAP CARD
========================================================= */

function SkillGapCard({ gap }) {
  const Icon = gap.icon;

  return (
    <div className="gap-card">

      <div
        className="gap-icon"
        style={{
          color: gap.color,
          background: `${gap.color}18`,
        }}
      >
        <Icon size={20} />
      </div>

      <div className="gap-content">

        <div className="gap-title-row">
          <h3>{gap.title}</h3>

          <span
            style={{
              color: gap.color,
            }}
          >
            {gap.label}
          </span>
        </div>

        <div className="gap-row">
          <span>Current</span>

          <div className="gap-progress">
            <div
              style={{
                width: `${gap.current}%`,
                background: gap.color,
              }}
            />
          </div>

          <strong>{gap.current}%</strong>
        </div>

        <div className="gap-row">
          <span>Required</span>

          <div className="gap-progress required">
            <div
              style={{
                width: `${gap.required}%`,
              }}
            />
          </div>

          <strong>{gap.required}%</strong>
        </div>

        <p>{gap.description}</p>

        <button className="find-resource">
          <ArrowRightIcon />
          Find Resources
        </button>

      </div>
    </div>
  );
}

function ArrowRightIcon() {
  return (
    <span className="arrow-icon">
      →
    </span>
  );
}

/* =========================================================
   MAIN COMPONENT
========================================================= */

export default function Skills() {
  const [skills, setSkills] = useState([]);
  const [gaps, setGaps] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    (async () => {
      try {
        const [skillData, gapData] = await Promise.all([skillService.getSkills(), skillService.getSkillGaps()]);
        setSkills(Array.isArray(skillData) ? skillData : []);
        setGaps(Array.isArray(gapData?.skill_gaps) ? gapData.skill_gaps : []);
      } catch (err) {
        setError(err.message || 'Unable to load skills.');
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const categories = useMemo(() => apiCategories(skills), [skills]);
  const targetRows = gaps.map((gap) => ({ skill: gap.skill, current: gap.current, target: gap.required, color: '#D49A37' }));
  const gapCards = gaps.map((gap) => ({ title: gap.skill, current: gap.current, required: gap.required, label: gap.priority, icon: Target, color: '#D49A37', description: gap.reason || 'A skill gap on your learning route.' }));
  const developingCount = skills.filter((skill) => skill.status === 'developing').length;
  const attentionCount = skills.filter((skill) => skill.status === 'needs_attention').length;

  if (loading) return <LoadingState message="Loading skills..." />;
  if (error) return <ErrorState message={error} onRetry={() => window.location.reload()} />;

  return (
      <div className="skills-page">

        {/* ================================================
            TOP BAR
        ================================================= */}

        <header className="skills-header">

          <div>
            <span className="page-eyebrow">
              SKILL INTELLIGENCE
            </span>

            <h1>Your Skills</h1>

            <p>
              Understand your strengths, identify gaps,
              and see what your goal requires next.
            </p>
              

          </div>
        </header>

        {/* ================================================
            MAIN GRID
        ================================================= */}

        <div className="skills-layout">

          {/* ============================================
              LEFT
          ============================================= */}

            <main className="skills-main">

              {/* ==========================================
                CURRENT PROFILE
            =========================================== */}

              <section className="profile-card">

                <div className="section-label">
                  YOUR CURRENT PROFILE
                </div>

                <p className="profile-description">
                  Your strongest skills are Python, SQL and
                  data handling. You’re building the machine
                  learning capabilities required for your
                  AI / ML Engineer goal.
                </p>

                <div className="profile-stats">

                  <div className="profile-stat">

                    <div
                      className="stat-icon green"
                    >
                      <BarChart3 size={19} />
                    </div>

                    <div>
                      <strong>{skills.length}</strong>
                      <span>SKILLS TRACKED</span>
                    </div>

                  </div>

                  <div className="profile-stat">

                    <div
                      className="stat-icon green"
                    >
                      <ShieldCheck size={19} />
                    </div>

                    <div>
                      <strong>5</strong>
                      <span>STRONG</span>
                    </div>

                  </div>

                  <div className="profile-stat">

                    <div
                      className="stat-icon gold"
                    >
                      <Target size={19} />
                    </div>

                    <div>
                      <strong>{developingCount}</strong>
                      <span>DEVELOPING</span>
                    </div>

                  </div>

                  <div className="profile-stat">

                    <div
                      className="stat-icon red"
                    >
                      <Crosshair size={19} />
                    </div>

                    <div>
                      <strong>{attentionCount}</strong>
                      <span>NEED ATTENTION</span>
                    </div>

                  </div>

                </div>

                {/* LANDSCAPE FILTER */}

                <div className="landscape">

                  <div className="section-label">
                    SKILL LANDSCAPE
                  </div>

                  <div className="filter-list">

                    {[
                      "All",
                      "Programming",
                      "Data",
                      "Machine Learning",
                      "AI / Deep Learning",
                      "MLOps",
                    ].map((filter, index) => (
                      <button
                        key={filter}
                        className={
                          index === 0
                            ? "filter active"
                            : "filter"
                        }
                      >
                        {filter}
                      </button>
                    ))}

                  </div>

                </div>

              </section>

              {/* ==========================================
                MASTERY
            =========================================== */}

              <section className="mastery-section">

                <div className="section-label">
                  SKILL MASTERY OVERVIEW
                </div>

                <div className="skill-grid">

                  {categories.map(
                    (category) => (
                      <SkillCategoryCard
                        key={category.id}
                        category={category}
                      />
                    )
                  )}

                </div>

              </section>

              {/* ==========================================
                CURRENT VS TARGET
            =========================================== */}

              <section className="target-card">

                <div className="section-label">
                  CURRENT VS TARGET
                </div>

                <div className="target-header">
                  <span>SKILL</span>
                  <span>CURRENT LEVEL</span>
                  <span>TARGET LEVEL</span>
                  <span>GAP</span>
                </div>

                <div className="target-list">

                  {targetRows.map(
                    (item) => {

                      const gap =
                        item.current -
                        item.target;

                      return (
                        <div
                          className="target-row"
                          key={item.skill}
                        >

                          <span className="target-name">
                            {item.skill}
                          </span>

                          <div className="target-level">

                            <strong>
                              {item.current}%
                            </strong>

                            <div className="target-progress">
                              <div
                                style={{
                                  width: `${item.current}%`,
                                  background:
                                    item.color,
                                }}
                              />
                            </div>

                          </div>

                          <div className="target-level">

                            <strong>
                              {item.target}%
                            </strong>

                            <div className="target-progress">
                              <div
                                style={{
                                  width: `${item.target}%`,
                                  background:
                                    item.target >
                                      item.current
                                      ? "#C69B3D"
                                      : "#8BAE4F",
                                }}
                              />
                            </div>

                          </div>

                          <strong
                            className={
                              gap >= 0
                                ? "gap-positive"
                                : "gap-negative"
                            }
                          >
                            {gap >= 0 ? "+" : ""}
                            {gap}%
                          </strong>

                        </div>
                      );
                    }
                  )}

                </div>

              </section>

            </main>

          {/* ============================================
              RIGHT SIDEBAR
          ============================================= */}

            <aside className="skills-sidebar">

              {/* SKILL GAPS */}

              <section className="side-panel">

                <div className="section-label">
                  SKILL GAPS
                </div>

                <div className="gap-list">

                  {gapCards.map(
                    (gap) => (
                      <SkillGapCard
                        key={gap.title}
                        gap={gap}
                      />
                    )
                  )}

                </div>

              </section>

              {/* INSIGHTS */}

              <section className="side-panel insights-panel">

                <div className="section-label">
                  SKILL INSIGHTS
                </div>

                <div className="insight-list">

                  {insights.map(
                    (insight) => {

                      const Icon =
                        insight.icon;

                      return (
                        <div
                          className="insight"
                          key={insight.title}
                        >

                          <div
                            className="insight-icon"
                            style={{
                              color:
                                insight.color,
                              background:
                                `${insight.color}18`,
                            }}
                          >
                            <Icon size={19} />
                          </div>

                          <div>
                            <strong>
                              {insight.title}
                            </strong>

                            <span>
                              {insight.description}
                            </span>
                          </div>

                        </div>
                      );
                    }
                  )}

                </div>

                <button className="view-insights">
                  View all insights
                  <span>→</span>
                </button>

              </section>

            </aside>

        </div>

      </div>
  );
}
