export type CinematicScene = {
  id: number;
  key: string;
  folder: string;
  frameCount: number;

  /*
   * Global scroll range
   * used by the cinematic system.
   */
  start: number;
  end: number;
};

export const CINEMATIC_SCENES: CinematicScene[] =
  [
    {
      id: 1,
      key: "scene-01",
      folder: "scene-01",
      frameCount: 150,

      start: 0,
      end: 0.23,
    },

    {
      id: 2,
      key: "scene-02",
      folder: "scene-02",
      frameCount: 150,

      start: 0.18,
      end: 0.43,
    },

    {
      id: 3,
      key: "scene-03",
      folder: "scene-03",
      frameCount: 150,

      start: 0.38,
      end: 0.63,
    },

    {
      id: 4,
      key: "scene-04",
      folder: "scene-04",
      frameCount: 150,

      start: 0.58,
      end: 0.83,
    },

    {
      id: 5,
      key: "scene-05",
      folder: "scene-05",
      frameCount: 150,

      start: 0.78,
      end: 1,
    },
  ];

export function getSceneById(
  id: number
) {
  return CINEMATIC_SCENES.find(
    (scene) =>
      scene.id === id
  );
}

export function getSceneByKey(
  key: string
) {
  return CINEMATIC_SCENES.find(
    (scene) =>
      scene.key === key
  );
}

export function getSceneLocalProgress(
  scene: CinematicScene,
  globalProgress: number
) {
  if (
    globalProgress <=
    scene.start
  ) {
    return 0;
  }

  if (
    globalProgress >=
    scene.end
  ) {
    return 1;
  }

  return (
    (globalProgress -
      scene.start) /
    (scene.end -
      scene.start)
  );
}