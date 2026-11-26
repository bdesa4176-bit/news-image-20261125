// Entry program for the news-image-20261125 bounty (Node 22, stdlib only).
// It ships the finished image: entry.png sits beside this file, and the
// program writes those exact bytes to /output/entry.png for the gate
// and the judge. The run is deterministic and needs no network.
// Local check:  mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const bytes = readFileSync(join(here, "entry.png"));
if (bytes.length === 0) throw new Error("entry.png is empty");
const dir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
mkdirSync(dir, { recursive: true });
writeFileSync(join(dir, "entry.png"), bytes);
