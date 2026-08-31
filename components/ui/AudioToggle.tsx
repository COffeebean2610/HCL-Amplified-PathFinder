"use client";

type AudioToggleProps = {
  isMuted: boolean;
  onToggle: () => void;
};

export default function AudioToggle({
  isMuted,
  onToggle,
}: AudioToggleProps) {
  return (
    <button
      type="button"
      onClick={onToggle}
      aria-label={
        isMuted
          ? "Enable sound"
          : "Mute sound"
      }
      className="
        group
        flex
        items-center
        gap-3
        rounded-full
        border
        border-white/10
        bg-black/20
        px-4
        py-2.5
        backdrop-blur-xl
        transition-all
        duration-300

        hover:border-white/20
        hover:bg-white/[0.07]
      "
    >
      <div
        className="
          flex
          h-4
          items-end
          gap-[2px]
        "
      >
        {[0, 1, 2].map(
          (bar) => (
            <span
              key={bar}
              className={`
                block
                w-[2px]
                rounded-full
                bg-white/70
                transition-all
                duration-300
                ${
                  isMuted
                    ? "h-[3px]"
                    : bar === 1
                      ? "h-[11px]"
                      : "h-[7px]"
                }
              `}
            />
          )
        )}
      </div>

      <span
        className="
          text-[9px]
          uppercase
          tracking-[0.26em]
          text-white/45
          transition-colors
          duration-300

          group-hover:text-white/70
        "
      >
        {isMuted
          ? "Sound off"
          : "Sound on"}
      </span>
    </button>
  );
}