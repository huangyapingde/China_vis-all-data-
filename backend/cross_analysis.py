"""
Cross-Dimensional Association Analysis Pipeline
================================================
Merges network, theme, and narrative data per script to explore
cross-dimensional correlations and typical patterns.

Output: frontend/public/data/cross_analysis.json
"""

import json
import os
import math
from collections import Counter, defaultdict

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "public", "data")


def pearson(xs, ys):
    """Compute Pearson correlation coefficient."""
    n = len(xs)
    if n < 3:
        return 0
    mx, my = sum(xs) / n, sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    d1 = math.sqrt(sum((x - mx) ** 2 for x in xs))
    d2 = math.sqrt(sum((y - my) ** 2 for y in ys))
    if d1 == 0 or d2 == 0:
        return 0
    return round(num / (d1 * d2), 4)


def load_data():
    # 1. Network data
    with open(os.path.join(OUTPUT_DIR, "networks_all.json"), "r", encoding="utf-8") as f:
        networks = json.load(f)
    net_map = {}
    for n in networks:
        sid = n["script_id"]
        cooc = n.get("cooccurrence", {})
        dial = n.get("dialogue", {})
        pw = n.get("power", {})
        net_map[sid] = {
            "title": n.get("title", ""),
            "type": n.get("type", ""),
            "character_count": n.get("character_count", 0),
            # Co-occurrence metrics
            "cooc_density": cooc.get("density", 0),
            "cooc_clustering": cooc.get("avg_clustering", 0),
            "cooc_path_length": cooc.get("avg_path_length", 0),
            "cooc_modularity": cooc.get("modularity", 0),
            "cooc_community_count": cooc.get("community_count", 0),
            "cooc_centralization": cooc.get("centralization", 0),
            # Dialogue metrics
            "dial_density": dial.get("density", 0),
            "dial_clustering": dial.get("avg_clustering", 0),
            "dial_centralization": dial.get("centralization", 0),
            # Power metrics
            "power_density": pw.get("density", 0),
            "power_centralization": pw.get("centralization", 0),
        }
    print(f"  Network data: {len(net_map)} scripts")

    # 2. Theme data
    with open(os.path.join(OUTPUT_DIR, "theme_script_distributions.json"), "r", encoding="utf-8") as f:
        theme_raw = json.load(f)
    theme_map = {}
    theme_names = theme_raw.get("theme_names", [])
    scripts_dict = theme_raw.get("scripts", {})
    for sid, sdata in scripts_dict.items():
        theme_map[sid] = {
            "title": sdata.get("title", ""),
            "type": sdata.get("type", ""),
            "theme_count": sdata.get("theme_count", 0),
            "theme_entropy": sdata.get("entropy", 0),
            "top_theme": sdata.get("top_themes", [{}])[0].get("theme", "") if sdata.get("top_themes") else "",
            "top_theme_score": sdata.get("top_themes", [{}])[0].get("score", 0) if sdata.get("top_themes") else 0,
            "distribution": sdata.get("distribution", {}),
        }
    print(f"  Theme data: {len(theme_map)} scripts")

    # 3. Narrative data
    with open(os.path.join(OUTPUT_DIR, "narrative_data.json"), "r", encoding="utf-8") as f:
        nar_raw = json.load(f)
    nar_map = {}
    for n in nar_raw.get("narratives", []):
        sid = n.get("script_id", "")
        nar_map[sid] = {
            "title": n.get("title", ""),
            "type": n.get("type", ""),
            "climax_position": n.get("climax_position", 0.5),
            "structure_type": n.get("structure_type", "single_peak"),
            "peak_timing": n.get("peak_timing", "middle"),
            "tension_range": n.get("tension_range", 0),
            "tension_mean": n.get("tension_mean", 0),
            "tension_std": n.get("tension_std", 0),
            "scene_count": n.get("scene_count", 0),
        }
    print(f"  Narrative data: {len(nar_map)} scripts")

    return net_map, theme_map, nar_map, theme_names


def build_cross_data(net_map, theme_map, nar_map, theme_names):
    """Merge all data sources on script_id and compute correlations."""

    # Find intersection of script_ids
    all_sids = set(net_map.keys()) & set(theme_map.keys()) & set(nar_map.keys())
    print(f"  Intersection: {len(all_sids)} scripts")

    # Build unified script entries
    scripts = []
    for sid in sorted(all_sids):
        net = net_map[sid]
        theme = theme_map[sid]
        nar = nar_map[sid]
        scripts.append({
            "script_id": sid,
            "title": net.get("title", theme.get("title", nar.get("title", ""))),
            "type": net.get("type", theme.get("type", nar.get("type", ""))),
            # Network metrics
            "character_count": net["character_count"],
            "cooc_density": net["cooc_density"],
            "cooc_clustering": net["cooc_clustering"],
            "cooc_path_length": net["cooc_path_length"],
            "cooc_modularity": net["cooc_modularity"],
            "cooc_community_count": net["cooc_community_count"],
            "cooc_centralization": net["cooc_centralization"],
            "dial_density": net["dial_density"],
            "power_density": net["power_density"],
            "power_centralization": net["power_centralization"],
            # Theme metrics
            "theme_count": theme["theme_count"],
            "theme_entropy": theme["theme_entropy"],
            "top_theme": theme["top_theme"],
            "top_theme_score": theme["top_theme_score"],
            "theme_distribution": theme.get("distribution", {}),
            # Narrative metrics
            "climax_position": nar["climax_position"],
            "structure_type": nar["structure_type"],
            "peak_timing": nar["peak_timing"],
            "tension_range": nar["tension_range"],
            "tension_mean": nar["tension_mean"],
            "tension_std": nar["tension_std"],
            "scene_count": nar["scene_count"],
        })

    # Define numeric dimensions for correlation
    dim_defs = {
        # Network dimensions
        "角色数": ("character_count", "网络"),
        "共现密度": ("cooc_density", "网络"),
        "聚集系数": ("cooc_clustering", "网络"),
        "模块度": ("cooc_modularity", "网络"),
        "社区数": ("cooc_community_count", "网络"),
        "中心化程度": ("cooc_centralization", "网络"),
        "对话密度": ("dial_density", "网络"),
        "权力密度": ("power_density", "网络"),
        "权力中心化": ("power_centralization", "网络"),
        # Theme dimensions
        "主题数": ("theme_count", "主题"),
        "主题熵": ("theme_entropy", "主题"),
        # Narrative dimensions
        "高潮位置": ("climax_position", "叙事"),
        "张力幅度": ("tension_range", "叙事"),
        "张力均值": ("tension_mean", "叙事"),
        "张力标准差": ("tension_std", "叙事"),
        "场次数": ("scene_count", "叙事"),
    }

    # Build correlation matrix
    dim_names = list(dim_defs.keys())
    dim_keys = [dim_defs[d][0] for d in dim_names]
    dim_cats = [dim_defs[d][1] for d in dim_names]

    corr_matrix = {}
    for i, name_i in enumerate(dim_names):
        corr_matrix[name_i] = {}
        for j, name_j in enumerate(dim_names):
            vals_i = [s[dim_keys[i]] for s in scripts if isinstance(s[dim_keys[i]], (int, float))]
            vals_j = [s[dim_keys[j]] for s in scripts if isinstance(s[dim_keys[j]], (int, float))]
            min_len = min(len(vals_i), len(vals_j))
            corr_matrix[name_i][name_j] = pearson(vals_i[:min_len], vals_j[:min_len])

    # Define pattern rules and find scripts matching each pattern
    patterns = find_patterns(scripts)

    # Cluster scripts by combined feature vector (simplified: rule-based)
    clusters = cluster_scripts(scripts)

    # Type-level aggregates across dimensions
    type_agg = compute_type_aggregates(scripts)

    # Distribution of structure types per theme type
    structure_by_theme = compute_structure_theme_cross(scripts)

    return {
        "summary": {
            "total_scripts": len(scripts),
            "dimension_names": dim_names,
            "dimension_categories": dim_cats,
            "correlation_matrix": corr_matrix,
        },
        "scripts": scripts,
        "patterns": patterns,
        "clusters": clusters,
        "type_aggregates": type_agg,
        "structure_theme_cross": structure_by_theme,
    }


def find_patterns(scripts):
    """Find typical cross-dimension patterns using rule-based analysis."""
    patterns = []

    # Pattern 1: High modularity + high theme entropy → complex multi-theme叙事
    high_mod = [s for s in scripts if s["cooc_modularity"] > 0.1]
    high_mod_high_entropy = [s for s in high_mod if s["theme_entropy"] > 2.5]
    high_mod_low_entropy = [s for s in high_mod if s["theme_entropy"] < 1.5]
    if high_mod:
        pct = len(high_mod_high_entropy) / len(high_mod) * 100
        patterns.append({
            "name": "高模块度 → 主题多样化",
            "description": "网络社区结构明显的剧本，主题多样性也更高",
            "correlation": round(len(high_mod_high_entropy) / max(1, len(high_mod)), 3),
            "support": f"{len(high_mod_high_entropy)}/{len(high_mod)} ({pct:.0f}%)",
            "dim1": "cooc_modularity", "dim2": "theme_entropy",
        })

    # Pattern 2: High centralization + single_peak → 权力集中型线性叙事
    high_cent = [s for s in scripts if s["cooc_centralization"] > 0.5]
    high_cent_single = [s for s in high_cent if s["structure_type"] == "single_peak"]
    if high_cent:
        pct = len(high_cent_single) / len(high_cent) * 100
        patterns.append({
            "name": "高中心化 → 单峰线性叙事",
            "description": "权力高度集中的剧本，叙事结构多为单峰线性",
            "correlation": round(len(high_cent_single) / max(1, len(high_cent)), 3),
            "support": f"{len(high_cent_single)}/{len(high_cent)} ({pct:.0f}%)",
            "dim1": "cooc_centralization", "dim2": "structure_type",
        })

    # Pattern 3: High power density → earlier climax
    high_power = [s for s in scripts if s["power_density"] > 0.1]
    early_climax = [s for s in high_power if s["climax_position"] < 0.5]
    if high_power:
        pct = len(early_climax) / len(high_power) * 100
        patterns.append({
            "name": "高权力密度 → 高潮前置",
            "description": "权力网络密集的剧本，叙事高潮更倾向于前半部分",
            "correlation": round(len(early_climax) / max(1, len(high_power)), 3),
            "support": f"{len(early_climax)}/{len(high_power)} ({pct:.0f}%)",
            "dim1": "power_density", "dim2": "climax_position",
        })

    # Pattern 4: Many characters + low modularity → 群像剧
    many_chars = [s for s in scripts if s["character_count"] > 10]
    many_chars_low_mod = [s for s in many_chars if s["cooc_modularity"] < 0.05]
    if many_chars:
        pct = len(many_chars_low_mod) / len(many_chars) * 100
        patterns.append({
            "name": "多角色低模块度 → 群像交织叙事",
            "description": "角色多但社区模糊，角色间跨阵营互动频繁",
            "correlation": round(len(many_chars_low_mod) / max(1, len(many_chars)), 3),
            "support": f"{len(many_chars_low_mod)}/{len(many_chars)} ({pct:.0f}%)",
            "dim1": "character_count", "dim2": "cooc_modularity",
        })

    # Pattern 5: High tension_std → multi_peak (节奏波动大→多高潮)
    high_var = [s for s in scripts if s["tension_std"] > 0.2]
    multi_peak = [s for s in high_var if s["structure_type"] in ("dual_peak", "multi_peak")]
    if high_var:
        pct = len(multi_peak) / len(high_var) * 100
        patterns.append({
            "name": "张力波动大 → 多峰结构",
            "description": "叙事张力波动剧烈的剧本，多高潮结构比例显著升高",
            "correlation": round(len(multi_peak) / max(1, len(high_var)), 3),
            "support": f"{len(multi_peak)}/{len(high_var)} ({pct:.0f}%)",
            "dim1": "tension_std", "dim2": "structure_type",
        })

    # Pattern 6: Theme entropy vs climax position
    high_entropy = [s for s in scripts if s["theme_entropy"] > 2.5]
    late_climax = [s for s in high_entropy if s["climax_position"] > 0.6]
    if high_entropy:
        pct = len(late_climax) / len(high_entropy) * 100
        patterns.append({
            "name": "主题多样 → 高潮靠后",
            "description": "主题丰富的剧本倾向于将高潮安排在更后的位置",
            "correlation": round(len(late_climax) / max(1, len(high_entropy)), 3),
            "support": f"{len(late_climax)}/{len(high_entropy)} ({pct:.0f}%)",
            "dim1": "theme_entropy", "dim2": "climax_position",
        })

    return patterns


def cluster_scripts(scripts):
    """Rule-based clustering of scripts by combined dimensions."""
    clusters = {
        "权力集中型": {"ids": [], "desc": "高中心化、高权力密度、单峰叙事", "color": "#ff7043"},
        "群像交织型": {"ids": [], "desc": "多角色、低模块度、主题多样", "color": "#42a5f5"},
        "情感驱动型": {"ids": [], "desc": "少角色、高聚类系数、多峰叙事", "color": "#ab47bc"},
        "传统叙事型": {"ids": [], "desc": "中等各项指标、单峰标准结构", "color": "#66bb6a"},
    }

    for s in scripts:
        if s["cooc_centralization"] > 0.5 and s["power_density"] > 0.05 and s["structure_type"] == "single_peak":
            clusters["权力集中型"]["ids"].append(s["script_id"])
        elif s["character_count"] > 8 and s["cooc_modularity"] < 0.08 and s["theme_entropy"] > 2.0:
            clusters["群像交织型"]["ids"].append(s["script_id"])
        elif s["character_count"] <= 6 and s["cooc_clustering"] > 0.7 and s["structure_type"] in ("dual_peak", "multi_peak"):
            clusters["情感驱动型"]["ids"].append(s["script_id"])
        else:
            clusters["传统叙事型"]["ids"].append(s["script_id"])

    result = []
    for name, data in clusters.items():
        cluster_scripts_data = [s for s in scripts if s["script_id"] in data["ids"]]
        if not cluster_scripts_data:
            continue
        # Compute centroid
        centroid = {
            "avg_density": sum(s["cooc_density"] for s in cluster_scripts_data) / len(cluster_scripts_data),
            "avg_centralization": sum(s["cooc_centralization"] for s in cluster_scripts_data) / len(cluster_scripts_data),
            "avg_entropy": sum(s["theme_entropy"] for s in cluster_scripts_data) / len(cluster_scripts_data),
            "avg_climax": sum(s["climax_position"] for s in cluster_scripts_data) / len(cluster_scripts_data),
            "avg_tension_std": sum(s["tension_std"] for s in cluster_scripts_data) / len(cluster_scripts_data),
            "avg_character_count": sum(s["character_count"] for s in cluster_scripts_data) / len(cluster_scripts_data),
            "avg_modularity": sum(s["cooc_modularity"] for s in cluster_scripts_data) / len(cluster_scripts_data),
        }
        # Representative scripts (closest to centroid)
        def dist(s):
            return abs(s["cooc_density"] - centroid["avg_density"]) + \
                   abs(s["cooc_centralization"] - centroid["avg_centralization"]) + \
                   abs(s["theme_entropy"] - centroid["avg_entropy"])
        reps = sorted(cluster_scripts_data, key=dist)[:5]
        result.append({
            "name": name,
            "size": len(data["ids"]),
            "description": data["desc"],
            "color": data["color"],
            "centroid": centroid,
            "representatives": [{"script_id": r["script_id"], "title": r["title"], "type": r["type"]} for r in reps],
        })

    return result


def compute_type_aggregates(scripts):
    """Compute average metrics per play type."""
    by_type = defaultdict(list)
    for s in scripts:
        by_type[s.get("type", "其他")].append(s)

    result = {}
    for tname, group in by_type.items():
        n = len(group)
        result[tname] = {
            "count": n,
            "avg_character_count": round(sum(s["character_count"] for s in group) / n, 2),
            "avg_cooc_density": round(sum(s["cooc_density"] for s in group) / n, 4),
            "avg_cooc_clustering": round(sum(s["cooc_clustering"] for s in group) / n, 4),
            "avg_cooc_modularity": round(sum(s["cooc_modularity"] for s in group) / n, 4),
            "avg_cooc_centralization": round(sum(s["cooc_centralization"] for s in group) / n, 4),
            "avg_power_density": round(sum(s["power_density"] for s in group) / n, 4),
            "avg_theme_entropy": round(sum(s["theme_entropy"] for s in group) / n, 4),
            "avg_climax_position": round(sum(s["climax_position"] for s in group) / n, 4),
            "avg_tension_std": round(sum(s["tension_std"] for s in group) / n, 4),
            "single_peak_pct": round(sum(1 for s in group if s["structure_type"] == "single_peak") / n, 4),
            "multi_peak_pct": round(sum(1 for s in group if s["structure_type"] in ("dual_peak", "multi_peak")) / n, 4),
        }
    return result


def compute_structure_theme_cross(scripts):
    """Cross-tabulation of structure type vs dominant theme."""
    cross = defaultdict(lambda: defaultdict(int))
    for s in scripts:
        stype = s["structure_type"]
        theme = s["top_theme"] or "其他"
        cross[stype][theme] += 1
    return {st: dict(th) for st, th in cross.items()}


def main():
    print("=" * 60)
    print("Cross-Dimensional Association Analysis")
    print("=" * 60)

    print("\n[1/3] Loading data sources...")
    net_map, theme_map, nar_map, theme_names = load_data()

    print("\n[2/3] Building cross-dimensional data...")
    cross_data = build_cross_data(net_map, theme_map, nar_map, theme_names)

    print(f"\n  Total scripts in cross analysis: {cross_data['summary']['total_scripts']}")
    print(f"  Dimensions: {len(cross_data['summary']['dimension_names'])}")
    print(f"  Patterns found: {len(cross_data['patterns'])}")
    print(f"  Clusters: {len(cross_data['clusters'])}")

    print("\n[3/3] Exporting...")
    with open(os.path.join(OUTPUT_DIR, "cross_analysis.json"), "w", encoding="utf-8") as f:
        json.dump(cross_data, f, ensure_ascii=False, indent=2)
    print(f"  [OK] cross_analysis.json")

    # Print key correlations
    print("\n  Key cross-dimension correlations:")
    mat = cross_data["summary"]["correlation_matrix"]
    dims = cross_data["summary"]["dimension_names"]
    highlights = [
        ("权力密度", "中心化程度"), ("模块度", "主题熵"),
        ("中心化程度", "高潮位置"), ("主题熵", "高潮位置"),
        ("张力标准差", "主题熵"), ("角色数", "主题数"),
        ("共现密度", "主题数"), ("权力中心化", "张力幅度"),
    ]
    for d1, d2 in highlights:
        if d1 in mat and d2 in mat[d1]:
            r = mat[d1][d2]
            print(f"    {d1} × {d2}: r = {r:+.4f}")

    print(f"\nDone! Data exported to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
