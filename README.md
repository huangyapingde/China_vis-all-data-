# 🎭 京剧剧本叙事与角色网络可视化分析系统 (Peking Opera Analytics)

本系统是一个针对京剧剧本的深度可视化分析平台，基于 1,473 部京剧剧本和 26,877 个角色数据。系统结合了自然语言处理（TF-IDF, PCA）、大语言模型（Qwen2.5-7B）以及复杂网络分析方法，从**行当推断**、**角色关系网络**、**主题建模**以及**叙事结构**四个维度对京剧进行全方位的量化分析与可视化展示。

---

## 📊 关键数据指标

| 指标 | 数值 |
|------|------|
| **剧本总数** | 1,473 |
| **角色实例总数** | 26,877 |
| **已标注行当** | 7,259 |
| **未标注角色（LLM/启发式推断）** | 19,375 |
| **行当分布** | 生 3085 / 旦 1495 / 净 1563 / 丑 1116 |
| **关系网络** | 1,380 个剧本共现/对话/权力三层网络 |
| **主题类别** | 15 类（战争军事、智谋策略、忠诚报国等） |
| **叙事分析** | 934 个剧本叙事结构（单峰 87%、双峰 10%、多峰 3%） |

---

## 🚀 系统架构

本系统采用**前后端分离**架构：
*   **后端 (Backend)**：基于 Python 的数据处理与分析管线。包括剧本解析、特征提取、角色-行当关联矩阵计算（PMI、纯度、信息熵）、三层复杂网络密度计算、TF-IDF 与 PCA 主题降维，以及调用 Qwen 批量预测和主题校验。
*   **前端 (Frontend)**：基于 Vite + React 的现代化单页 Web 应用。使用 **ECharts** 和 **D3.js** 构建高交互性的可视化图表，包括桑基图、关系网络力导图、时序雷达图、主题演化曲线等。

---

## 📂 目录结构说明

```text
China_vis/
├── backend/                  # 后端数据处理与分析管线 (Python)
│   ├── process_data.py       # 核心角色与行当特征提取及指标计算
│   ├── network_analysis.py   # 角色共现、对话、权力三层网络指标计算
│   ├── theme_analysis.py     # 主题建模与 TF-IDF + PCA 空间投影
│   ├── narrative_analysis.py # 高斯平滑、峰值检测与四阶段叙事分割
│   ├── llm_classify.py       # 大模型行当标注与预测
│   └── llm_classify_batch.py # 大模型批量标注处理
├── data/                     # 1473 部原始京剧剧本 JSON 数据集 (包含多级子目录)
├── frontend/                 # 前端可视化展示系统 (Vite + React)
│   ├── public/data/          # 后端分析导出的 JSON 可视化数据集 (包含 all-data precomputed 结果)
│   ├── src/
│   │   ├── components/       # 30+ 个独立的可视化图表与 UI 组件 (集成高级交互逻辑)
│   │   ├── hooks/            # 数据加载与处理自定义 React Hooks
│   │   ├── App.jsx           # 系统主入口与多任务导航控制
│   │   ├── index.css         # 系统现代暗色系风格样式
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
└── README.md                 # 项目说明文档
```

---

## 🎭 核心分析模块

### 任务一：行当推断与分析 (Role & Hangdang)
*   **分析方法**：提取角色台词长度、频次、情感词频、权力指令频次等行为特征，利用互信息（PMI）、纯度和熵度量角色类型与生、旦、净、丑四大行当的关联度，辅以大模型推断未标注角色的行当。
*   **可视化组件**：
    *   `SankeyChart`：角色类型到四大行当的映射流向桑基图。
    *   `ScatterChart`：基于行为特征投影的角色分布聚类散点图。
    *   `PurityEntropyChart` / `PMITable`：行当纯度、信息熵及 PMI 关联度明细。
    *   `StackedBarChart` / `TimeSeriesChart`：跨卷/时期的行当占比演化堆叠图。

### 任务二：角色关系网络分析 (Social & Power Network)
*   **分析方法**：构建**共现层**（场景共现）、**对话层**（台词承接）和**权力层**（命令与服从）三层网络。基于 PageRank、度、中间中心性等多维指标评估角色影响力，利用 Louvain 算法识别阵营社区。
*   **可视化组件**：
    *   `ForceGraph`：支持三层切换的力导向关系网络图（节点大小对应度中心性，颜色对应社区）。
    *   `CommunityGraph`：Louvain 社区划分与阵营结构展示。
    *   `RadarChart` / `CentralityTable`：核心角色多维中心性影响力的雷达图与详表。
    *   `NetworkComparison`：历史戏、家庭戏、公案戏、神话戏等不同剧种的网络密度与结构差异对比。

### 任务三：主题建模与分析 (Topic & Theme Modeling)
*   **分析方法**：基于精心提炼 of 京剧 15 类主题词库进行关键词匹配与 TF-IDF 向量化，使用 PCA 投影探索主题空间，并利用 Qwen2.5:7b 进行大模型标注验证。
*   **可视化组件**：
    *   `TopicTypeBar` / `TopicHeatmap`：不同剧种的主题构成比例与强度对比。
    *   `TopicSpaceChart`：PCA 降维后的剧本主题空间散点分布。
    *   `TopicNetwork`：基于主题共现关系的网络图。
    *   `TopicTimeline`：特定剧本的主题在各场景中的动态演化时序图。

### 任务四：叙事结构分析 (Narrative Structure)
*   **分析方法**：综合情绪张力、冲突强度和事件密度特征，利用高斯滑动窗口平滑与峰值检测识别叙事高潮，进行经典的“起、承、转、合”四阶段自动分割，并聚类出单峰、双峰与多峰叙事模板。
*   **可视化组件**：
    *   `TemplateCurves`：不同剧种的归一化叙事张力平均模板曲线。
    *   `NarrativeCurve`：单部剧本中张力、冲突、事件、情绪曲线场景级演变。
    *   `StageSegmentation`：叙事四阶段分割 of 场景可视化。
    *   `ClimaxDistribution`：叙事高潮位置分布柱状图。

---

## 🛠️ 快速开始

### 1. 运行数据处理管线 (Python 后端)
如果您需要重新运行分析并更新可视化数据，请进入 `backend` 目录。
可以使用传统的 `pip` 全局安装依赖运行，或者使用 `uv` 包管理器：

**使用 uv (推荐)**：
```bash
# 创建虚拟环境
uv venv backend/.venv

# 安装依赖
uv pip install --python backend/.venv/Scripts/python.exe networkx numpy scipy scikit-learn

# 执行分析管线 (按需运行)
uv run --python backend/.venv/Scripts/python.exe python backend/process_data.py
uv run --python backend/.venv/Scripts/python.exe python backend/network_analysis.py
uv run --python backend/.venv/Scripts/python.exe python backend/theme_analysis.py
uv run --python backend/.venv/Scripts/python.exe python backend/narrative_analysis.py
```

**使用 pip**：
```bash
pip install networkx numpy scipy scikit-learn

python backend/process_data.py
python backend/network_analysis.py
python backend/theme_analysis.py
python backend/narrative_analysis.py
```

### 2. 启动前端可视化面板 (React 前端)
进入 `frontend` 目录，安装依赖并启动 Vite 开发服务器：
```bash
cd frontend
npm install
npm run dev
```
启动后在浏览器打开终端输出的本地地址（默认 `http://localhost:5173`）即可体验高交互的可视化系统。

---

## 📊 数据洞察速览
*   **历史戏**：呈现高度的中心化（星型网络结构），权力网络密度显著高于其他剧种，叙事节奏多为中后期的高潮单峰结构，主题往往是战争军事与智谋策略的二元组合。
*   **家庭戏**：呈多中心分散结构，角色间的情感互动紧密但权力层级低，叙事中多峰结构占比显著，主题高度集中于家庭伦理与恋爱，情感起伏大。
*   **公案戏**：高交互密度，对话网络最复杂，呈现“调查 → 冲突 → 判决”的分段双峰或多峰结构。
