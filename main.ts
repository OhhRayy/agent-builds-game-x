// Entry program for "The agent builds a game from one prompt" (Node 22,
// standard library only). It copies POST.json from the repository root to
// /output/POST.json, where the gate reads it. That is the whole job: the
// entry itself is the X post named in POST.json, and the house reads that
// post's views and interactions from X — nothing this program writes about
// the post is scored.
//
// The POST.json shipped here holds a placeholder address, so the gate
// refuses it as it stands. Replace it with the real post's address
// (https://x.com/<handle>/status/<id>) before submitting.
//
// Local check:
//   mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync, readFileSync } from "node:fs";
import { join } from "node:path";

const BOT_DIR = process.env.MAKEFUN_BOT_DIR ?? "/bot";
const OUTPUT_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";

mkdirSync(OUTPUT_DIR, { recursive: true });

const source = join(BOT_DIR, "POST.json");
const target = join(OUTPUT_DIR, "POST.json");

try {
  copyFileSync(source, target);
} catch (err) {
  console.error(`Could not copy POST.json from ${BOT_DIR}: ${(err as Error).message}`);
  process.exit(1);
}

// Fail loudly if POST.json is not a JSON object with a url string,
// instead of handing the gate a file it cannot read.
const parsed = JSON.parse(readFileSync(target, "utf8")) as unknown;
if (typeof parsed !== "object" || parsed === null || typeof (parsed as { url?: unknown }).url !== "string") {
  console.error("POST.json must be a JSON object with a string \"url\" field.");
  process.exit(1);
}
