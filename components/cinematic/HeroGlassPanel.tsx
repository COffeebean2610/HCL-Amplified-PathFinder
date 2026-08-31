"use client";

type HeroGlassPanelProps = {
  className?: string;
};

export default function HeroGlassPanel({
  className = "",
}: HeroGlassPanelProps) {
  return (
    <div
      className={`
        pointer-events-none
        absolute
        left-1/2
        top-1/2
        z-20
        h-[54vh]
        w-[78vw]
        max-w-[1180px]
        -translate-x-1/2
        -translate-y-1/2
        overflow-hidden
        rounded-[40px]
        border
        border-white/[0.045]
        bg-white/[0.018]
        backdrop-blur-[10px]
        shadow-[0_40px_140px_rgba(0,0,0,0.28)]
        will-change-transform
        ${className}
      `}
    >
      <div
        className="
          absolute
          inset-0
          bg-gradient-to-br
          from-white/[0.028]
          via-transparent
          to-cyan-300/[0.015]
        "
      />

      <div
        className="
          absolute
          inset-x-[8%]
          top-[18%]
          h-px
          bg-gradient-to-r
          from-transparent
          via-white/[0.07]
          to-transparent
        "
      />

      <div
        className="
          absolute
          inset-x-[14%]
          bottom-[16%]
          h-px
          bg-gradient-to-r
          from-transparent
          via-cyan-200/[0.05]
          to-transparent
        "
      />
    </div>
  );
}