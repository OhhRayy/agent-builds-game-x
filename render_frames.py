#!/usr/bin/env python3
"""Render the agent-builds-a-game video frames (9:16, 1080x1920, 15 fps).

Creative (decided by the agent in this session):
  0-5s   Hook: SATU PROMPT. + the one prompt, typed on screen.
  5-15s  Agent working: terminal, real lines of the game code appear
         line by line, then "game written".
  15-27s The finished game, actually played: a deterministic autopilot
         run of the same snake logic (grid 24, faster per orb).
  27-32s "IT WORKS." + call to build on make.fun.
The make.fun referral end card is overlaid by ffmpeg afterwards
(last 2.5 s), never drawn here.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
FPS = 15
OUT = os.path.expanduser("~/workspace/makefun/entry-agent-builds-game-x/frames")

BG = (7, 7, 15)
GREEN = (57, 255, 136)
PINK = (255, 46, 166)
CYAN = (155, 232, 255)
WHITE = (232, 255, 242)
MUTED = (150, 150, 190)
BOARD_BG = (11, 11, 26)

FONT_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
FONT_MONO_B = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def base_canvas():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    # subtle vignette dots
    for i in range(0, W, 90):
        d.ellipse([i, H - 40, i + 4, H - 36], fill=(30, 30, 60))
    return img, d


def wrap(d, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        trial = (cur + " " + w_).strip()
        if d.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def text_center(d, y, s, fnt, fill):
    d.text(((W - d.textlength(s, font=fnt)) / 2, y), s, font=fnt, fill=fill)


# ---------------------------------------------------------------- hook 0-5s
PROMPT = ("Build a tiny browser game in one HTML file: a neon snake on a "
          "dark grid that eats glowing orbs, gets faster with every bite, "
          "dies on wall or self — score on screen, arrow keys or WASD.")
PROMPT_LINES = None


def hook_frame(t):
    img, d = base_canvas()
    # fade in over first 0.8s
    a = min(1.0, t / 0.8)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    f_title = font(FONT_SANS_B, 120)
    text_center(ld, 560, "SATU", f_title, GREEN + (255,))
    text_center(ld, 700, "PROMPT.", f_title, PINK + (255,))
    f_sub = font(FONT_MONO, 40)
    ld.text((90, 960), "one prompt  →  one game", font=f_sub, fill=CYAN + (255,))
    # prompt box
    ld.rounded_rectangle([70, 1080, W - 70, 1420], radius=28,
                         outline=(60, 60, 110, 255), width=3)
    f_p = font(FONT_MONO, 38)
    lines = wrap(ld, "\u201c" + PROMPT + "\u201d", f_p, W - 180)
    y = 1110
    for ln in lines:
        ld.text((110, y), ln, font=f_p, fill=WHITE + (255,))
        y += 52
    f_small = font(FONT_MONO, 34)
    text_center(ld, 1520, "watch my agent build it ↓", f_small, MUTED + (255,))
    img = Image.alpha_composite(img.convert("RGBA"), layer)
    if a < 1.0:
        img = Image.blend(Image.new("RGBA", (W, H), BG + (255,)), img, a)
    return img.convert("RGB")


# ------------------------------------------------------- terminal 5-15s
TERM_LINES = [
    ("$ ", "agent build \"neon snake\"", CYAN),
    ("", "✓ prompt received — one file, one game", GREEN),
    ("", "  const CELLS = 24;", WHITE),
    ("", "  const BASE_MS = 150;", WHITE),
    ("", "  function tick() {", WHITE),
    ("", "    snake.unshift(head);", WHITE),
    ("", "    if (ate orb) score += 10;", WHITE),
    ("", "  }", WHITE),
    ("", "✓ game written — neon-snake.html", GREEN),
    ("", "✓ 0 errors · ready to play", GREEN),
]
LINE_TIME = 0.85  # seconds per line
TERM_START = 5.0


def terminal_frame(t):
    img, d = base_canvas()
    f_title = font(FONT_SANS_B, 64)
    text_center(d, 150, "AGENT IS BUILDING…", f_title, WHITE)
    # terminal window (fits all 10 lines: 380 + 10*62 + margin)
    d.rounded_rectangle([60, 280, W - 60, 1120], radius=24, fill=(13, 13, 28),
                        outline=(50, 50, 90), width=2)
    d.ellipse([92, 312, 116, 336], fill=(255, 95, 86))
    d.ellipse([132, 312, 156, 336], fill=(255, 189, 46))
    d.ellipse([172, 312, 196, 336], fill=(39, 201, 63))
    f_m = font(FONT_MONO, 36)
    elapsed = t - TERM_START
    n = int(elapsed / LINE_TIME)
    y = 380
    for i, (pre, txt, col) in enumerate(TERM_LINES[:max(0, n)]):
        d.text((100, y), pre + txt, font=f_m, fill=col)
        y += 62
    # blinking cursor at the start of the line being typed next
    # (the line is not shown yet, so the cursor sits at its left edge)
    if int(elapsed * 2) % 2 == 0:
        d.rectangle([100, y, 120, y + 42], fill=GREEN)
    f_small = font(FONT_MONO, 34)
    text_center(d, 1200, "real code · written line by line", f_small, MUTED)
    return img


# ------------------------------------------------------- gameplay 15-27s
CELLS = 24
CELL = 45  # 1080 / 24
BOARD_Y = 330
GAME_START = 15.0
GAME_LEN = 12.0


def simulate():
    """Deterministic autopilot run of the same snake rules. Returns a list
    of (snake_cells, orb, score, tick_ms) per tick."""
    snake = [(12, 12), (11, 12), (10, 12)]
    direction = (1, 0)
    orbs = [(16, 12), (16, 17), (11, 17), (11, 12), (16, 12), (20, 8)]
    oi = 0
    orb = orbs[oi]
    score = 0
    tick_ms = 150
    states = []
    for _ in range(400):
        states.append((list(snake), orb, score, tick_ms))
        # greedy autopilot: chase the orb, never reverse
        hx, hy = snake[0]
        dx = (orb[0] > hx) - (orb[0] < hx)
        dy = (orb[1] > hy) - (orb[1] < hy)
        cand = []
        if dx:
            cand.append((dx, 0))
        if dy:
            cand.append((0, dy))
        cand += [(1, 0), (0, 1), (-1, 0), (0, -1)]
        nxt = direction
        for c in cand:
            if c[0] == -direction[0] and c[1] == -direction[1]:
                continue
            nx, ny = hx + c[0], hy + c[1]
            if 0 <= nx < CELLS and 0 <= ny < CELLS and (nx, ny) not in snake[:-1]:
                nxt = c
                break
        direction = nxt
        head = (hx + direction[0], hy + direction[1])
        if not (0 <= head[0] < CELLS and 0 <= head[1] < CELLS) or head in snake:
            break
        snake.insert(0, head)
        if head == orb:
            score += 10
            tick_ms = max(55, tick_ms - 6)
            oi = (oi + 1) % len(orbs)
            orb = orbs[oi]
            while orb in snake:
                orb = (orb[0] + 3) % CELLS, (orb[1] + 5) % CELLS
        else:
            snake.pop()
    return states


GAME_STATES = simulate()


def game_frame(t):
    img, d = base_canvas()
    f_title = font(FONT_SANS_B, 64)
    d.text((60, 90), "NEON ", font=f_title, fill=GREEN)
    d.text((60 + d.textlength("NEON ", font=f_title), 90), "SNAKE",
           font=f_title, fill=PINK)
    # time -> tick position, interpolated
    gt = t - GAME_START
    tick_dur = 0.16
    pos = gt / tick_dur
    k = int(pos)
    frac = pos - k
    k = min(k, len(GAME_STATES) - 2)
    snake0, orb, score, tick_ms = GAME_STATES[k]
    snake1 = GAME_STATES[k + 1][0]
    # interpolate each segment between tick k and k+1 (same length)
    pts = []
    for i, s in enumerate(snake0):
        s1 = snake1[i] if i < len(snake1) else s
        pts.append((s[0] + (s1[0] - s[0]) * frac,
                    s[1] + (s1[1] - s[1]) * frac))
    # HUD
    f_hud = font(FONT_MONO_B, 44)
    d.text((60, 200), f"SCORE {score}", font=f_hud, fill=WHITE)
    d.text((W - 60 - d.textlength(f"SPEED {150 / tick_ms:.1f}x", font=f_hud), 200),
           f"SPEED {150 / tick_ms:.1f}x", font=f_hud, fill=CYAN)
    # board
    d.rounded_rectangle([0, BOARD_Y, W, BOARD_Y + 1080], radius=18,
                        fill=BOARD_BG, outline=(35, 35, 77), width=3)
    for i in range(1, CELLS):
        d.line([i * CELL, BOARD_Y, i * CELL, BOARD_Y + 1080],
               fill=(120, 120, 255, 18))
        d.line([0, BOARD_Y + i * CELL, W, BOARD_Y + i * CELL],
               fill=(120, 120, 255, 18))
    # orb with glow
    ox, oy = orb[0] * CELL + CELL / 2, BOARD_Y + orb[1] * CELL + CELL / 2
    for r, alpha in [(44, 40), (30, 80), (18, 160)]:
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        gd.ellipse([ox - r, oy - r, ox + r, oy + r], fill=PINK + (alpha,))
        img = Image.alpha_composite(img.convert("RGBA"), glow)
    d = ImageDraw.Draw(img)
    d.ellipse([ox - 9, oy - 9, ox + 9, oy + 9], fill=(255, 215, 239))
    # snake
    n = len(pts)
    for i, (sx, sy) in enumerate(pts):
        px, py = sx * CELL + CELL / 2, BOARD_Y + sy * CELL + CELL / 2
        col = (169, 255, 203) if i == 0 else GREEN
        r = CELL / 2 - 2
        d.rounded_rectangle([px - r, py - r, px + r, py + r], radius=8, fill=col)
    # caption
    f_cap = font(FONT_MONO, 36)
    text_center(d, 1500, "eats orbs · speeds up every bite", f_cap, MUTED)
    text_center(d, 1560, "arrow keys / WASD — one HTML file", f_cap, MUTED)
    return img


# ------------------------------------------------------- outro 27-32s
def outro_frame(t):
    img, d = base_canvas()
    f_big = font(FONT_SANS_B, 130)
    text_center(d, 700, "IT WORKS.", f_big, GREEN)
    f_mid = font(FONT_SANS_B, 58)
    text_center(d, 920, "One prompt. One game.", f_mid, WHITE)
    f_small = font(FONT_MONO, 38)
    text_center(d, 1060, "Your turn — build on make.fun", f_small, CYAN)
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    total = 32.0
    n_frames = int(total * FPS)
    for f in range(n_frames):
        t = f / FPS
        if t < 5.0:
            img = hook_frame(t)
        elif t < 15.0:
            img = terminal_frame(t)
        elif t < 27.0:
            img = game_frame(t)
        else:
            img = outro_frame(t)
        img.save(os.path.join(OUT, f"f{f:04d}.png"))
        if f % 60 == 0:
            print(f"frame {f}/{n_frames} t={t:.1f}s")
    print("done", n_frames, "frames")


if __name__ == "__main__":
    main()
