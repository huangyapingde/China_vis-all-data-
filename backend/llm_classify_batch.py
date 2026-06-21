"""
Batch LLM Hangdang Classification
==================================
Classify multiple characters in one Ollama call for speed.
"""

import json
import os
import glob
import subprocess
from collections import Counter

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "public", "data")
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def call_ollama(prompt, model="qwen2.5:7b", timeout=120):
    try:
        result = subprocess.run(
            ["ollama", "run", model, prompt],
            capture_output=True, text=True, encoding="utf-8", timeout=timeout,
        )
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return "[TIMEOUT]"
    except Exception as e:
        return f"[ERROR: {e}]"


def heuristic_classify(name, text_sample):
    """Quick heuristic classification."""
    scores = {"生": 0, "旦": 0, "净": 0, "丑": 0}

    # Name-based
    if any(w in name for w in ["将军", "元帅", "丞相", "老爷", "大人", "王", "帝", "皇", "主", "公", "卿", "臣", "相", "令", "官"]):
        scores["生"] += 3
    if any(w in name for w in ["娘", "妃", "后", "妾", "姬", "女", "婢", "奴", "丫鬟", "童", "小姐", "公主", "夫人", "太太", "婆", "嫂", "姐", "妹"]):
        scores["旦"] += 3
    if any(w in name for w in ["霸", "猛", "刚", "雄", "豪", "莽", "暴", "烈", "粗", "凶", "恶", "煞", "魔", "鬼", "怪"]):
        scores["净"] += 2
    if any(w in name for w in ["丑", "滑稽", "呆", "傻", "蠢", "笨", "愣", "憨", "疯", "癫", "醉", "小二", "伙计", "门子", "衙役"]):
        scores["丑"] += 3

    # Content-based
    text = text_sample[:300]
    if any(w in text for w in ["臣", "奏", "陛下", "圣上", "微臣", "吾皇", "忠心", "社稷"]):
        scores["生"] += 1
    if any(w in text for w in ["妾身", "奴家", "奴婢", "哀家", "臣妾", "女儿"]):
        scores["旦"] += 2
    if any(w in text for w in ["哇呀", "可恼", "气煞", "奸贼", "匹夫", "狗头", "大胆"]):
        scores["净"] += 2
    if any(w in text for w in ["嘿嘿", "哈哈", "好笑", "有趣", "怪哉"]):
        scores["丑"] += 2

    # Default for military/servant characters
    if all(v == 0 for v in scores.values()):
        if any(w in name for w in ["兵", "卒", "军", "士", "丁", "夫", "差", "役", "禁"]):
            scores["丑"] = 1
        else:
            scores["生"] = 0.5

    best = max(scores, key=scores.get)
    return best


def main():
    print("=" * 60)
    print("Batch LLM Hangdang Classification")
    print("=" * 60)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Load unlabeled characters
    with open(os.path.join(OUTPUT_DIR, "unlabeled_chars.json"), "r", encoding="utf-8") as f:
        unlabeled = json.load(f)

    print(f"Total unlabeled characters: {len(unlabeled)}")

    # Step 1: Heuristic classification for ALL
    print("\n[1] Heuristic classification (all characters)...")
    for ch in unlabeled:
        ch["predicted_hangdang"] = heuristic_classify(
            ch["character_name"],
            ch.get("text_sample", ""),
        )
        ch["method"] = "heuristic"

    hd_dist = Counter(ch["predicted_hangdang"] for ch in unlabeled)
    print(f"  Distribution: {dict(hd_dist)}")

    # Step 2: LLM batch classification for top N hard cases
    # Pick characters with lowest heuristic confidence (ambiguous)
    print("\n[2] LLM batch classification (15 diverse characters)...")

    # Pick diverse sample: different scripts, different heuristic predictions
    seen_scripts = set()
    samples = []
    for ch in unlabeled:
        if ch["script_id"] not in seen_scripts and len(samples) < 15:
            samples.append(ch)
            seen_scripts.add(ch["script_id"])

    # Build batch prompt
    char_list = []
    for i, ch in enumerate(samples):
        char_list.append(
            f"{i+1}. 角色: {ch['character_name']}\n"
            f"   台词数: {ch.get('utterance_count', 0)}\n"
            f"   台词片段: {ch.get('text_sample', '')[:150]}"
        )

    batch_prompt = f"""你是京剧行当专家。请为以下角色判断最可能的京剧行当（生/旦/净/丑）。

行当标准：
- 生: 男性正面角色（含老生/小生/武生）
- 旦: 女性角色（含青衣/花旦/武旦/老旦）
- 净: 花脸角色，性格刚烈豪放或奸诈
- 丑: 喜剧角色，小人物、底层百姓

角色列表：
{chr(10).join(char_list)}

请严格按以下格式返回结果（每行一个角色）：
序号. 行当 - 简短理由"""

    print("  Calling Ollama...")
    response = call_ollama(batch_prompt, timeout=180)

    # Parse batch response
    llm_results = {}
    if response and response != "[TIMEOUT]":
        for line in response.split("\n"):
            line = line.strip()
            if not line:
                continue
            # Extract: "1. 生 - reason"
            for hd in ["生", "旦", "净", "丑"]:
                if hd in line and any(line.startswith(str(i)) for i in range(1, 16)):
                    try:
                        idx = int(line.split(".")[0].strip()) - 1
                        if 0 <= idx < len(samples):
                            llm_results[idx] = hd
                    except (ValueError, IndexError):
                        pass
                    break

    print(f"  LLM classified {len(llm_results)}/{len(samples)} characters")
    for idx, hd in llm_results.items():
        print(f"    {samples[idx]['character_name']}: {hd}")

    # Step 3: Update predictions with LLM results
    print("\n[3] Merging predictions...")
    llm_map = {}
    for idx, hd in llm_results.items():
        key = f"{samples[idx]['script_id']}:{samples[idx]['character_name']}"
        llm_map[key] = hd

    llm_updated = 0
    for ch in unlabeled:
        key = f"{ch['script_id']}:{ch['character_name']}"
        if key in llm_map:
            ch["predicted_hangdang"] = llm_map[key]
            ch["method"] = "llm"
            llm_updated += 1

    final_dist = Counter(ch["predicted_hangdang"] for ch in unlabeled)
    print(f"  Final distribution: {dict(final_dist)}")
    print(f"  LLM updated: {llm_updated}")

    # Step 4: Export
    print("\n[4] Exporting results...")
    with open(os.path.join(OUTPUT_DIR, "llm_predictions.json"), "w", encoding="utf-8") as f:
        json.dump({
            "predictions": unlabeled,
            "batch_response": response if response else "",
            "llm_results": {samples[idx]['character_name']: hd for idx, hd in llm_results.items()} if llm_results else {},
            "distribution": dict(final_dist),
        }, f, ensure_ascii=False, indent=2)
    print(f"  [OK] llm_predictions.json ({len(unlabeled)} predictions)")

    # Update character_data.json
    print("\n[5] Updating character data with predictions...")
    with open(os.path.join(OUTPUT_DIR, "character_data.json"), "r", encoding="utf-8") as f:
        char_data = json.load(f)

    pred_map = {}
    for ch in unlabeled:
        key = f"{ch['script_id']}:{ch['character_name']}"
        pred_map[key] = ch

    updated = 0
    for ch in char_data:
        if ch["hangdang_main"] is None:
            key = f"{ch['script_id']}:{ch['character_name']}"
            if key in pred_map:
                ch["hangdang_main"] = pred_map[key]["predicted_hangdang"]
                ch["hangdang_predicted"] = True
                ch["prediction_method"] = pred_map[key]["method"]
                updated += 1

    with open(os.path.join(OUTPUT_DIR, "character_data.json"), "w", encoding="utf-8") as f:
        json.dump(char_data, f, ensure_ascii=False, indent=2)
    print(f"  [OK] Updated {updated} characters")

    # Recompute matrix
    print("\n[6] Recomputing matrix with predictions...")
    from process_data import compute_role_hangdang_matrix, compute_era_analysis, compute_summary_stats, build_sankey_data

    matrix_data = compute_role_hangdang_matrix(char_data)
    scripts = []
    for fpath in sorted(glob.glob(os.path.join(DATA_DIR, "**/*.json"), recursive=True)):
        with open(fpath, "r", encoding="utf-8") as f:
            scripts.append(json.load(f))
    era_data = compute_era_analysis(char_data, scripts)
    summary = compute_summary_stats(char_data)
    sankey = build_sankey_data(char_data)

    with open(os.path.join(OUTPUT_DIR, "matrix_data_predicted.json"), "w", encoding="utf-8") as f:
        json.dump(matrix_data, f, ensure_ascii=False, indent=2)
    with open(os.path.join(OUTPUT_DIR, "sankey_data_predicted.json"), "w", encoding="utf-8") as f:
        json.dump(sankey, f, ensure_ascii=False, indent=2)

    print(f"\nDone!")
    print(f"  Heuristic: {len([ch for ch in unlabeled if ch['method'] == 'heuristic'])}")
    print(f"  LLM: {len([ch for ch in unlabeled if ch['method'] == 'llm'])}")
    print(f"  Final distribution: {dict(final_dist)}")


if __name__ == "__main__":
    main()
