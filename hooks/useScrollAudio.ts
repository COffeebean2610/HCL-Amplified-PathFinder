"use client";

import {
  useCallback,
  useEffect,
  useRef,
} from "react";

import { Howl } from "howler";

import {
  createAmbientSound,
} from "../lib/audio-engine";

type AmbientSounds = {
  scene1?: Howl;
  scene2?: Howl;
  scene3?: Howl;
  scene4?: Howl;
  scene5?: Howl;
};

export function useScrollAudio(
  isMuted: boolean
) {
  const soundsRef =
    useRef<AmbientSounds>({});

  const isMutedRef =
    useRef(isMuted);

  useEffect(() => {
    isMutedRef.current =
      isMuted;
  }, [isMuted]);

  useEffect(() => {
    const scene1 =
      createAmbientSound(
        "/audio/ambient/scene1-tension-drone.mp3",
        0
      );

    const scene2 =
      createAmbientSound(
        "/audio/ambient/scene2-data-pulse.mp3",
        0
      );

    const scene3 =
      createAmbientSound(
        "/audio/ambient/scene3-resolution-pad.mp3",
        0
      );

    const scene4 =
      createAmbientSound(
        "/audio/ambient/scene4-pathway-rise.mp3",
        0
      );

    const scene5 =
      createAmbientSound(
        "/audio/ambient/scene5-journey-resolve.mp3",
        0
      );

    soundsRef.current = {
      scene1,
      scene2,
      scene3,
      scene4,
      scene5,
    };

    return () => {
      scene1.unload();
      scene2.unload();
      scene3.unload();
      scene4.unload();
      scene5.unload();

      soundsRef.current = {};
    };
  }, []);

  const ensurePlaying =
    useCallback(
      (sound?: Howl) => {
        if (!sound) return;

        if (!sound.playing()) {
          sound.play();
        }
      },
      []
    );

  const setVolume =
    useCallback(
      (
        sound: Howl | undefined,
        volume: number
      ) => {
        if (!sound) return;

        sound.volume(
          Math.max(
            0,
            Math.min(
              1,
              volume
            )
          )
        );
      },
      []
    );

  const setScrollAudioProgress =
    useCallback(
      (progress: number) => {
        const {
          scene1,
          scene2,
          scene3,
          scene4,
          scene5,
        } = soundsRef.current;

        if (
          !scene1 ||
          !scene2 ||
          !scene3 ||
          !scene4 ||
          !scene5
        ) {
          return;
        }

        if (
          isMutedRef.current
        ) {
          setVolume(scene1, 0);
          setVolume(scene2, 0);
          setVolume(scene3, 0);
          setVolume(scene4, 0);
          setVolume(scene5, 0);
          return;
        }

        ensurePlaying(scene1);
        ensurePlaying(scene2);
        ensurePlaying(scene3);
        ensurePlaying(scene4);
        ensurePlaying(scene5);

        const p =
          Math.max(
            0,
            Math.min(
              1,
              progress
            )
          );

        /*
         * Scene 1
         */
        let volume1 = 0;

        if (p < 0.17) {
          volume1 = 0.2;
        } else if (
          p <= 0.23
        ) {
          volume1 =
            0.2 *
            (1 -
              (p - 0.17) /
                0.06);
        }

        /*
         * Scene 2
         */
        let volume2 = 0;

        if (
          p >= 0.17 &&
          p < 0.23
        ) {
          volume2 =
            0.22 *
            ((p - 0.17) /
              0.06);
        } else if (
          p >= 0.23 &&
          p < 0.37
        ) {
          volume2 = 0.22;
        } else if (
          p <= 0.43 &&
          p >= 0.37
        ) {
          volume2 =
            0.22 *
            (1 -
              (p - 0.37) /
                0.06);
        }

        /*
         * Scene 3
         */
        let volume3 = 0;

        if (
          p >= 0.37 &&
          p < 0.43
        ) {
          volume3 =
            0.24 *
            ((p - 0.37) /
              0.06);
        } else if (
          p >= 0.43 &&
          p < 0.57
        ) {
          volume3 = 0.24;
        } else if (
          p >= 0.57 &&
          p <= 0.63
        ) {
          volume3 =
            0.24 *
            (1 -
              (p - 0.57) /
                0.06);
        }

        /*
         * Scene 4
         */
        let volume4 = 0;

        if (
          p >= 0.57 &&
          p < 0.63
        ) {
          volume4 =
            0.26 *
            ((p - 0.57) /
              0.06);
        } else if (
          p >= 0.63 &&
          p < 0.77
        ) {
          volume4 = 0.26;
        } else if (
          p >= 0.77 &&
          p <= 0.83
        ) {
          volume4 =
            0.26 *
            (1 -
              (p - 0.77) /
                0.06);
        }

        /*
         * Scene 5
         */
        let volume5 = 0;

        if (
          p >= 0.77 &&
          p < 0.83
        ) {
          volume5 =
            0.27 *
            ((p - 0.77) /
              0.06);
        } else if (
          p >= 0.83 &&
          p < 0.94
        ) {
          volume5 = 0.27;
        } else if (
          p >= 0.94
        ) {
          const endingFade =
            Math.max(
              0.55,
              1 -
                (p - 0.94) /
                  0.06
            );

          volume5 =
            0.27 *
            endingFade;
        }

        setVolume(
          scene1,
          volume1
        );

        setVolume(
          scene2,
          volume2
        );

        setVolume(
          scene3,
          volume3
        );

        setVolume(
          scene4,
          volume4
        );

        setVolume(
          scene5,
          volume5
        );
      },
      [
        ensurePlaying,
        setVolume,
      ]
    );

  useEffect(() => {
    if (!isMuted) return;

    const {
      scene1,
      scene2,
      scene3,
      scene4,
      scene5,
    } = soundsRef.current;

    scene1?.volume(0);
    scene2?.volume(0);
    scene3?.volume(0);
    scene4?.volume(0);
    scene5?.volume(0);
  }, [isMuted]);

  return {
    setScrollAudioProgress,
  };
}