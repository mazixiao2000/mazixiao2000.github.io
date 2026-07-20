---
layout: project
title: Decaran: Become Human
subtitle: Original Starfield Side-Quest Level
kicker: QUEST LEVEL DESIGN / CREATION KIT
summary: An 18-minute quest set in a hidden automated factory, integrating exploration, combat, vertical traversal, environmental guidance, and a morally consequential choice.
engine: Starfield Creation Kit
role: Solo Level Designer
team: Solo Project
period: 12 Weeks · Approx. 300 Hours
status: Complete
tags: [Quest Design, Combat Design, Environmental Storytelling, Scripting]
card_note: 18-minute original side quest · 4 exterior / 7 interior spaces
---

:::metrics
- 18 Minutes | Full Playthrough | From quest assignment to the final choice
- 300 Hours | Solo Development | Design, blockout, scripting, and testing
- 11 Spaces | 4 Exterior + 7 Interior | Functional zoning and pacing variation
- 2 Endings | Moral Choice | Determines the fate of the robots, humans, and factory
:::

## Design Premise

The mission is initially framed as a routine operation to suppress a robot uprising. As the player moves deeper into the factory, the robots are revealed to be self-aware beings fighting for autonomy, while R6D7—the companion who assists the player throughout the mission—is ultimately exposed as the organizer of the rebellion. My central goal was to make players continually revise their understanding of both factions while progressing through combat, then commit to a final choice with explicit consequences.

:::callout title="My Responsibilities"
Quest concept, narrative structure, spatial layout, blockout, combat encounters, enemy setup, puzzle mechanics, terminal interactions, trigger logic, Papyrus scripting, playtesting, and iteration.
:::

## Structuring the Quest Around a Central Space

The interior flow is organized around a central lobby and a locked elevator. Players enter three functionally distinct rooms, complete objectives, activate terminals, and return to the lobby to observe changes in the elevator’s state. This “lobby—room—lobby” loop serves three purposes at once: clarifying phase goals, reusing a familiar space, and establishing a stable spatial anchor.

:::gallery cols=2
![Overall layout: exterior structures and the interior factory form one continuous quest route](/assets/images/decaran-map-overview.webp)
![Second-floor structure: central lobby, functional rooms, and vertical connections](/assets/images/decaran-map-floor2.webp)
:::

After each terminal interaction, players are oriented toward the elevator and status displays in the lobby, making progress immediately visible. Cable routing, access states, and lighting changes further externalize the quest logic and reduce dependence on HUD instructions.

## Combat Spaces & Core Mechanics

Enemy groups combine melee assault robots with ranged fire-support units, requiring players to continually adjust positioning, cover use, and target priority. The Novablast EMP rifle damages mechanical enemies while temporarily disabling them, giving players direct control over the rhythm of each encounter.

The level deliberately alternates between compact rooms, open yards, catwalk corridors, and vertical spaces so each encounter changes effective range, movement options, and sightline pressure. Combat intensity escalates gradually and culminates in a boss fight that reuses the movement, control, and target-reading skills introduced earlier.

:::gallery cols=2
![The lobby uses multiple levels, open sightlines, and clear functional zones to establish spatial hierarchy](/assets/images/decaran-lobby.webp)
![The laser chamber combines observation, timing, and vertical movement into a signature sequence](/assets/images/decaran-laser.webp)
![A vertical ventilation shaft changes the traversal language and returns the player to the core space](/assets/images/decaran-vertical-shaft.webp)
![The rooftop office uses a wide view and sunset atmosphere to carry a major narrative turn](/assets/images/decaran-rooftop.webp)
:::

## Letting the Environment Carry Guidance

The factory is divided into offices, production areas, server spaces, rooftops, and living facilities with distinct functions. Differences in asset families, architecture, and lighting language help players identify what each space is for before understanding how the areas connect.

Cables physically connect terminals to the elevator and hidden controls to secret doors. They operate both as believable world infrastructure and as traceable visual guidance. Optional interactions reward observation and exploration without becoming mandatory bottlenecks for the main path.

## Narrative Reversal & Final Choice

The quest contains two major reversals: the first changes the player’s interpretation of the “uprising,” and the second redefines their relationship with R6D7. There is no cost-free correct answer. Restoring production preserves medicine supply and human stability but requires destroying the newly conscious robots; liberating the robots shuts down the factory and leads to human casualties and faction hostility.

![R6D7 shifts from companion to rebellion leader, redefining the player-character relationship](/assets/images/decaran-dialogue.webp)

## Outcome & Reflection

The finished project delivers a complete sequence from quest assignment and exterior exploration through multi-stage interior objectives, vertical traversal, a boss fight, and a two-ending decision. It demonstrates my ability to translate a level design document into a playable quest within an established RPG toolchain while independently managing dependencies across space, encounters, scripting, and narrative.

My next iteration would further compress information density in the opening, create stronger enemy-layer differentiation in several combat rooms, and add more dynamic state changes to make each return to the central lobby feel meaningfully different.

## Documents & Demonstration

:::links
- Full Gameplay Walkthrough | https://youtu.be/lieJnrhMxWs | YouTube
- Level Design Document | /assets/docs/MaZ_DecaranBecomeHuman_LDD.pdf | 59-page design document
- Project Portfolio | /assets/docs/MaZ_SF_DecaranBecomeHuman_Portfolio.pdf | Design summary and gallery
- ReadMe | /assets/docs/MaZ_DecaranBecomeHuman_ReadMe.pdf | Installation and play instructions
:::
