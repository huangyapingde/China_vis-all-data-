"""
Character Relationship Network Analysis Pipeline
==================================================
Builds multi-layer networks from Peking Opera scripts:
- Layer 1: Co-occurrence network
- Layer 2: Dialogue network (directed)
- Layer 3: Power/command network (directed)
Computes graph metrics and compares across play types.
"""

import json
import os
import glob
import re
from collections import Counter, defaultdict
from math import log2
import networkx as nx
import warnings
warnings.filterwarnings("ignore")

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "public", "data")

COMMAND_WORDS = {"传", "令", "斩", "杀", "绑", "拿下", "推出", "听令", "遵命", "得令",
                 "吩咐", "差遣", "命你", "速去", "快去", "不许", "违令", "升帐", "升堂", "拿下"}

OBEY_WORDS = {"遵命", "得令", "遵旨", "领旨", "是", "在", "晓得", "知道", "听令"}

# ── Script Type Classification ──────────────────────────────────────

def classify_script_type(plot_text, characters, title, alias_list):
    """Classify script into: 历史戏, 家庭戏, 公案戏, 神话戏, 其他"""
    all_text = plot_text + title + " ".join(alias_list)
    for c in characters:
        all_text += c.get("name", "")

    scores = {"历史戏": 0, "家庭戏": 0, "公案戏": 0, "神话戏": 0, "其他": 0}

    # Historical keywords
    historical_kw = ["军", "兵", "战", "攻", "伐", "征", "帅", "将", "阵", "敌", "城",
                     "王", "帝", "皇", "权", "朝", "谋", "计", "丞", "相", "国", "邦",
                     "叛", "反", "降", "伏", "胜", "败", "退", "进"]
    for kw in historical_kw:
        if kw in all_text:
            scores["历史戏"] += 1

    # Family keywords
    family_kw = ["母", "父", "子", "女", "妻", "夫", "儿", "媳", "婿", "兄", "弟", "姐",
                 "妹", "娘", "爹", "家", "婚", "嫁", "娶", "孝", "贤", "亲", "骨肉",
                 "团圆", "离别", "重逢", "认", "养"]
    for kw in family_kw:
        if kw in all_text:
            scores["家庭戏"] += 1

    # Legal case keywords
    legal_kw = ["案", "审", "判", "告", "诉", "冤", "状", "堂", "官", "府", "衙",
                "罪", "刑", "罚", "斩", "铡", "监", "押", "囚", "牢", "狱", "犯",
                "原告", "被告", "大人", "明察", "冤枉", "招", "供"]
    for kw in legal_kw:
        if kw in all_text:
            scores["公案戏"] += 1

    # Mythological keywords
    myth_kw = ["仙", "神", "佛", "菩萨", "鬼", "妖", "怪", "龙王", "天宫", "地府",
               "仙丹", "法术", "变化", "显灵", "托梦", "阴魂", "轮回", "投胎"]
    for kw in myth_kw:
        if kw in all_text:
            scores["神话戏"] += 1

    # Normalize based on character names
    if any("娘娘" in c.get("name", "") or "妃" in c.get("name", "") for c in characters):
        scores["历史戏"] += 3

    best = max(scores, key=scores.get)
    # If "其他" is highest but there are meaningful scores elsewhere, pick second best
    if best == "其他":
        sorted_scores = sorted(scores.items(), key=lambda x: -x[1])
        if sorted_scores[0][1] == 0 and sorted_scores[1][1] > 0:
            best = sorted_scores[1][0]

    return best


# ── Network Extraction ──────────────────────────────────────────────

def build_cooccurrence_network(scenes, char_names):
    """Build co-occurrence network: characters in same scene are connected."""
    G = nx.Graph()
    G.add_nodes_from(char_names)

    for scene in scenes:
        scene_chars = set()
        for utt in scene.get("utterances", []):
            c = utt.get("character")
            if c:
                scene_chars.add(c)

        scene_chars = list(scene_chars & set(char_names))
        for i in range(len(scene_chars)):
            for j in range(i + 1, len(scene_chars)):
                if G.has_edge(scene_chars[i], scene_chars[j]):
                    G[scene_chars[i]][scene_chars[j]]["weight"] += 1
                else:
                    G.add_edge(scene_chars[i], scene_chars[j], weight=1)
    return G


def build_dialogue_network(scenes, char_names):
    """Build directed dialogue network: A speaks, then B responds."""
    DG = nx.DiGraph()
    DG.add_nodes_from(char_names)

    for scene in scenes:
        utterances = scene.get("utterances", [])
        for i in range(len(utterances) - 1):
            a = utterances[i].get("character")
            b = utterances[i + 1].get("character")
            if a and b and a != b and a in char_names and b in char_names:
                if DG.has_edge(a, b):
                    DG[a][b]["weight"] += 1
                else:
                    DG.add_edge(a, b, weight=1)
    return DG


def build_power_network(scenes, char_names):
    """Build directed power/command network based on keyword detection."""
    PG = nx.DiGraph()
    PG.add_nodes_from(char_names)

    for scene in scenes:
        utterances = scene.get("utterances", [])
        for i in range(len(utterances)):
            c = utterances[i].get("character")
            text = utterances[i].get("text", "")
            if not c or c not in char_names:
                continue

            # Check if this utterance contains a command
            has_command = any(kw in text for kw in COMMAND_WORDS)

            if has_command:
                # Look for who responds (obeys) within next few lines
                for j in range(i + 1, min(i + 4, len(utterances))):
                    responder = utterances[j].get("character")
                    resp_text = utterances[j].get("text", "")
                    if responder and responder != c and responder in char_names:
                        has_obey = any(kw in resp_text for kw in OBEY_WORDS)
                        if has_obey:
                            if PG.has_edge(c, responder):
                                PG[c][responder]["weight"] += 1
                            else:
                                PG.add_edge(c, responder, weight=1)
                            break
    return PG


def compute_graph_metrics(G, is_directed=False):
    """Compute comprehensive graph metrics."""
    n = G.number_of_nodes()
    e = G.number_of_edges()
    max_edges = n * (n - 1) if is_directed else n * (n - 1) / 2

    metrics = {
        "nodes": n,
        "edges": e,
        "density": round(e / max_edges, 4) if max_edges > 0 else 0,
    }

    if n < 2:
        metrics.update({
            "avg_clustering": 0, "avg_path_length": 0,
            "components": 0, "modularity": 0,
            "top_degree": [], "top_pagerank": [], "top_betweenness": [],
            "communities": [],
        })
        return metrics

    # Clustering
    try:
        metrics["avg_clustering"] = round(nx.average_clustering(G), 4)
    except:
        metrics["avg_clustering"] = 0

    # Average path length (on largest component)
    try:
        if is_directed:
            largest_cc = max(nx.weakly_connected_components(G), key=len)
        else:
            largest_cc = max(nx.connected_components(G), key=len)
        subG = G.subgraph(largest_cc)
        if subG.number_of_nodes() > 1:
            metrics["avg_path_length"] = round(nx.average_shortest_path_length(subG), 4)
        else:
            metrics["avg_path_length"] = 0
    except:
        metrics["avg_path_length"] = 0

    # Components
    if is_directed:
        metrics["components"] = nx.number_weakly_connected_components(G)
    else:
        metrics["components"] = nx.number_connected_components(G)

    # Centrality (Top 5)
    try:
        degree = dict(G.degree())
        top_deg = sorted(degree.items(), key=lambda x: -x[1])[:5]
        metrics["top_degree"] = [{"name": n, "value": v} for n, v in top_deg]
        metrics["centralization"] = round(
            sum(max(degree.values()) - v for v in degree.values()) / max(1, (n - 1) * (n - 2)), 4
        )
    except:
        metrics["top_degree"] = []
        metrics["centralization"] = 0

    # PageRank
    try:
        pr = nx.pagerank(G, alpha=0.85, max_iter=100)
        top_pr = sorted(pr.items(), key=lambda x: -x[1])[:5]
        metrics["top_pagerank"] = [{"name": n, "value": round(v, 4)} for n, v in top_pr]
    except:
        metrics["top_pagerank"] = []

    # Betweenness
    try:
        bc = nx.betweenness_centrality(G, normalized=True)
        top_bc = sorted(bc.items(), key=lambda x: -x[1])[:5]
        metrics["top_betweenness"] = [{"name": n, "value": round(v, 4)} for n, v in top_bc]
    except:
        metrics["top_betweenness"] = []

    # Community detection (Louvain via greedy modularity)
    try:
        communities = list(nx.community.greedy_modularity_communities(G))
        metrics["modularity"] = round(nx.community.modularity(G, communities), 4)
        community_map = {}
        for ci, comm in enumerate(communities):
            for node in comm:
                community_map[node] = ci
        metrics["communities"] = [
            {"id": ci, "members": list(members), "size": len(members)}
            for ci, members in enumerate(communities)
        ]
        metrics["community_count"] = len(communities)
        metrics["community_map"] = community_map
    except:
        metrics["modularity"] = 0
        metrics["communities"] = []
        metrics["community_count"] = 0
        metrics["community_map"] = {}

    return metrics


# ── Main Pipeline ───────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("Character Relationship Network Analysis Pipeline")
    print("=" * 60)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 1. Load all scripts
    print("\n[1/8] Loading scripts...")
    scripts = []
    for fpath in sorted(glob.glob(os.path.join(DATA_DIR, "**/*.json"), recursive=True)):
        with open(fpath, "r", encoding="utf-8") as f:
            scripts.append(json.load(f))
    print(f"  Loaded {len(scripts)} scripts")

    # 2. Classify scripts by type
    print("\n[2/8] Classifying scripts by type...")
    type_map = {}
    for s in scripts:
        stype = classify_script_type(
            s.get("plot", ""), s.get("characters", []),
            s.get("title", ""), s.get("alias", [])
        )
        type_map[s["script_id"]] = stype
        s["classified_type"] = stype

    type_counts = Counter(type_map.values())
    print(f"  Classification: {dict(type_counts)}")

    # 3. Extract networks per script
    print("\n[3/8] Building networks for each script...")
    all_networks = []
    type_networks = defaultdict(list)

    for s in scripts:
        sid = s["script_id"]
        title = s["title"]
        stype = s["classified_type"]
        char_names = [c["name"] for c in s.get("characters", [])]
        scenes = s.get("scenes", [])

        if len(char_names) < 2:
            continue

        # Build networks
        G_cooc = build_cooccurrence_network(scenes, char_names)
        DG_dial = build_dialogue_network(scenes, char_names)
        DG_power = build_power_network(scenes, char_names)

        # Compute metrics
        cooc_metrics = compute_graph_metrics(G_cooc, is_directed=False)
        dial_metrics = compute_graph_metrics(DG_dial, is_directed=True)
        power_metrics = compute_graph_metrics(DG_power, is_directed=True)

        # Build serializable graph data for frontend
        def graph_to_json(G, is_directed=False):
            nodes = []
            for node in G.nodes():
                degree = G.degree(node)
                nodes.append({
                    "id": node,
                    "degree": degree,
                    "label": node,
                })
            edges = []
            for u, v, data in G.edges(data=True):
                edges.append({
                    "source": u,
                    "target": v,
                    "weight": data.get("weight", 1),
                    "type": "directed" if is_directed else "undirected",
                })
            return {"nodes": nodes, "edges": edges}

        net_entry = {
            "script_id": sid,
            "title": title,
            "type": stype,
            "character_count": len(char_names),
            "characters": char_names,
            "cooccurrence": {
                **cooc_metrics,
                "graph": graph_to_json(G_cooc),
            },
            "dialogue": {
                **dial_metrics,
                "graph": graph_to_json(DG_dial, is_directed=True),
            },
            "power": {
                **power_metrics,
                "graph": graph_to_json(DG_power, is_directed=True),
            },
        }
        all_networks.append(net_entry)
        type_networks[stype].append(net_entry)

    print(f"  Built networks for {len(all_networks)} scripts")

    # 4. Aggregate metrics by play type
    print("\n[4/8] Computing type-level aggregate metrics...")
    type_aggregates = {}
    for stype, nets in type_networks.items():
        if len(nets) < 2:
            continue

        agg = {
            "count": len(nets),
            "cooccurrence": {},
            "dialogue": {},
            "power": {},
        }

        for layer in ["cooccurrence", "dialogue", "power"]:
            metrics_list = [n[layer] for n in nets]
            keys = ["density", "avg_clustering", "avg_path_length", "components",
                    "modularity", "community_count", "nodes", "edges", "centralization"]

            agg[layer] = {}
            for k in keys:
                vals = [m[k] for m in metrics_list if k in m and isinstance(m[k], (int, float))]
                if vals:
                    agg[layer][f"avg_{k}"] = round(sum(vals) / len(vals), 4)
                    agg[layer][f"std_{k}"] = round(
                        (sum((v - sum(vals)/len(vals))**2 for v in vals) / len(vals)) ** 0.5, 4
                    )

        # Top characters by PageRank across type
        all_pr = defaultdict(float)
        all_pr_count = defaultdict(int)
        for n in nets:
            for entry in n["cooccurrence"].get("top_pagerank", []):
                all_pr[entry["name"]] += entry["value"]
                all_pr_count[entry["name"]] += 1

        agg["top_characters"] = sorted(
            [{"name": n, "total_pr": round(v, 4), "appearances": all_pr_count[n]}
             for n, v in all_pr.items()],
            key=lambda x: -x["total_pr"]
        )[:10]

        type_aggregates[stype] = agg

    print(f"  Aggregated {len(type_aggregates)} play types")

    # 5. Build type comparison data
    print("\n[5/8] Building type comparison metrics...")
    comparison = {
        "types": list(type_aggregates.keys()),
        "metrics": {},
    }

    metric_labels = {
        "avg_density": "网络密度",
        "avg_clustering": "聚集系数",
        "avg_path_length": "平均路径长度",
        "avg_modularity": "模块度",
        "avg_community_count": "社区数量",
        "avg_centralization": "中心化程度",
        "avg_nodes": "平均角色数",
    }

    for key, label in metric_labels.items():
        comparison["metrics"][key] = {
            "label": label,
            "values": {},
        }
        for stype, agg in type_aggregates.items():
            # Check all layers, pick cooccurrence first
            for layer in ["cooccurrence", "dialogue", "power"]:
                if key in agg.get(layer, {}):
                    comparison["metrics"][key]["values"][stype] = agg[layer][key]
                    break

    # 6. Build character-level cross-script data for radar charts
    print("\n[6/8] Building character centrality database...")
    character_centrality = defaultdict(lambda: {"degree": [], "pagerank": [], "betweenness": [], "count": 0})
    for net in all_networks:
        for node_data in net["cooccurrence"]["graph"]["nodes"]:
            name = node_data["id"]
            character_centrality[name]["degree"].append(node_data["degree"])
            character_centrality[name]["count"] += 1
        for pr in net["cooccurrence"].get("top_pagerank", []):
            character_centrality[pr["name"]]["pagerank"].append(pr["value"])
        for bc in net["cooccurrence"].get("top_betweenness", []):
            character_centrality[bc["name"]]["betweenness"].append(bc["value"])

    char_summary = {}
    for name, data in character_centrality.items():
        if data["count"] >= 2:
            char_summary[name] = {
                "appearances": data["count"],
                "avg_degree": round(sum(data["degree"]) / len(data["degree"]), 2) if data["degree"] else 0,
                "avg_pagerank": round(sum(data["pagerank"]) / len(data["pagerank"]), 4) if data["pagerank"] else 0,
                "avg_betweenness": round(sum(data["betweenness"]) / len(data["betweenness"]), 4) if data["betweenness"] else 0,
            }

    # Top characters by each metric
    top_by_metric = {
        "top_degree": sorted(char_summary.items(), key=lambda x: -x[1]["avg_degree"])[:15],
        "top_pagerank": sorted(char_summary.items(), key=lambda x: -x[1]["avg_pagerank"])[:15],
        "top_betweenness": sorted(char_summary.items(), key=lambda x: -x[1]["avg_betweenness"])[:15],
    }

    # 7. Build network overview for each type (pick representative scripts)
    print("\n[7/8] Selecting representative scripts...")
    representatives = {}
    for stype, nets in type_networks.items():
        # Pick the script with highest density (most interesting network)
        if nets:
            best = max(nets, key=lambda n: n["cooccurrence"]["edges"])
            representatives[stype] = {
                "title": best["title"],
                "script_id": best["script_id"],
                "character_count": best["character_count"],
                "cooccurrence": {k: v for k, v in best["cooccurrence"].items() if k != "graph" and k != "community_map"},
                "dialogue": {k: v for k, v in best["dialogue"].items() if k != "graph" and k != "community_map"},
                "power": {k: v for k, v in best["power"].items() if k != "graph" and k != "community_map"},
                "graph": best["cooccurrence"]["graph"],
                "communities": best["cooccurrence"]["communities"],
            }

    # 8. Export all data
    print("\n[8/8] Exporting data...")

    # Full per-script network data
    with open(os.path.join(OUTPUT_DIR, "networks_all.json"), "w", encoding="utf-8") as f:
        json.dump(all_networks, f, ensure_ascii=False, indent=2)
    print(f"  [OK] networks_all.json ({len(all_networks)} scripts)")

    # Type aggregates
    with open(os.path.join(OUTPUT_DIR, "network_type_aggregates.json"), "w", encoding="utf-8") as f:
        json.dump(type_aggregates, f, ensure_ascii=False, indent=2)
    print(f"  [OK] network_type_aggregates.json")

    # Comparison data
    with open(os.path.join(OUTPUT_DIR, "network_comparison.json"), "w", encoding="utf-8") as f:
        json.dump(comparison, f, ensure_ascii=False, indent=2)
    print(f"  [OK] network_comparison.json")

    # Character centrality DB
    with open(os.path.join(OUTPUT_DIR, "character_centrality.json"), "w", encoding="utf-8") as f:
        json.dump({
            "characters": char_summary,
            "top_by_metric": {k: [{"name": n, "values": v} for n, v in vals] for k, vals in top_by_metric.items()},
        }, f, ensure_ascii=False, indent=2)
    print(f"  [OK] character_centrality.json ({len(char_summary)} characters)")

    # Representatives
    with open(os.path.join(OUTPUT_DIR, "network_representatives.json"), "w", encoding="utf-8") as f:
        json.dump(representatives, f, ensure_ascii=False, indent=2)
    print(f"  [OK] network_representatives.json ({len(representatives)} types)")

    # Summary
    with open(os.path.join(OUTPUT_DIR, "network_summary.json"), "w", encoding="utf-8") as f:
        json.dump({
            "total_scripts": len(all_networks),
            "type_distribution": dict(type_counts),
            "type_aggregates": {
                stype: {
                    "count": agg["count"],
                    "cooc_density": agg["cooccurrence"].get("avg_density", 0),
                    "cooc_clustering": agg["cooccurrence"].get("avg_clustering", 0),
                    "cooc_modularity": agg["cooccurrence"].get("avg_modularity", 0),
                    "dial_density": agg["dialogue"].get("avg_density", 0),
                    "power_density": agg["power"].get("avg_density", 0),
                }
                for stype, agg in type_aggregates.items()
            },
        }, f, ensure_ascii=False, indent=2)
    print(f"  [OK] network_summary.json")

    print(f"\nDone!")
    print(f"  Script types: {dict(type_counts)}")
    for stype, agg in type_aggregates.items():
        print(f"  {stype}: {agg['count']} scripts, "
              f"density={agg['cooccurrence'].get('avg_density', 'N/A'):.4f}, "
              f"modularity={agg['cooccurrence'].get('avg_modularity', 'N/A'):.4f}")


if __name__ == "__main__":
    main()
