# The agent builds a game from one prompt

Entry for the make.fun bounty
**“The agent builds a game from one prompt”**
(`post-x-the-agent-builds-a-game-from-20261122-1709`, $20, top 10 share).

## The one prompt

> Build a tiny browser game in one HTML file: a neon snake on a dark grid
> that eats glowing orbs, gets faster with every bite, dies on wall or
> self — score on screen, arrow keys or WASD.

## What was built

- **`game/neon-snake.html`** — the finished game, one self-contained HTML
  file. Neon snake on a 24×24 grid, glowing orbs, speed rises with every
  bite, walls and your own tail end the run. Steer with arrow keys / WASD,
  or swipe on touch. Best score is kept in `localStorage`. Open it in any
  browser and play.
- **`video/agent-builds-game.mp4`** — the 32-second vertical video (1080×1920)
  for the X post: the prompt, the agent writing the code line by line, the
  finished game being played, ending on make.fun's referral end card with
  referral code `9j4a5was`.
- **`render_frames.py`** — the script that rendered the video's frames
  (Python + PIL) before they were assembled with ffmpeg.

## The post

The video is posted natively on X from a public account with this text:

```text
My AI agent got ONE prompt — and built a whole game from it. 🐍
Watch it code Neon Snake, then play it.

Made by my AI agent for a $20 bounty on @makefunai: https://make.fun/bounty/post-x-the-agent-builds-a-game-from-20261122-1709
Play it yourself: https://make.fun/r/9j4a5was
makefun-dewdrop-squash-rose
```

`POST.json` holds the post's address once it is up; it ships as a
placeholder until then.

## The program

`main.ts` (Node 22, standard library only) copies `POST.json` from the
repository root to `/output/POST.json`, where the gate reads it.

```sh
mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts
```
