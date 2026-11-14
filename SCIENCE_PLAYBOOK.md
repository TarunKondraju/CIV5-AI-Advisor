# Civ 5 BNW Deity — Fast Science Victory Playbook

Sources: PCJ Law ("10 Tips To Beat Deity", Deity Games 1–3, guide videos) — transcripts in `transcripts/`.
Marbozir BNW Deity Let's Plays are being added in `transcripts/marbozir_bnw/` (section 9 to be filled from them).
Benchmarks are **Quick speed** (multiply by ~1.5 for Standard).

## 0. The two rules that matter most
1. **Empire strength vs. getting there fast enough.** A huge empire that launches late loses to a small one that launches early. Every decision: does this get the spaceship out sooner?
2. **Nobody else is allowed to win first.** Each turn, check rivals for: spaceship parts / Apollo, tourism influence, city-state allies (diplo), capitals taken (domination). Kill threats with diplomacy, spies and votes before they matter.

3. **No wars, ever (player's rule).** Win by science, culture or diplomacy — whichever is closest. Defend only; never take cities. Military exists purely to deter attacks.

### Peaceful backup victories
- **Diplomatic:** the same science/gold economy works. From the Renaissance, spend spare gold on city-state influence (Patronage opener, Consulates in Freedom/Order), keep spies rigging elections, and build the UN (Globalization). Switch to this if an AI is racing you to space or if you have lots of gold per turn.
- **Cultural:** only if the start suits it (lots of wonders, Aesthetics/Exploration, theming bonuses). Needs Hotels/Airports, Great Works and open borders. Pick early (by Renaissance); it doesn't fit a pure science build.
- The advisor picks the fastest one each era based on rival progress and your yields.

## 1. Game setup (recommended for a peaceful science game)
- Civ: **Babylon** (free Great Scientist at Writing, extra GS rate, strong walls), **Korea**, or a generic civ — Persia is fine.
- Map: Continents or Pangaea, **Small**, **Quick speed**, Strategic Balance resources, standard/low sea level.
- Mods: **only Civ5AIBridge**. Disable Community Patch / Vox Populi / EUI-VP — they change the rules these strategies rely on.
- `ENABLE_WONDER_RUSH` at the top of `Civ5AIBridge/StateExporter.lua` instantly finishes your wonders (a cheat). Set to `false` for a fair game.

## 2. Opening (T1–T30)
- **Settle in place** unless 1 tile moves onto a hill / river / luxury / next to a mountain — but keep two 2+ food tiles in range (needed to reach pop 3).
- **Build: Scout → Scout →** then one of:
  - **Shrine** if a good pantheon is still available (faith/culture/food: e.g. God of the Open Sky / Desert Folklore / Fertility Rites / Goddess of Festivals / Monument to the Gods for wonders),
  - else **Monument** (saves up to ~10 turns on finishing Tradition),
  - else **Worker**.
- **Never Granary before the first Settler.**
- Steal a worker from a city-state if one is unguarded (early workers are huge) — *only* if you can tolerate the influence hit; skip it if you want peace.
- **Policies: Tradition** (opener → Legalism/Aristocracy → Oligarchy → Landed Elite/Monarchy → finisher). Liberty only if you plan 5+ settlers before National College.

## 3. Expansion (T20–T60)
- **Build Settlers at pop 3**, production-focus at pop 3 (growing to 4 isn't worth the time).
- Aim **4–5 cities, one per luxury** (4 cities on 3 luxuries is OK). Settle contested spots first.
- Don't settle right next to an AI capital or in land an AI is clearly heading for — that's the #1 cause of Deity war declarations.
- **Food caravan** from capital before NC (Caravan: Animal Husbandry; Cargo Ship: Sailing) — send it from an expand *to* the capital to grow it tall. Second caravan to help a weak expand or win a key city-state quest.

## 4. National College (key benchmark)
- **Libraries everywhere by ~T55–60**, **NC by T67 (Quick) / T100 (Standard)**. Switch from Granary to Library if needed.
- Wonders only if nobody else has the tech yet and they don't delay NC/caravans. "Your build queue is fragile — protect it."
- Good science wonders when uncontested: Great Library (meh), Porcelain Tower, Leaning Tower, Oxford (national), Hubble (2 GS), Great Lighthouse only on water maps. Petra/Hanging Gardens if land suits.

## 5. Mid game (T70–T130 quick)
- **Universities** right after Education (PCJ: T84 capital / ~T90 expands). Work **scientist specialists** in cities big enough — they generate Great Scientists.
- **Rationalism** as soon as Renaissance opens; finisher is important. Before that, spare policies into Patronage opener (city-state friendship) or Tradition remainder.
- Growth targets: **capital 25+, 2–3 core cities 18–20+, others 15+**. Late cities (post-NC/conquered) need help: food/production trade routes + buy key buildings.
- **Public Schools** (Scientific Theory): PCJ benchmark ~T123–128.
- **Save Great Scientists** for late (bulb Plastics/Satellites/end techs) unless you're playing "no saving" style like PCJ Game 3. Plant Academies early only with spare GS before Rationalism.
- **Ideology**: choose what the *majority/strongest* neighbours pick (or Freedom/Order for science). Ideological mismatch is the main late-game "isolated diplomatically" cause and causes unhappiness.

## 6. Late game (T130–launch)
- **Research Labs** (Plastics) — PCJ benchmark ~T150 capital / ~T154 expands. Factories in the 3–4 core cities.
- Tech target order: **Plastics → Satellites (Hubble, Cockpit) → Rocketry (Apollo) → Advanced Ballistics (Boosters) → Nanotechnology (Stasis) → Particle Physics (Engine)** — adjust by turns-to-research shown in the briefing.
- **Apollo Program** in the highest-production city. Then 6 parts: 3 Boosters, Cockpit, Stasis Chamber, Engine. Build in 3–4 core cities in parallel; walk/rail them to the capital.
- **Great Engineers hurry spaceship parts** — save them. Gold buys parts too (save a gold bank for the last 1–2).
- Keep 2–4 modern defensive units (upgrade old ones with gold) — Deity AIs attack when your military looks weak while you build parts.

## 7. Diplomacy rules (avoid wars, avoid isolation)
- Take every **Declaration of Friendship** you're offered with civs that aren't hated by everyone; never denounce unless forced.
- **Trade luxuries/strategics for gold-per-turn** (not lump sums) — funds upgrades/purchases without hurting relations.
- Keep a **credible military score**: the AI attacks the weakest-looking neighbour. Composite Bows/Crossbows early, upgrade later; walls in border cities.
- Don't send missionaries into AI cities, don't settle near them, don't snipe their obvious wonders if they're "Guarded/Deceptive".
- **Spies**: one in your capital (counter-spy) once rivals have Renaissance; others in city-states to rig elections, or in the leading AI's capital to steal tech.
- **World Congress**: vote for science/your interests, against embargoes on you. If an AI nears diplomatic victory, ally its city-states' rivals or buy influence before the UN vote.
- If an AI is attacking: hold on defensible terrain/inside cities, then offer **white peace** every turn (AIs usually accept after ~10 turns). Don't pay tribute; don't take cities you can't support (they hurt happiness and Science time).

## 8. Watch-list each turn (the advisor checks these)
- Any city building "Nothing", idle workers, unused policy/culture or faith.
- Happiness < 0, gold income < 0, growth stalled.
- Foreign military within 5 tiles; who's at war / denounced me / approach Deceptive/Hostile.
- Rival tech count, era, projects (Apollo / parts), tourism `influential_over`, city-state allies.

## 9. Marbozir lessons
_(to be extracted from `transcripts/marbozir_bnw/` once downloads finish)_
