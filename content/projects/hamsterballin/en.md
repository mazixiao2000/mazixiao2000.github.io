---
layout: project
title: Hamsterballin’
subtitle: UE5 Local Multiplayer Racing Game
kicker: RACING LEVEL DESIGN / CAMERA SYSTEM
summary: Hamsterballin' is a UE5 local multiplayer racing game. On a 42-person team, I was responsible for the final track, the cableway shortcut system, and camera design, using continuous iteration to improve navigation, route choice, and spectacle at racing speed.
engine: Unreal Engine 5
role: Final Track / Cableway System / Camera Design
team: 42-Person Team
period: 12 Weeks · Scrum
status: Coming Soon to Steam
tags: [3D, Local Multiplayer, Racing, Mario Kart-Like]
card_note: Final-track owner · Cableway system and camera design
---

## One-Sentence Overview

*Hamsterballin'* is a UE5 local multiplayer racing game. On a 42-person team, I was responsible for the final track, the cableway shortcut system, and camera design, using continuous iteration to improve navigation, route choice, and spectacle at racing speed.

## Project Tags

:::metrics
- Project Type | 3D / Local Multiplayer / Racing / Mario Kart-Like | Unreal Engine 5
- Responsibilities | Final Track / Cableway System / Camera Design | Level and presentation work
- Development | 12 Weeks / 42-Person Team | Cross-disciplinary collaboration
- Method | Scrum Agile Development | Coming soon to Steam
:::

## Project Introduction

*Hamsterballin’* is a local multiplayer racing game in which players control rolling, bouncing hamster balls and compete across tracks filled with mechanisms, shortcuts, and three-dimensional terrain. The project was developed for SMU Guildhall’s Team Game Project II course by a 42-person team over 12 weeks and is coming soon to Steam.

:::video platform="YouTube" id="HZVYPpXkfO8" title="Hamsterballin’ Official Trailer"
:::

## My Work

### 1. Final Track: Gacha Galaxy

I believe an excellent racing track should be connected by a series of powerful “memory points.” In *Mario Kart*, for example, players may not remember every corner or every detail, but they remember the quicksand vortex on the desert track and the giant eel on the underwater track. When I design a track, I first imagine these memory points, arrange the rhythm of their appearances, and connect these peak experiences naturally with ordinary track segments.

As the primary owner of the final track, I led its thematic concept, track layout, and cross-department collaboration with the programming and art teams, advancing the level from concept through final implementation.

### 1.1 Establishing the Core Level Concept

When the project entered track production, we needed to complete a full track within a short schedule. I quickly established our design goal: a giant central landmark that could serve as both a navigational marker and a memory anchor. I proposed building the track around a giant robot.

However, given the short development schedule and limited art staffing, I discussed the idea with the team leader and quickly revised the concept into a capsule machine. This change preserved the central-landmark design while significantly reducing art production costs. It ultimately produced the overall spatial structure of “circling the capsule machine—crossing through the capsule machine—entering its interior and returning to the start.”

### 1.2 Leading the Core-Area Design

After establishing the overall layout, I designed the track’s starting area, finish area, and the capsule-machine zone at the heart of the level.

To let the track pass through the capsule machine, we wrapped a “Saturn ring” around the spherical upper section, allowing the route to split in two at this location. The level name “Gacha Galaxy” came from this idea.

Because the capsule machine had to support navigation, visual focus, and thematic expression at the same time, I communicated extensively with the art team and continuously adjusted model scale, track connections, and player sightlines so the art served navigation and the racing experience.

### 1.3 Driving Iteration of the Core Gameplay

Across multiple playtests, we found that after entering the capsule machine, players had to pass through three consecutive spiral tubes to return to the upper level. This design had three problems:

- It was repetitive and offered little room for interaction.
- Players easily lost their sense of direction.
- Prolonged rotation caused 3D motion sickness for some players.

The team initially planned only to reduce the route to a single spiral tube. I believed this did not address the root problem, because once players entered the tube, they had almost no decisions or actions to make and simply drove forward.

I therefore proposed replacing the entire section with a cableway system. This solution eliminated the repetitive route and created additional experiential value:

- Fixed cameras strengthened players’ spatial orientation.
- High-speed racing briefly shifted into a more observational rhythm.
- A close view of the giant capsule machine reinforced the level’s central memory point.

The team ultimately adopted and implemented this proposal.

### 1.4 Project Outcome

The track was completed successfully, released with the game, and became the final track of the full experience.

### 2. Cableway System and Camera Design

Beginning in the project’s POCT phase, I independently proposed, designed, and implemented the cableway shortcut system. I was responsible for shortcut planning, interaction logic, and player-facing camera presentation. During cableway movement, the camera showcases scenery, previews upcoming routes, and reinforces direction, allowing the system to serve as shortcut, navigation tool, and presentation sequence at once.

During POCT, I drew inspiration from games such as *Balance* and *Splatoon* and attempted to build a high-speed cableway system during early gameplay exploration. Because our racing game was based entirely on physics simulation, however, the cableway could not constrain the player reliably, and the idea had to be set aside.

I still did not want to abandon the direction during POCG. Further exploration showed that three or four cables could hold the player’s hamster ball between them, constraining it entirely through physics while creating strong playful and presentation potential. From that point on, the feature became one of the project’s primary mechanics and was intended for use as a track shortcut.

During full production, I naturally continued developing the system in collaboration with the art and programming teams, and I designed every cableway in the final track. The cableway I am most proud of begins near the start of the race as the player approaches the “Saturn ring” above the capsule machine. I extended the cableway far outward, bent it back in the opposite direction to form a graceful arc, let the player move away from the track, and then cut back toward the center at high speed. I pulled the camera far back and used a zoom shot so players could feel the speed while viewing the entire track centered on the capsule machine.

Late in development, I was asked to optimize every cableway camera across every track. Even with limited time—and even though the team told me I could decline if the workload was too heavy—I accepted the task.

The camera system behind the cableways was, frankly, extremely simple. On a cableway, a dedicated camera took control from the third-person camera behind the player and always followed two rules:

1. It always faced the player.
2. Its movement percentage along the camera path always matched the player’s movement percentage along the cableway.

This made camera setup extremely difficult. There was no precise control, so every shot had to be tuned manually through experience.

I quickly embedded myself with the other two level-design groups, communicated their needs, established a working rhythm with them, and ultimately configured and optimized 11 cableway camera sequences across all three tracks.

:::gallery cols=2
![Track One: the cableway entrance creates a clear split from the main route](/assets/images/hamster-cableway-01.webp)
![Track One: continuous camera movement reveals the mechanical space and the upcoming direction](/assets/images/hamster-cableway-02.webp)
![Track Two: an elevated shortcut crosses above the main route to create a positional advantage](/assets/images/hamster-cableway-03.webp)
![Track Two: the composition during transit previews the route’s rejoin point](/assets/images/hamster-cableway-04.webp)
![Track Three: the elevated rail reinforces the major landmark and regional orientation](/assets/images/hamster-cableway-05.webp)
![Track Three: the camera presents the capsule-machine core and establishes the final objective](/assets/images/hamster-cableway-06.webp)
![Track Three: continuous routing preserves visual rhythm and spatial continuity](/assets/images/hamster-cableway-07.webp)
![Cableway exit: view and control return smoothly to the main track](/assets/images/hamster-cableway-08.webp)
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

| Feedback | Analysis | Solution |
|---|---|---|
|  |  |  |
|  |  |  |
|  |  |  |

## Project Summary

### What Went Well

- Completed the design, production, and iteration of the final track, “Gacha Galaxy.”
- Completed all cableway camera setups, improving navigation and presentation during high-speed movement.
- Collaborated efficiently with programming, art, and design teams, and the project was successfully released on Steam.

### Even Better If

- The cableway camera system was too limited. I should have followed up more closely with the programming team and made additional requests to improve this important system.
- Some shortcut routes had an imbalanced risk–reward relationship in early versions and required multiple rounds of playtesting.
- At racing speed, some camera transitions interfered with the player’s view of the route ahead, requiring continuous adjustment to camera angles and timing.
- Because multiplayer racing depends heavily on player behavior, some design problems could only be discovered through extensive multiplayer testing.
- Begin multiplayer playtesting earlier and validate route design during the greybox phase.
- Add more routes with strategic differences to improve replayability.
- Enrich the final lap with dynamic events and visual feedback to further strengthen the climax.

### What I Learned

- Racing-project flow design experience
- Presentation and camera-sequence experience
- Level-design philosophy
- Playtesting and iteration
- Cross-department production pipelines in a large team

### Files and Downloads

:::links
- Steam Store Page | https://store.steampowered.com/app/4319370/Hamsterballin/ | Official project page
- Cableway System and Camera Demonstration | https://youtu.be/NM2TgDevFbo | Demonstration video
:::
