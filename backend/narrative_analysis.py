"""
Narrative Structure Analysis Pipeline
=======================================
Extracts scene-level narrative curves (emotion, conflict, event density),
detects peaks, segments into 4-stage structure, and compares across play types.
"""

import json
import os
import glob
import re
import warnings
from collections import Counter, defaultdict
from math import sqrt

import numpy as np
from scipy.signal import find_peaks
from scipy.ndimage import gaussian_filter1d

warnings.filterwarnings("ignore")

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "public", "data")

# ── Keyword Dictionaries ─────────────────────────────────────────────

EMOTION_POSITIVE = {"喜", "欢", "欣", "悦", "乐", "笑", "爱", "敬", "善", "良", "美",
                    "吉", "祥", "福", "瑞", "庆", "贺", "赏", "封", "升", "胜",
                    "团圆", "重逢", "相聚", "大捷", "得胜", "荣升", "封赏"}

EMOTION_NEGATIVE = {"悲", "哀", "怒", "恨", "怨", "哭", "泣", "叹", "愁", "忧", "惧",
                    "怕", "惊", "慌", "惨", "死", "亡", "败", "失", "误", "错",
                    "伤心", "悲痛", "痛哭", "哀伤", "凄惨", "不幸", "大祸", "灾难"}

CONFLICT_WORDS = {"杀", "攻", "斩", "伐", "征", "战", "斗", "打", "冲", "击",
                  "反", "叛", "抗", "拒", "驳", "争", "辩", "斥", "骂", "喝",
                  "不", "非", "勿", "莫", "休", "岂", "焉", "安能", "岂可",
                  "大胆", "放肆", "反了", "拿命", "可恼", "气煞", "奸贼",
                  "违令", "斩首", "拿下", "推出", "刀", "剑", "枪", "戟",
                  "退兵", "攻城", "杀进", "冲锋", "埋伏", "厮杀", "血战"}

ACTION_WORDS = {"上", "下", "去", "来", "走", "跑", "跳", "进", "出", "过",
                "传", "令", "叫", "唤", "请", "带", "拿", "取", "送", "报",
                "禀", "奏", "启", "宣", "召", "调", "派", "遣", "发", "收",
                "进见", "参见", "叩见", "启禀", "传令", "听令", "升帐"}

STAGE_WORDS = {"上", "下", "同上", "过场", "开场", "下场", "摆", "设", "置",
               "擂鼓", "鸣锣", "起霸", "走边", "趟马", "圆场"}


# ── Feature Extraction ────────────────────────────────────────────────

def clean_text(text):
    return re.sub(r'[（(].*?[）)]', '', text.strip())


def count_keywords(text, keyword_set):
    return sum(text.count(kw) for kw in keyword_set)


def extract_scene_features(script):
    """Extract narrative features for each scene in a script."""
    scenes = script.get("scenes", [])
    if len(scenes) < 2:
        return None

    features = []
    for scene in scenes:
        utterances = scene.get("utterances", [])
        if not utterances:
            features.append(None)
            continue

        # Count character utterances only (skip stage directions)
        char_utts = [u for u in utterances if u.get("character") and u.get("type") != "stage"]
        stage_utts = [u for u in utterances if u.get("type") == "stage" or u.get("character") is None]

        all_text = " ".join(clean_text(u.get("text", "")) for u in utterances)
        char_text = " ".join(clean_text(u.get("text", "")) for u in char_utts)

        # 1. Emotion intensity
        pos_count = count_keywords(all_text, EMOTION_POSITIVE)
        neg_count = count_keywords(all_text, EMOTION_NEGATIVE)
        total_text_len = max(len(all_text), 1)
        emotion_raw = (pos_count - neg_count) / (total_text_len ** 0.5) * 10
        emotion_valence = round(max(-1, min(1, emotion_raw / 20)), 4)
        emotion_intensity = round((pos_count + neg_count) / total_text_len * 100, 4)

        # 2. Conflict intensity
        conflict_count = count_keywords(all_text, CONFLICT_WORDS)
        conflict_intensity = round(conflict_count / max(len(utterances), 1) * 10, 4)

        # 3. Event density
        action_count = count_keywords(all_text, ACTION_WORDS)
        stage_count = len(stage_utts)
        event_density = round((action_count + stage_count) / max(len(utterances), 1) * 10, 4)

        # 4. Character activity
        active_chars = set()
        for u in char_utts:
            c = u.get("character")
            if c:
                active_chars.add(c)
        char_count = len(active_chars)
        dialogue_turns = len(char_utts)
        char_activity = round(char_count, 2)

        features.append({
            "scene_id": scene.get("scene_id", 0),
            "scene_name": scene.get("name", ""),
            "utterance_count": len(utterances),
            "dialogue_turns": dialogue_turns,
            "emotion_valence": emotion_valence,
            "emotion_intensity": emotion_intensity,
            "conflict_intensity": conflict_intensity,
            "event_density": event_density,
            "char_count": char_count,
            "char_activity": char_activity,
        })

    # Fill None values with neighbors
    for i in range(len(features)):
        if features[i] is None:
            # Copy from nearest valid neighbor
            for offset in range(1, len(features)):
                if i - offset >= 0 and features[i - offset] is not None:
                    features[i] = dict(features[i - offset])
                    features[i]["scene_id"] = i
                    features[i]["interpolated"] = True
                    break
                if i + offset < len(features) and features[i + offset] is not None:
                    features[i] = dict(features[i + offset])
                    features[i]["scene_id"] = i
                    features[i]["interpolated"] = True
                    break
        if features[i] is None:
            features[i] = {
                "scene_id": i, "utterance_count": 0, "dialogue_turns": 0,
                "emotion_valence": 0, "emotion_intensity": 0,
                "conflict_intensity": 0, "event_density": 0,
                "char_count": 0, "char_activity": 0, "interpolated": True,
            }

    return [f for f in features if f is not None]


# ── Narrative Stage Segmentation ──────────────────────────────────────

def detect_narrative_stages(features, sigma=1.5):
    """Segment scene sequence into 4 narrative stages using peak detection."""
    n = len(features)
    if n < 4:
        return None

    # Extract primary signal: weighted combination of conflict + event density
    conflict = np.array([f["conflict_intensity"] for f in features])
    event = np.array([f["event_density"] for f in features])
    emotion = np.array([f["emotion_intensity"] for f in features])

    # Smooth
    conflict_s = gaussian_filter1d(conflict.astype(float), sigma=sigma)
    event_s = gaussian_filter1d(event.astype(float), sigma=sigma)

    # Combined narrative tension signal
    tension = conflict_s * 0.5 + event_s * 0.3 + emotion * 0.2

    # Detect peaks and valleys
    peaks, peak_props = find_peaks(tension, prominence=np.ptp(tension) * 0.15, distance=max(1, n // 5))
    valleys, _ = find_peaks(-tension, prominence=np.ptp(tension) * 0.1, distance=max(1, n // 5))

    # Find main peak (climax)
    if len(peaks) > 0:
        main_peak = peaks[np.argmax(tension[peaks])]
    else:
        main_peak = n // 2  # fallback: middle

    # Segment into 4 stages
    # 开端 (Setup): before first significant rise
    # 发展 (Development): rising to climax
    # 高潮 (Climax): around the main peak
    # 结局 (Resolution): after climax

    # Find the rise start (first valley or start)
    rise_start = 0
    for v in valleys:
        if v < main_peak:
            rise_start = v
        else:
            break

    climax_start = max(0, main_peak - max(1, n // 10))
    climax_end = min(n - 1, main_peak + max(1, n // 10))

    # Find resolution start (first valley after climax)
    resolution_start = n
    for v in valleys:
        if v > main_peak:
            resolution_start = v
            break

    stages = []
    for i in range(n):
        if i < rise_start:
            stage = "opening"  # 开端
        elif i < climax_start:
            stage = "development"  # 发展
        elif i <= climax_end:
            stage = "climax"  # 高潮
        else:
            stage = "resolution"  # 结局
        stages.append(stage)

    # Compute stage-level metrics
    stage_metrics = {}
    for stage_name in ["opening", "development", "climax", "resolution"]:
        indices = [i for i, s in enumerate(stages) if s == stage_name]
        if indices:
            stage_metrics[stage_name] = {
                "scene_range": [indices[0], indices[-1]],
                "scene_count": len(indices),
                "avg_conflict": round(float(np.mean([conflict[i] for i in indices])), 4),
                "avg_emotion": round(float(np.mean([emotion[i] for i in indices])), 4),
                "avg_event": round(float(np.mean([event[i] for i in indices])), 4),
            }

    # Narrative metrics
    climax_position = main_peak / max(n - 1, 1)  # 0-1 normalized
    tension_range = float(np.ptp(tension))
    tension_mean = float(np.mean(tension))
    tension_std = float(np.std(tension))

    # Structure type classification
    n_peaks = len(peaks)
    prominent_peaks = sum(1 for p in peak_props.get("prominences", []) if p > np.ptp(tension) * 0.2) if len(peaks) > 0 else 0

    if n_peaks <= 1 or prominent_peaks <= 1:
        structure_type = "single_peak"  # 单峰结构
    elif prominent_peaks >= 3:
        structure_type = "multi_peak"  # 多峰结构
    else:
        structure_type = "dual_peak"  # 双峰结构

    # Peak timing classification
    if climax_position < 0.35:
        peak_timing = "early"  # 早期高潮
    elif climax_position < 0.65:
        peak_timing = "middle"  # 中期高潮
    else:
        peak_timing = "late"  # 晚期高潮

    return {
        "stages": stages,
        "stage_metrics": stage_metrics,
        "main_peak_scene": int(main_peak),
        "peak_count": n_peaks,
        "climax_position": round(climax_position, 4),
        "peak_timing": peak_timing,
        "structure_type": structure_type,
        "tension_range": round(tension_range, 4),
        "tension_mean": round(tension_mean, 4),
        "tension_std": round(tension_std, 4),
        "narrative_curve": {
            "tension": [round(float(v), 4) for v in tension],
            "conflict_smooth": [round(float(v), 4) for v in conflict_s],
            "event_smooth": [round(float(v), 4) for v in event_s],
            "emotion": [round(float(v), 4) for v in emotion],
        },
    }


# ── Script Type Classification ────────────────────────────────────────

def classify_script_type_simple(script):
    all_text = script.get("plot", "") + script.get("title", "")
    scores = {"历史戏": 0, "家庭戏": 0, "公案戏": 0, "神话戏": 0, "其他": 0}
    for kw in ["军", "兵", "战", "攻", "伐", "帅", "将", "阵"]:
        if kw in all_text: scores["历史戏"] += 1
    for kw in ["母", "父", "子", "女", "妻", "夫", "家", "婚", "嫁", "孝"]:
        if kw in all_text: scores["家庭戏"] += 1
    for kw in ["案", "审", "判", "告", "冤", "状", "堂", "府", "衙"]:
        if kw in all_text: scores["公案戏"] += 1
    for kw in ["仙", "神", "佛", "鬼", "妖", "怪"]:
        if kw in all_text: scores["神话戏"] += 1
    return max(scores, key=scores.get)


# ── Main Pipeline ─────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("Narrative Structure Analysis Pipeline")
    print("=" * 60)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 1. Load scripts
    print("\n[1/7] Loading scripts...")
    scripts = []
    for fpath in sorted(glob.glob(os.path.join(DATA_DIR, "**/*.json"), recursive=True)):
        with open(fpath, "r", encoding="utf-8") as f:
            scripts.append(json.load(f))
    print(f"  Loaded {len(scripts)} scripts")

    # 2. Extract scene features
    print("\n[2/7] Extracting scene-level features...")
    all_narratives = []
    script_scenes_map = {}

    for s in scripts:
        sid = s["script_id"]
        features = extract_scene_features(s)
        if features is None or len(features) < 3:
            continue

        result = detect_narrative_stages(features)
        if result is None:
            continue

        stype = classify_script_type_simple(s)

        all_narratives.append({
            "script_id": sid,
            "title": s["title"],
            "type": stype,
            "scene_count": len(features),
            "scenes": features,
            "stages": result["stages"],
            "stage_metrics": result["stage_metrics"],
            "main_peak_scene": result["main_peak_scene"],
            "climax_position": result["climax_position"],
            "peak_timing": result["peak_timing"],
            "structure_type": result["structure_type"],
            "tension_range": result["tension_range"],
            "tension_mean": result["tension_mean"],
            "tension_std": result["tension_std"],
            "narrative_curve": result["narrative_curve"],
        })

        script_scenes_map[sid] = features

    print(f"  Analyzed {len(all_narratives)} scripts with narrative structure")

    # 3. Aggregate by play type
    print("\n[3/7] Computing type-level aggregates...")
    type_narratives = defaultdict(list)
    for n in all_narratives:
        type_narratives[n["type"]].append(n)

    type_aggregates = {}
    for stype, narratives in type_narratives.items():
        if len(narratives) < 2:
            continue
        n = len(narratives)

        # Structure type distribution
        structure_dist = Counter(na["structure_type"] for na in narratives)
        peak_timing_dist = Counter(na["peak_timing"] for na in narratives)

        # Average metrics
        climax_positions = [na["climax_position"] for na in narratives]
        tension_ranges = [na["tension_range"] for na in narratives]
        tension_stds = [na["tension_std"] for na in narratives]

        type_aggregates[stype] = {
            "count": n,
            "structure_distribution": dict(structure_dist),
            "peak_timing_distribution": dict(peak_timing_dist),
            "avg_climax_position": round(sum(climax_positions) / n, 4),
            "avg_tension_range": round(sum(tension_ranges) / n, 4),
            "avg_tension_std": round(sum(tension_stds) / n, 4),
            "structure_type_pct": {
                k: round(v / n * 100, 1) for k, v in structure_dist.items()
            },
            "peak_timing_pct": {
                k: round(v / n * 100, 1) for k, v in peak_timing_dist.items()
            },
        }

    print(f"  Aggregated {len(type_aggregates)} types")

    # 4. Build narrative comparison data
    print("\n[4/7] Building comparison data...")
    comparison = {
        "types": list(type_aggregates.keys()),
        "metrics": {},
    }

    metric_keys = [
        ("avg_climax_position", "高潮位置(归一化)"),
        ("avg_tension_range", "张力幅度"),
        ("avg_tension_std", "节奏波动性"),
    ]

    for key, label in metric_keys:
        comparison["metrics"][key] = {
            "label": label,
            "values": {t: type_aggregates[t][key] for t in type_aggregates if key in type_aggregates[t]},
        }

    # 5. Build feature vectors for clustering
    print("\n[5/7] Building narrative feature vectors...")
    narrative_features = []
    for na in all_narratives:
        vec = [
            na["tension_range"],
            na["tension_std"],
            na["climax_position"],
            na.get("scene_count", 0),
            1 if na["structure_type"] == "single_peak" else 0,
            1 if na["structure_type"] == "multi_peak" else 0,
        ]
        narrative_features.append({
            "script_id": na["script_id"],
            "title": na["title"],
            "type": na["type"],
            "structure_type": na["structure_type"],
            "climax_position": na["climax_position"],
            "features": vec,
            "stage_metrics": na["stage_metrics"],
        })

    # Simple PCA-like 2D projection
    if len(narrative_features) >= 4:
        from sklearn.decomposition import PCA
        feat_matrix = np.array([nf["features"] for nf in narrative_features])
        # Normalize
        feat_norm = (feat_matrix - feat_matrix.mean(axis=0)) / (feat_matrix.std(axis=0) + 1e-8)
        pca = PCA(n_components=2, random_state=42)
        pca_2d = pca.fit_transform(feat_norm)
        for i, nf in enumerate(narrative_features):
            nf["x"] = round(float(pca_2d[i][0]), 4)
            nf["y"] = round(float(pca_2d[i][1]), 4)
    else:
        for nf in narrative_features:
            nf["x"] = nf["climax_position"]
            nf["y"] = nf["tension_range"]

    # 6. Build stage template curves (average per type)
    print("\n[6/7] Building stage templates...")
    stage_templates = {}
    for stype, narratives in type_narratives.items():
        if len(narratives) < 3:
            continue

        # Collect tension curves, normalized to same length
        curves = []
        for na in narratives:
            curve = na["narrative_curve"]["tension"]
            if len(curve) > 0:
                # Resample to 12 points
                old_len = len(curve)
                new_curve = np.interp(
                    np.linspace(0, old_len - 1, 12),
                    np.arange(old_len),
                    curve
                )
                curves.append(new_curve)

        if curves:
            avg_curve = np.mean(curves, axis=0)
            std_curve = np.std(curves, axis=0)
            stage_templates[stype] = {
                "avg_curve": [round(float(v), 4) for v in avg_curve],
                "std_curve": [round(float(v), 4) for v in std_curve],
                "sample_count": len(curves),
            }

    # 7. Export
    print("\n[7/7] Exporting data...")

    # Full narrative data
    with open(os.path.join(OUTPUT_DIR, "narrative_data.json"), "w", encoding="utf-8") as f:
        json.dump({
            "narratives": all_narratives,
            "features": narrative_features,
        }, f, ensure_ascii=False, indent=2)
    print(f"  [OK] narrative_data.json ({len(all_narratives)} scripts)")

    # Type aggregates
    with open(os.path.join(OUTPUT_DIR, "narrative_type_aggregates.json"), "w", encoding="utf-8") as f:
        json.dump(type_aggregates, f, ensure_ascii=False, indent=2)
    print(f"  [OK] narrative_type_aggregates.json")

    # Comparison
    with open(os.path.join(OUTPUT_DIR, "narrative_comparison.json"), "w", encoding="utf-8") as f:
        json.dump(comparison, f, ensure_ascii=False, indent=2)
    print(f"  [OK] narrative_comparison.json")

    # Stage templates
    with open(os.path.join(OUTPUT_DIR, "narrative_templates.json"), "w", encoding="utf-8") as f:
        json.dump(stage_templates, f, ensure_ascii=False, indent=2)
    print(f"  [OK] narrative_templates.json")

    # Summary
    structure_counts = Counter(na["structure_type"] for na in all_narratives)
    peak_counts = Counter(na["peak_timing"] for na in all_narratives)

    with open(os.path.join(OUTPUT_DIR, "narrative_summary.json"), "w", encoding="utf-8") as f:
        json.dump({
            "total_scripts": len(all_narratives),
            "structure_distribution": dict(structure_counts),
            "peak_timing_distribution": dict(peak_counts),
            "type_counts": {t: a["count"] for t, a in type_aggregates.items()},
        }, f, ensure_ascii=False, indent=2)
    print(f"  [OK] narrative_summary.json")

    print(f"\nDone!")
    print(f"  Scripts analyzed: {len(all_narratives)}")
    print(f"  Structure types: {dict(structure_counts)}")
    print(f"  Peak timing: {dict(peak_counts)}")
    for stype, agg in type_aggregates.items():
        print(f"  {stype}: avg climax={agg['avg_climax_position']:.3f}, "
              f"structures={agg['structure_type_pct']}")


if __name__ == "__main__":
    main()
