"use client";

export default function Scene1Overload() {
  return (
    <div
      className="
        scene-1-copy
        pointer-events-none
        absolute
        inset-0
        z-30
      "
    >
      {/* subtle readability gradient */}
      <div
        className="
          absolute
          inset-y-0
          left-0
          w-[72%]
          bg-gradient-to-r
          from-black/65
          via-black/30
          to-transparent
        "
      />

      {/* subtle glow */}
      <div
        className="
          absolute
          left-[18%]
          top-1/2
          h-[420px]
          w-[420px]
          -translate-y-1/2
          rounded-full
          bg-cyan-300/[0.025]
          blur-[120px]
        "
      />

      {/* main copy */}
      <div
        className="
          absolute
          left-[7%]
          top-1/2
          z-20
          w-[48%]
          max-w-[760px]
          -translate-y-1/2

          max-md:left-6
          max-md:w-[88%]
        "
      >
        <p
          className="
            scene1-kicker
            mb-6
            text-[11px]
            font-semibold
            uppercase
            tracking-[0.46em]
            text-cyan-100/55
          "
        >
          The problem
        </p>

        <h1
          className="
            scene1-title
            text-[clamp(3.4rem,6.5vw,7.4rem)]
            font-medium
            leading-[0.88]
            tracking-[-0.065em]
            text-white
          "
        >
          Too much
          <br />

          <span className="text-white/42">
            to learn.
          </span>
        </h1>

        <p
          className="
            scene1-description
            mt-7
            max-w-[520px]
            text-[15px]
            font-medium
            leading-7
            text-white/52

            md:text-[17px]
          "
        >
          Thousands of courses.
          Hundreds of technologies.
          Endless career paths.
        </p>

        <div
          className="
            scene1-question
            mt-7
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

          <p
            className="
              text-sm
              font-semibold
              tracking-[-0.01em]
              text-white/82
            "
          >
            What should I learn next?
          </p>
        </div>
      </div>
    </div>
  );
}