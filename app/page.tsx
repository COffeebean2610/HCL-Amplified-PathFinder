"use client";

import {
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";

import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import Lenis from "lenis";

import ScrollCanvas, {
  ScrollCanvasHandle,
} from "../components/cinematic/ScrollCanvas";

import CinematicLoader from "../components/cinematic/CinematicLoader";

import Scene1Overload from "../components/cinematic/Scene1Overload";
import Scene2Pathways from "../components/cinematic/Scene2Pathways";
import Scene3Understanding from "../components/cinematic/Scene3Understanding";
import Scene4PersonalizedPath from "../components/cinematic/Scene4PersonalizedPath";
import Scene5Journey from "../components/cinematic/Scene5Journey";

import AudioToggle from "../components/ui/AudioToggle";

import { useFramePreloader } from "../hooks/useFramePreloader";
import { useScrollAudio } from "../hooks/useScrollAudio";
import { useSoundEffects } from "../hooks/useSoundEffects";

import { unlockAudio } from "../lib/audio-engine";

gsap.registerPlugin(ScrollTrigger);

export default function Home() {
  /*
   * ============================================================
   * MASTER WRAPPER
   * ============================================================
   */

  const wrapperRef = useRef<HTMLElement>(null);

  /*
   * ============================================================
   * CANVAS REFS
   * ============================================================
   */

  const scene1CanvasRef =
    useRef<ScrollCanvasHandle>(null);

  const scene2CanvasRef =
    useRef<ScrollCanvasHandle>(null);

  const scene3CanvasRef =
    useRef<ScrollCanvasHandle>(null);

  const scene4CanvasRef =
    useRef<ScrollCanvasHandle>(null);

  const scene5CanvasRef =
    useRef<ScrollCanvasHandle>(null);

  /*
   * ============================================================
   * BACKGROUND LAYERS
   * ============================================================
   */

  const layer1Ref =
    useRef<HTMLDivElement>(null);

  const layer2Ref =
    useRef<HTMLDivElement>(null);

  const layer3Ref =
    useRef<HTMLDivElement>(null);

  const layer4Ref =
    useRef<HTMLDivElement>(null);

  const layer5Ref =
    useRef<HTMLDivElement>(null);

  /*
   * ============================================================
   * FOREGROUND OVERLAYS
   * ============================================================
   */

  const overlay1Ref =
    useRef<HTMLDivElement>(null);

  const overlay2Ref =
    useRef<HTMLDivElement>(null);

  const overlay3Ref =
    useRef<HTMLDivElement>(null);

  const overlay4Ref =
    useRef<HTMLDivElement>(null);

  const overlay5Ref =
    useRef<HTMLDivElement>(null);

  /*
   * ============================================================
   * ACTIVE SCENE
   * ============================================================
   */

  const [activeScene, setActiveScene] =
    useState(1);

  const activeSceneRef =
    useRef(1);

  /*
   * ============================================================
   * AUDIO STATE
   * ============================================================
   */

  const [isMuted, setIsMuted] =
    useState(true);

  const isMutedRef =
    useRef(true);

  useEffect(() => {
    isMutedRef.current = isMuted;
  }, [isMuted]);

  /*
   * ============================================================
   * FRAME PRELOADING
   * ============================================================
   */

  const {
    initialReady,
    loadingProgress,
    preloadScene,
  } = useFramePreloader();

  /*
   * ============================================================
   * AMBIENT AUDIO
   * ============================================================
   */

  const {
    setScrollAudioProgress,
  } = useScrollAudio(isMuted);

  /*
   * ============================================================
   * SOUND EFFECTS
   * ============================================================
   */

  const {
    playTyping,
    playClick,
    playWhoosh,
    playChime,
    playIgnite,
    playPrerequisiteLock,
    playSkillComplete,
    playProgressUpdate,
    playFinalReveal,
  } = useSoundEffects();

  /*
   * ============================================================
   * SFX GUARDS
   * ============================================================
   */

  const prerequisiteTriggeredRef =
    useRef(false);

  const skillCompleteTriggeredRef =
    useRef(false);

  const progressUpdateTriggeredRef =
    useRef(false);

  const finalRevealTriggeredRef =
    useRef(false);

  /*
   * ============================================================
   * BODY LOCK WHILE FIRST SCENE LOADS
   * ============================================================
   */

  useEffect(() => {
    document.body.style.overflow =
      initialReady ? "" : "hidden";

    return () => {
      document.body.style.overflow = "";
    };
  }, [initialReady]);

  /*
   * ============================================================
   * SOUND TOGGLE
   * ============================================================
   */

  const handleSoundToggle =
    useCallback(async () => {
      await unlockAudio();

      playClick();

      setIsMuted(
        (previous) => !previous
      );
    }, [playClick]);

  /*
   * ============================================================
   * ACTIVE SCENE CHANGE
   * ============================================================
   */

  const updateActiveScene =
    useCallback(
      (nextScene: number) => {
        if (
          activeSceneRef.current === nextScene
        ) {
          return;
        }

        const previousScene =
          activeSceneRef.current;

        activeSceneRef.current =
          nextScene;

        setActiveScene(nextScene);

        if (isMutedRef.current) {
          return;
        }

        playWhoosh();

        if (nextScene === 1) {
          window.setTimeout(() => {
            if (!isMutedRef.current) {
              playTyping();
            }
          }, 140);
        }

        if (
          nextScene === 3 &&
          previousScene === 2
        ) {
          window.setTimeout(() => {
            if (!isMutedRef.current) {
              playChime();
            }
          }, 170);

          window.setTimeout(() => {
            if (!isMutedRef.current) {
              playIgnite();
            }
          }, 520);
        }

        if (
          nextScene === 4 &&
          previousScene === 3
        ) {
          window.setTimeout(() => {
            if (!isMutedRef.current) {
              playIgnite();
            }
          }, 220);
        }

        if (
          nextScene === 5 &&
          previousScene === 4
        ) {
          window.setTimeout(() => {
            if (!isMutedRef.current) {
              playChime();
            }
          }, 180);
        }
      },
      [
        playTyping,
        playWhoosh,
        playChime,
        playIgnite,
      ]
    );

  /*
   * ============================================================
   * MASTER CINEMATIC ENGINE
   * ============================================================
   */

  useEffect(() => {
    if (!initialReady) {
      return;
    }

    const wrapper =
      wrapperRef.current;

    const layer1 =
      layer1Ref.current;

    const layer2 =
      layer2Ref.current;

    const layer3 =
      layer3Ref.current;

    const layer4 =
      layer4Ref.current;

    const layer5 =
      layer5Ref.current;

    const overlay1 =
      overlay1Ref.current;

    const overlay2 =
      overlay2Ref.current;

    const overlay3 =
      overlay3Ref.current;

    const overlay4 =
      overlay4Ref.current;

    const overlay5 =
      overlay5Ref.current;

    if (
      !wrapper ||
      !layer1 ||
      !layer2 ||
      !layer3 ||
      !layer4 ||
      !layer5 ||
      !overlay1 ||
      !overlay2 ||
      !overlay3 ||
      !overlay4 ||
      !overlay5
    ) {
      return;
    }

    /*
     * ==========================================================
     * LENIS
     * ==========================================================
     */

    const lenis = new Lenis({
      duration: 0.92,
      smoothWheel: true,
      wheelMultiplier: 0.9,
      touchMultiplier: 1,
    });

    let rafId = 0;

    const raf = (
      time: number
    ) => {
      lenis.raf(time);

      ScrollTrigger.update();

      rafId =
        requestAnimationFrame(raf);
    };

    rafId =
      requestAnimationFrame(raf);

    /*
     * ==========================================================
     * GSAP CONTEXT
     * ==========================================================
     */

    const context =
      gsap.context(() => {
        /*
         * ======================================================
         * INITIAL BACKGROUND STATES
         * ======================================================
         */

        gsap.set(layer1, {
          opacity: 1,
          scale: 1,
        });

        gsap.set(
          [
            layer2,
            layer3,
            layer4,
            layer5,
          ],
          {
            opacity: 0,
            scale: 1.01,
          }
        );

        /*
         * ======================================================
         * INITIAL OVERLAY STATES
         * ======================================================
         */

        gsap.set(overlay1, {
          opacity: 1,
          visibility: "visible",
        });

        gsap.set(
          [
            overlay2,
            overlay3,
            overlay4,
            overlay5,
          ],
          {
            opacity: 0,
            visibility: "hidden",
          }
        );

        gsap.set(
          [
            ".scene-2-copy",
            ".scene-3-copy",
            ".scene-4-copy",
            ".scene-5-copy",
          ],
          {
            opacity: 1,
          }
        );

        /*
         * ======================================================
         * FINAL CTA INITIAL
         * ======================================================
         */

        gsap.set(
          ".final-cta",
          {
            opacity: 0,
            visibility: "hidden",
            y: 40,
            scale: 0.965,
            filter: "blur(10px)",
          }
        );

        /*
         * ======================================================
         * SCENE 1
         * ======================================================
         */

        const scene1Timeline =
          gsap.timeline({
            paused: true,
          });

        scene1Timeline
          .fromTo(
            ".scene1-kicker",
            {
              opacity: 0,
              y: 14,
            },
            {
              opacity: 1,
              y: 0,
              duration: 0.7,
              ease: "power3.out",
            }
          )

          .fromTo(
            ".scene1-title",
            {
              opacity: 0,
              y: 40,
              scale: 0.97,
              filter: "blur(6px)",
            },
            {
              opacity: 1,
              y: 0,
              scale: 1,
              filter: "blur(0px)",
              duration: 1.05,
              ease: "power4.out",
            },
            "-=0.35"
          )

          .fromTo(
            ".scene1-description",
            {
              opacity: 0,
              y: 18,
            },
            {
              opacity: 1,
              y: 0,
              duration: 0.8,
              ease: "power3.out",
            },
            "-=0.5"
          )

          .fromTo(
            ".scene1-question",
            {
              opacity: 0,
              x: -18,
            },
            {
              opacity: 1,
              x: 0,
              duration: 0.8,
              ease: "power3.out",
            },
            "-=0.45"
          )

          /*
           * short hold
           */

          .to(
            {},
            {
              duration: 0.7,
            }
          )

          /*
           * Scene 1 text disappears
           */

          .to(
            [
              ".scene1-kicker",
              ".scene1-title",
              ".scene1-description",
              ".scene1-question",
            ],
            {
              opacity: 0,
              y: -20,
              filter: "blur(5px)",
              duration: 0.65,
              stagger: 0.035,
              ease: "power2.inOut",
            }
          );

        /*
         * ======================================================
         * SCENE 2
         * ======================================================
         */

        const scene2Timeline =
          gsap.timeline({
            paused: true,
          });

        scene2Timeline
          .fromTo(
            ".scene2-question",
            {
              opacity: 0,
              y: 40,
              scale: 0.97,
              filter: "blur(7px)",
            },
            {
              opacity: 1,
              y: 0,
              scale: 1,
              filter: "blur(0px)",
              duration: 1.05,
              ease: "power4.out",
            }
          )

          .to(
            ".scene2-question",
            {
              y: -8,
              duration: 0.85,
              ease: "sine.inOut",
            }
          )

          .to(
            ".scene2-question",
            {
              opacity: 0,
              y: -28,
              scale: 0.96,
              filter: "blur(6px)",
              duration: 0.65,
              ease: "power2.inOut",
            }
          )

          .fromTo(
            ".scene2-origin",
            {
              opacity: 0,
              scale: 0,
            },
            {
              opacity: 1,
              scale: 1,
              duration: 0.45,
              ease: "power3.out",
            }
          )

          .fromTo(
            ".scene2-line",
            {
              opacity: 0,
              scaleX: 0,
            },
            {
              opacity: 1,
              scaleX: 1,
              duration: 1,
              stagger: 0.07,
              ease: "power3.inOut",
            }
          )

          .fromTo(
            ".scene2-node",
            {
              opacity: 0,
              scale: 0.78,
              y: 12,
              filter: "blur(5px)",
            },
            {
              opacity: 1,
              scale: 1,
              y: 0,
              filter: "blur(0px)",
              duration: 0.72,
              stagger: 0.1,
              ease: "power3.out",
            },
            "-=0.45"
          )

          .to(
            {},
            {
              duration: 0.55,
            }
          )

          .to(
            [
              ".scene2-line",
              ".scene2-node",
              ".scene2-origin",
            ],
            {
              opacity: 0,
              scale: 1.06,
              filter: "blur(6px)",
              duration: 0.72,
              ease: "power2.inOut",
            }
          );

        /*
         * ======================================================
         * SCENE 3
         *
         * ENTER LEFT
         * EXIT LEFT
         * ======================================================
         */

        const scene3Timeline =
          gsap.timeline({
            paused: true,
          });

        scene3Timeline
          .fromTo(
            ".scene3-intro",
            {
              opacity: 0,
              x: -90,
              filter: "blur(8px)",
            },
            {
              opacity: 1,
              x: 0,
              filter: "blur(0px)",
              duration: 1.15,
              ease: "power4.out",
            }
          )

          .fromTo(
            ".scene3-kicker",
            {
              opacity: 0,
              x: -25,
            },
            {
              opacity: 1,
              x: 0,
              duration: 0.7,
              ease: "power3.out",
            },
            "-=0.65"
          )

          .fromTo(
            ".scene3-title",
            {
              opacity: 0,
              x: -40,
            },
            {
              opacity: 1,
              x: 0,
              duration: 0.85,
              ease: "power4.out",
            },
            "-=0.5"
          )

          .fromTo(
            ".scene3-description",
            {
              opacity: 0,
              x: -30,
            },
            {
              opacity: 1,
              x: 0,
              duration: 0.75,
              ease: "power3.out",
            },
            "-=0.45"
          )

          /*
           * hold
           */

          .to(
            {},
            {
              duration: 0.65,
            }
          )

          /*
           * first message exits left
           */

          .to(
            ".scene3-intro",
            {
              opacity: 0,
              x: -80,
              filter: "blur(5px)",
              duration: 0.75,
              ease: "power2.inOut",
            }
          )

          /*
           * second message enters left
           */

          .fromTo(
            ".scene3-gap",
            {
              opacity: 0,
              x: -90,
              filter: "blur(8px)",
            },
            {
              opacity: 1,
              x: 0,
              filter: "blur(0px)",
              duration: 1,
              ease: "power4.out",
            },
            "-=0.15"
          )

          /*
           * accent path
           */

          .fromTo(
            ".scene3-path",
            {
              opacity: 0,
              width: "0%",
            },
            {
              opacity: 1,
              width: "34%",
              duration: 0.9,
              ease: "power3.inOut",
            },
            "-=0.45"
          )

          .to(
            {},
            {
              duration: 0.55,
            }
          )

          /*
           * second message exits left
           */

          .to(
            ".scene3-gap",
            {
              opacity: 0,
              x: -90,
              filter: "blur(6px)",
              duration: 0.72,
              ease: "power2.inOut",
            }
          )

          .to(
            ".scene3-path",
            {
              opacity: 0,
              width: "48%",
              duration: 0.55,
              ease: "power2.inOut",
            },
            "-=0.4"
          );

        /*
         * ======================================================
         * SCENE 4
         *
         * LEFT SIDE STORY
         * ======================================================
         */

        const scene4Timeline =
          gsap.timeline({
            paused: true,
          });

        scene4Timeline
          /*
           * title enters left
           */

          .fromTo(
            ".scene4-title",
            {
              opacity: 0,
              x: -100,
              filter: "blur(8px)",
            },
            {
              opacity: 1,
              x: 0,
              filter: "blur(0px)",
              duration: 1.15,
              ease: "power4.out",
            }
          )

          .to(
            {},
            {
              duration: 0.75,
            }
          )

          /*
           * title exits left
           */

          .to(
            ".scene4-title",
            {
              opacity: 0,
              x: -90,
              filter: "blur(6px)",
              duration: 0.72,
              ease: "power2.inOut",
            }
          )

          /*
           * mastered skill
           */

          .fromTo(
            ".scene4-mastered",
            {
              opacity: 0,
              x: -50,
            },
            {
              opacity: 1,
              x: 0,
              duration: 0.7,
              ease: "power3.out",
            }
          )

          .to(
            {},
            {
              duration: 0.45,
            }
          )

          .to(
            ".scene4-mastered",
            {
              opacity: 0,
              x: -50,
              duration: 0.55,
              ease: "power2.inOut",
            }
          )

          /*
           * prerequisite
           */

          .fromTo(
            ".scene4-prerequisite",
            {
              opacity: 0,
              x: -50,
            },
            {
              opacity: 1,
              x: 0,
              duration: 0.7,
              ease: "power3.out",
            },
            "-=0.1"
          )

          .to(
            {},
            {
              duration: 0.45,
            }
          )

          .to(
            ".scene4-prerequisite",
            {
              opacity: 0,
              x: -50,
              duration: 0.55,
              ease: "power2.inOut",
            }
          )

          /*
           * destination
           */

          .fromTo(
            ".scene4-destination",
            {
              opacity: 0,
              x: 45,
              filter: "blur(5px)",
            },
            {
              opacity: 1,
              x: 0,
              filter: "blur(0px)",
              duration: 0.8,
              ease: "power4.out",
            }
          )

          .to(
            {},
            {
              duration: 0.5,
            }
          )

          .to(
            ".scene4-destination",
            {
              opacity: 0,
              x: 50,
              filter: "blur(5px)",
              duration: 0.65,
              ease: "power2.inOut",
            }
          );

        /*
         * ======================================================
         * SCENE 5
         * ======================================================
         */

        const scene5Timeline =
          gsap.timeline({
            paused: true,
          });

        scene5Timeline
          .fromTo(
            ".scene5-dashboard",
            {
              opacity: 0,
              scale: 0.92,
              z: -160,
              filter: "blur(8px)",
            },
            {
              opacity: 0.58,
              scale: 1,
              z: 0,
              filter: "blur(0px)",
              duration: 1,
              ease: "power4.out",
            }
          )

          .fromTo(
            ".scene5-progress",
            {
              opacity: 0,
              y: 20,
            },
            {
              opacity: 1,
              y: 0,
              duration: 0.72,
              ease: "power3.out",
            },
            "-=0.45"
          )

          .fromTo(
            ".scene5-progress-track",
            {
              opacity: 0,
              scaleX: 0,
            },
            {
              opacity: 1,
              scaleX: 1,
              duration: 0.72,
              ease: "power3.inOut",
            },
            "-=0.35"
          )

          .to(
            ".scene5-progress-fill",
            {
              width: "72%",
              duration: 1,
              ease: "power3.inOut",
            }
          )

          .fromTo(
            [
              ".scene5-current",
              ".scene5-next",
            ],
            {
              opacity: 0,
              y: 15,
            },
            {
              opacity: 1,
              y: 0,
              duration: 0.65,
              stagger: 0.12,
              ease: "power3.out",
            },
            "-=0.45"
          )

          .fromTo(
            ".scene5-update",
            {
              opacity: 0,
              y: 10,
              scale: 0.96,
            },
            {
              opacity: 1,
              y: 0,
              scale: 1,
              duration: 0.58,
              ease: "power3.out",
            }
          )

          .to(
            {},
            {
              duration: 0.4,
            }
          )

          .to(
            ".scene5-update",
            {
              opacity: 0,
              y: -10,
              duration: 0.45,
              ease: "power2.inOut",
            }
          )

          /*
           * dashboard leaves before CTA
           */

          .to(
            [
              ".scene5-dashboard",
              ".scene5-progress",
              ".scene5-progress-track",
              ".scene5-current",
              ".scene5-next",
            ],
            {
              opacity: 0,
              scale: 1.04,
              filter: "blur(6px)",
              duration: 0.82,
              ease: "power2.inOut",
            }
          );

        /*
         * ======================================================
         * MASTER SCROLLTRIGGER
         * ======================================================
         */

        const scrollTrigger =
          ScrollTrigger.create({
            trigger: wrapper,

            start: "top top",

            end: "+=11500",

            pin: true,

            scrub: 0.34,

            anticipatePin: 1,

            invalidateOnRefresh: true,

            onUpdate: (self) => {
              const p =
                self.progress;

              /*
               * ===============================================
               * AUDIO
               * ===============================================
               */

              setScrollAudioProgress(p);

              /*
               * ===============================================
               * PRELOAD
               * ===============================================
               */

              if (p > 0.06) {
                void preloadScene(2);
              }

              if (p > 0.22) {
                void preloadScene(3);
              }

              if (p > 0.42) {
                void preloadScene(4);
              }

              if (p > 0.61) {
                void preloadScene(5);
              }

              /*
               * ===============================================
               * ACTIVE SCENE
               * ===============================================
               */

              if (p < 0.2) {
                updateActiveScene(1);
              } else if (p < 0.4) {
                updateActiveScene(2);
              } else if (p < 0.6) {
                updateActiveScene(3);
              } else if (p < 0.8) {
                updateActiveScene(4);
              } else {
                updateActiveScene(5);
              }

              /*
               * ===============================================
               * HARD OVERLAY GATES
               * ===============================================
               */

              const scene1Visible =
                p < 0.165;

              const scene2Visible =
                p >= 0.17 &&
                p < 0.385;

              const scene3Visible =
                p >= 0.38 &&
                p < 0.585;

              const scene4Visible =
                p >= 0.58 &&
                p < 0.785;

              const scene5Visible =
                p >= 0.78 &&
                p < 0.945;

              gsap.set(
                overlay1,
                {
                  opacity:
                    scene1Visible
                      ? 1
                      : 0,

                  visibility:
                    scene1Visible
                      ? "visible"
                      : "hidden",
                }
              );

              gsap.set(
                overlay2,
                {
                  opacity:
                    scene2Visible
                      ? 1
                      : 0,

                  visibility:
                    scene2Visible
                      ? "visible"
                      : "hidden",
                }
              );

              gsap.set(
                overlay3,
                {
                  opacity:
                    scene3Visible
                      ? 1
                      : 0,

                  visibility:
                    scene3Visible
                      ? "visible"
                      : "hidden",
                }
              );

              gsap.set(
                overlay4,
                {
                  opacity:
                    scene4Visible
                      ? 1
                      : 0,

                  visibility:
                    scene4Visible
                      ? "visible"
                      : "hidden",
                }
              );

              gsap.set(
                overlay5,
                {
                  opacity:
                    scene5Visible
                      ? 1
                      : 0,

                  visibility:
                    scene5Visible
                      ? "visible"
                      : "hidden",
                }
              );

              /*
               * ===============================================
               * LOCAL TIMELINE PROGRESS
               * ===============================================
               */

              const scene1Progress =
                gsap.utils.clamp(
                  0,
                  1,
                  p / 0.16
                );

              const scene2Progress =
                gsap.utils.clamp(
                  0,
                  1,
                  (p - 0.17) /
                    0.215
                );

              const scene3Progress =
                gsap.utils.clamp(
                  0,
                  1,
                  (p - 0.38) /
                    0.205
                );

              const scene4Progress =
                gsap.utils.clamp(
                  0,
                  1,
                  (p - 0.58) /
                    0.205
                );

              const scene5Progress =
                gsap.utils.clamp(
                  0,
                  1,
                  (p - 0.78) /
                    0.165
                );

              scene1Timeline.progress(
                scene1Progress
              );

              scene2Timeline.progress(
                scene2Progress
              );

              scene3Timeline.progress(
                scene3Progress
              );

              scene4Timeline.progress(
                scene4Progress
              );

              scene5Timeline.progress(
                scene5Progress
              );

              /*
               * ===============================================
               * CANVAS PROGRESS
               * ===============================================
               */

              if (p <= 0.23) {
                scene1CanvasRef.current?.setProgress(
                  p / 0.23
                );
              } else {
                scene1CanvasRef.current?.setProgress(
                  1
                );
              }

              if (
                p >= 0.18 &&
                p <= 0.43
              ) {
                scene2CanvasRef.current?.setProgress(
                  (p - 0.18) /
                    0.25
                );
              } else if (
                p > 0.43
              ) {
                scene2CanvasRef.current?.setProgress(
                  1
                );
              } else {
                scene2CanvasRef.current?.setProgress(
                  0
                );
              }

              if (
                p >= 0.38 &&
                p <= 0.63
              ) {
                scene3CanvasRef.current?.setProgress(
                  (p - 0.38) /
                    0.25
                );
              } else if (
                p > 0.63
              ) {
                scene3CanvasRef.current?.setProgress(
                  1
                );
              } else {
                scene3CanvasRef.current?.setProgress(
                  0
                );
              }

              if (
                p >= 0.58 &&
                p <= 0.83
              ) {
                scene4CanvasRef.current?.setProgress(
                  (p - 0.58) /
                    0.25
                );
              } else if (
                p > 0.83
              ) {
                scene4CanvasRef.current?.setProgress(
                  1
                );
              } else {
                scene4CanvasRef.current?.setProgress(
                  0
                );
              }

              if (p >= 0.78) {
                scene5CanvasRef.current?.setProgress(
                  (p - 0.78) /
                    0.22
                );
              } else {
                scene5CanvasRef.current?.setProgress(
                  0
                );
              }

              /*
               * ===============================================
               * BACKGROUND CROSSFADE
               * ===============================================
               */

              const scene1Out =
                gsap.utils.clamp(
                  0,
                  1,
                  1 -
                    (p - 0.17) /
                      0.06
                );

              const scene2In =
                gsap.utils.clamp(
                  0,
                  1,
                  (p - 0.17) /
                    0.06
                );

              const scene2Out =
                gsap.utils.clamp(
                  0,
                  1,
                  1 -
                    (p - 0.37) /
                      0.06
                );

              const scene3In =
                gsap.utils.clamp(
                  0,
                  1,
                  (p - 0.37) /
                    0.06
                );

              const scene3Out =
                gsap.utils.clamp(
                  0,
                  1,
                  1 -
                    (p - 0.57) /
                      0.06
                );

              const scene4In =
                gsap.utils.clamp(
                  0,
                  1,
                  (p - 0.57) /
                    0.06
                );

              const scene4Out =
                gsap.utils.clamp(
                  0,
                  1,
                  1 -
                    (p - 0.77) /
                      0.06
                );

              const scene5In =
                gsap.utils.clamp(
                  0,
                  1,
                  (p - 0.77) /
                    0.06
                );

              gsap.set(layer1, {
                opacity:
                  scene1Out,

                scale:
                  1 +
                  scene1Progress *
                    0.015,
              });

              gsap.set(layer2, {
                opacity:
                  Math.min(
                    scene2In,
                    scene2Out
                  ),

                scale:
                  1.01 -
                  scene2In * 0.01,
              });

              gsap.set(layer3, {
                opacity:
                  Math.min(
                    scene3In,
                    scene3Out
                  ),

                scale:
                  1.01 -
                  scene3In * 0.01,
              });

              gsap.set(layer4, {
                opacity:
                  Math.min(
                    scene4In,
                    scene4Out
                  ),

                scale:
                  1.01 -
                  scene4In * 0.01,
              });

              gsap.set(layer5, {
                opacity:
                  scene5In,

                scale:
                  1.01 -
                  scene5In * 0.01,
              });

              /*
               * ===============================================
               * SCENE 4 SOUND
               * ===============================================
               */

              if (
                p >= 0.69 &&
                !prerequisiteTriggeredRef.current
              ) {
                prerequisiteTriggeredRef.current =
                  true;

                if (
                  !isMutedRef.current
                ) {
                  playPrerequisiteLock();
                }
              }

              if (p < 0.67) {
                prerequisiteTriggeredRef.current =
                  false;
              }

              if (
                p >= 0.75 &&
                !skillCompleteTriggeredRef.current
              ) {
                skillCompleteTriggeredRef.current =
                  true;

                if (
                  !isMutedRef.current
                ) {
                  playSkillComplete();
                }
              }

              if (p < 0.73) {
                skillCompleteTriggeredRef.current =
                  false;
              }

              /*
               * ===============================================
               * SCENE 5 UPDATE SOUND
               * ===============================================
               */

              if (
                p >= 0.86 &&
                !progressUpdateTriggeredRef.current
              ) {
                progressUpdateTriggeredRef.current =
                  true;

                if (
                  !isMutedRef.current
                ) {
                  playProgressUpdate();
                }
              }

              if (p < 0.84) {
                progressUpdateTriggeredRef.current =
                  false;
              }

              /*
               * ===============================================
               * FINAL REVEAL SOUND
               * ===============================================
               */

              if (
                p >= 0.945 &&
                !finalRevealTriggeredRef.current
              ) {
                finalRevealTriggeredRef.current =
                  true;

                if (
                  !isMutedRef.current
                ) {
                  playFinalReveal();
                }
              }

              if (p < 0.925) {
                finalRevealTriggeredRef.current =
                  false;
              }

              /*
               * ===============================================
               * FINAL CTA
               * ===============================================
               */

              const finalCTA =
                p < 0.945
                  ? 0
                  : gsap.utils.clamp(
                      0,
                      1,
                      (p - 0.945) /
                        0.045
                    );

              gsap.set(
                ".final-cta",
                {
                  opacity:
                    finalCTA,

                  visibility:
                    finalCTA > 0
                      ? "visible"
                      : "hidden",

                  y:
                    40 *
                    (1 -
                      finalCTA),

                  scale:
                    0.965 +
                    finalCTA *
                      0.035,

                  filter:
                    `blur(${
                      (1 -
                        finalCTA) *
                      10
                    }px)`,
                }
              );

              /*
               * ===============================================
               * MASTER PROGRESS
               * ===============================================
               */

              gsap.set(
                ".cinematic-progress-fill",
                {
                  scaleX: p,
                }
              );

              /*
               * ===============================================
               * SCROLL HELPER
               * ===============================================
               */

              const helper =
                gsap.utils.clamp(
                  0,
                  1,
                  1 -
                    p / 0.085
                );

              gsap.set(
                ".scroll-helper",
                {
                  opacity:
                    helper,

                  y:
                    8 *
                    (1 -
                      helper),
                }
              );
            },
          });

        ScrollTrigger.refresh();

        return () => {
          scrollTrigger.kill();
        };
      }, wrapper);

    /*
     * ==========================================================
     * CLEANUP
     * ==========================================================
     */

    return () => {
      cancelAnimationFrame(
        rafId
      );

      lenis.destroy();

      context.revert();
    };
  }, [
    initialReady,
    preloadScene,
    updateActiveScene,
    setScrollAudioProgress,
    playPrerequisiteLock,
    playSkillComplete,
    playProgressUpdate,
    playFinalReveal,
  ]);

  /*
   * ============================================================
   * UI
   * ============================================================
   */

  return (
    <main
      className="
        min-h-screen
        bg-black
        text-white
      "
    >
      {/* LOADER */}

      <CinematicLoader
        progress={
          loadingProgress
        }
        visible={
          !initialReady
        }
      />

      {/* ==================================================== */}
      {/* NAVIGATION */}
      {/* ==================================================== */}

      <nav
        className="
          fixed
          inset-x-0
          top-0
          z-[200]
          flex
          items-center
          justify-between
          px-5
          py-5

          md:px-10
          md:py-7
        "
      >
        <div
          className="
            flex
            items-center
            gap-3
          "
        >
          <div
            className="
              flex
              h-7
              w-7
              items-center
              justify-center
              rounded-full
              border
              border-white/15
              bg-black/20
              backdrop-blur-xl
            "
          >
            <div
              className="
                h-1.5
                w-1.5
                rounded-full
                bg-cyan-200
                shadow-[0_0_12px_rgba(165,243,252,0.7)]
              "
            />
          </div>

          <span
            className="
              text-[10px]
              font-semibold
              uppercase
              tracking-[0.32em]
              text-white/90

              md:text-xs
            "
          >
            AI Career PathFinder
          </span>
        </div>

        <AudioToggle
          isMuted={isMuted}
          onToggle={
            handleSoundToggle
          }
        />
      </nav>

      {/* ==================================================== */}
      {/* MASTER CINEMATIC */}
      {/* ==================================================== */}

      <section
        ref={wrapperRef}
        className="
          relative
          h-screen
          w-full
          overflow-hidden
          bg-[#020306]
          [perspective:1400px]
        "
      >
        {/* ================================================= */}
        {/* SCENE 1 BACKGROUND */}
        {/* ================================================= */}

        <div
          ref={layer1Ref}
          className="
            absolute
            inset-0
            will-change-[opacity,transform]
          "
        >
          <ScrollCanvas
            ref={
              scene1CanvasRef
            }
            folder="scene-01"
            frameCount={150}
          />
        </div>

        {/* ================================================= */}
        {/* SCENE 2 BACKGROUND */}
        {/* ================================================= */}

        <div
          ref={layer2Ref}
          className="
            absolute
            inset-0
            opacity-0
            will-change-[opacity,transform]
          "
        >
          <ScrollCanvas
            ref={
              scene2CanvasRef
            }
            folder="scene-02"
            frameCount={150}
          />
        </div>

        {/* ================================================= */}
        {/* SCENE 3 BACKGROUND */}
        {/* ================================================= */}

        <div
          ref={layer3Ref}
          className="
            absolute
            inset-0
            opacity-0
            will-change-[opacity,transform]
          "
        >
          <ScrollCanvas
            ref={
              scene3CanvasRef
            }
            folder="scene-03"
            frameCount={150}
          />
        </div>

        {/* ================================================= */}
        {/* SCENE 4 BACKGROUND */}
        {/* ================================================= */}

        <div
          ref={layer4Ref}
          className="
            absolute
            inset-0
            opacity-0
            will-change-[opacity,transform]
          "
        >
          <ScrollCanvas
            ref={
              scene4CanvasRef
            }
            folder="scene-04"
            frameCount={150}
          />
        </div>

        {/* ================================================= */}
        {/* SCENE 5 BACKGROUND */}
        {/* ================================================= */}

        <div
          ref={layer5Ref}
          className="
            absolute
            inset-0
            opacity-0
            will-change-[opacity,transform]
          "
        >
          <ScrollCanvas
            ref={
              scene5CanvasRef
            }
            folder="scene-05"
            frameCount={150}
          />
        </div>

        {/* ================================================= */}
        {/* CINEMATIC FILM TREATMENT */}
        {/* ================================================= */}

        <div
          className="
            pointer-events-none
            absolute
            inset-0
            z-10
            bg-black/[0.03]
          "
        />

        <div
          className="
            pointer-events-none
            absolute
            inset-0
            z-10
            bg-[radial-gradient(circle_at_center,transparent_42%,rgba(0,0,0,0.72)_128%)]
          "
        />

        <div
          className="
            pointer-events-none
            absolute
            inset-x-0
            top-0
            z-10
            h-44
            bg-gradient-to-b
            from-black/60
            via-black/10
            to-transparent
          "
        />

        <div
          className="
            pointer-events-none
            absolute
            inset-x-0
            bottom-0
            z-10
            h-72
            bg-gradient-to-t
            from-black/78
            via-black/18
            to-transparent
          "
        />

        {/* ================================================= */}
        {/* SCENE 1 OVERLAY */}
        {/* ================================================= */}

        <div
          ref={overlay1Ref}
          className="
            pointer-events-none
            absolute
            inset-0
            z-30
          "
        >
          <Scene1Overload />
        </div>

        {/* ================================================= */}
        {/* SCENE 2 OVERLAY */}
        {/* ================================================= */}

        <div
          ref={overlay2Ref}
          className="
            pointer-events-none
            invisible
            absolute
            inset-0
            z-30
            opacity-0
          "
        >
          <Scene2Pathways />
        </div>

        {/* ================================================= */}
        {/* SCENE 3 OVERLAY */}
        {/* ================================================= */}

        <div
          ref={overlay3Ref}
          className="
            pointer-events-none
            invisible
            absolute
            inset-0
            z-30
            opacity-0
          "
        >
          <Scene3Understanding />
        </div>

        {/* ================================================= */}
        {/* SCENE 4 OVERLAY */}
        {/* ================================================= */}

        <div
          ref={overlay4Ref}
          className="
            pointer-events-none
            invisible
            absolute
            inset-0
            z-30
            opacity-0
          "
        >
          <Scene4PersonalizedPath />
        </div>

        {/* ================================================= */}
        {/* SCENE 5 OVERLAY */}
        {/* ================================================= */}

        <div
          ref={overlay5Ref}
          className="
            pointer-events-none
            invisible
            absolute
            inset-0
            z-40
            opacity-0
          "
        >
          <Scene5Journey />
        </div>

        {/* ================================================= */}
        {/* FINAL CTA */}
        {/* ================================================= */}

        <div
          className="
            final-cta
            pointer-events-none
            invisible
            absolute
            inset-0
            z-[70]
            flex
            items-center
            justify-center
            px-6
            opacity-0
          "
        >
          {/* cinematic focus */}

          <div
            className="
              absolute
              inset-0
              bg-[radial-gradient(circle_at_center,rgba(8,25,38,0.18)_0%,rgba(1,5,9,0.56)_48%,rgba(0,0,0,0.9)_100%)]
            "
          />

          {/* glow */}

          <div
            className="
              absolute
              left-1/2
              top-[46%]
              h-[430px]
              w-[650px]
              -translate-x-1/2
              -translate-y-1/2
              rounded-full
              bg-cyan-200/[0.035]
              blur-[130px]
            "
          />

          <div
            className="
              pointer-events-auto
              relative
              z-10
              w-full
              max-w-4xl
              text-center
            "
          >
            {/* eyebrow */}

            <div
              className="
                mx-auto
                flex
                items-center
                justify-center
                gap-4
              "
            >
              <div
                className="
                  h-px
                  w-8
                  bg-gradient-to-r
                  from-transparent
                  to-cyan-100/45
                "
              />

              <p
                className="
                  text-[10px]
                  font-semibold
                  uppercase
                  tracking-[0.5em]
                  text-cyan-100/60
                "
              >
                Your next move
              </p>

              <div
                className="
                  h-px
                  w-8
                  bg-gradient-to-l
                  from-transparent
                  to-cyan-100/45
                "
              />
            </div>

            {/* final heading */}

            <h2
              className="
                mt-8
                text-[clamp(3.5rem,6.5vw,7rem)]
                font-medium
                leading-[0.9]
                tracking-[-0.065em]
                text-white
              "
            >
              A path built

              <br />

              <span
                className="
                  bg-gradient-to-r
                  from-white/40
                  via-white/65
                  to-cyan-100/45
                  bg-clip-text
                  text-transparent
                "
              >
                around you.
              </span>
            </h2>

            {/* supporting copy */}

            <p
              className="
                mx-auto
                mt-8
                max-w-lg
                text-[15px]
                font-medium
                leading-7
                text-white/50
              "
            >
              Your skills understood.
              Your gaps identified.
              Your next step ready.
            </p>

            {/* CTA */}

            <button
              type="button"
              onClick={() => {
                if (
                  !isMutedRef.current
                ) {
                  playClick();
                }
              }}
              className="
                group
                mt-10
                inline-flex
                items-center
                gap-5
                rounded-full
                border
                border-white/10
                bg-white
                px-8
                py-4
                text-sm
                font-semibold
                text-black
                shadow-[0_20px_70px_rgba(255,255,255,0.1)]
                transition-all
                duration-300

                hover:scale-[1.035]
                hover:shadow-[0_22px_80px_rgba(255,255,255,0.16)]
              "
            >
              Start My Path

              <span
                className="
                  text-lg
                  transition-transform
                  duration-300

                  group-hover:translate-x-1
                "
              >
                →
              </span>
            </button>

            <div
              className="
                mx-auto
                mt-12
                h-px
                w-36
                bg-gradient-to-r
                from-transparent
                via-white/25
                to-transparent
              "
            />
          </div>
        </div>

        {/* ================================================= */}
        {/* SCENE COUNTER */}
        {/* ================================================= */}

        <div
          className="
            pointer-events-none
            absolute
            bottom-6
            left-6
            z-[90]
            hidden
            items-center
            gap-4

            sm:flex
            md:bottom-8
            md:left-8
          "
        >
          

          <div
            className="
              flex
              items-center
              gap-3
            "
          >
            <span
              className="
                text-[9px]
                font-semibold
                tracking-[0.3em]
                text-white/70
              "
            >
              {String(
                activeScene
              ).padStart(2, "0")}
            </span>

            <span
              className="
                text-[9px]
                text-white/25
              "
            >
              /
            </span>

            <span
              className="
                text-[9px]
                tracking-[0.3em]
                text-white/35
              "
            >
              05
            </span>
          </div>
        </div>

        {/* ================================================= */}
        {/* SCROLL TO EXPLORE */}
        {/* ================================================= */}

        <div
          className="
            scroll-helper
            pointer-events-none
            absolute
            bottom-7
            left-1/2
            z-[100]
            -translate-x-1/2

            md:bottom-9
          "
        >
          <div
            className="
              flex
              flex-col
              items-center
              gap-3
            "
          >
            <div
              className="
                h-px
                w-44
                bg-gradient-to-r
                from-transparent
                via-white/45
                to-transparent
              "
            />

            <span
              className="
                whitespace-nowrap
                text-[10px]
                font-bold
                uppercase
                tracking-[0.42em]
                text-white/80

                md:text-[11px]
              "
            >
              Scroll to Explore
            </span>

            <div
              className="
                h-5
                w-px
                bg-gradient-to-b
                from-white/50
                to-transparent
              "
            />
          </div>
        </div>

        {/* ================================================= */}
        {/* MASTER PROGRESS */}
        {/* ================================================= */}

        <div
          className="
            pointer-events-none
            absolute
            bottom-0
            left-0
            z-[150]
            h-px
            w-full
            overflow-hidden
            bg-white/[0.04]
          "
        >
          <div
            className="
              cinematic-progress-fill
              h-full
              w-full
              origin-left
              scale-x-0
              bg-gradient-to-r
              from-cyan-200/20
              via-cyan-100/65
              to-white/80
              will-change-transform
            "
          />
        </div>
      </section>
    </main>
  );
}