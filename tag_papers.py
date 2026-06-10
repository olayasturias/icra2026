import json
import re

# Read taxonomy
with open('data/topics/taxonomy.txt', 'r', encoding='utf-8') as f:
    taxonomy_lines = f.readlines()

# Parse taxonomy
taxonomy_codes = {}
for line in taxonomy_lines:
    if line.strip() and line.startswith('- '):
        match = re.match(r'- (\w+):', line)
        if match:
            code = match.group(1)
            taxonomy_codes[code] = True

print(f"Loaded {len(taxonomy_codes)} topic codes")

# Read batch
with open('data/topics/batches/batch_006.json', 'r', encoding='utf-8') as f:
    papers = json.load(f)

print(f"Loaded {len(papers)} papers")

# Define assignments - mapping paper id to topics and primary
assignments = {
    "pp:2324": {"topics": ["localization", "perception"], "primary": "localization"},
    "pp:2328": {"topics": ["navigation", "diffusion_policy", "sim2real"], "primary": "diffusion_policy"},
    "pp:2329": {"topics": ["motion_planning", "navigation"], "primary": "motion_planning"},
    "pp:2334": {"topics": ["aerial", "manipulation", "rl"], "primary": "aerial"},
    "pp:2338": {"topics": ["rl", "world_models"], "primary": "rl"},
    "pp:2342": {"topics": ["world_models", "manipulation", "perception"], "primary": "world_models"},
    "pp:2344": {"topics": ["navigation", "field"], "primary": "field"},
    "pp:2346": {"topics": ["aerial", "control"], "primary": "aerial"},
    "pp:2347": {"topics": ["motion_planning", "vla"], "primary": "motion_planning"},
    "pp:2348": {"topics": ["vla", "manipulation"], "primary": "vla"},
    "pp:2350": {"topics": ["teleoperation", "medical", "perception"], "primary": "medical"},
    "pp:2352": {"topics": ["medical", "motion_planning"], "primary": "medical"},
    "pp:2354": {"topics": ["tactile", "soft", "perception"], "primary": "tactile"},
    "pp:2357": {"topics": ["marine", "control"], "primary": "marine"},
    "pp:2363": {"topics": ["dexterous", "grasping", "tactile"], "primary": "dexterous"},
    "pp:2371": {"topics": ["marine", "motion_planning"], "primary": "marine"},
    "pp:2375": {"topics": ["vla", "navigation"], "primary": "vla"},
    "pp:2376": {"topics": ["grasping", "tactile", "control"], "primary": "grasping"},
    "pp:2377": {"topics": ["navigation", "vla", "perception"], "primary": "navigation"},
    "pp:2380": {"topics": ["multi_robot", "imitation"], "primary": "multi_robot"},
    "pp:2386": {"topics": ["localization", "perception"], "primary": "localization"},
    "pp:2390": {"topics": ["rl", "control"], "primary": "rl"},
    "pp:2393": {"topics": ["slam", "multi_robot"], "primary": "slam"},
    "pp:2398": {"topics": ["slam", "state_estimation", "sensor_fusion"], "primary": "slam"},
    "pp:2400": {"topics": ["mapping", "sensor_fusion"], "primary": "mapping"},
    "pp:2403": {"topics": ["state_estimation", "sensor_fusion"], "primary": "state_estimation"},
    "pp:2404": {"topics": ["slam", "perception"], "primary": "slam"},
    "pp:2406": {"topics": ["marine", "sensor_fusion", "mapping"], "primary": "marine"},
    "pp:2416": {"topics": ["hri", "perception"], "primary": "hri"},
    "pp:2418": {"topics": ["mobile_manipulation", "diffusion_policy"], "primary": "mobile_manipulation"},
    "pp:2419": {"topics": ["grasping", "manipulation", "perception"], "primary": "grasping"},
    "pp:2421": {"topics": ["wearable", "perception"], "primary": "wearable"},
    "pp:2424": {"topics": ["slam", "sensor_fusion"], "primary": "slam"},
    "pp:2425": {"topics": ["legged", "rl"], "primary": "legged"},
    "pp:2428": {"topics": ["control", "collision_avoidance"], "primary": "control"},
    "pp:2430": {"topics": ["diffusion_policy", "manipulation"], "primary": "manipulation"},
    "pp:2433": {"topics": ["navigation", "perception"], "primary": "navigation"},
    "pp:2436": {"topics": ["imitation", "manipulation", "perception"], "primary": "manipulation"},
    "pp:2439": {"topics": ["control", "manipulation"], "primary": "control"},
    "pp:2441": {"topics": ["multi_robot", "perception"], "primary": "multi_robot"},
    "pp:2442": {"topics": ["imitation", "manipulation"], "primary": "imitation"},
    "pp:2443": {"topics": ["state_estimation", "perception"], "primary": "perception"},
    "pp:2445": {"topics": ["soft", "manipulation", "hardware"], "primary": "soft"},
    "pp:2447": {"topics": ["imitation", "manipulation"], "primary": "manipulation"},
    "pp:2450": {"topics": ["autonomous_driving", "benchmarking"], "primary": "autonomous_driving"},
    "pp:2452": {"topics": ["perception", "reconstruction"], "primary": "perception"},
    "pp:2454": {"topics": ["mobile_manipulation", "imitation"], "primary": "mobile_manipulation"},
    "pp:2457": {"topics": ["manipulation", "control", "field"], "primary": "field"},
    "pp:2462": {"topics": ["navigation", "motion_planning"], "primary": "navigation"},
    "pp:2463": {"topics": ["diffusion_policy", "manipulation"], "primary": "diffusion_policy"},
    "pp:2466": {"topics": ["control", "collision_avoidance"], "primary": "control"},
    "pp:2468": {"topics": ["autonomous_driving", "perception"], "primary": "autonomous_driving"},
    "pp:2470": {"topics": ["imitation", "benchmarking"], "primary": "imitation"},
    "pp:2472": {"topics": ["tactile", "perception"], "primary": "tactile"},
    "pp:2473": {"topics": ["vla", "manipulation", "tactile"], "primary": "vla"},
    "pp:2476": {"topics": ["medical", "control", "soft"], "primary": "medical"},
    "pp:2477": {"topics": ["vla", "navigation"], "primary": "vla"},
    "pp:2478": {"topics": ["hri", "perception", "teleoperation"], "primary": "hri"},
    "pp:2479": {"topics": ["synthetic_data", "perception"], "primary": "synthetic_data"},
    "pp:2480": {"topics": ["multi_robot", "control"], "primary": "multi_robot"},
    "pp:2483": {"topics": ["humanoid", "benchmarking"], "primary": "humanoid"},
    "pp:2484": {"topics": ["manipulation", "vla"], "primary": "manipulation"},
    "pp:2488": {"topics": ["navigation", "imitation"], "primary": "navigation"},
    "pp:2491": {"topics": ["manipulation", "control"], "primary": "manipulation"},
    "pp:2492": {"topics": ["slam", "state_estimation"], "primary": "slam"},
    "pp:2494": {"topics": ["hri", "perception"], "primary": "hri"},
    "pp:2499": {"topics": ["perception", "manipulation"], "primary": "perception"},
    "pp:2507": {"topics": ["hri", "perception"], "primary": "hri"},
    "pp:2508": {"topics": ["space", "motion_planning"], "primary": "space"},
    "pp:2509": {"topics": ["multi_robot", "control"], "primary": "multi_robot"},
    "pp:2510": {"topics": ["marine", "rl"], "primary": "marine"},
    "pp:2518": {"topics": ["marine", "control"], "primary": "marine"},
    "pp:2536": {"topics": ["autonomous_driving", "hri"], "primary": "autonomous_driving"},
    "pp:2538": {"topics": ["imitation", "perception"], "primary": "imitation"},
    "pp:2543": {"topics": ["manipulation", "control"], "primary": "manipulation"},
    "pp:2550": {"topics": ["tactile", "perception"], "primary": "tactile"},
    "pp:2551": {"topics": ["manipulation", "hardware"], "primary": "manipulation"},
    "pp:2553": {"topics": ["navigation", "hri"], "primary": "navigation"},
    "pp:2563": {"topics": ["perception", "sensor_fusion"], "primary": "perception"},
    "pp:2565": {"topics": ["marine", "field"], "primary": "marine"},
    "pp:2567": {"topics": ["field", "vla"], "primary": "field"},
    "pp:2569": {"topics": ["aerial", "hri"], "primary": "aerial"},
    "pp:2573": {"topics": ["diffusion_policy", "imitation"], "primary": "diffusion_policy"},
    "pp:2575": {"topics": ["radar", "localization"], "primary": "localization"},
    "pp:2577": {"topics": ["vla", "manipulation"], "primary": "vla"},
    "pp:2578": {"topics": ["aerial", "grasping", "tactile"], "primary": "aerial"},
    "pp:2580": {"topics": ["control", "navigation", "field"], "primary": "field"},
    "pp:2586": {"topics": ["rl", "imitation"], "primary": "rl"},
    "pp:2590": {"topics": ["reconstruction", "vla"], "primary": "reconstruction"},
    "pp:2591": {"topics": ["navigation", "vla"], "primary": "navigation"},
    "pp:2599": {"topics": ["multi_robot", "navigation"], "primary": "multi_robot"},
    "pp:2603": {"topics": ["object_detection", "benchmarking"], "primary": "object_detection"},
    "pp:2607": {"topics": ["reconstruction", "perception"], "primary": "reconstruction"},
    "pp:2610": {"topics": ["medical", "rl"], "primary": "medical"},
    "pp:2618": {"topics": ["hri", "perception"], "primary": "hri"},
    "pp:2620": {"topics": ["perception", "object_detection"], "primary": "perception"},
    "pp:2623": {"topics": ["medical", "control"], "primary": "medical"},
    "pp:2625": {"topics": ["imitation", "manipulation"], "primary": "imitation"},
    "pp:2634": {"topics": ["vla", "imitation"], "primary": "vla"},
    "pp:2635": {"topics": ["manipulation", "control"], "primary": "manipulation"},
    "pp:2639": {"topics": ["aerial", "state_estimation"], "primary": "aerial"},
    "pp:2646": {"topics": ["benchmarking", "imitation"], "primary": "benchmarking"},
    "pp:2650": {"topics": ["tactile", "benchmarking"], "primary": "benchmarking"},
    "pp:2654": {"topics": ["diffusion_policy", "imitation"], "primary": "diffusion_policy"},
    "pp:2655": {"topics": ["autonomous_driving", "control"], "primary": "autonomous_driving"},
    "pp:2656": {"topics": ["multi_robot", "control"], "primary": "multi_robot"},
    "pp:2657": {"topics": ["manipulation", "perception"], "primary": "manipulation"},
    "pp:2660": {"topics": ["reconstruction", "perception"], "primary": "reconstruction"},
    "pp:2661": {"topics": ["vla", "rl"], "primary": "vla"},
    "pp:2662": {"topics": ["humanoid", "control"], "primary": "humanoid"},
    "pp:2666": {"topics": ["autonomous_driving", "perception"], "primary": "autonomous_driving"},
    "pp:2668": {"topics": ["tactile", "manipulation"], "primary": "tactile"},
    "pp:2678": {"topics": ["radar", "localization"], "primary": "localization"},
    "pp:2686": {"topics": ["imitation", "grasping"], "primary": "imitation"},
    "pp:2687": {"topics": ["motion_planning", "vla"], "primary": "motion_planning"},
    "pp:2688": {"topics": ["marine", "motion_planning"], "primary": "marine"},
    "pp:2695": {"topics": ["teleoperation", "medical", "control"], "primary": "medical"},
    "pp:2696": {"topics": ["multi_robot", "motion_planning"], "primary": "multi_robot"},
    "pp:2701": {"topics": ["perception", "object_detection"], "primary": "perception"},
    "pp:2703": {"topics": ["grasping", "imitation"], "primary": "grasping"},
    "pp:2706": {"topics": ["vla", "rl"], "primary": "vla"},
    "pp:2707": {"topics": ["synthetic_data", "autonomous_driving"], "primary": "synthetic_data"},
    "pp:2708": {"topics": ["soft", "state_estimation"], "primary": "soft"},
    "pp:2716": {"topics": ["slam", "sensor_fusion"], "primary": "slam"},
    "pp:2717": {"topics": ["legged", "field"], "primary": "legged"},
    "pp:2719": {"topics": ["medical", "control"], "primary": "medical"},
    "pp:2720": {"topics": ["hri", "perception"], "primary": "hri"},
    "pp:2726": {"topics": ["benchmarking", "autonomous_driving"], "primary": "benchmarking"},
    "pp:2728": {"topics": ["manipulation", "control"], "primary": "manipulation"},
    "pp:2730": {"topics": ["control", "sim2real"], "primary": "control"},
    "pp:2731": {"topics": ["perception", "benchmarking"], "primary": "perception"},
    "pp:2734": {"topics": ["autonomous_driving", "control"], "primary": "autonomous_driving"},
    "pp:2735": {"topics": ["wearable", "control"], "primary": "wearable"},
    "pp:2736": {"topics": ["control", "state_estimation"], "primary": "control"},
    "pp:2738": {"topics": ["synthetic_data", "vla"], "primary": "synthetic_data"},
    "pp:2739": {"topics": ["slam", "benchmarking"], "primary": "slam"},
    "pp:2742": {"topics": ["slam", "state_estimation"], "primary": "slam"},
    "pp:2743": {"topics": ["slam", "motion_planning"], "primary": "slam"},
    "pp:2748": {"topics": ["marine", "multi_robot", "rl"], "primary": "marine"},
    "pp:2750": {"topics": ["navigation", "localization"], "primary": "navigation"},
    "pp:2751": {"topics": ["marine", "legged", "hardware"], "primary": "legged"},
    "pp:2752": {"topics": ["manipulation", "perception"], "primary": "manipulation"},
    "pp:2756": {"topics": ["aerial", "control"], "primary": "aerial"},
    "pp:2757": {"topics": ["hri", "vla"], "primary": "hri"},
    "pp:2761": {"topics": ["legged", "control"], "primary": "legged"},
    "pp:2766": {"topics": ["teleoperation", "manipulation"], "primary": "teleoperation"},
    "pp:2769": {"topics": ["perception", "state_estimation"], "primary": "perception"},
    "pp:2770": {"topics": ["humanoid", "rl"], "primary": "humanoid"},
    "pp:2771": {"topics": ["tactile", "sim2real"], "primary": "tactile"},
    "pp:2772": {"topics": ["wearable", "state_estimation"], "primary": "wearable"},
    "pp:2774": {"topics": ["perception", "reconstruction"], "primary": "perception"},
    "pp:2776": {"topics": ["imitation", "control"], "primary": "imitation"},
    "pp:2778": {"topics": ["state_estimation", "slam"], "primary": "slam"},
    "pp:2780": {"topics": ["marine", "legged", "hardware"], "primary": "legged"},
    "pp:2781": {"topics": ["vla", "manipulation"], "primary": "vla"},
    "pp:2782": {"topics": ["navigation", "vla"], "primary": "navigation"},
    "pp:2783": {"topics": ["perception", "uncertainty"], "primary": "perception"},
    "pp:2785": {"topics": ["perception", "state_estimation"], "primary": "perception"},
    "pp:2787": {"topics": ["perception", "uncertainty"], "primary": "perception"},
    "pp:2789": {"topics": ["medical", "control", "perception"], "primary": "medical"},
}

# Verify all assignments
print(f"\nVerifying {len(assignments)} paper assignments...")

valid_topics = set(taxonomy_codes.keys())
valid = True
for paper_id, data in assignments.items():
    for topic in data["topics"]:
        if topic not in valid_topics:
            print(f"ERROR: {paper_id} uses invalid topic '{topic}'")
            valid = False
    if data["primary"] not in valid_topics:
        print(f"ERROR: {paper_id} primary '{data['primary']}' not in taxonomy")
        valid = False

if not valid:
    print("FAILED validation")
    exit(1)

# Build output: map each paper id to its assignment
output = {}
for paper_id, data in assignments.items():
    output[paper_id] = {
        "topics": data["topics"],
        "primary": data["primary"]
    }

# Write output
import os
os.makedirs('data/topics/out', exist_ok=True)
with open('data/topics/out/batch_006.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"SUCCESS: Wrote {len(output)} paper assignments to data/topics/out/batch_006.json")
