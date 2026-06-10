#!/usr/bin/env python
"""Curated robotics topic taxonomy for the ICRA 2026 topic map.

Each topic is {id, label, group, desc}. `id` is the stable node id used in the
graph and as the LLM's enum value; `label` is the display name; `group` is a
coarse super-category used to colour nodes; `desc` disambiguates the topic for
the tagging model. Seeded from the most frequent IEEE Index Terms in
data/metadata.json plus the workshop themes.
"""

from __future__ import annotations

TOPICS: list[dict] = [
    # --- State estimation & mapping ---
    {"id": "slam", "label": "SLAM", "group": "Estimation & Mapping",
     "desc": "Simultaneous localization and mapping; pose-graph/factor-graph back-ends."},
    {"id": "localization", "label": "Localization", "group": "Estimation & Mapping",
     "desc": "Global/relative localization, place recognition, re-localization, GNSS."},
    {"id": "mapping", "label": "Mapping", "group": "Estimation & Mapping",
     "desc": "Map building/representation: occupancy, semantic, prior/HD maps."},
    {"id": "state_estimation", "label": "State Estimation & Calibration", "group": "Estimation & Mapping",
     "desc": "Filtering, sensor/extrinsic calibration, odometry, pose estimation."},
    {"id": "sensor_fusion", "label": "Sensor Fusion", "group": "Estimation & Mapping",
     "desc": "Multi-sensor fusion (LiDAR, camera, IMU, radar) for perception/estimation."},

    # --- Perception ---
    {"id": "perception", "label": "Visual Perception", "group": "Perception",
     "desc": "Deep learning for visual perception, segmentation, scene understanding."},
    {"id": "object_detection", "label": "Object Detection & Tracking", "group": "Perception",
     "desc": "Object detection, multi-object tracking, recognition."},
    {"id": "reconstruction", "label": "3D Reconstruction & Gaussian Splatting", "group": "Perception",
     "desc": "3D/NeRF/Gaussian-splatting reconstruction, novel-view synthesis, depth."},
    {"id": "tactile", "label": "Tactile Sensing", "group": "Perception",
     "desc": "Tactile/vision-tactile sensing, electronic skin, contact perception."},
    {"id": "radar", "label": "Radar Sensing", "group": "Perception",
     "desc": "Radar-based perception, mapping, tracking in robotics."},
    {"id": "neuromorphic", "label": "Neuromorphic & Event Vision", "group": "Perception",
     "desc": "Event cameras, spiking/neuromorphic perception and computing."},

    # --- Learning ---
    {"id": "rl", "label": "Reinforcement Learning", "group": "Learning",
     "desc": "Reinforcement learning for control, locomotion, manipulation."},
    {"id": "imitation", "label": "Imitation & Learning from Demonstration", "group": "Learning",
     "desc": "Imitation learning, learning from demonstration, behavior cloning, teleop data."},
    {"id": "diffusion_policy", "label": "Diffusion & Generative Policies", "group": "Learning",
     "desc": "Diffusion policies, flow matching, generative models for action."},
    {"id": "vla", "label": "Vision-Language-Action & Foundation Models", "group": "Learning",
     "desc": "VLA models, LLMs/VLMs for robotics, robot foundation models, language-conditioned policies."},
    {"id": "world_models", "label": "World Models & Representation Learning", "group": "Learning",
     "desc": "World models, self-supervised/representation learning, predictive models."},

    # --- Manipulation ---
    {"id": "manipulation", "label": "Manipulation", "group": "Manipulation",
     "desc": "Robotic manipulation, manipulation planning, contact-rich manipulation."},
    {"id": "grasping", "label": "Grasping", "group": "Manipulation",
     "desc": "Grasp planning/detection, perception for grasping."},
    {"id": "dexterous", "label": "Dexterous & Multifingered Hands", "group": "Manipulation",
     "desc": "Dexterous manipulation, multifingered/anthropomorphic hands."},
    {"id": "mobile_manipulation", "label": "Mobile & Bimanual Manipulation", "group": "Manipulation",
     "desc": "Mobile manipulation, whole-body and bimanual manipulation."},

    # --- Locomotion & platforms ---
    {"id": "legged", "label": "Legged Locomotion", "group": "Locomotion & Platforms",
     "desc": "Legged robots, quadruped/biped locomotion and control."},
    {"id": "humanoid", "label": "Humanoids", "group": "Locomotion & Platforms",
     "desc": "Humanoid robots, whole-body humanoid control and loco-manipulation."},
    {"id": "aerial", "label": "Aerial Robots / UAVs", "group": "Locomotion & Platforms",
     "desc": "UAVs, drones, aerial systems perception/control, aerial manipulation."},
    {"id": "marine", "label": "Marine & Underwater", "group": "Locomotion & Platforms",
     "desc": "Underwater/marine robots, surface vessels, underwater perception."},
    {"id": "space", "label": "Space & Planetary", "group": "Locomotion & Platforms",
     "desc": "Space robotics, planetary exploration, orbital/lunar robotics."},
    {"id": "soft", "label": "Soft Robotics", "group": "Locomotion & Platforms",
     "desc": "Soft robots, continuum robots, soft materials and actuation."},

    # --- Planning & control ---
    {"id": "motion_planning", "label": "Motion & Path Planning", "group": "Planning & Control",
     "desc": "Motion/path planning, trajectory generation, sampling-based planning."},
    {"id": "control", "label": "Optimization & Optimal Control", "group": "Planning & Control",
     "desc": "Optimal control, MPC, trajectory optimization, optimization for robotics."},
    {"id": "navigation", "label": "Navigation", "group": "Planning & Control",
     "desc": "Autonomous navigation, social/crowd navigation, exploration."},
    {"id": "collision_avoidance", "label": "Collision Avoidance & Safety", "group": "Planning & Control",
     "desc": "Collision avoidance, safe control, control barrier functions, safety guarantees."},
    {"id": "multi_robot", "label": "Multi-Robot & Swarm", "group": "Planning & Control",
     "desc": "Multi-robot systems, swarms, cooperative/connected autonomy."},

    # --- Applications & domains ---
    {"id": "autonomous_driving", "label": "Autonomous Driving", "group": "Applications",
     "desc": "Self-driving vehicles, driving perception/prediction/planning."},
    {"id": "pedestrian", "label": "Human Motion & Pedestrian Prediction", "group": "Applications",
     "desc": "Human/pedestrian motion prediction and trajectory forecasting."},
    {"id": "medical", "label": "Medical & Surgical Robotics", "group": "Applications",
     "desc": "Surgical robots, medical imaging robotics, continuum medical devices."},
    {"id": "hri", "label": "Human-Robot Interaction", "group": "Applications",
     "desc": "Human-robot interaction, social robotics, shared autonomy, assistive."},
    {"id": "teleoperation", "label": "Teleoperation", "group": "Applications",
     "desc": "Teleoperation, telepresence, haptic interfaces."},
    {"id": "wearable", "label": "Wearable & Exoskeletons", "group": "Applications",
     "desc": "Exoskeletons, prosthetics, wearable robots, motion assistance."},
    {"id": "field", "label": "Field & Inspection Robotics", "group": "Applications",
     "desc": "Field robotics, infrastructure/asset inspection, agriculture, environmental, mining."},

    # --- Methods & tooling ---
    {"id": "sim2real", "label": "Sim2Real & Digital Twins", "group": "Methods & Tooling",
     "desc": "Simulation, sim-to-real transfer, digital twins, real2sim."},
    {"id": "synthetic_data", "label": "Synthetic & Generative Data", "group": "Methods & Tooling",
     "desc": "Synthetic data generation, data augmentation, generative scene/asset creation."},
    {"id": "uncertainty", "label": "Uncertainty & Robustness", "group": "Methods & Tooling",
     "desc": "Uncertainty quantification, robustness, open-world reliability, conformal methods."},
    {"id": "benchmarking", "label": "Benchmarks & Datasets", "group": "Methods & Tooling",
     "desc": "Datasets, benchmarks, reproducibility, evaluation."},
    {"id": "hardware", "label": "Mechanism Design & Hardware", "group": "Methods & Tooling",
     "desc": "Mechanism/actuator design, novel hardware, computing hardware/acceleration."},
]

IDS = [t["id"] for t in TOPICS]
GROUPS = sorted({t["group"] for t in TOPICS})


def taxonomy_prompt() -> str:
    """Bulleted taxonomy for the tagging system prompt."""
    return "\n".join(f"- {t['id']}: {t['label']} — {t['desc']}" for t in TOPICS)


if __name__ == "__main__":
    print(f"{len(TOPICS)} topics, {len(GROUPS)} groups")
    print(taxonomy_prompt())
