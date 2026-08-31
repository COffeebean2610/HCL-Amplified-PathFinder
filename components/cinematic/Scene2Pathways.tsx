"use client";

export default function Scene2Pathways() {
  return (
    <div
      className="
        scene-2-copy
        pointer-events-none
        absolute inset-0 z-30
        flex items-center justify-center
        overflow-hidden
        px-6
        opacity-0
      "
    >
      {/* Very subtle central glow */}
      <div
        className="
          scene2-glow
          absolute left-1/2 top-1/2
          h-[520px] w-[520px]
          -translate-x-1/2 -translate-y-1/2
          rounded-full
          bg-cyan-300/[0.035]
          blur-[120px]
        "
      />

      {/* Main composition */}
      <div
        className="
          relative
          flex h-full w-full
          max-w-[1400px]
          items-center justify-center
          [perspective:1400px]
        "
      >
        {/* ================================ */}
        {/* CENTRAL QUESTION */}
        {/* ================================ */}

        <div
          className="
            scene2-question
            absolute z-30
            text-center
            will-change-transform
          "
        >
          <p
            className="
              mb-6
              text-[10px]
              uppercase
              tracking-[0.5em]
              text-white/30
            "
          >
            The uncertainty
          </p>

          <h2
            className="
              text-5xl
              font-medium
              leading-[0.92]
              tracking-[-0.055em]
              md:text-7xl
              lg:text-[6.7rem]
            "
          >
            What should
            <br />

            <span className="text-white/25">
              I learn next?
            </span>
          </h2>
        </div>

        {/* ================================ */}
        {/* CENTRAL ORIGIN */}
        {/* ================================ */}

        <div
          className="
            scene2-origin
            absolute left-1/2 top-1/2
            z-20
            h-3 w-3
            -translate-x-1/2 -translate-y-1/2
            rounded-full
            bg-white/90
            opacity-0
            shadow-[0_0_30px_rgba(255,255,255,0.5)]
          "
        />

        {/* ================================ */}
        {/* PATH LINES */}
        {/* ================================ */}

        <div
          className="
            scene2-line scene2-line-left
            absolute
            left-1/2 top-1/2
            z-10
            h-px w-[30vw]
            max-w-[430px]
            origin-right
            -translate-x-full
            -rotate-[14deg]
            bg-gradient-to-l
            from-white/35
            to-transparent
            opacity-0
          "
        />

        <div
          className="
            scene2-line scene2-line-center
            absolute
            left-1/2 top-1/2
            z-10
            h-px w-[28vw]
            max-w-[400px]
            origin-left
            bg-gradient-to-r
            from-cyan-100/35
            to-transparent
            opacity-0
          "
        />

        <div
          className="
            scene2-line scene2-line-right
            absolute
            left-1/2 top-1/2
            z-10
            h-px w-[30vw]
            max-w-[430px]
            origin-left
            rotate-[14deg]
            bg-gradient-to-r
            from-white/35
            to-transparent
            opacity-0
          "
        />

        {/* ================================ */}
        {/* PATH DESTINATIONS */}
        {/* ================================ */}

        <div
          className="
            scene2-node scene2-node-1
            absolute
            left-[13%] top-[30%]
            opacity-0
          "
        >
          <Node label="Data" />
        </div>

        <div
          className="
            scene2-node scene2-node-2
            absolute
            right-[13%] top-[30%]
            opacity-0
          "
        >
          <Node label="AI" />
        </div>

        <div
          className="
            scene2-node scene2-node-3
            absolute
            left-1/2 bottom-[20%]
            -translate-x-1/2
            opacity-0
          "
        >
          <Node label="Cloud" />
        </div>
      </div>
    </div>
  );
}

function Node({
  label,
}: {
  label: string;
}) {
  return (
    <div className="flex flex-col items-center gap-3">
      <div
        className="
          h-2.5 w-2.5
          rounded-full
          border border-white/35
          bg-white/10
          shadow-[0_0_25px_rgba(255,255,255,0.18)]
        "
      />

      <span
        className="
          text-[9px]
          uppercase
          tracking-[0.38em]
          text-white/35
        "
      >
        {label}
      </span>
    </div>
  );
}