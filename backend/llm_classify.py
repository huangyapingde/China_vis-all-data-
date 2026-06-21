"""
LLM-assisted Hangdang Classification
=====================================
Uses Ollama + Qwen2.5:7b to predict Peking Opera role types (hangdang)
for characters without explicit labels.

Two-tier approach:
1. Keyword-based heuristic classification (fast, for all characters)
2. LLM-based classification (for a representative sample to validate/improve)
"""

import json
import os
import glob
import re
import time
from collections import Counter, defaultdict
import subprocess

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "public", "data")

# ── Heuristic classification rules ─────────────────────────────────

# Character name patterns → hangdang hints
NAME_HINTS = {
    "生": [
        r"(将军|元帅|都督|丞相|老爷|大人|王|帝|皇|君|主|公|侯|伯|子|男|卿|臣|相|将|帅|令|官|员|郎|士|夫|生|才|贤|明)",
        r"(赵|钱|孙|李|周|吴|郑|王|冯|陈|褚|卫|蒋|沈|韩|杨|朱|秦|尤|许|何|吕|施|张|孔|曹|严|华|金|魏|陶|姜).{0,2}(不包含娘|妃|后|妾|姬|婢|奴|丫鬟|童)",
    ],
    "旦": [
        r"(娘|妃|后|妾|姬|女|婢|奴|丫鬟|童|小姐|公主|夫人|太太|婆|嫂|姐|妹|姑|姨|婶|姆)",
        r"(旦|青衣|花旦|武旦)",
    ],
    "净": [
        r"(霸|猛|刚|雄|豪|杰|莽|暴|烈|粗|凶|恶|煞|魔|鬼|怪|妖)",
        r"(净|花脸|黑头|铜锤)",
    ],
    "丑": [
        r"(丑|滑稽|诙谐|逗|闹|笑|趣|怪|呆|傻|蠢|笨|愣|憨|疯|癫|醉)",
        r"(店家|小二|伙计|门子|衙役|禁卒|刽子|解差|更夫|船夫|轿夫|马夫|脚夫|樵夫|渔夫|农夫|乞丐|花子|叫化)",
    ],
}

# Utterance content hints
CONTENT_HINTS = {
    "生": ["忠心", "报国", "仁义", "礼智", "道德", "朝纲", "社稷", "天下", "百姓", "苍生",
           "臣", "奏", "启奏", "陛下", "圣上", "微臣", "为臣", "吾皇"],
    "旦": ["妾身", "奴家", "奴婢", "哀家", "本宫", "臣妾", "女儿", "红妆", "绣房", "闺中"],
    "净": ["哇呀", "可恼", "气煞", "好贼", "奸贼", "匹夫", "狗头", "大胆", "反了", "拿命来"],
    "丑": ["嘿嘿", "哈哈", "好笑", "有趣", "怪哉", "稀奇", "不得了", "坏啦", "糟了"],
}


def call_ollama(prompt, model="qwen2.5:7b", timeout=90):
    """Call Ollama API via CLI."""
    try:
        result = subprocess.run(
            ["ollama", "run", model, prompt],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=timeout,
        )
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return "[TIMEOUT]"
    except Exception as e:
        return f"[ERROR: {e}]"


def heuristic_classify(name, text_sample):
    """Quick heuristic classification based on name and text patterns."""
    scores = defaultdict(int)

    for hd, patterns in NAME_HINTS.items():
        for pat in patterns:
            if re.search(pat, name):
                scores[hd] += 3

    for hd, keywords in CONTENT_HINTS.items():
        for kw in keywords:
            if kw in text_sample:
                scores[hd] += 1

    # Fallback based on common patterns
    if not scores:
        if any(kw in name for kw in ["兵", "卒", "军", "士", "丁", "夫", "差"]):
            scores["丑"] = 1
        elif any(kw in name for kw in ["官", "令", "将"]):
            scores["生"] = 1
        else:
            scores["生"] = 0.5  # default

    best = max(scores, key=scores.get)
    return best, dict(scores)


def build_llm_prompt(name, text_sample, utterance_count):
    """Build prompt for LLM classification."""
    prompt = f"""你是一位京剧行当专家。请根据以下角色信息判断其京剧行当（生/旦/净/丑及细分）。

角色名称：{name}
台词样本：{text_sample[:300]}
台词数量：{utterance_count}句

请判断该角色最可能的行当。行当分类标准：
- 生：男性正面角色，包括老生（年长稳重）、小生（年轻英俊）、武生（武艺高强）
- 旦：女性角色，包括青衣（端庄）、花旦（活泼）、武旦（女将）、老旦（老年女性）
- 净：花脸角色，性格刚烈、豪放或奸诈，多为武将或权臣
- 丑：喜剧角色，多为小人物、底层百姓、滑稽人物

请按以下格式回答（只回答行当，不要解释）：
行当：<生/旦/净/丑>
细分类别：<如老生、青衣、花脸等>"""

    return prompt


def classify_sample(characters, n=100):
    """Run LLM classification on a sample of unlabeled characters."""
    # Pick diverse samples
    samples = characters[:n]

    results = []
    print(f"Running LLM classification on {len(samples)} characters...")

    for i, ch in enumerate(samples):
        prompt = build_llm_prompt(
            ch["character_name"],
            ch.get("text_sample", ""),
            ch.get("utterance_count", 0),
        )

        response = call_ollama(prompt)

        # Parse response
        hd_main = None
        hd_sub = None
        for line in response.split("\n"):
            line = line.strip()
            if "行当" in line or "生" in line or "旦" in line or "净" in line or "丑" in line:
                # Extract hangdang
                if "生" in line:
                    hd_main = "生"
                elif "旦" in line:
                    hd_main = "旦"
                elif "净" in line:
                    hd_main = "净"
                elif "丑" in line:
                    hd_main = "丑"
                break

        # Fallback to heuristic if LLM fails
        if not hd_main:
            hd_main, _ = heuristic_classify(ch["character_name"], ch.get("text_sample", ""))

        results.append({
            **ch,
            "llm_hangdang": hd_main,
            "llm_raw_response": response[:100],
            "method": "llm",
        })

        if (i + 1) % 10 == 0:
            print(f"  Processed {i + 1}/{len(samples)}...")

        time.sleep(0.3)  # rate limit

    return results


def main():
    print("=" * 60)
    print("LLM-Assisted Hangdang Classification")
    print("=" * 60)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Load unlabeled characters
    with open(os.path.join(OUTPUT_DIR, "unlabeled_chars.json"), "r", encoding="utf-8") as f:
        unlabeled = json.load(f)

    print(f"\nTotal unlabeled characters: {len(unlabeled)}")

    # 1. Heuristic classification for ALL unlabeled characters
    print("\n[1] Running heuristic classification on all unlabeled characters...")
    heuristic_results = []
    for ch in unlabeled:
        hd, scores = heuristic_classify(ch["character_name"], ch.get("text_sample", ""))
        heuristic_results.append({
            **ch,
            "predicted_hangdang": hd,
            "scores": scores,
            "method": "heuristic",
        })

    hd_dist = Counter(r["predicted_hangdang"] for r in heuristic_results)
    print(f"  Heuristic prediction distribution: {dict(hd_dist)}")

    # 2. LLM classification on a sample (around 50 chars)
    print("\n[2] Running LLM classification on a sample...")
    # Pick diverse characters (different scripts)
    seen_scripts = set()
    diverse_samples = []
    for ch in unlabeled:
        if ch["script_id"] not in seen_scripts and len(diverse_samples) < 50:
            diverse_samples.append(ch)
            seen_scripts.add(ch["script_id"])

    llm_results = classify_sample(diverse_samples, n=len(diverse_samples))
    llm_dist = Counter(r["llm_hangdang"] for r in llm_results)
    print(f"  LLM prediction distribution: {dict(llm_dist)}")

    # 3. Merge: use LLM results where available, heuristic for the rest
    print("\n[3] Merging predictions...")
    llm_map = {}
    for r in llm_results:
        key = f"{r['script_id']}:{r['character_name']}"
        llm_map[key] = r["llm_hangdang"]

    final_predictions = []
    for r in heuristic_results:
        key = f"{r['script_id']}:{r['character_name']}"
        if key in llm_map:
            r["predicted_hangdang"] = llm_map[key]
            r["method"] = "llm"
        final_predictions.append(r)

    final_dist = Counter(r["predicted_hangdang"] for r in final_predictions)
    print(f"  Final distribution: {dict(final_dist)}")

    # 4. Compare LLM vs Heuristic for the sample
    print("\n[4] Comparing LLM vs Heuristic...")
    matches = 0
    mismatches = []
    for r in llm_results:
        key = f"{r['script_id']}:{r['character_name']}"
        heuristic_hd = None
        for hr in heuristic_results:
            if f"{hr['script_id']}:{hr['character_name']}" == key:
                heuristic_hd = hr["predicted_hangdang"]
                break
        if heuristic_hd == r["llm_hangdang"]:
            matches += 1
        else:
            mismatches.append({
                "name": r["character_name"],
                "heuristic": heuristic_hd,
                "llm": r["llm_hangdang"],
                "text": r.get("text_sample", "")[:100],
            })

    agreement = matches / len(llm_results) * 100 if llm_results else 0
    print(f"  LLM-Heuristic agreement: {agreement:.1f}%")
    print(f"  Mismatches: {len(mismatches)}")

    # 5. Export results
    print("\n[5] Exporting...")

    with open(os.path.join(OUTPUT_DIR, "llm_predictions.json"), "w", encoding="utf-8") as f:
        json.dump({
            "predictions": final_predictions,
            "llm_sample": llm_results,
            "agreement_rate": agreement,
            "mismatches": mismatches,
            "distribution": dict(final_dist),
        }, f, ensure_ascii=False, indent=2)
    print(f"  [OK] llm_predictions.json ({len(final_predictions)} predictions)")

    # Also update the character_data.json with predicted hangdangs
    print("\n[6] Updating character data with predictions...")
    with open(os.path.join(OUTPUT_DIR, "character_data.json"), "r", encoding="utf-8") as f:
        char_data = json.load(f)

    # Create lookup for predictions
    pred_map = {}
    for r in final_predictions:
        key = f"{r['script_id']}:{r['character_name']}"
        pred_map[key] = r

    # Update character data
    updated_count = 0
    for ch in char_data:
        if ch["hangdang_main"] is None:
            key = f"{ch['script_id']}:{ch['character_name']}"
            if key in pred_map:
                ch["hangdang_main"] = pred_map[key]["predicted_hangdang"]
                ch["hangdang_predicted"] = True
                ch["prediction_method"] = pred_map[key]["method"]
                updated_count += 1

    with open(os.path.join(OUTPUT_DIR, "character_data.json"), "w", encoding="utf-8") as f:
        json.dump(char_data, f, ensure_ascii=False, indent=2)
    print(f"  [OK] Updated {updated_count} character hangdangs with predictions")

    # Recompute matrix with predictions
    print("\n[7] Recomputing role-hangdang matrix with predictions...")
    from process_data import compute_role_hangdang_matrix, compute_era_analysis, compute_summary_stats, build_sankey_data

    matrix_data = compute_role_hangdang_matrix(char_data)

    # Load scripts for era analysis
    scripts = []
    for fpath in sorted(glob.glob(os.path.join(DATA_DIR, "**/*.json"), recursive=True)):
        with open(fpath, "r", encoding="utf-8") as f:
            scripts.append(json.load(f))

    era_data = compute_era_analysis(char_data, scripts)
    summary = compute_summary_stats(char_data)
    sankey = build_sankey_data(char_data)

    with open(os.path.join(OUTPUT_DIR, "matrix_data_predicted.json"), "w", encoding="utf-8") as f:
        json.dump(matrix_data, f, ensure_ascii=False, indent=2)

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
    with open(os.path.join(OUTPUT_DIR, "overall_predicted.json"), "w", encoding="utf-8") as f:
        json.dump(overall, f, ensure_ascii=False, indent=2)

    print(f"\nDone! Processed {len(unlabeled)} characters.")
    print(f"  Heuristic only: {len([r for r in final_predictions if r['method'] == 'heuristic'])}")
    print(f"  LLM verified: {len([r for r in final_predictions if r['method'] == 'llm'])}")
    print(f"  LLM-Heuristic agreement: {agreement:.1f}%")


if __name__ == "__main__":
    main()
