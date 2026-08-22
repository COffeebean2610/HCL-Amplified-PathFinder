import { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowRight, ChevronDown, ChevronUp, Check, Circle, Clock, BookOpen, Wrench } from 'lucide-react';
import {
  ReactFlow, Background, Controls, useNodesState, useEdgesState,
  Handle, Position, MiniMap
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { Button } from '../components/common/Button';
import { LoadingState, ErrorState } from '../components/common/States';
import { Drawer } from '../components/common/Modal';
import { routeService } from '../services/routeService';
import { mockResources, mockProjects } from '../data/mockData';

// Custom route node for React Flow
function RouteNode({ data }) {
  const statusColors = {
    completed: '#8C9A7A',
    current: '#C89B5B',
    upcoming: '#383832',
    goal: '#C89B5B',
  };
  const color = statusColors[data.status] || '#383832';

  return (
    <div
      onClick={() => data.onNodeClick(data)}
      className="cursor-pointer px-4 py-3 rounded-lg border transition-all"
      style={{
        minWidth: 160,
        backgroundColor: data.status === 'current' ? '#C89B5B10' : '#22221E',
        borderColor: color,
        borderWidth: data.status === 'goal' ? 2 : 1,
      }}
    >
      <Handle type="target" position={Position.Top} style={{ borderColor: color, background: '#171714' }} />
      <div className="flex items-center gap-2">
        <div
          className="w-2 h-2 rounded-full flex-shrink-0"
          style={{
            backgroundColor: data.status === 'completed' ? color : 'transparent',
            borderWidth: 2,
            borderStyle: 'solid',
            borderColor: color,
          }}
        />
        <span className="text-xs font-semibold" style={{ color: data.status === 'upcoming' ? '#77766F' : '#F3F0E8' }}>
          {data.label}
        </span>
      </div>
      {data.status === 'current' && (
        <div className="mt-1.5 ml-4">
          <span className="text-[9px] font-semibold uppercase tracking-widest text-[#C89B5B]">Current</span>
        </div>
      )}
      <Handle type="source" position={Position.Bottom} style={{ borderColor: color, background: '#171714' }} />
    </div>
  );
}

const nodeTypes = { routeNode: RouteNode };

const FLOW_NODES = [
  { id: 'n1', type: 'routeNode', position: { x: 100, y: 0 }, data: { label: 'Python', status: 'completed' } },
  { id: 'n2', type: 'routeNode', position: { x: 100, y: 100 }, data: { label: 'Statistics', status: 'completed' } },
  { id: 'n3', type: 'routeNode', position: { x: 100, y: 200 }, data: { label: 'Machine Learning', status: 'current' } },
  { id: 'n4', type: 'routeNode', position: { x: 100, y: 300 }, data: { label: 'Deep Learning', status: 'upcoming' } },
  { id: 'n5', type: 'routeNode', position: { x: 100, y: 400 }, data: { label: 'LLM Fundamentals', status: 'upcoming' } },
  { id: 'n6', type: 'routeNode', position: { x: 100, y: 500 }, data: { label: 'Embeddings', status: 'upcoming' } },
  { id: 'n7', type: 'routeNode', position: { x: 100, y: 600 }, data: { label: 'Vector Database', status: 'upcoming' } },
  { id: 'n8', type: 'routeNode', position: { x: 100, y: 700 }, data: { label: 'RAG', status: 'upcoming' } },
  { id: 'n9', type: 'routeNode', position: { x: 100, y: 800 }, data: { label: 'AI Agents', status: 'upcoming' } },
  { id: 'n10', type: 'routeNode', position: { x: 100, y: 900 }, data: { label: 'Deployment', status: 'upcoming', isGoal: true } },
];

const FLOW_EDGES = [
  { id: 'e1-2', source: 'n1', target: 'n2', style: { stroke: '#383832', strokeWidth: 1 } },
  { id: 'e2-3', source: 'n2', target: 'n3', style: { stroke: '#383832', strokeWidth: 1 } },
  { id: 'e3-4', source: 'n3', target: 'n4', style: { stroke: '#383832', strokeWidth: 1 } },
  { id: 'e4-5', source: 'n4', target: 'n5', style: { stroke: '#383832', strokeWidth: 1 } },
  { id: 'e5-6', source: 'n5', target: 'n6', style: { stroke: '#383832', strokeWidth: 1 } },
  { id: 'e6-7', source: 'n6', target: 'n7', style: { stroke: '#383832', strokeWidth: 1 } },
  { id: 'e7-8', source: 'n7', target: 'n8', style: { stroke: '#383832', strokeWidth: 1 } },
  { id: 'e8-9', source: 'n8', target: 'n9', style: { stroke: '#383832', strokeWidth: 1 } },
  { id: 'e9-10', source: 'n9', target: 'n10', style: { stroke: '#383832', strokeWidth: 1 } },
];

function StageAccordion({ stage, isExpanded, onToggle }) {
  const statusColor = {
    completed: '#8C9A7A',
    current: '#C89B5B',
    upcoming: '#77766F',
  }[stage.status];

  return (
    <div className={`border rounded-xl overflow-hidden ${stage.status === 'current' ? 'border-[#C89B5B]/30' : 'border-[#383832]'}`}>
      <button
        className="w-full flex items-center justify-between px-5 py-4 text-left cursor-pointer hover:bg-[#22221E]/50 transition-colors"
        onClick={onToggle}
      >
        <div className="flex items-center gap-4">
          <span className="text-[10px] text-[#77766F] font-medium w-6">{stage.number}</span>
          <div>
            <div className="text-sm font-semibold text-[#F3F0E8]">{stage.title}</div>
            <div className="text-[10px] uppercase tracking-widest font-semibold mt-0.5" style={{ color: statusColor }}>
              {stage.status}
            </div>
          </div>
        </div>
        {isExpanded ? <ChevronUp size={14} className="text-[#77766F]" /> : <ChevronDown size={14} className="text-[#77766F]" />}
      </button>

      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="px-5 pb-5 border-t border-[#383832]">
              {stage.completedSkills?.length > 0 && (
                <div className="mt-4">
                  <div className="text-[10px] text-[#8C9A7A] uppercase tracking-widest mb-2">Completed</div>
                  {stage.completedSkills.map((s) => (
                    <div key={s} className="flex items-center gap-2 py-1.5">
                      <Check size={12} className="text-[#8C9A7A]" />
                      <span className="text-sm text-[#AAA89F]">{s}</span>
                    </div>
                  ))}
                </div>
              )}
              {stage.currentSkill && (
                <div className="mt-4">
                  <div className="text-[10px] text-[#C89B5B] uppercase tracking-widest mb-2">Current</div>
                  <div className="flex items-center gap-2 py-1.5">
                    <ArrowRight size={12} className="text-[#C89B5B]" />
                    <span className="text-sm text-[#F3F0E8]">{stage.currentSkill}</span>
                    {stage.estimatedMinutes && (
                      <span className="text-xs text-[#77766F] flex items-center gap-1">
                        <Clock size={10} />~{stage.estimatedMinutes} min
                      </span>
                    )}
                  </div>
                </div>
              )}
              {stage.upcomingSkills?.length > 0 && (
                <div className="mt-4">
                  <div className="text-[10px] text-[#77766F] uppercase tracking-widest mb-2">Upcoming</div>
                  {stage.upcomingSkills.map((s) => (
                    <div key={s} className="flex items-center gap-2 py-1.5">
                      <Circle size={10} className="text-[#383832]" />
                      <span className="text-sm text-[#77766F]">{s}</span>
                    </div>
                  ))}
                </div>
              )}
              {stage.status === 'current' && (
                <div className="mt-5">
                  <Button size="sm" icon={<ArrowRight size={13} />}>Continue Learning</Button>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default function RouteDetails() {
  const { routeId } = useParams();
  const navigate = useNavigate();
  const [route, setRoute] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedStage, setExpandedStage] = useState('stage-4');
  const [view, setView] = useState('timeline');
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [drawerNode, setDrawerNode] = useState(null);

  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  const handleNodeClick = useCallback((nodeData) => {
    setDrawerNode(nodeData);
    setDrawerOpen(true);
  }, []);

  useEffect(() => {
    (async () => {
      try {
        const data = await routeService.getRouteById(routeId);
        setRoute(data);
      } catch (e) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    })();
  }, [routeId]);

  useEffect(() => {
    const enriched = FLOW_NODES.map((n) => ({
      ...n,
      data: { ...n.data, onNodeClick: handleNodeClick },
    }));
    setNodes(enriched);
    setEdges(FLOW_EDGES);
  }, [handleNodeClick]);

  if (loading) return <LoadingState message="Loading your route..." />;
  if (error) return <ErrorState message={error} />;

  return (
    <div className="max-w-5xl mx-auto px-6 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="label mb-3">My Learning Route</div>
        <div className="flex items-start justify-between">
          <div>
            <h1 className="font-serif text-3xl text-[#F3F0E8] mb-1">Your Route</h1>
            <p className="text-sm text-[#AAA89F]">A personalized sequence designed to take you from your current skills to your goal.</p>
          </div>
        </div>
      </div>

      {/* Goal card */}
      <div className="border border-[#C89B5B]/20 rounded-xl p-5 mb-8 flex items-center justify-between">
        <div>
          <div className="label text-[#C89B5B] mb-1">Destination</div>
          <div className="text-base font-semibold text-[#F3F0E8]">{route?.title}</div>
        </div>
        <div className="text-right">
          <div className="text-2xl font-semibold text-[#C89B5B]">{route?.progress}%</div>
          <div className="text-xs text-[#77766F]">Complete</div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        {[
          { label: 'Stages', value: route?.totalStages || 7 },
          { label: 'Skills', value: route?.totalSkills || 18 },
          { label: 'Projects', value: route?.totalProjects || 6 },
        ].map((s) => (
          <div key={s.label} className="border border-[#383832] rounded-xl p-4 text-center">
            <div className="text-2xl font-semibold text-[#F3F0E8]">{s.value}</div>
            <div className="text-xs text-[#77766F] mt-1">{s.label}</div>
          </div>
        ))}
      </div>

      {/* View toggle */}
      <div className="flex gap-1 p-1 bg-[#22221E] border border-[#383832] rounded-lg w-fit mb-8">
        {['timeline', 'roadmap'].map((v) => (
          <button
            key={v}
            onClick={() => setView(v)}
            className={`px-4 py-1.5 rounded text-xs font-medium capitalize transition-all cursor-pointer ${
              view === v ? 'bg-[#C89B5B] text-[#171714]' : 'text-[#77766F] hover:text-[#F3F0E8]'
            }`}
          >
            {v}
          </button>
        ))}
      </div>

      {view === 'timeline' && (
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Left: stages */}
          <div className="lg:col-span-2 space-y-3">
            {route?.stages.map((stage) => (
              <StageAccordion
                key={stage.id}
                stage={stage}
                isExpanded={expandedStage === stage.id}
                onToggle={() => setExpandedStage(expandedStage === stage.id ? null : stage.id)}
              />
            ))}
            {/* Milestone */}
            <div className="border border-[#383832] border-dashed rounded-xl px-5 py-4">
              <div className="flex items-center gap-3">
                <Wrench size={14} className="text-[#C89B5B]" />
                <div>
                  <div className="text-[10px] text-[#C89B5B] uppercase tracking-widest font-semibold">Build Milestone</div>
                  <div className="text-sm text-[#F3F0E8] mt-0.5">AI Recommendation Engine</div>
                </div>
              </div>
            </div>
            {/* Destination */}
            <div className="border-2 border-[#C89B5B]/40 rounded-xl px-5 py-4 flex items-center gap-3">
              <div className="w-4 h-4 rounded-full border-2 border-[#C89B5B] flex items-center justify-center">
                <div className="w-1.5 h-1.5 rounded-full bg-[#C89B5B]" />
              </div>
              <div>
                <div className="text-[10px] text-[#C89B5B] uppercase tracking-widest font-semibold">Destination</div>
                <div className="text-sm font-semibold text-[#F3F0E8]">{route?.title}</div>
              </div>
            </div>
          </div>

          {/* Right: resources & projects */}
          <div className="space-y-6">
            <div>
              <div className="label mb-3 flex items-center gap-2">
                <BookOpen size={12} /> Recommended Resources
              </div>
              <div className="space-y-2">
                {mockResources.slice(0, 3).map((r) => (
                  <button
                    key={r.id}
                    onClick={() => navigate(`/resources/${r.id}`)}
                    className="w-full text-left border border-[#383832] rounded-lg px-4 py-3 hover:border-[#C89B5B]/30 transition-colors cursor-pointer"
                  >
                    <div className="text-xs font-medium text-[#F3F0E8]">{r.title}</div>
                    <div className="text-[10px] text-[#77766F] mt-1">{r.type} · {r.duration}</div>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {view === 'roadmap' && (
        <div className="border border-[#383832] rounded-xl overflow-hidden" style={{ height: 600 }}>
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            nodeTypes={nodeTypes}
            fitView
            fitViewOptions={{ padding: 0.3 }}
            style={{ background: '#171714' }}
          >
            <Background color="#383832" gap={24} size={1} variant="dots" />
            <Controls style={{ background: '#22221E', border: '1px solid #383832' }} />
          </ReactFlow>
        </div>
      )}

      {/* Node Drawer */}
      <Drawer isOpen={drawerOpen} onClose={() => setDrawerOpen(false)} title={drawerNode?.label || 'Skill Detail'}>
        {drawerNode && (
          <div className="space-y-6">
            <div>
              <div className="text-xl font-semibold text-[#F3F0E8] mb-1">{drawerNode.label}</div>
              <div
                className="text-xs font-semibold uppercase tracking-widest"
                style={{ color: drawerNode.status === 'completed' ? '#8C9A7A' : drawerNode.status === 'current' ? '#C89B5B' : '#77766F' }}
              >
                {drawerNode.status}
              </div>
            </div>

            {drawerNode.status !== 'completed' && (
              <div className="border border-[#C89B5B]/20 rounded-lg px-4 py-3">
                <div className="label text-[#A96A5F] mb-1">Skill Gap</div>
                <div className="text-sm text-[#AAA89F]">Estimated: 3 weeks to reach target proficiency</div>
              </div>
            )}

            <div>
              <div className="label mb-3">Recommended Courses</div>
              {mockResources.slice(0, 2).map((r) => (
                <div key={r.id} className="border border-[#383832] rounded-lg px-4 py-3 mb-2">
                  <div className="text-sm text-[#F3F0E8]">{r.title}</div>
                  <div className="text-xs text-[#77766F] mt-0.5">{r.duration}</div>
                </div>
              ))}
            </div>

            <div>
              <div className="label mb-3">Recommended Project</div>
              <div className="border border-[#383832] rounded-lg px-4 py-3">
                <div className="text-sm text-[#F3F0E8]">Predictive Maintenance System</div>
                <div className="text-xs text-[#77766F] mt-0.5">Intermediate · 6 hours</div>
              </div>
            </div>

            <Button fullWidth icon={<ArrowRight size={14} />} onClick={() => navigate('/resources')}>
              Start Learning
            </Button>
          </div>
        )}
      </Drawer>
    </div>
  );
}
