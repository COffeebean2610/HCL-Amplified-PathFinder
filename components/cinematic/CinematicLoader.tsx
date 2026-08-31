"use client";

type CinematicLoaderProps = {
  progress: number;
  visible: boolean;
};

export default function CinematicLoader({
  progress,
  visible,
}: CinematicLoaderProps) {
  return (
    <div
      className={`
        fixed
        inset-0
        z-[999]
        flex
        items-center
        justify-center
        bg-[#020306]
        transition-all
        duration-700

        ${
          visible
            ? "pointer-events-auto opacity-100"
            : "pointer-events-none opacity-0"
        }
      `}
    >
      <div
        className="
          relative
          z-10
          w-full
          max-w-sm
          px-8
          text-center
        "
      >
        <p
          className="
            text-[10px]
            uppercase
            tracking-[0.45em]
            text-white/30
          "
        >
          AI Career PathFinder
        </p>

        <h1
          className="
            mt-6
            text-2xl
            font-medium
            tracking-[-0.03em]
            text-white
            md:text-3xl
          "
        >
          Preparing your journey
        </h1>

        <div
          className="
            mt-10
            h-px
            w-full
            overflow-hidden
            bg-white/10
          "
        >
          <div
            className="
              h-full
              bg-white
              transition-[width]
              duration-300
              ease-out
            "
            style={{
              width: `${progress}%`,
            }}
          />
        </div>

        <div
          className="
            mt-4
            flex
            justify-between
            text-[9px]
            uppercase
            tracking-[0.3em]
            text-white/25
          "
        >
          <span>
            Loading experience
          </span>

          <span>
            {progress}%
          </span>
        </div>
      </div>

      <div
        className="
          pointer-events-none
          absolute
          left-1/2
          top-1/2
          h-[420px]
          w-[420px]
          -translate-x-1/2
          -translate-y-1/2
          rounded-full
          bg-cyan-400/[0.025]
          blur-[120px]
        "
      />
    </div>
  );
}