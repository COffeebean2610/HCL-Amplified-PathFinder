"use client";

import {
  useCallback,
  useEffect,
  useRef,
} from "react";

import { Howl } from "howler";

import {
  createSoundEffect,
} from "../lib/audio-engine";

type Effects = {
  typing?: Howl;
  click?: Howl;
  whoosh?: Howl;
  chime?: Howl;
  ignite?: Howl;

  prerequisiteLock?: Howl;
  skillComplete?: Howl;

  progressUpdate?: Howl;
  finalReveal?: Howl;
};

export function useSoundEffects() {
  const effectsRef =
    useRef<Effects>({});

  useEffect(() => {
    effectsRef.current = {
      typing:
        createSoundEffect(
          "/audio/sfx/typing-soft.wav",
          0.22
        ),

      click:
        createSoundEffect(
          "/audio/sfx/ui-click-minimal.wav",
          0.22
        ),

      whoosh:
        createSoundEffect(
          "/audio/sfx/whoosh-airy.wav",
          0.28
        ),

      chime:
        createSoundEffect(
          "/audio/sfx/glass-chime-clarity.wav",
          0.3
        ),

      ignite:
        createSoundEffect(
          "/audio/sfx/path-ignite.wav",
          0.34
        ),

      prerequisiteLock:
        createSoundEffect(
          "/audio/sfx/prerequisite-lock.mp3",
          0.3
        ),

      skillComplete:
        createSoundEffect(
          "/audio/sfx/skill-complete.mp3",
          0.33
        ),

      progressUpdate:
        createSoundEffect(
          "/audio/sfx/progress-update.wav",
          0.3
        ),

      finalReveal:
        createSoundEffect(
          "/audio/sfx/final-reveal.wav",
          0.36
        ),
    };

    return () => {
      Object.values(
        effectsRef.current
      ).forEach(
        (sound) => {
          sound?.unload();
        }
      );

      effectsRef.current = {};
    };
  }, []);

  const playTyping =
    useCallback(() => {
      effectsRef.current
        .typing
        ?.play();
    }, []);

  const playClick =
    useCallback(() => {
      effectsRef.current
        .click
        ?.play();
    }, []);

  const playWhoosh =
    useCallback(() => {
      effectsRef.current
        .whoosh
        ?.play();
    }, []);

  const playChime =
    useCallback(() => {
      effectsRef.current
        .chime
        ?.play();
    }, []);

  const playIgnite =
    useCallback(() => {
      effectsRef.current
        .ignite
        ?.play();
    }, []);

  const playPrerequisiteLock =
    useCallback(() => {
      effectsRef.current
        .prerequisiteLock
        ?.play();
    }, []);

  const playSkillComplete =
    useCallback(() => {
      effectsRef.current
        .skillComplete
        ?.play();
    }, []);

  const playProgressUpdate =
    useCallback(() => {
      effectsRef.current
        .progressUpdate
        ?.play();
    }, []);

  const playFinalReveal =
    useCallback(() => {
      effectsRef.current
        .finalReveal
        ?.play();
    }, []);

  return {
    playTyping,
    playClick,
    playWhoosh,
    playChime,
    playIgnite,

    playPrerequisiteLock,
    playSkillComplete,

    playProgressUpdate,
    playFinalReveal,
  };
}