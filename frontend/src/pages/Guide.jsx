import { useState } from 'react';
import { motion } from 'framer-motion';
import { Sparkles, Send, ArrowRight } from 'lucide-react';
import { Button } from '../components/common/Button';

const SUGGESTED = [
  'Why is this my next step?',
  'Can I skip this module?',
  'What should I practice today?',
  'Why do I need this skill?',
  'How long will my route take?',
];

const MOCK_RESPONSES = {
  'Why is this my next step?': "Model Evaluation is your next step because you've completed Supervised Learning, Classification, and Regression. Evaluating your models is the prerequisite gate before Ensemble Methods — without it, you wouldn't be able to measure whether your models actually work.",
  'Can I skip this module?': "Skipping Model Evaluation is not recommended. It's a hard prerequisite for the next 3 stages. Without it, you'd have no way to validate models you build in Deep Learning or MLOps. I'd suggest spending 45 minutes on it now — it will unlock your next stage.",
  'What should I practice today?': "Today I'd recommend working through the Cross Validation notebook in your Machine Learning stage. You have 45 minutes available, and this directly addresses your highest-priority skill gap.",
  'Why do I need this skill?': "Model Evaluation is foundational to everything that follows. In Deep Learning, you'll evaluate neural networks. In MLOps, you'll monitor model performance in production. Without knowing how to evaluate a model, you can't know if your AI system is actually working.",
};

export default function Guide() {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: "You're ready to move into model evaluation. I can answer questions about your current route, skill gaps, or next step." }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const sendMessage = async (text) => {
    const msg = text || input.trim();
    if (!msg) return;
    setInput('');
    setMessages((m) => [...m, { role: 'user', content: msg }]);
    setLoading(true);

    await new Promise((r) => setTimeout(r, 800));
    const response = MOCK_RESPONSES[msg] || `That's a great question about "${msg}". Based on your current route, I'd suggest focusing on Model Evaluation first — it's directly blocking your progression to the Deep Learning stage. Once you clear that gap, your next 3 skills will unlock automatically.`;
    setMessages((m) => [...m, { role: 'assistant', content: response }]);
    setLoading(false);
  };

  return (
    <div className="max-w-3xl mx-auto px-6 py-8 h-full flex flex-col">
      <div className="mb-6">
        <div className="label mb-3">AI Guide</div>
        <h1 className="font-serif text-3xl text-[#F3F0E8] mb-2">RouteMaster Guide</h1>
        <p className="text-[#AAA89F]">Ask about your route, skill gaps, next steps, or why certain things are recommended.</p>
      </div>

      {/* Suggested questions */}
      <div className="mb-6">
        <div className="label mb-3">Suggested Questions</div>
        <div className="flex flex-wrap gap-2">
          {SUGGESTED.map((q) => (
            <button
              key={q}
              onClick={() => sendMessage(q)}
              className="px-3 py-1.5 border border-[#383832] rounded-lg text-xs text-[#AAA89F] hover:text-[#F3F0E8] hover:border-[#C89B5B]/30 transition-colors cursor-pointer"
            >
              {q}
            </button>
          ))}
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 space-y-4 mb-6 overflow-y-auto">
        {messages.map((msg, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {msg.role === 'assistant' && (
              <div className="w-6 h-6 rounded-full bg-[#C89B5B]/15 border border-[#C89B5B]/30 flex items-center justify-center mr-3 mt-1 flex-shrink-0">
                <Sparkles size={11} className="text-[#C89B5B]" />
              </div>
            )}
            <div
              className={`max-w-sm rounded-xl px-4 py-3 text-sm leading-relaxed ${
                msg.role === 'user'
                  ? 'bg-[#C89B5B]/10 border border-[#C89B5B]/20 text-[#F3F0E8]'
                  : 'bg-[#22221E] border border-[#383832] text-[#AAA89F]'
              }`}
            >
              {msg.content}
            </div>
          </motion.div>
        ))}
        {loading && (
          <div className="flex items-center gap-3">
            <div className="w-6 h-6 rounded-full bg-[#C89B5B]/15 border border-[#C89B5B]/30 flex items-center justify-center">
              <Sparkles size={11} className="text-[#C89B5B]" />
            </div>
            <div className="flex gap-1.5">
              {[0, 1, 2].map((i) => (
                <motion.div
                  key={i}
                  className="w-1.5 h-1.5 rounded-full bg-[#C89B5B]"
                  animate={{ opacity: [0.3, 1, 0.3] }}
                  transition={{ duration: 1, repeat: Infinity, delay: i * 0.2 }}
                />
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="flex gap-3">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => { if (e.key === 'Enter') sendMessage(); }}
          placeholder="Ask about your route, skills, or next step..."
          className="flex-1"
        />
        <Button onClick={() => sendMessage()} icon={<Send size={14} />} disabled={!input.trim()}>
          Send
        </Button>
      </div>
    </div>
  );
}
