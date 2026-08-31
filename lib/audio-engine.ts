"use client";

import { Howl, Howler } from "howler";

export const createAmbientSound = (
  src: string,
  volume = 0.2
) => {
  return new Howl({
    src: [src],
    loop: true,
    volume,
    preload: true,
    html5: false,
  });
};

export const createSoundEffect = (
  src: string,
  volume = 0.4
) => {
  return new Howl({
    src: [src],
    loop: false,
    volume,
    preload: true,
    html5: false,
  });
};

export const unlockAudio = async () => {
  try {
    if (
      Howler.ctx &&
      Howler.ctx.state === "suspended"
    ) {
      await Howler.ctx.resume();
    }
  } catch (error) {
    console.error(
      "Unable to unlock audio:",
      error
    );
  }
};

export const stopAllAudio = () => {
  Howler.stop();
};