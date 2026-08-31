"use client";

export default function Scene5Journey() {
  return (
    <div
      className="
        scene-5-copy
        pointer-events-none
        absolute
        inset-0
        z-30
        overflow-hidden
      "
    >
      {/* Dashboard */}

      <div
        className="
          scene5-dashboard
          absolute
          left-1/2
          top-[48%]
          h-[52vh]
          w-[72vw]
          max-w-[1080px]
          -translate-x-1/2
          -translate-y-1/2
          rounded-[34px]
          border
          border-white/[0.07]
          bg-black/20
          opacity-0
          backdrop-blur-xl
          shadow-[0_35px_120px_rgba(0,0,0,0.35)]
        "
      >
        <div
          className="
            absolute
            inset-0
            rounded-[34px]
            bg-gradient-to-br
            from-white/[0.04]
            via-transparent
            to-cyan-200/[0.02]
          "
        />
      </div>

      {/* progress */}

      <div
        className="
          scene5-progress
          absolute
          left-1/2
          top-[27%]
          z-40
          -translate-x-1/2
          text-center
          opacity-0
        "
      >
        <p
          className="
            text-[10px]
            font-semibold
            uppercase
            tracking-[0.45em]
            text-cyan-100/55
          "
        >
          Your learning journey
        </p>

        <h2
          className="
            mt-5
            text-6xl
            font-medium
            tracking-[-0.06em]
            text-white

            md:text-7xl
          "
        >
          72%
        </h2>

        <p
          className="
            mt-3
            text-sm
            font-medium
            text-white/45
          "
        >
          toward AI / ML Engineer
        </p>
      </div>

      {/* progress line */}

      <div
        className="
          scene5-progress-track
          absolute
          left-1/2
          top-[46%]
          z-40
          h-px
          w-[42%]
          -translate-x-1/2
          bg-white/12
          opacity-0
        "
      >
        <div
          className="
            scene5-progress-fill
            h-full
            w-0
            bg-gradient-to-r
            from-cyan-200/80
            via-white/70
            to-cyan-200/60
          "
        />
      </div>

      {/* current */}

      <div
        className="
          scene5-current
          absolute
          left-[24%]
          top-[57%]
          z-40
          opacity-0
        "
      >
        <p
          className="
            text-[9px]
            font-semibold
            uppercase
            tracking-[0.35em]
            text-white/28
          "
        >
          Current
        </p>

        <p
          className="
            mt-2
            text-lg
            font-medium
            text-white/85
          "
        >
          Deep Learning
        </p>
      </div>

      {/* next */}

      <div
        className="
          scene5-next
          absolute
          right-[22%]
          top-[57%]
          z-40
          text-right
          opacity-0
        "
      >
        <p
          className="
            text-[9px]
            font-semibold
            uppercase
            tracking-[0.35em]
            text-white/28
          "
        >
          Next milestone
        </p>

        <p
          className="
            mt-2
            text-lg
            font-medium
            text-white/85
          "
        >
          Build a Deep Learning Project
        </p>
      </div>

      {/* intelligent update */}

      <div
        className="
          scene5-update
          absolute
          bottom-[17%]
          left-1/2
          z-50
          -translate-x-1/2
          opacity-0
        "
      >
        <div
          className="
            rounded-full
            border
            border-cyan-100/[0.12]
            bg-black/25
            px-5
            py-3
            backdrop-blur-xl
          "
        >
          <span
            className="
              text-[10px]
              font-semibold
              uppercase
              tracking-[0.3em]
              text-cyan-100/65
            "
          >
            Learning progress updated
          </span>
        </div>
      </div>
    </div>
  );
}