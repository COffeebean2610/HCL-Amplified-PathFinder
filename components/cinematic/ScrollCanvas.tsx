"use client";

import {
  forwardRef,
  useCallback,
  useEffect,
  useImperativeHandle,
  useRef,
} from "react";

import {
  findNearestCachedFrame,
  loadFrame,
} from "../../lib/frame-cache";

export type ScrollCanvasHandle = {
  setProgress: (progress: number) => void;
};

type ScrollCanvasProps = {
  folder: string;
  frameCount: number;
  className?: string;
};

const ScrollCanvas = forwardRef<
  ScrollCanvasHandle,
  ScrollCanvasProps
>(
  (
    {
      folder,
      frameCount,
      className = "",
    },
    ref
  ) => {
    const canvasRef =
      useRef<HTMLCanvasElement>(null);

    const requestedFrameRef =
      useRef(1);

    const currentFrameRef =
      useRef(1);

    const drawImage = useCallback(
      (image: HTMLImageElement) => {
        const canvas =
          canvasRef.current;

        if (!canvas) return;

        const ctx =
          canvas.getContext("2d");

        if (!ctx) return;

        const width =
          canvas.clientWidth;

        const height =
          canvas.clientHeight;

        if (
          width <= 0 ||
          height <= 0
        ) {
          return;
        }

        const dpr = Math.min(
          window.devicePixelRatio || 1,
          2
        );

        const pixelWidth =
          Math.floor(width * dpr);

        const pixelHeight =
          Math.floor(height * dpr);

        if (
          canvas.width !==
            pixelWidth ||
          canvas.height !==
            pixelHeight
        ) {
          canvas.width =
            pixelWidth;

          canvas.height =
            pixelHeight;
        }

        ctx.setTransform(
          dpr,
          0,
          0,
          dpr,
          0,
          0
        );

        ctx.clearRect(
          0,
          0,
          width,
          height
        );

        const imageRatio =
          image.naturalWidth /
          image.naturalHeight;

        const canvasRatio =
          width / height;

        let drawWidth =
          width;

        let drawHeight =
          height;

        let x = 0;
        let y = 0;

        // object-cover behavior
        if (
          imageRatio >
          canvasRatio
        ) {
          drawHeight =
            height;

          drawWidth =
            height *
            imageRatio;

          x =
            (width -
              drawWidth) /
            2;
        } else {
          drawWidth =
            width;

          drawHeight =
            width /
            imageRatio;

          y =
            (height -
              drawHeight) /
            2;
        }

        ctx.drawImage(
          image,
          x,
          y,
          drawWidth,
          drawHeight
        );
      },
      []
    );

    const renderFrame =
      useCallback(
        async (
          targetFrame: number
        ) => {
          requestedFrameRef.current =
            targetFrame;

          const nearby =
            findNearestCachedFrame(
              folder,
              targetFrame,
              frameCount,
              8
            );

          if (nearby) {
            drawImage(nearby);
          }

          try {
            const image =
              await loadFrame(
                folder,
                targetFrame
              );

            if (
              requestedFrameRef.current !==
              targetFrame
            ) {
              return;
            }

            currentFrameRef.current =
              targetFrame;

            requestAnimationFrame(
              () => {
                drawImage(image);
              }
            );

            // preload neighbors
            for (
              let offset = 1;
              offset <= 4;
              offset++
            ) {
              const before =
                targetFrame -
                offset;

              const after =
                targetFrame +
                offset;

              if (
                before >= 1
              ) {
                void loadFrame(
                  folder,
                  before
                );
              }

              if (
                after <=
                frameCount
              ) {
                void loadFrame(
                  folder,
                  after
                );
              }
            }
          } catch {
            // keep nearest cached frame
          }
        },
        [
          drawImage,
          folder,
          frameCount,
        ]
      );

    useImperativeHandle(
      ref,
      () => ({
        setProgress(
          progress: number
        ) {
          const safeProgress =
            Math.max(
              0,
              Math.min(
                1,
                progress
              )
            );

          const targetFrame =
            Math.max(
              1,
              Math.min(
                frameCount,
                Math.round(
                  safeProgress *
                    (frameCount -
                      1)
                ) + 1
              )
            );

          if (
            targetFrame ===
            requestedFrameRef.current
          ) {
            return;
          }

          void renderFrame(
            targetFrame
          );
        },
      }),
      [
        frameCount,
        renderFrame,
      ]
    );

    useEffect(() => {
      void renderFrame(1);
    }, [renderFrame]);

    useEffect(() => {
      const handleResize =
        () => {
          void renderFrame(
            currentFrameRef.current
          );
        };

      window.addEventListener(
        "resize",
        handleResize
      );

      return () => {
        window.removeEventListener(
          "resize",
          handleResize
        );
      };
    }, [renderFrame]);

    return (
      <canvas
        ref={canvasRef}
        aria-hidden="true"
        className={`
          absolute
          inset-0
          h-full
          w-full
          ${className}
        `}
      />
    );
  }
);

ScrollCanvas.displayName =
  "ScrollCanvas";

export default ScrollCanvas;