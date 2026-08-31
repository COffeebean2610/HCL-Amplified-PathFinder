"use client";

import {
  forwardRef,
  ReactNode,
} from "react";

type Props = {
  children: ReactNode;
  className?: string;
};

const CinematicScene =
  forwardRef<HTMLDivElement, Props>(
    (
      {
        children,
        className = "",
      },
      ref
    ) => {
      return (
        <div
          ref={ref}
          className={`
            absolute
            inset-0
            overflow-hidden
            [perspective:1400px]
            ${className}
          `}
        >
          {children}
        </div>
      );
    }
  );

CinematicScene.displayName =
  "CinematicScene";

export default CinematicScene;