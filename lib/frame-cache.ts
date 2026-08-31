const imageCache = new Map<
  string,
  HTMLImageElement
>();

const loadingPromises = new Map<
  string,
  Promise<HTMLImageElement>
>();

export function getFrameUrl(
  folder: string,
  frame: number
) {
  const frameNumber =
    String(frame).padStart(
      4,
      "0"
    );

  return `/frames/${folder}/frame-${frameNumber}.webp`;
}

export function getCachedFrame(
  folder: string,
  frame: number
) {
  const url =
    getFrameUrl(
      folder,
      frame
    );

  return imageCache.get(url);
}

export function loadFrame(
  folder: string,
  frame: number
): Promise<HTMLImageElement> {
  const url =
    getFrameUrl(
      folder,
      frame
    );

  const cached =
    imageCache.get(url);

  if (cached) {
    return Promise.resolve(
      cached
    );
  }

  const existingPromise =
    loadingPromises.get(url);

  if (existingPromise) {
    return existingPromise;
  }

  const promise =
    new Promise<HTMLImageElement>(
      (resolve, reject) => {
        const image =
          new Image();

        image.decoding =
          "async";

        image.onload = () => {
          imageCache.set(
            url,
            image
          );

          loadingPromises.delete(
            url
          );

          resolve(image);
        };

        image.onerror = () => {
          loadingPromises.delete(
            url
          );

          reject(
            new Error(
              `Unable to load frame: ${url}`
            )
          );
        };

        image.src = url;
      }
    );

  loadingPromises.set(
    url,
    promise
  );

  return promise;
}

export async function preloadFrames(
  folder: string,
  startFrame: number,
  endFrame: number
) {
  const jobs: Promise<HTMLImageElement>[] =
    [];

  for (
    let frame = startFrame;
    frame <= endFrame;
    frame++
  ) {
    jobs.push(
      loadFrame(
        folder,
        frame
      )
    );
  }

  await Promise.allSettled(
    jobs
  );
}

export function findNearestCachedFrame(
  folder: string,
  targetFrame: number,
  frameCount: number,
  searchRadius = 8
) {
  const exact =
    getCachedFrame(
      folder,
      targetFrame
    );

  if (exact) {
    return exact;
  }

  for (
    let offset = 1;
    offset <= searchRadius;
    offset++
  ) {
    const previous =
      targetFrame -
      offset;

    const next =
      targetFrame +
      offset;

    if (
      previous >= 1
    ) {
      const previousImage =
        getCachedFrame(
          folder,
          previous
        );

      if (
        previousImage
      ) {
        return previousImage;
      }
    }

    if (
      next <= frameCount
    ) {
      const nextImage =
        getCachedFrame(
          folder,
          next
        );

      if (
        nextImage
      ) {
        return nextImage;
      }
    }
  }

  return undefined;
}

export function clearFrameCache() {
  imageCache.clear();
  loadingPromises.clear();
}