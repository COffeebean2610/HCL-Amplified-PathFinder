import { motion } from 'framer-motion';
import { AlertCircle } from 'lucide-react';
import { Button } from './Button';

export function LoadingState({ message = 'Loading...' }) {
  return (
    <div className="flex flex-col items-center justify-center py-24 gap-4">
      <div className="flex gap-1.5">
        {[0, 1, 2].map((i) => (
          <motion.div
            key={i}
            className="w-1.5 h-1.5 rounded-full bg-[#C89B5B]"
            animate={{ opacity: [0.3, 1, 0.3] }}
            transition={{ duration: 1.2, repeat: Infinity, delay: i * 0.2 }}
          />
        ))}
      </div>
      <p className="text-sm text-[#77766F]">{message}</p>
    </div>
  );
}

export function SkeletonBlock({ className = '' }) {
  return <div className={`shimmer rounded ${className}`} />;
}

export function ErrorState({ message = "Something went wrong.", onRetry }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 gap-4 text-center">
      <AlertCircle size={32} className="text-[#A96A5F]" />
      <div>
        <p className="text-[#F3F0E8] font-medium">{message}</p>
        <p className="text-sm text-[#77766F] mt-1">We couldn't load this right now.</p>
      </div>
      {onRetry && (
        <Button variant="secondary" size="sm" onClick={onRetry}>Try Again</Button>
      )}
    </div>
  );
}

export function EmptyState({ icon, title, description, action }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 gap-4 text-center">
      {icon && <div className="text-[#383832]">{icon}</div>}
      <div>
        <p className="text-[#F3F0E8] font-medium">{title}</p>
        {description && <p className="text-sm text-[#77766F] mt-1 max-w-xs">{description}</p>}
      </div>
      {action}
    </div>
  );
}
