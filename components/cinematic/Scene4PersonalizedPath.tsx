"use client";

export default function Scene4PersonalizedPath() {
  return (
    <div
      className="
        scene-4-copy
        pointer-events-none
        absolute
        inset-0
        z-30
        overflow-hidden
      "
    >
      {/* LEFT GRADIENT */}

      <div
        className="
          absolute
          inset-y-0
          left-0
          w-[55%]
          bg-gradient-to-r
          from-black/72
          via-black/30
          to-transparent
        "
      />

      {/* ================================================= */}
      {/* INTRO COPY */}
      {/* ================================================= */}

      <div
        className="
          scene4-title
          absolute
          left-[7%]
          top-1/2
          z-50
          w-[40%]
          max-w-[650px]
          -translate-y-1/2
          opacity-0

          max-md:left-6
          max-md:w-[85%]
        "
      >
        <p
          className="
            text-[10px]
            font-semibold
            uppercase
            tracking-[0.48em]
            text-cyan-100/55
          "
        >
          Your personalized route
        </p>

        <h2
          className="
            mt-6
            text-[clamp(3rem,5.2vw,6rem)]
            font-medium
            leading-[0.9]
            tracking-[-0.06em]
            text-white
          "
        >
          Not a playlist.
          <br />

          <span className="text-white/35">
            A path built for you.
          </span>
        </h2>

        <p
          className="
            mt-7
            max-w-[470px]
            text-[15px]
            font-medium
            leading-7
            text-white/48
          "
        >
          Skills you already know are skipped.
          Missing prerequisites are added.
          The route adapts as you progress.
        </p>
      </div>

      {/* ================================================= */}
      {/* MASTERED MESSAGE */}
      {/* ================================================= */}

      <div
        className="
          scene4-mastered
          absolute
          bottom-[19%]
          left-[7%]
          z-50
          opacity-0
        "
      >
        <div
          className="
            flex
            items-center
            gap-3
            rounded-full
            border
            border-white/[0.10]
            bg-black/30
            px-5
            py-3
            backdrop-blur-xl
          "
        >
          <div
            className="
              flex
              h-5
              w-5
              items-center
              justify-center
              rounded-full
              bg-cyan-100/10
              text-xs
              text-cyan-100
            "
          >
            ✓
          </div>

          <div>
            <p
              className="
                text-[9px]
                font-semibold
                uppercase
                tracking-[0.32em]
                text-white/30
              "
            >
              Already mastered
            </p>

            <p
              className="
                mt-1
                text-sm
                font-medium
                text-white/80
              "
            >
              Python Foundations
            </p>
          </div>
        </div>
      </div>

      {/* ================================================= */}
      {/* PREREQUISITE MESSAGE */}
      {/* ================================================= */}

      <div
        className="
          scene4-prerequisite
          absolute
          bottom-[19%]
          left-[7%]
          z-50
          opacity-0
        "
      >
        <div
          className="
            rounded-full
            border
            border-cyan-100/[0.14]
            bg-cyan-100/[0.04]
            px-5
            py-3
            backdrop-blur-xl
          "
        >
          <p
            className="
              text-[10px]
              font-semibold
              uppercase
              tracking-[0.32em]
              text-cyan-100/65
            "
          >
            Missing prerequisite added
          </p>
        </div>
      </div>

      {/* ================================================= */}
      {/* DESTINATION */}
      {/* ================================================= */}

      <div
        className="
          scene4-destination
          absolute
          bottom-[17%]
          right-[7%]
          z-50
          opacity-0
          text-right
        "
      >
        <p
          className="
            text-[9px]
            font-semibold
            uppercase
            tracking-[0.4em]
            text-white/30
          "
        >
          Destination
        </p>

        <p
          className="
            mt-2
            text-2xl
            font-medium
            tracking-[-0.04em]
            text-white

            md:text-3xl
          "
        >
          AI / ML Engineer
        </p>
      </div>
    </div>
  );
}