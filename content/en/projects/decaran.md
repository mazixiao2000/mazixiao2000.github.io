---
layout: project
slug: decaran
title: Decaran: Become Human
subtitle: Original Starfield Side-Quest Level
kicker: QUEST LEVEL DESIGN / CREATION KIT
summary: An 18-minute quest set in an automated desert factory, integrating exploration, combat, vertical traversal, environmental guidance, and a morally consequential final choice.
cover: /assets/images/decaran-cover.webp
hero: /assets/images/decaran-overview.webp
engine: Starfield Creation Kit
role: Solo Level Designer
team: Solo Project
period: 12 Weeks · Approx. 300 Hours
status: Complete
featured: true
category: personal
order: 1
tags: [Quest Design, Combat Design, Environmental Storytelling, Scripting]
card_note: 18-minute side quest · 4 exterior spaces / 7 interior spaces
---

:::metrics
- 18 Minutes | Full Playtime | From mission briefing to final decision
- 300 Hours | Solo Development | Design, blockout, scripting, and testing
- 11 Spaces | 4 Exterior + 7 Interior | Functional zoning and pacing variation
- 2 Endings | Moral Choice | Changes the fate of the robots, workers, and factory
:::

## Design Premise

The mission is initially framed as a routine operation to suppress a robot uprising. As the player advances, the robots are revealed to be self-aware beings fighting for autonomy, and R6D7—the companion who has guided the player through the facility—is exposed as the leader of the rebellion. My core goal was to make the player repeatedly revise their understanding of both sides while still moving through an action-driven quest, then make a final choice with visible consequences.

:::callout title="My Responsibilities"
Mission concept, narrative structure, spatial layout, blockout, combat encounters, enemy composition, puzzle mechanics, terminal interactions, trigger logic, Papyrus scripting, playtesting, and iteration.
:::

## Organizing the Mission Around a Central Space

The interior flow is organized around a central lobby and a locked elevator. The player must enter three functionally distinct rooms, complete an objective in each, activate a terminal, and return to the lobby to observe the elevator's changing state. This lobby–room–lobby loop serves three purposes: it clarifies the current phase, reuses a familiar space, and establishes a stable spatial anchor.

:::gallery cols=2
![Overall layout connecting the exterior approach with the factory interior](/assets/images/decaran-map-overview.webp)
![Second-floor organization around the central lobby, functional rooms, and vertical links](/assets/images/decaran-map-floor2.webp)
:::

After each terminal interaction, the player's view is naturally directed toward the lobby elevator and its state indicators. Cables, access states, and lighting changes visualize mission progress and reduce dependence on HUD instructions.

## Combat Spaces & Core Mechanics

Enemy groups combine melee assault robots with ranged units, requiring the player to adjust positioning, cover use, and target priority. The Novablast EMP rifle temporarily incapacitates mechanical enemies while dealing damage, giving the player a tool for controlling combat tempo.

The level intentionally alternates between compact rooms, open yards, elevated catwalks, and vertical spaces so encounters differ in range, movement options, and sightline pressure. Intensity rises over time and culminates in a boss encounter that reuses previously learned movement, control, and target-priority skills.

:::gallery cols=2
![The lobby establishes hierarchy through multiple elevations, open views, and clear functional zoning](/assets/images/decaran-lobby.webp)
![The laser section combines observation, timing, and vertical traversal into a memorable sequence](/assets/images/decaran-laser.webp)
![A vertical shaft changes the player's movement mode before reconnecting to the core space](/assets/images/decaran-vertical-shaft.webp)
![The rooftop office uses an open vista and sunset atmosphere to support a narrative turn](/assets/images/decaran-rooftop.webp)
:::

## Letting the Environment Carry Guidance

Rather than relying only on objective markers, I used cables, light states, door framing, elevated landmarks, and visual contrast to communicate route and function. The player should understand where power is being directed, which rooms remain incomplete, and how the facility is organized by reading the environment.

:::gallery cols=2
![Exterior geometry frames the factory entrance and establishes the final destination early](/assets/images/decaran-exterior.webp)
![Dialogue staging gives the companion a clear position without blocking the player's movement](/assets/images/decaran-dialogue.webp)
:::

## Iteration & Takeaways

Playtests led to revisions in objective timing, enemy density, door logic, environmental guidance, and the transition into the final choice. The project strengthened my ability to connect narrative beats with spatial structure and to implement a complete playable quest independently inside a production-scale editor.
