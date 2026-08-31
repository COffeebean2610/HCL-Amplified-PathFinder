"use client";

import {
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";

import {
  CINEMATIC_SCENES,
} from "../lib/cinematic-scenes";

import {
  loadFrame,
} from "../lib/frame-cache";

export function useFramePreloader() {
  const [
    initialReady,
    setInitialReady,
  ] = useState(false);

  const [
    loadingProgress,
    setLoadingProgress,
  ] = useState(0);

  const loadedScenesRef =
    useRef(
      new Set<number>()
    );

  const loadingScenesRef =
    useRef(
      new Set<number>()
    );

  const preloadScene =
    useCallback(
      async (
        sceneId: number,
        showProgress = false
      ) => {
        if (
          loadedScenesRef.current.has(
            sceneId
          ) ||
          loadingScenesRef.current.has(
            sceneId
          )
        ) {
          return;
        }

        const scene =
          CINEMATIC_SCENES.find(
            (item) =>
              item.id === sceneId
          );

        if (!scene) return;

        loadingScenesRef.current.add(
          sceneId
        );

        const batchSize = 8;

        for (
          let start = 1;
          start <=
          scene.frameCount;
          start += batchSize
        ) {
          const end =
            Math.min(
              start +
                batchSize -
                1,
              scene.frameCount
            );

          const requests: Promise<HTMLImageElement>[] =
            [];

          for (
            let frame = start;
            frame <= end;
            frame++
          ) {
            requests.push(
              loadFrame(
                scene.folder,
                frame
              )
            );
          }

          await Promise.allSettled(
            requests
          );

          if (showProgress) {
            setLoadingProgress(
              Math.round(
                (end /
                  scene.frameCount) *
                  100
              )
            );
          }

          await new Promise<void>(
            (resolve) => {
              requestAnimationFrame(
                () => resolve()
              );
            }
          );
        }

        loadedScenesRef.current.add(
          sceneId
        );

        loadingScenesRef.current.delete(
          sceneId
        );
      },
      []
    );

  useEffect(() => {
    let cancelled = false;

    const start =
      async () => {
        /*
         * Initial experience:
         * load Scene 1 first.
         */
        await preloadScene(
          1,
          true
        );

        if (cancelled) return;

        setLoadingProgress(100);
        setInitialReady(true);

        /*
         * Start Scene 2 quietly.
         */
        window.setTimeout(
          () => {
            if (!cancelled) {
              void preloadScene(
                2
              );
            }
          },
          350
        );
      };

    void start();

    return () => {
      cancelled = true;
    };
  }, [preloadScene]);

  return {
    initialReady,
    loadingProgress,
    preloadScene,
  };
}