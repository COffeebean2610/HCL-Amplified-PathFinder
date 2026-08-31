"use client";

export default function Scene3Understanding() {
  return (
    <div
      className="
        scene-3-copy
        pointer-events-none
        absolute
        inset-0
        z-30
        overflow-hidden
      "
    >
      {/* LEFT SIDE READABILITY GRADIENT */}

      <div
        className="
          absolute
          inset-y-0
          left-0
          w-[58%]
          bg-gradient-to-r
          from-black/70
          via-black/32
          to-transparent
        "
      />

      {/* SUBTLE GLOW */}

      <div
        className="
          absolute
          left-[12%]
          top-1/2
          h-[420px]
          w-[420px]
          -translate-y-1/2
          rounded-full
          bg-cyan-300/[0.035]
          blur-[120px]
        "
      />

      {/* ================================================= */}
      {/* INTRO COPY — LEFT SIDE */}
      {/* ================================================= */}

      <div
        className="
          scene3-intro
          absolute
          left-[7%]
          top-1/2
          z-40
          w-[38%]
          max-w-[600px]
          -translate-y-1/2

          max-md:left-6
          max-md:w-[82%]
        "
      >
        <p
          className="
            scene3-kicker
            text-[10px]
            font-semibold
            uppercase
            tracking-[0.48em]
            text-cyan-100/55
          "
        >
          Understanding you
        </p>

        <h2
          className="
            scene3-title
            mt-6
            text-[clamp(3rem,5.4vw,6.2rem)]
            font-medium
            leading-[0.9]
            tracking-[-0.06em]
            text-white
          "
        >
          Your skills.
          <br />

          <span className="text-white/38">
            Your goals.
          </span>
        </h2>

        <p
          className="
            scene3-description
            mt-7
            max-w-[470px]
            text-[15px]
            font-medium
            leading-7
            text-white/48
          "
        >
          We understand what you already know,
          where you want to go and what is
          missing in between.
        </p>
      </div>

      {/* ================================================= */}
      {/* SECOND MESSAGE — LEFT SIDE */}
      {/* ================================================= */}

      <div
        className="
          scene3-gap
          absolute
          left-[7%]
          top-1/2
          z-50
          w-[42%]
          max-w-[650px]
          -translate-y-1/2
          opacity-0

          max-md:left-6
          max-md:w-[86%]
        "
      >
        <p
          className="
            text-[10px]
            font-semibold
            uppercase
            tracking-[0.48em]
            text-cyan-100/60
          "
        >
          Skill gap identified
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
          Now the path
          <br />

          <span className="text-white/35">
            becomes clear.
          </span>
        </h2>

        <div
          className="
            mt-8
            flex
            items-center
            gap-4
          "
        >
          <div
            className="
              h-px
              w-12
              bg-cyan-100/45
            "
          />

          <span
            className="
              text-sm
              font-semibold
              text-white/70
            "
          >
            Personalized from here.
          </span>
        </div>
      </div>

      {/* PATH ACCENT */}

      <div
        className="
          scene3-path
          absolute
          bottom-[18%]
          left-[7%]
          z-40
          h-px
          w-0
          bg-gradient-to-r
          from-cyan-100/70
          via-cyan-100/35
          to-transparent
          opacity-0
        "
      />
    </div>
  );
}