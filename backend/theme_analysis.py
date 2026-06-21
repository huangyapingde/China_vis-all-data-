"""
Theme/Topic Modeling & Analysis Pipeline for Peking Opera
===========================================================
1. Extract & clean all utterances
2. Theme scoring via keyword dictionaries + TF-IDF
3. LLM-assisted theme labeling (Ollama Qwen2.5)
4. Script-level topic distribution
5. Topic co-occurrence (PMI) & association rules
6. Scene-level topic evolution
7. Cross-play-type comparison
"""

import json
import os
import glob
import re
import subprocess
import warnings
from collections import Counter, defaultdict
from math import log2

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA

warnings.filterwarnings("ignore")

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "public", "data")

# ── Theme Categories & Keyword Dictionaries ──────────────────────────
# 15 Peking Opera themes with rich keyword sets

THEME_DICT = {
    "战争军事": {
        "keywords": ["战", "杀", "攻", "兵", "军", "将", "马", "刀", "枪", "箭", "阵", "敌",
                     "征", "伐", "冲锋", "埋伏", "攻城", "守城", "大败", "取胜", "得胜",
                     "退兵", "进兵", "会阵", "交锋", "厮杀", "血战", "鼓角", "旌旗",
                     "甲胄", "兵器", "粮草", "营寨", "起兵", "发兵", "收兵", "回营"],
        "weight": 1.0,
    },
    "智谋策略": {
        "keywords": ["计", "谋", "策", "算", "料", "机", "巧", "妙", "智", "慧",
                     "安排", "定计", "用计", "设伏", "空城", "火攻", "水淹",
                     "反间", "离间", "诈降", "诱敌", "声东击西", "调虎离山",
                     "山人", "妙计", "神机妙算", "运筹", "帷幄", "锦囊"],
        "weight": 1.0,
    },
    "忠诚报国": {
        "keywords": ["忠", "报国", "忠心", "赤胆", "鞠躬", "尽瘁", "保国", "卫国",
                     "社稷", "江山", "汉室", "兴汉", "扶汉", "保主", "护主",
                     "为主", "尽忠", "效忠", "精忠", "肝胆", "丹心", "碧血",
                     "以身许国", "马革裹尸", "死而后已", "忠烈", "忠义"],
        "weight": 0.9,
    },
    "家庭伦理": {
        "keywords": ["母", "父", "子", "女", "妻", "夫", "儿", "媳", "兄", "弟", "姐", "妹",
                     "家", "堂", "闺", "房", "孝", "养", "奉", "敬", "顺",
                     "教子", "训子", "认亲", "团圆", "离散", "重逢", "寻亲",
                     "骨肉", "血脉", "宗族", "门庭", "祖", "孙", "婆", "媳"],
        "weight": 0.9,
    },
    "爱情情感": {
        "keywords": ["爱", "情", "恋", "思", "慕", "念", "相思", "倾心", "钟情",
                     "婚", "嫁", "娶", "姻缘", "良缘", "佳偶", "鸳鸯", "连理",
                     "花烛", "洞房", "红线", "月老", "缘", "妾", "郎", "娘子",
                     "恩爱", "痴情", "钟情", "海誓山盟", "比翼", "双飞"],
        "weight": 0.9,
    },
    "正义审判": {
        "keywords": ["审", "判", "案", "冤", "状", "告", "诉", "官司", "明断",
                     "青天", "铁面", "无私", "秉公", "执法", "按律", "定罪",
                     "昭雪", "申冤", "鸣冤", "公道", "天理", "王法", "国法",
                     "原告", "被告", "证人", "口供", "招认", "画押", "堂威"],
        "weight": 0.9,
    },
    "权力斗争": {
        "keywords": ["权", "篡", "夺", "争", "斗", "霸", "篡位", "夺权", "弄权",
                     "专权", "擅权", "把持", "朝政", "废立", "挟天子", "令诸侯",
                     "谋反", "篡逆", "逼宫", "夺位", "争宠", "争功", "倾轧",
                     "排挤", "陷害", "诬告", "谗言", "进谗", "弄臣", "权臣"],
        "weight": 0.85,
    },
    "神仙鬼怪": {
        "keywords": ["仙", "神", "佛", "鬼", "妖", "怪", "精", "魔", "龙", "凤",
                     "天宫", "地府", "阴曹", "阎罗", "判官", "小鬼", "无常",
                     "菩萨", "罗汉", "金刚", "天王", "星君", "真君", "天尊",
                     "托梦", "显灵", "显圣", "变化", "法术", "妖术", "仙法"],
        "weight": 0.9,
    },
    "喜剧幽默": {
        "keywords": ["笑", "闹", "趣", "逗", "戏", "诙谐", "滑稽", "荒唐", "胡闹",
                     "取笑", "打趣", "捉弄", "耍笑", "卖弄", "吹牛", "扯淡",
                     "错认", "误会", "巧合", "巧遇", "冒名", "顶替", "冒充",
                     "出丑", "丢人", "献丑", "出洋相", "闹笑话"],
        "weight": 0.8,
    },
    "悲情苦难": {
        "keywords": ["哭", "悲", "苦", "哀", "痛", "伤", "惨", "凄", "惨", "冤",
                     "身亡", "惨死", "丧命", "夭折", "殉", "自尽", "投河", "上吊",
                     "家破", "人亡", "流离", "失所", "逃难", "遭难", "遇害",
                     "哭诉", "悲啼", "哀告", "苦命", "薄命", "红颜薄命"],
        "weight": 0.85,
    },
    "忠孝节义": {
        "keywords": ["节", "义", "烈", "贞", "贤", "德", "廉", "耻", "仁", "恕",
                     "守节", "殉节", "全节", "节烈", "贞烈", "贤良", "贤德",
                     "义气", "侠义", "道义", "大义", "仗义", "疏财", "舍生取义",
                     "杀身成仁", "凛然", "大节", "高风", "亮节", "清风", "傲骨"],
        "weight": 0.85,
    },
    "复仇雪恨": {
        "keywords": ["仇", "恨", "报", "雪", "复仇", "报仇", "雪恨", "血债", "讨还",
                     "不共戴天", "杀父", "夺妻", "灭门", "屠戮", "血洗",
                     "手刃", "亲斩", "诛杀", "追杀", "寻仇", "积怨", "宿怨"],
        "weight": 0.9,
    },
    "君臣关系": {
        "keywords": ["君", "臣", "主", "陛下", "圣上", "万岁", "微臣", "为臣", "臣子",
                     "奏", "启奏", "面圣", "进谏", "劝谏", "死谏", "忠谏",
                     "封赏", "赐", "封官", "加爵", "升迁", "贬谪", "罢官",
                     "托孤", "辅政", "监国", "摄政", "垂帘", "听政", "临朝"],
        "weight": 0.9,
    },
    "兄弟情谊": {
        "keywords": ["兄", "弟", "结义", "结拜", "桃园", "金兰", "手足", "同胞",
                     "患难", "共苦", "同甘", "同生共死", "义结", "八拜", "生死",
                     "刎颈", "莫逆", "知己", "知音", "肝胆相照", "推心置腹"],
        "weight": 0.8,
    },
    "女性命运": {
        "keywords": ["女", "妇", "娘", "婆", "嫂", "姑", "姨", "婶", "母", "妃", "后",
                     "守寡", "改嫁", "殉夫", "卖身", "被弃", "休", "出", "逐",
                     "巾帼", "不让须眉", "女中豪杰", "女丈夫", "奇女子",
                     "红颜", "薄命", "青楼", "烟花", "风尘", "沦落", "飘零"],
        "weight": 0.8,
    },
}

# ── Text Cleaning ────────────────────────────────────────────────────

STAGE_DIRECTION_PATTERNS = [
    r"^[^。，！？]{1,5}$",               # very short lines
    r"^(哽|呀|咦|哦|哎|嗨|喂|呸|哼|唉|咳|咧|兮)$",  # interjections
    r"^(同上|同下|同上场|同下场|龙套|众人|四兵士|四大铠)$",
]

def is_noise(text):
    """Filter out stage directions and noise."""
    if not text or len(text.strip()) <= 2:
        return True
    for pat in STAGE_DIRECTION_PATTERNS:
        if re.match(pat, text.strip()):
            return True
    return False


def clean_text(text):
    """Clean utterance text."""
    text = text.strip()
    # Remove parenthetical notes
    text = re.sub(r'[（(].*?[）)]', '', text)
    # Remove repeated punctuation
    text = re.sub(r'[。，！？…]{3,}', '。', text)
    return text


def tokenize_chinese(text):
    """Simple Chinese tokenizer: split by characters and common patterns."""
    # Extract 2-3 char bigrams for keyword matching
    chars = list(text.replace(" ", ""))
    bigrams = [''.join(chars[i:i+2]) for i in range(len(chars)-1)]
    trigrams = [''.join(chars[i:i+3]) for i in range(len(chars)-2)]
    return set(chars + bigrams + trigrams)


def score_theme(text, theme_name, theme_info):
    """Score a single utterance against a theme."""
    tokens = tokenize_chinese(text)
    score = 0
    for kw in theme_info["keywords"]:
        if kw in text:
            # Longer keyword matches get higher scores
            score += len(kw) * 0.5
    return score * theme_info["weight"]


# ── LLM Theme Labeling ────────────────────────────────────────────────

def call_ollama(prompt, model="qwen2.5:7b", timeout=180):
    try:
        result = subprocess.run(
            ["ollama", "run", model, prompt],
            capture_output=True, text=True, encoding="utf-8", timeout=timeout,
        )
        return result.stdout.strip()
    except:
        return "[ERROR]"


def llm_label_themes(scripts_sample, n=5):
    """Use LLM to label themes for sample scripts."""
    results = []
    for s in scripts_sample[:n]:
        title = s["title"]
        plot = s.get("plot", "")[:300]
        chars = [c["name"] for c in s.get("characters", [])][:8]

        prompt = f"""你是京剧主题分析专家。请为以下剧本识别主要主题。

剧本：{title}
情节：{plot}
主要角色：{', '.join(chars)}

请从以下主题类别中选择最匹配的2-3个主题（按相关性排序）：
战争军事 | 智谋策略 | 忠诚报国 | 家庭伦理 | 爱情情感 | 正义审判 |
权力斗争 | 神仙鬼怪 | 喜剧幽默 | 悲情苦难 | 忠孝节义 | 复仇雪恨 |
君臣关系 | 兄弟情谊 | 女性命运

请严格按格式返回（一行一个主题）：
主题：<主题名>"""

        response = call_ollama(prompt)
        themes = []
        for line in response.split("\n"):
            if "主题" in line:
                for t in THEME_DICT:
                    if t in line:
                        themes.append(t)
                        break

        results.append({
            "script_id": s["script_id"],
            "title": title,
            "llm_themes": themes,
            "llm_raw": response[:200],
        })
    return results


# ── Main Pipeline ─────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("Theme/Topic Modeling & Analysis Pipeline")
    print("=" * 60)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # ── 1. Load & extract utterances ──
    print("\n[1/9] Loading scripts & extracting utterances...")
    scripts = []
    all_utterances = []
    script_texts = {}
    scene_texts = defaultdict(list)

    for fpath in sorted(glob.glob(os.path.join(DATA_DIR, "**/*.json"), recursive=True)):
        with open(fpath, "r", encoding="utf-8") as f:
            s = json.load(f)
        scripts.append(s)

        sid = s["script_id"]
        script_lines = []
        for scene in s.get("scenes", []):
            scene_lines = []
            for utt in scene.get("utterances", []):
                c = utt.get("character")
                utype = utt.get("type", "")
                text = clean_text(utt.get("text", ""))

                # Skip stage directions and noise
                if utype == "stage" or is_noise(text):
                    continue

                script_lines.append(text)
                scene_lines.append(text)
                all_utterances.append({
                    "script_id": sid,
                    "title": s["title"],
                    "scene_id": scene.get("scene_id", 0),
                    "character": c,
                    "type": utype,
                    "text": text,
                })

            scene_texts[f"{sid}:{scene.get('scene_id', 0)}"] = " ".join(scene_lines)

        script_texts[sid] = " ".join(script_lines)

    print(f"  Loaded {len(scripts)} scripts, {len(all_utterances)} utterances")

    # ── 2. Theme scoring at utterance level ──
    print("\n[2/9] Scoring utterances against themes...")
    theme_names = list(THEME_DICT.keys())

    utterance_themes = []
    for utt in all_utterances:
        scores = {}
        for tname, tinfo in THEME_DICT.items():
            s = score_theme(utt["text"], tname, tinfo)
            if s > 0:
                scores[tname] = round(s, 2)
        if scores:
            utterance_themes.append({**utt, "theme_scores": scores})

    print(f"  {len(utterance_themes)} utterances matched themes")

    # ── 3. Scene-level aggregation ──
    print("\n[3/9] Aggregating at scene level...")
    scene_theme_data = []
    for scene_key, text in scene_texts.items():
        parts = scene_key.split(":")
        sid, sc_id = parts[0], int(parts[1]) if len(parts) > 1 else 0

        scores = {}
        for tname, tinfo in THEME_DICT.items():
            s = score_theme(text, tname, tinfo)
            if s > 0:
                scores[tname] = s

        if scores:
            total = sum(scores.values())
            normalized = {k: round(v / total, 4) for k, v in scores.items()}
            scene_theme_data.append({
                "script_id": sid,
                "scene_id": sc_id,
                "theme_scores": scores,
                "theme_distribution": normalized,
            })

    print(f"  {len(scene_theme_data)} scenes with theme data")

    # ── 4. Script-level topic distribution ──
    print("\n[4/9] Computing script-level topic distributions...")
    script_themes = {}
    for sid, text in script_texts.items():
        scores = {}
        for tname, tinfo in THEME_DICT.items():
            s = score_theme(text, tname, tinfo)
            scores[tname] = s

        total = max(sum(scores.values()), 1)
        normalized = {k: round(v / total, 4) for k, v in scores.items()}
        top_themes = sorted(scores.items(), key=lambda x: -x[1])[:3]

        script_themes[sid] = {
            "scores": scores,
            "distribution": normalized,
            "top_themes": [{"theme": t, "score": round(s, 2)} for t, s in top_themes],
            "theme_count": sum(1 for v in scores.values() if v > 0),
            "entropy": round(
                -sum((v / total) * log2(v / total) for v in scores.values() if v > 0), 4
            ),
        }

    # ── 5. TF-IDF topic extraction ──
    print("\n[5/9] Running TF-IDF for topic term extraction...")
    corpus = list(script_texts.values())
    script_ids = list(script_texts.keys())

    vectorizer = TfidfVectorizer(
        max_features=2000,
        tokenizer=lambda x: [x[i:i+2] for i in range(len(x)-1)],
        lowercase=False,
        max_df=0.8,
        min_df=3,
    )

    try:
        tfidf_matrix = vectorizer.fit_transform(corpus)
        # Handle sklearn API difference (0.21 vs 0.24+)
        try:
            feature_names = vectorizer.get_feature_names_out()
        except AttributeError:
            feature_names = vectorizer.get_feature_names()

        # Get top terms per script (topic keywords)
        script_top_terms = {}
        for i, sid in enumerate(script_ids):
            row = tfidf_matrix[i].toarray().flatten()
            top_indices = row.argsort()[-20:][::-1]
            top_terms = [(feature_names[j], round(float(row[j]), 4)) for j in top_indices if row[j] > 0]
            script_top_terms[sid] = top_terms[:10]

        # PCA for topic space visualization
        # Use min(n_samples, n_features, 50) components
        n_components = min(min(tfidf_matrix.shape), 10)
        pca = PCA(n_components=n_components, random_state=42)
        pca_result = pca.fit_transform(tfidf_matrix.toarray())
        pca_2d = pca_result[:, :2]

        # Map PCA to themes for scatter
        pca_points = []
        for i, sid in enumerate(script_ids):
            st = script_themes.get(sid, {})
            pca_points.append({
                "script_id": sid,
                "title": ".",
                "x": round(float(pca_2d[i][0]), 4),
                "y": round(float(pca_2d[i][1]), 4),
                "top_themes": [t["theme"] for t in st.get("top_themes", [])[:2]],
                "entropy": st.get("entropy", 0),
            })

        explained_var = [round(float(v), 4) for v in pca.explained_variance_ratio_[:2]]
    except Exception as e:
        print(f"  TF-IDF/PCA warning: {e}, building fallback PCA from theme distributions")
        # Fallback: PCA on theme distribution vectors
        theme_vectors = []
        for sid in script_ids:
            st = script_themes.get(sid, {})
            vec = [st["distribution"].get(t, 0) for t in theme_names] if st else [0]*len(theme_names)
            theme_vectors.append(vec)
        theme_vecs_arr = np.array(theme_vectors)
        if len(theme_vecs_arr) > 1:
            pca = PCA(n_components=min(len(theme_names), 10), random_state=42)
            pca_result = pca.fit_transform(theme_vecs_arr)
            pca_2d = pca_result[:, :2]
            pca_points = []
            for i, sid in enumerate(script_ids):
                st = script_themes.get(sid, {})
                pca_points.append({
                    "script_id": sid,
                    "title": ".",
                    "x": round(float(pca_2d[i][0]), 4),
                    "y": round(float(pca_2d[i][1]), 4),
                    "top_themes": [t["theme"] for t in st.get("top_themes", [])[:2]],
                    "entropy": st.get("entropy", 0),
                })
            explained_var = [round(float(v), 4) for v in pca.explained_variance_ratio_[:2]]
        else:
            pca_points = []
            explained_var = [0, 0]
        script_top_terms = {}

    # Attach script metadata
    sid_to_meta = {}
    for s in scripts:
        stype = classify_script_type_simple(s)
        sid_to_meta[s["script_id"]] = {
            "title": s["title"],
            "type": stype,
        }

    for pt in pca_points:
        meta = sid_to_meta.get(pt["script_id"], {})
        pt["title"] = meta.get("title", "")
        pt["type"] = meta.get("type", "其他")

    # ── 6. Topic co-occurrence & PMI ──
    print("\n[6/9] Computing topic co-occurrence & PMI...")
    cooc = defaultdict(lambda: defaultdict(int))
    topic_totals = defaultdict(int)
    total_scripts = len(script_themes)

    for sid, st in script_themes.items():
        themes_present = [t for t, s in st["scores"].items() if s > 0]
        for t in themes_present:
            topic_totals[t] += 1
        for i in range(len(themes_present)):
            for j in range(i + 1, len(themes_present)):
                cooc[themes_present[i]][themes_present[j]] += 1
                cooc[themes_present[j]][themes_present[i]] += 1

    # PMI matrix
    pmi_matrix = {}
    for t1 in theme_names:
        pmi_matrix[t1] = {}
        for t2 in theme_names:
            if t1 == t2:
                pmi_matrix[t1][t2] = 0
                continue
            co_count = cooc[t1].get(t2, 0)
            if co_count == 0:
                pmi_matrix[t1][t2] = 0
                continue
            p_t1 = topic_totals[t1] / total_scripts
            p_t2 = topic_totals[t2] / total_scripts
            p_joint = co_count / total_scripts
            pmi = log2(p_joint / (p_t1 * p_t2)) if p_joint > 0 else 0
            pmi_matrix[t1][t2] = round(pmi, 3)

    # Top co-occurring pairs
    cooc_pairs = []
    for t1 in theme_names:
        for t2 in theme_names:
            if t1 < t2 and cooc[t1].get(t2, 0) > 0:
                cooc_pairs.append({
                    "theme1": t1, "theme2": t2,
                    "count": cooc[t1][t2],
                    "pmi": pmi_matrix[t1].get(t2, 0),
                })
    cooc_pairs.sort(key=lambda x: -x["pmi"])

    # Association rules
    assoc_rules = []
    for t1 in theme_names:
        for t2 in theme_names:
            if t1 == t2:
                continue
            co_count = cooc[t1].get(t2, 0)
            if co_count < 3:
                continue
            support = co_count / total_scripts
            confidence = co_count / topic_totals[t1] if topic_totals[t1] > 0 else 0
            lift = confidence / (topic_totals[t2] / total_scripts) if topic_totals[t2] > 0 else 0
            if lift > 1.5:
                assoc_rules.append({
                    "antecedent": t1, "consequent": t2,
                    "support": round(support, 4),
                    "confidence": round(confidence, 4),
                    "lift": round(lift, 2),
                })
    assoc_rules.sort(key=lambda x: -x["lift"])

    # ── 7. Scene-level topic evolution ──
    print("\n[7/9] Computing scene-level topic evolution...")
    script_evolutions = {}
    for sid in list(script_ids)[:50]:  # top 50 scripts
        scenes = [sc for sc in scene_theme_data if sc["script_id"] == sid]
        scenes.sort(key=lambda x: x["scene_id"])

        if len(scenes) < 3:
            continue

        timeline = []
        for sc in scenes:
            top = sorted(sc["theme_distribution"].items(), key=lambda x: -x[1])[:3]
            timeline.append({
                "scene_id": sc["scene_id"],
                "top_themes": [{"theme": t, "strength": round(s, 4)} for t, s in top],
            })

        script_evolutions[sid] = {
            "title": sid_to_meta.get(sid, {}).get("title", sid),
            "type": sid_to_meta.get(sid, {}).get("type", "其他"),
            "scene_count": len(scenes),
            "timeline": timeline,
        }

    # ── 8. Type-level comparison ──
    print("\n[8/9] Computing type-level theme comparisons...")
    type_themes = defaultdict(lambda: defaultdict(float))
    type_counts = defaultdict(int)

    for sid, st in script_themes.items():
        stype = sid_to_meta.get(sid, {}).get("type", "其他")
        type_counts[stype] += 1
        for t, v in st["distribution"].items():
            type_themes[stype][t] += v

    type_avg_themes = {}
    for stype in type_themes:
        cnt = type_counts[stype]
        type_avg_themes[stype] = {
            "distribution": {t: round(v / cnt, 4) for t, v in type_themes[stype].items()},
            "script_count": cnt,
        }

    # Build type-comparison heatmap data
    type_comparison = {
        "types": sorted(type_avg_themes.keys()),
        "themes": theme_names,
        "matrix": {},
    }
    for stype, data in type_avg_themes.items():
        type_comparison["matrix"][stype] = {
            t: data["distribution"].get(t, 0) for t in theme_names
        }

    # ── 9. LLM labeling (sample) ──
    print("\n[9/9] LLM theme labeling (sample)...")
    llm_results = llm_label_themes(scripts, n=10)
    print(f"  LLM labeled {len(llm_results)} scripts")

    # ── Export ──
    print("\n" + "=" * 60)
    print("Exporting data...")

    # Script-level topic distributions
    with open(os.path.join(OUTPUT_DIR, "theme_script_distributions.json"), "w", encoding="utf-8") as f:
        json.dump({
            "scripts": {
                sid: {
                    **st,
                    "title": sid_to_meta.get(sid, {}).get("title", ""),
                    "type": sid_to_meta.get(sid, {}).get("type", "其他"),
                    "top_terms": script_top_terms.get(sid, []),
                }
                for sid, st in script_themes.items()
            },
            "theme_names": theme_names,
        }, f, ensure_ascii=False, indent=2)
    print(f"  [OK] theme_script_distributions.json")

    # Topic co-occurrence & PMI
    with open(os.path.join(OUTPUT_DIR, "theme_cooccurrence.json"), "w", encoding="utf-8") as f:
        json.dump({
            "cooc_matrix": {t1: {t2: cooc[t1].get(t2, 0) for t2 in theme_names} for t1 in theme_names},
            "pmi_matrix": pmi_matrix,
            "top_pairs": cooc_pairs[:30],
            "association_rules": assoc_rules[:30],
            "topic_totals": dict(topic_totals),
        }, f, ensure_ascii=False, indent=2)
    print(f"  [OK] theme_cooccurrence.json")

    # PCA topic space
    with open(os.path.join(OUTPUT_DIR, "theme_topic_space.json"), "w", encoding="utf-8") as f:
        json.dump({
            "points": pca_points,
            "explained_variance": explained_var,
            "theme_names": theme_names,
        }, f, ensure_ascii=False, indent=2)
    print(f"  [OK] theme_topic_space.json ({len(pca_points)} points)")

    # Type-level comparison
    with open(os.path.join(OUTPUT_DIR, "theme_type_comparison.json"), "w", encoding="utf-8") as f:
        json.dump(type_comparison, f, ensure_ascii=False, indent=2)
    print(f"  [OK] theme_type_comparison.json")

    # Scene evolution
    with open(os.path.join(OUTPUT_DIR, "theme_evolution.json"), "w", encoding="utf-8") as f:
        json.dump(script_evolutions, f, ensure_ascii=False, indent=2)
    print(f"  [OK] theme_evolution.json ({len(script_evolutions)} scripts)")

    # Sankey data (script type → theme → pattern)
    sankey_nodes = []
    sankey_links = []

    # Node sets
    type_set = sorted(type_avg_themes.keys())
    theme_set = theme_names[:8]  # Top 8 themes for clarity

    all_nodes = type_set + theme_set
    node_idx = {n: i for i, n in enumerate(all_nodes)}
    sankey_nodes = [{"name": n} for n in all_nodes]

    for stype, data in type_avg_themes.items():
        for t in theme_set:
            v = data["distribution"].get(t, 0)
            if v > 0.01:
                sankey_links.append({
                    "source": node_idx[stype],
                    "target": node_idx[t],
                    "value": round(v * 100, 1),
                })

    with open(os.path.join(OUTPUT_DIR, "theme_sankey.json"), "w", encoding="utf-8") as f:
        json.dump({"nodes": sankey_nodes, "links": sankey_links}, f, ensure_ascii=False, indent=2)
    print(f"  [OK] theme_sankey.json")

    # LLM results
    with open(os.path.join(OUTPUT_DIR, "theme_llm_labels.json"), "w", encoding="utf-8") as f:
        json.dump(llm_results, f, ensure_ascii=False, indent=2)
    print(f"  [OK] theme_llm_labels.json")

    # Summary
    summary = {
        "total_scripts": len(script_themes),
        "total_utterances": len(all_utterances),
        "theme_count": len(theme_names),
        "top_cooc_pairs": cooc_pairs[:5],
        "top_rules": assoc_rules[:5],
        "type_distribution": dict(type_counts),
    }
    with open(os.path.join(OUTPUT_DIR, "theme_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"  [OK] theme_summary.json")

    print(f"\nDone!")
    print(f"  Scripts: {len(script_themes)}")
    print(f"  Utterances: {len(all_utterances)}")
    print(f"  Top pairs: {[(p['theme1'], p['theme2'], p['pmi']) for p in cooc_pairs[:5]]}")


def classify_script_type_simple(script):
    """Quick script type classification (reuse from network_analysis)."""
    all_text = script.get("plot", "") + script.get("title", "")
    for c in script.get("characters", []):
        all_text += c.get("name", "")

    scores = {"历史戏": 0, "家庭戏": 0, "公案戏": 0, "神话戏": 0, "其他": 0}
    for kw in ["军", "兵", "战", "攻", "伐", "征", "帅", "将"]:
        if kw in all_text: scores["历史戏"] += 1
    for kw in ["母", "父", "子", "女", "妻", "夫", "家", "婚", "嫁"]:
        if kw in all_text: scores["家庭戏"] += 1
    for kw in ["案", "审", "判", "告", "冤", "状", "堂", "府", "衙"]:
        if kw in all_text: scores["公案戏"] += 1
    for kw in ["仙", "神", "佛", "鬼", "妖", "怪", "龙"]:
        if kw in all_text: scores["神话戏"] += 1
    return max(scores, key=scores.get)


if __name__ == "__main__":
    main()
