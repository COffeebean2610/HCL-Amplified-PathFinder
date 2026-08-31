# AI Career PathFinder — Cinematic Landing Page

A scroll-controlled cinematic landing page for **AI Career PathFinder** built with Next.js, TypeScript, Tailwind CSS, GSAP ScrollTrigger, Lenis, and Howler.js.

## Requirements

- Node.js 20+
- npm
- Git

Check:

```bash
node -v
npm -v
git --version
```

## Install

Clone:

```bash
git clone <YOUR_REPOSITORY_URL>
cd ai-career-pathfinder
```

Install dependencies:

```bash
npm install
```

If needed:

```bash
npm install gsap lenis howler
npm install -D @types/howler
```

Run:

```bash
npm run dev
```

Open `http://localhost:3000`.

Production:

```bash
npm run build
npm start
```

## Expected media files

```text
public/videos/
├── scene-01.mp4
├── scene-02.mp4
├── scene-03.mp4
└── scene-04.mp4

public/audio/ambient/
├── scene1-tension-drone.mp3
├── scene2-data-pulse.mp3
├── scene3-resolution-pad.mp3
└── scene4-pathway-rise.mp3

public/audio/sfx/
├── typing-soft.wav
├── ui-click-minimal.wav
├── whoosh-airy.wav
├── glass-chime-clarity.wav
├── path-ignite.wav
├── prerequisite-lock.mp3
└── skill-complete.mp3
```

## Main structure

```text
app/page.tsx
components/cinematic/
components/ui/AudioToggle.tsx
hooks/useScrollAudio.ts
hooks/useSoundEffects.ts
lib/audio-engine.ts
public/videos/
public/audio/
```

## Notes

Browsers block audible autoplay. Click the sound button once before expecting audio.

If you see `404` for audio/video, check the exact filename and extension.

Do not use duplicate extensions like `scene-01.mp4.mp4`.

## GitHub large files

GitHub rejects individual files larger than 100 MB. If needed:

```bash
git lfs install
git lfs track "*.mp4"
git lfs track "*.mp3"
git lfs track "*.wav"
git add .gitattributes
```
