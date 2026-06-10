#!/usr/bin/env python
"""Robot-platform / embodiment taxonomy for the ICRA 2026 platform map.

Same interface as taxonomy.py (TOPICS, IDS, GROUP_COLORS, GROUPS,
taxonomy_prompt) so the shared pipeline scripts can switch via --kind platforms.

A paper is tagged by the kind of robot / environment the proposed work is
tested or deployed on (e.g. aerial UAV, ground UGV, marine AUV/ROV, humanoid,
manipulator arm). Simulation-only / dataset / theory work with no physical
platform is tagged `sim`.
"""

from __future__ import annotations

TOPICS: list[dict] = [
    # --- Aerial ---
    {"id": "uav", "label": "Aerial / UAV", "group": "Air",
     "desc": "Drones, quadrotors, multirotors, fixed-wing, blimps, flapping-wing, aerial manipulators — flying robots."},

    # --- Ground ---
    {"id": "ugv", "label": "Ground / Wheeled Mobile", "group": "Ground",
     "desc": "Wheeled/tracked mobile robots, UGVs, indoor mobile bases, delivery robots (non-car, non-space)."},
    {"id": "car", "label": "Autonomous Vehicle", "group": "Ground",
     "desc": "Self-driving cars/trucks/buses, on-road autonomous driving platforms."},
    {"id": "legged", "label": "Legged (Quadruped/Hexapod)", "group": "Ground",
     "desc": "Quadruped or multi-legged robots (e.g. ANYmal, Go1, Spot), hexapods — NOT humanoids."},

    # --- Humanoid ---
    {"id": "humanoid", "label": "Humanoid / Biped", "group": "Humanoid",
     "desc": "Humanoid robots, bipeds, whole-body humanoid control and loco-manipulation."},

    # --- Manipulation platforms ---
    {"id": "arm", "label": "Manipulator Arm", "group": "Manipulation",
     "desc": "Fixed-base robotic arm(s), tabletop / dual-arm manipulation setups."},
    {"id": "hand", "label": "Hand / Gripper", "group": "Manipulation",
     "desc": "Dexterous multifingered hands, grippers, end-effectors as the studied platform."},
    {"id": "mobile_manip", "label": "Mobile Manipulator", "group": "Manipulation",
     "desc": "Mobile base + arm platforms (e.g. PR2, TIAGo, mobile manipulators)."},

    # --- Aquatic ---
    {"id": "marine", "label": "Marine / Underwater", "group": "Water",
     "desc": "AUVs, ROVs, USV/surface vessels, underwater or marine robots."},

    # --- Space ---
    {"id": "space", "label": "Space / Planetary", "group": "Space",
     "desc": "Planetary rovers, orbital/free-flying space robots, lunar/Mars systems."},

    # --- Bodies: soft / medical / assistive ---
    {"id": "soft", "label": "Soft / Continuum Robot", "group": "Bio & Assistive",
     "desc": "Soft robots, continuum/inflatable robots, bio-inspired soft bodies."},
    {"id": "medical", "label": "Medical / Surgical Robot", "group": "Bio & Assistive",
     "desc": "Surgical robots, catheters, capsule robots, continuum medical devices, in-body micro-robots."},
    {"id": "wearable", "label": "Wearable / Exoskeleton / Prosthetic", "group": "Bio & Assistive",
     "desc": "Exoskeletons, prosthetics, orthoses, wearable assistive devices on a human body."},

    # --- Other embodiments / scope ---
    {"id": "micro", "label": "Micro / Modular / Unconventional", "group": "Other",
     "desc": "Microrobots, modular/reconfigurable robots, snake/climbing/tensegrity, other unconventional embodiments."},
    {"id": "multi", "label": "Multi-Robot / Swarm", "group": "Other",
     "desc": "Teams/swarms of robots where the multi-robot system itself is the platform (mixed or homogeneous)."},
    {"id": "sim", "label": "Simulation / No Physical Robot", "group": "Non-physical",
     "desc": "Simulation-only studies, datasets, benchmarks, or theory with no physical robot deployment."},
]

IDS = [t["id"] for t in TOPICS]

# Group -> colour (Manim palette), in legend order.
GROUP_COLORS = {
    "Air": "#58C4DD",
    "Ground": "#83C167",
    "Humanoid": "#F0AC5F",
    "Manipulation": "#FC6255",
    "Water": "#5CD0B3",
    "Space": "#CF8DE5",
    "Bio & Assistive": "#E8C547",
    "Other": "#E07A9B",
    "Non-physical": "#8A93A6",
}
GROUPS = list(GROUP_COLORS.keys())


def taxonomy_prompt() -> str:
    return "\n".join(f"- {t['id']}: {t['label']} — {t['desc']}" for t in TOPICS)


if __name__ == "__main__":
    print(f"{len(TOPICS)} platforms, {len(GROUPS)} groups")
    print(taxonomy_prompt())
