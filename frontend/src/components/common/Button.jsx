import { motion } from 'framer-motion';

const variants = {
  primary: {
    bg: 'bg-[#C89B5B] hover:bg-[#D4AA6C]',
    text: 'text-[#171714]',
    border: '',
  },
  secondary: {
    bg: 'bg-transparent hover:bg-[#22221E]',
    text: 'text-[#F3F0E8]',
    border: 'border border-[#383832]',
  },
  ghost: {
    bg: 'bg-transparent hover:bg-[#22221E]',
    text: 'text-[#AAA89F] hover:text-[#F3F0E8]',
    border: '',
  },
  danger: {
    bg: 'bg-transparent hover:bg-[#A96A5F]/10',
    text: 'text-[#A96A5F]',
    border: 'border border-[#A96A5F]/30',
  },
};

const sizes = {
  sm: 'px-3 py-1.5 text-xs',
  md: 'px-4 py-2 text-sm',
  lg: 'px-6 py-3 text-sm',
};

export function Button({
  children,
  variant = 'primary',
  size = 'md',
  onClick,
  disabled = false,
  className = '',
  type = 'button',
  fullWidth = false,
  icon,
  loading = false,
}) {
  const v = variants[variant];
  const s = sizes[size];

  return (
    <motion.button
      type={type}
      onClick={onClick}
      disabled={disabled || loading}
      whileTap={{ scale: 0.97 }}
      className={`
        inline-flex items-center justify-center gap-2 font-medium rounded-lg
        transition-all duration-150 cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed
        ${v.bg} ${v.text} ${v.border} ${s}
        ${fullWidth ? 'w-full' : ''} ${className}
      `}
    >
      {loading ? (
        <span className="w-3.5 h-3.5 border-2 border-current border-t-transparent rounded-full animate-spin" />
      ) : icon ? (
        <span className="flex-shrink-0">{icon}</span>
      ) : null}
      {children}
    </motion.button>
  );
}

export function IconButton({ icon, onClick, label, className = '' }) {
  return (
    <motion.button
      onClick={onClick}
      whileTap={{ scale: 0.93 }}
      aria-label={label}
      className={`p-2 rounded-lg text-[#77766F] hover:text-[#F3F0E8] hover:bg-[#22221E] transition-colors cursor-pointer ${className}`}
    >
      {icon}
    </motion.button>
  );
}
