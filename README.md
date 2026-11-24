[![make.fun bounty](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/aicryptoch/makefun-news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/aicryptoch/makefun-news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124)

Bounty: [https://make.fun/bounty/news-image-20261124](https://make.fun/bounty/news-image-20261124)

# THE COMPASS ROSE — Tuesday 24 November 2026 in one image

One front page that sums up Tuesday 24 November 2026: 41 stories across
7 regions, every one dated that day. Gold, Bitcoin and a $3.8bn GTA VI
launch lead; Nvidia's Jensen Huang returns as CEO (+31%); Ukraine sinks
the Russian corvette Merkury off Benghazi with seven sea drones; COP31
ends with no deal, the first since 2000; and the Democrats take both
chambers 258–173.

## What is in this repository

- `entry.png` — the finished front page, exactly 1024×1024 px.
- `main.py` — the entrypoint (standard library only). It copies
  `entry.png` to the output directory and enforces the gate in code:
  real PNG, exactly 1024×1024, at most 1 MiB. Run it with
  `MAKEFUN_OUTPUT_DIR=out python3 main.py`.
- `compose.py` — the build-time renderer that drew `entry.png`
  (flat layered scenes, a dotted world map from coastline polygons with
  numbered pins, and the full page layout). It needs Pillow locally;
  the graded program does not.
- `fonts/` — Playfair Display (Black / Bold / Italic) and DejaVu Sans
  (regular / bold), used by the renderer.
- `README.md` — this file.

## How the page is built

Masthead in Playfair Black with the date set large underneath; a strip
of the day's numbers (7 sea drones, $3,588 gold, $61,284 Bitcoin,
$3.8bn GTA VI, +31% Nvidia, 258–173 House, COP31 no deal, 15 killed
near Kyiv); a colour-coded region count; three lead stories; twelve
more cards; a timeline of the hours that made Tuesday with every time
zone labelled; a dotted world map whose pins match the story numbers;
26 more briefs under ALSO ON; a DATE CHECK box naming six stories that
are *not* today's news; and a footer listing the sources and the
certainty legend. Every card carries a REPORTED tag and its source, and
every deck carries at least two facts.

All figures come from the day's wires (Reuters, AP, CNN, Times, WSJ,
Guardian, CoinPaprika, BBC and others) as locked in the NI24 pool.
Nothing is invented: where a figure was reported on Monday evening it
is labelled Monday; Tuesday slots carry their Tuesday time and zone.

## Licence

MIT — see `LICENSE`.
