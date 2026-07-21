---
layout: project
title: FLING
subtitle: Unity 2D Precision Platformer
kicker: GAME DESIGN / LEVEL DESIGN
summary: A 2D platformer built around fishing-rod swings and precise control. I designed the core gameplay and most of the levels, rescued the prototype by redefining its central mechanic, and created a complete difficulty curve from onboarding to advanced challenges.
engine: Unity
role: Game Design / Level Design
team: 4-Person Team
period: 6 Weeks · Scrum
status: Coming Soon to Steam
tags: [2D, Side-Scrolling, Platformer, Celeste-Like]
card_note: Core gameplay · Majority of levels · Difficulty curve
---

## One-Sentence Overview

A 2D platformer built around fishing-rod swings and precise control. I designed the core gameplay and most of the levels, rescued the prototype by redefining its central mechanic, and created a complete difficulty curve from onboarding to advanced challenges.

## Project Tags

:::metrics
- Project Type | 2D / Side-Scrolling / Platformer / Celeste-Like | Unity
- Responsibilities | Game Design / Level Design | Core gameplay and most levels
- Development | 6 Weeks / 4-Person Team | Small-team production
- Method | Scrum Agile Development | Coming soon to Steam
:::

## Project Introduction

*FLING* is a 2D platformer centered on precise control. Players take the role of a fox and use a fishing rod to swing, grab, and reposition themselves while tackling increasingly difficult platforming challenges in a dark, mysterious cave.

:::video platform="YouTube" id="" title="FLING Game Trailer"
:::

## My Work

### 1. Game Design

This project faced trouble from the moment it began.

During our first brainstorming session, we proposed a game in which the player used a fishing rod as a grappling hook for platforming, combat, fishing, and exploration in a Metroidvania-like world. This aligned closely with my philosophy of “extending a complete design from one simple but interesting mechanic.”

After considering the development schedule, however, we decided to focus production on platforming and use a linear level structure similar to *Celeste*.

The basic prototype was established, but early tests showed that pure high-speed grappling platforming was not fun and demanded too much input precision. After testing it, the dean of the school expressed disappointment. The project was close to being cut, and the team was also facing reorganization.

That weekend, I played the 1992 GBA game *Super Mario Land 2* on a retro handheld. In it, Yoshi can throw eggs in any direction on a 2D plane. But how could an old console with only a D-pad and A and B buttons support such a complex action? Its solution was to stop every mechanism and enemy in the level after the throw button was pressed. The player could then use the D-pad to choose a direction slowly, throw the egg, and allow time to begin moving again.

That gave me a solution to our project’s problem. At the beginning of the next week, I proposed a “time stop” mechanic: when the player is airborne and uses the right stick to fire the grappling hook, time stops. The player has enough time to aim precisely, and when the right stick is released, the hook fires and time resumes. A programmer implemented this simple mechanic in only one minute, but the small change completely transformed the game. The excessively high precision requirement disappeared; players gained more room and tolerance to act; and the press-and-release rhythm of firing the hook improved the game’s pacing while adding greater strategic and mechanical depth. It became the project’s core gameplay. (The behavior is similar to Link triggering slow motion while firing a bow in midair in *The Legend of Zelda: Breath of the Wild*.)

### 2. Level Design

The project uses a seamless level structure inspired by *Celeste*. It originally contained 16 level rooms; Levels 4 and 10 were removed from the final version.

I designed most of the levels—Levels 1 through 8, Level 12, and Levels 14 through 16—covering onboarding, growth, and advanced challenges. I focused especially on difficult levels near the end of the game while also managing the overall difficulty curve. During development, multiple rounds of public playtest feedback led me to restructure, remove, and repace levels.

My favorite is Level 16. As the final level, I began with two goals:

1. Include every mechanic in the game.
2. At the end of the hardest challenge—and therefore at the end of the entire game—release all the pressure accumulated throughout the experience.

I accomplished both goals well. For the first, I chained every game mechanic together into a new level and used the game’s “bubble” mechanism in an unconventional way at the end, going beyond the player’s established assumptions to create one final surprise. For the second, I placed a sequence of bubbles at the end of the level so the player could be launched repeatedly back to the surface, creating an exhilarating experience and delivering emotional release.

:::gallery cols=2
![Basic movement and the bubble mechanism](/assets/images/fling-screenshot-1.webp)
![Teaching a mechanic in a low-risk environment](/assets/images/fling-screenshot-2.webp)
![Fishing-rod aiming and movement path](/assets/images/fling-screenshot-3.webp)
![Chained grappling combined with hazardous terrain](/assets/images/fling-screenshot-4.webp)
![Bubble combinations in an advanced challenge](/assets/images/fling-screenshot-5.webp)
![The final stage’s comprehensive challenge](/assets/images/fling-screenshot-6.webp)
:::

## Timeline

| Phase | Date | Goal | Work Completed |
|---|---|---|---|
| POCT |  |  |  |
| POCG |  |  |  |
| Prototype |  |  |  |
| Vertical Slice |  |  |  |
| Alpha |  |  |  |
| Beta |  |  |  |
| Launch |  |  |  |

## Playtesting and Iteration

| Problem | Iteration | Result |
|---|---|---|
| Local spikes in the difficulty curve | Reordered rooms, removed two redundant levels, and added mechanic transitions | Players felt that the overall increase in difficulty was natural, with only the final level remaining especially challenging. |
| High learning cost for new mechanics | Rebuilt the tutorial levels, taught complex mechanics in separate steps, and then recombined them | Players could generally master every core mechanic independently; only a small number needed additional prompts. |
| The ending felt incomplete | Rebuilt the final level to summarize the mechanics and release accumulated tension | The final level became the game’s climax and provided a complete ending experience. |

## Project Summary

### What Went Well

- **Redefined the core gameplay and successfully rescued the prototype.** Reworked the high-execution grappling mechanic into the central idea of “launching yourself,” substantially improving fun and controllability.
- **Completed a full difficulty curve.** Built a progressive learning experience from basic onboarding and mechanic combinations to the final challenge, and continuously improved its pacing through multiple playtests.
- **Created a memorable final level.** The final level integrates every mechanic and uses emotional-release design to give the player a complete and rewarding conclusion.

### Even Better If

- Conduct player testing earlier. More feedback from real players during the prototype phase could have revealed core gameplay problems sooner and reduced the cost of large late-stage revisions.
- Add more transitional levels between mechanics. Some mechanics still have learning gaps; the skill-building process could be divided more finely to make the difficulty curve smoother.
- Continue expanding level variation. More mechanism combinations and situational changes could keep the experience fresh while preserving the same core gameplay.

### What I Learned

- Playtesting matters more than design assumptions. Player feedback reveals real problems more effectively than the designer’s own judgment, and excellent levels emerge through continuous iteration.
- A final level is responsible for more than difficulty. It should summarize the full game’s mechanics, validate the player’s growth, and create emotional closure and release.
- Level design serves the player’s experience. What players truly remember is not an individual mechanism, but the complete experience created by challenge, growth, and emotional change.

### Files and Downloads

:::links
- Game Design Document | /assets/docs/fling/fling_gdd.docx | Design document · DOCX · Approx. 41 MB
- GroundZero FLING ReadMe | /assets/docs/fling/GroundZero_FLING_Readme.docx | Installation and project information · DOCX
- Project Portfolio | /assets/docs/fling/MaZ_TGP1_FLING_Portfolio.docx | Project portfolio · DOCX
:::
