"""
Peking Opera Role Analysis Pipeline
=====================================
1. Parse all JSON scripts → character table
2. Extract behavioral/sentiment/power features
3. Compute role-hangdang correspondence (PMI, purity, entropy)
4. LLM-assisted hangdang prediction for unlabeled characters
5. Export processed data for React dashboard
"""

import json
import os
import glob
import re
from collections import Counter, defaultdict
from math import log2
import warnings

warnings.filterwarnings("ignore")

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "public", "data")


# ── Keyword dictionaries ──────────────────────────────────────────────

COMMAND_WORDS = {"传", "令", "斩", "杀", "绑", "拿下", "推出", "听令", "遵命", "得令",
                 "吩咐", "差遣", "命你", "速去", "快去", "不许", "违令", "升帐", "升堂"}

BATTLE_WORDS = {"杀", "攻", "退兵", "冲锋", "迎敌", "大战", "对阵", "会阵", "交锋",
                "枪", "刀", "箭", "戟", "埋伏", "追杀", "攻城", "守城"}

EMOTION_WORDS = {"叹", "怒", "笑", "哭", "恨", "悲", "喜", "惊", "慌", "恼",
                 "哀", "愁", "悔", "愧", "羞", "怕", "恐"}

ROLE_KEYWORDS = {
    "将军": ["将军", "元帅", "都督", "先锋", "大将", "老将", "上将军"],
    "谋士": ["军师", "丞相", "参谋", "谋士", "山人", "先生"],
    "帝王": ["朕", "孤", "寡人", "皇帝", "圣上", "陛下", "万岁", "主公", "大王", "皇"],
    "后妃": ["皇后", "贵妃", "娘娘", "妃", "后", "嫔"],
    "官员": ["大人", "老爷", "官", "太守", "县令", "刺史", "宰相", "尚书", "侍郎"],
    "士兵": ["卒", "兵", "将官", "旗牌", "报子", "探子", "军士", "小军"],
    "平民": ["百姓", "老丈", "老军", "老汉", "婆子", "民女", "农夫", "渔夫"],
    "仆役": ["童儿", "丫鬟", "院子", "家院", "门子", "下人", "奴", "婢"],
    "神仙": ["仙", "神", "佛", "菩萨", "鬼", "妖", "怪", "龙王", "星君", "天王"],
    "侠客": ["英雄", "好汉", "壮士", "义士", "豪杰", "侠"],
    "书生": ["秀才", "举人", "才子", "书生", "学士", "学子"],
    "武将": ["武将", "猛将", "战将", "勇将", "虎将"],
    "奸臣": ["奸臣", "权臣", "太师", "国舅", "国丈"],
    "女将": ["女将", "女兵", "女英雄"],
    "僧道": ["和尚", "道士", "法师", "长老", "禅师", "真人", "仙长"],
}

HANGDANG_SUBCATEGORIES = {
    "生": ["老生", "小生", "武生", "红生", "娃娃生"],
    "旦": ["青衣", "花旦", "武旦", "老旦", "刀马旦", "彩旦", "闺门旦"],
    "净": ["铜锤花脸", "架子花脸", "武净"],
    "丑": ["文丑", "武丑", "丑旦"],
}

# Normalize hangdang to 4 main categories
HANGDANG_MAP = {}
for main, subs in HANGDANG_SUBCATEGORIES.items():
    for s in subs:
        HANGDANG_MAP[s] = main
    HANGDANG_MAP[main] = main


def load_all_scripts():
    scripts = []
    for fpath in sorted(glob.glob(os.path.join(DATA_DIR, "**/*.json"), recursive=True)):
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)
        scripts.append(data)
    return scripts


def normalize_hangdang(hd):
    """Normalize hangdang to 4 main categories: 生/旦/净/丑"""
    if not hd:
        return None
    # Exact match
    if hd in HANGDANG_MAP:
        return HANGDANG_MAP[hd]
    # Try substring match for compound labels like "净（铜锤花脸）"
    for key, val in HANGDANG_MAP.items():
        if key in hd:
            return val
    # Fallback: first char heuristic
    for cat in ["生", "旦", "净", "丑", "末"]:
        if cat in hd:
            if cat == "末":
                return "生"
            return cat
    return None


def classify_role_type(name, text_corpus):
    """Classify character role type based on name and text keywords."""
    matched = []
    for role_type, keywords in ROLE_KEYWORDS.items():
        score = 0
        for kw in keywords:
            if kw in name:
                score += 3
            if kw in text_corpus:
                score += 1
        if score > 0:
            matched.append((role_type, score))
    matched.sort(key=lambda x: -x[1])
    if matched:
        return matched[0][0]
    return "其他"


def extract_character_features(scripts):
    """Build character-level feature table from all scripts."""
    character_data = []  # list of dicts
    unlabeled_chars = []  # characters appearing in utterances but not in character list

    for script in scripts:
        sid = script["script_id"]
        title = script["title"]
        source = script.get("source", "")
        plot = script.get("plot", "")

        # Map character names to their hangdang
        char_hd = {}
        for c in script.get("characters", []):
            char_hd[c["name"]] = c.get("hangdang")

        # Collect all utterances per character
        char_texts = defaultdict(list)
        char_lines = defaultdict(list)  # raw utterances
        char_types = defaultdict(Counter)
        char_scenes = defaultdict(set)

        total_utterances = 0
        for scene in script.get("scenes", []):
            sid_scene = scene.get("scene_id", 0)
            for utt in scene.get("utterances", []):
                total_utterances += 1
                cname = utt.get("character")
                if cname is None:
                    continue
                text = utt.get("text", "")
                utype = utt.get("type", "")

                char_texts[cname].append(text)
                char_lines[cname].append(text)
                char_types[cname][utype] += 1
                char_scenes[cname].add(sid_scene)

        # Build interaction graph
        interactions = defaultdict(set)
        for scene in script.get("scenes", []):
            scene_chars = set()
            for utt in scene.get("utterances", []):
                cname = utt.get("character")
                if cname:
                    scene_chars.add(cname)
            for c in scene_chars:
                interactions[c].update(scene_chars - {c})

        # Build features for each character
        for cname in char_texts:
            all_text = "".join(char_texts[cname])
            utterance_count = len(char_lines[cname])
            avg_text_len = len(all_text) / utterance_count if utterance_count > 0 else 0
            total_text_len = len(all_text)
            scene_count = len(char_scenes[cname])
            total_scenes = len(script.get("scenes", []))

            # Dominance: consecutive utterances
            lines = char_lines[cname]
            consecutive_count = 0
            max_consecutive = 0
            current_streak = 0
            # We can't easily compute consecutive without utterance-level ordering
            # Instead, count total as fraction of script
            utt_fraction = utterance_count / total_utterances if total_utterances > 0 else 0

            # Power/behavior keywords
            command_count = sum(all_text.count(w) for w in COMMAND_WORDS)
            battle_count = sum(all_text.count(w) for w in BATTLE_WORDS)
            emotion_count = sum(all_text.count(w) for w in EMOTION_WORDS)

            # Role type
            role_type = classify_role_type(cname, all_text)

            # Hangdang
            hd = char_hd.get(cname)
            hd_normalized = normalize_hangdang(hd)

            # Degree (interaction count)
            degree = len(interactions.get(cname, set()))

            # Is main character (appears in many scenes, high utterance count)
            is_main = scene_count >= total_scenes * 0.3 and utt_fraction > 0.05

            character_data.append({
                "script_id": sid,
                "title": title,
                "source": source,
                "character_name": cname,
                "hangdang": hd,
                "hangdang_main": hd_normalized,
                "role_type": role_type,
                "utterance_count": utterance_count,
                "total_text_len": total_text_len,
                "avg_text_len": round(avg_text_len, 2),
                "scene_count": scene_count,
                "total_scenes": total_scenes,
                "utterance_fraction": round(utt_fraction, 4),
                "degree": degree,
                "is_main_character": is_main,
                "command_score": command_count,
                "battle_score": battle_count,
                "emotion_score": emotion_count,
                "text_sample": all_text[:200],
            })

        # Find unlabeled characters (appear in utterances but not in character list)
        for cname in char_texts:
            if cname not in char_hd:
                unlabeled_chars.append({
                    "script_id": sid,
                    "title": title,
                    "character_name": cname,
                    "text_sample": "".join(char_texts[cname])[:300],
                    "utterance_count": len(char_lines[cname]),
                })

    return character_data, unlabeled_chars


def compute_role_hangdang_matrix(character_data):
    """Build role-hangdang co-occurrence matrix and compute PMI, purity, entropy."""
    # Count co-occurrences
    cooc = defaultdict(lambda: defaultdict(int))
    role_totals = defaultdict(int)
    hd_totals = defaultdict(int)
    total = 0

    for ch in character_data:
        rt = ch["role_type"]
        hd = ch["hangdang_main"]
        if hd is None:
            continue
        cooc[rt][hd] += 1
        role_totals[rt] += 1
        hd_totals[hd] += 1
        total += 1

    # PMI matrix
    pmi_matrix = {}
    for rt in cooc:
        pmi_matrix[rt] = {}
        for hd in cooc[rt]:
            p_rt_hd = cooc[rt][hd] / total
            p_rt = role_totals[rt] / total
            p_hd = hd_totals[hd] / total
            pmi = log2(p_rt_hd / (p_rt * p_hd)) if p_rt_hd > 0 else 0
            pmi_matrix[rt][hd] = round(pmi, 3)

    # Purity: for each hangdang, what fraction is the dominant role type?
    purity = {}
    for hd in hd_totals:
        max_count = max(cooc[rt][hd] for rt in cooc)
        purity[hd] = round(max_count / hd_totals[hd], 3)

    # Entropy of role distribution per hangdang
    entropy = {}
    for hd in hd_totals:
        ent = 0
        for rt in cooc:
            p = cooc[rt][hd] / hd_totals[hd] if hd_totals[hd] > 0 else 0
            if p > 0:
                ent -= p * log2(p)
        entropy[hd] = round(ent, 3)

    return {
        "matrix": {rt: dict(hds) for rt, hds in cooc.items()},
        "pmi": pmi_matrix,
        "purity": purity,
        "entropy": entropy,
        "role_totals": dict(role_totals),
        "hd_totals": dict(hd_totals),
    }


def compute_era_analysis(character_data, scripts):
    """Analyze hangdang distribution changes across script volumes/groups.

    Script IDs format: XXYYYZZ where XX=series, YYY=volume, ZZ=script
    Group by volume (first 5 chars of script_id) as proxy for period/compilation.
    """
    # Group by volume (first 5 chars of script_id)
    volume_groups = defaultdict(list)
    for ch in character_data:
        sid = ch.get("script_id", "")
        volume_key = sid[:5] if len(sid) >= 5 else sid
        if ch["hangdang_main"]:
            volume_groups[volume_key].append(ch["hangdang_main"])

    volume_data = {}
    for vol, hds in sorted(volume_groups.items()):
        cnt = Counter(hds)
        total = sum(cnt.values())
        volume_data[f"卷{vol}"] = {
            "total": total,
            "distribution": {k: round(v / total, 4) for k, v in cnt.items()},
            "counts": dict(cnt),
            "volume_id": vol,
        }

    # Time series data sorted by volume
    time_series = []
    for vol_name, vd in sorted(volume_data.items(), key=lambda x: x[1]["volume_id"]):
        time_series.append({
            "era": vol_name,
            **vd["distribution"],
            "total": vd["total"],
        })

    return {
        "era_analysis": volume_data,
        "time_series": time_series,
    }


def compute_summary_stats(character_data):
    """Compute overall summary statistics."""
    hd_counts = Counter(ch["hangdang"] for ch in character_data if ch["hangdang"])
    hd_main_counts = Counter(ch["hangdang_main"] for ch in character_data if ch["hangdang_main"])
    role_counts = Counter(ch["role_type"] for ch in character_data)

    # Hangdang per script
    script_hd = defaultdict(lambda: defaultdict(int))
    for ch in character_data:
        if ch["hangdang_main"]:
            script_hd[ch["title"]][ch["hangdang_main"]] += 1

    # Characters missing hangdang
    missing_hd = sum(1 for ch in character_data if ch["hangdang"] is None)

    return {
        "total_characters": len(character_data),
        "hangdang_distribution": dict(hd_counts.most_common()),
        "hangdang_main_distribution": dict(hd_main_counts.most_common()),
        "role_type_distribution": dict(role_counts.most_common()),
        "missing_hangdang_count": missing_hd,
        "unique_scripts": len(set(ch["script_id"] for ch in character_data)),
    }


def build_sankey_data(character_data):
    """Build Sankey diagram data: Role Type → Hangdang flow."""
    links = defaultdict(lambda: defaultdict(int))
    for ch in character_data:
        rt = ch["role_type"]
        hd = ch["hangdang_main"]
        if hd:
            links[rt][hd] += 1

    all_roles = sorted(set(links.keys()))
    all_hds = sorted(set(hd for rt_links in links.values() for hd in rt_links))

    nodes = [{"name": r} for r in all_roles] + [{"name": h} for h in all_hds]
    node_idx = {n["name"]: i for i, n in enumerate(nodes)}

    edges = []
    for rt in all_roles:
        for hd in all_hds:
            if links[rt][hd] > 0:
                edges.append({
                    "source": node_idx[rt],
                    "target": node_idx[hd],
                    "value": links[rt][hd],
                })

    return {"nodes": nodes, "links": edges}


def main():
    print("=" * 60)
    print("Peking Opera Role Analysis Pipeline")
    print("=" * 60)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 1. Load all scripts
    print("\n[1/6] Loading scripts...")
    scripts = load_all_scripts()
    print(f"  Loaded {len(scripts)} scripts.")

    # 2. Extract character features
    print("\n[2/6] Extracting character features...")
    character_data, unlabeled_chars = extract_character_features(scripts)
    print(f"  Extracted {len(character_data)} character entries.")
    print(f"  Found {len(unlabeled_chars)} unlabeled characters.")

    # 3. Compute role-hangdang matrix
    print("\n[3/6] Computing role-hangdang correspondence matrix...")
    matrix_data = compute_role_hangdang_matrix(character_data)
    print(f"  Role types: {len(matrix_data['role_totals'])}")
    print(f"  Hangdang categories: {len(matrix_data['hd_totals'])}")

    # 4. Compute era analysis
    print("\n[4/6] Computing era/period analysis...")
    era_data = compute_era_analysis(character_data, scripts)
    print(f"  Eras: {list(era_data['era_analysis'].keys())}")

    # 5. Summary statistics
    print("\n[5/6] Computing summary statistics...")
    summary = compute_summary_stats(character_data)

    # 6. Build Sankey data
    print("\n[6/6] Building visualization data...")
    sankey = build_sankey_data(character_data)

    # ── Export all processed data ──
    print("\n" + "=" * 60)
    print("Exporting data...")

    # Main character data (for scatter plots, tables)
    with open(os.path.join(OUTPUT_DIR, "character_data.json"), "w", encoding="utf-8") as f:
        json.dump(character_data, f, ensure_ascii=False, indent=2)
    print(f"  [OK] character_data.json ({len(character_data)} entries)")

    # Unlabeled characters (for LLM prediction)
    with open(os.path.join(OUTPUT_DIR, "unlabeled_chars.json"), "w", encoding="utf-8") as f:
        json.dump(unlabeled_chars, f, ensure_ascii=False, indent=2)
    print(f"  [OK] unlabeled_chars.json ({len(unlabeled_chars)} entries)")

    # Matrix data (for heatmap, PMI table)
    with open(os.path.join(OUTPUT_DIR, "matrix_data.json"), "w", encoding="utf-8") as f:
        json.dump(matrix_data, f, ensure_ascii=False, indent=2)
    print(f"  [OK] matrix_data.json")

    # Era analysis
    with open(os.path.join(OUTPUT_DIR, "era_data.json"), "w", encoding="utf-8") as f:
        json.dump(era_data, f, ensure_ascii=False, indent=2)
    print(f"  [OK] era_data.json")

    # Summary stats
    with open(os.path.join(OUTPUT_DIR, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"  [OK] summary.json")

    # Sankey data
    with open(os.path.join(OUTPUT_DIR, "sankey_data.json"), "w", encoding="utf-8") as f:
        json.dump(sankey, f, ensure_ascii=False, indent=2)
    print(f"  [OK] sankey_data.json")

    # Overall stats
    overall = {
        **summary,
        "matrix_summary": {
            "purity": matrix_data["purity"],
            "entropy": matrix_data["entropy"],
        },
        "era_summary": {
            era: {"total": ed["total"], "distribution": ed["distribution"]}
            for era, ed in era_data["era_analysis"].items()
        },
    }
    with open(os.path.join(OUTPUT_DIR, "overall.json"), "w", encoding="utf-8") as f:
        json.dump(overall, f, ensure_ascii=False, indent=2)
    print(f"  [OK] overall.json")

    print(f"\nProcessing complete! Data exported to: {OUTPUT_DIR}")
    print(f"\nSummary:")
    print(f"  - Total characters: {summary['total_characters']}")
    print(f"  - Unique scripts: {summary['unique_scripts']}")
    print(f"  - Hangdang distribution: {summary['hangdang_main_distribution']}")
    print(f"  - Missing hangdang: {summary['missing_hangdang_count']}")
    print(f"  - Role types: {summary['role_type_distribution']}")


if __name__ == "__main__":
    main()
