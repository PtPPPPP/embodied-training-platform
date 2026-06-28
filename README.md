# 桌面具身智能训练平台 MVP

> 用一台笔记本，跑通"感知 → 规划 → 决策 → 控制 → 执行"的具身智能闭环。
> **完全不依赖真实硬件**，纯仿真即可完整演示与教学。

这是一个面向高校 AI 社团的低成本具身智能教学/竞赛平台 Demo。后端用 **FastAPI** 提供机器人控制 API，前端用 **React + Vite** 提供 Web 控制台，底层用一个二维栅格仿真器模拟小车、障碍物、目标物体、路径规划与机械臂抓取——任何一台装了 Python 的普通电脑都能跑起来。

---

## ✨ 功能亮点

| 模块 | 能力 |
|------|------|
| 🗺️ 二维桌面地图 | 10×10 栅格，可视化小车、障碍物与目标物体 |
| 🚗 底盘控制 | 前进 / 后退 / 左转 / 右转 / 停止，可调速度 |
| 🧭 路径规划 | BFS（4 邻域）自动避障，可视化路径 |
| 👁️ 模拟视觉 | 返回红 / 蓝方块等目标列表 |
| 🦾 机械臂抓取 | 模拟 `grab` 抓取与 `reset` 复位 |
| 💬 文字指令 | 自然语言触发任务（如"前进""抓取红色方块""移动到 A 点"） |
| 🌐 Web 控制台 | 浏览器打开即用，状态、地图、日志一目了然 |

> 🎯 **设计理念**：所有能力通过统一接口暴露。当前是 `Simulated*` 仿真实现，后续可逐个替换为真实硬件驱动，而上层任务逻辑、Web 控制台与示例脚本几乎不用改。

---

## 🧰 技术栈

- **后端**：Python 3.10+ · FastAPI · Pydantic · Uvicorn
- **前端**：React 19 · Vite 6 · TypeScript 5
- **通信**：HTTP / `fetch`（前端 ↔ 后端）

---

## 🚀 快速开始

### 1. 启动后端

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
python -m uvicorn main:app --app-dir backend --reload
```

启动后访问：

| 地址 | 说明 |
|------|------|
| http://127.0.0.1:8000/health | 健康检查 |
| http://127.0.0.1:8000/docs | 自动生成的 API 文档（Swagger UI，可直接调试） |

### 2. 启动前端

另开一个终端：

```powershell
cd frontend
npm install
npm run dev
```

打开 Web 控制台：http://127.0.0.1:5173

> 后端默认开启 CORS，允许 `localhost:5173` 与 `127.0.0.1:5173` 访问，前后端可直接联调。

---

## 📡 API 参考

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET`  | `/health` | 健康检查 |
| `GET`  | `/api/robot/state` | 获取机器人状态（位置 / 朝向 / 已抓取物体等） |
| `POST` | `/api/robot/chassis/move` | 底盘移动（`command`、`speed`） |
| `POST` | `/api/planner/path` | 路径规划（`start`、`goal`、可选 `obstacles`） |
| `GET`  | `/api/vision/objects` | 获取视觉目标列表 |
| `POST` | `/api/robot/arm/grab` | 机械臂抓取（`object_id`） |
| `POST` | `/api/task/command` | 文字指令解析与执行（`text`） |
| `POST` | `/api/robot/reset` | 机器人复位 |

请求/响应字段详见 http://127.0.0.1:8000/docs。

---

## 🏗️ 系统架构

```
┌──────────────────────────────────────────────┐
│  Web 控制台（React + Vite，端口 5173）          │
│  状态面板 / 小车控制 / 路径规划 / 机械臂 / 指令 / 地图 / 日志
└───────────────────┬──────────────────────────┘
                    │  HTTP（fetch）
┌───────────────────▼──────────────────────────┐
│  FastAPI 机器人控制服务（端口 8000）            │
│  /api/robot/*  /api/planner/*  /api/vision/*  /api/task/*
└───────────────────┬──────────────────────────┘
                    │
┌───────────────────▼──────────────────────────┐
│  RobotSimulator（10×10 仿真核心，统一门面）     │
│   ├─ SimulatedChassis   底盘：前进/后退/左转/右转/停止
│   ├─ SimulatedArm       机械臂：grab / reset
│   ├─ SimpleVision       视觉：返回模拟目标列表
│   ├─ GridPlanner        规划：BFS 4 邻域
│   └─ TaskManager        任务：文字指令 → 动作
└──────────────────────────────────────────────┘
```

---

## 🧪 示例脚本

后端启动后，可运行 `examples/` 下的示例脚本快速体验各模块：

```powershell
python examples\simple_move.py            # 底盘移动
python examples\path_planning_demo.py     # 路径规划
python examples\vision_demo.py            # 模拟视觉
python examples\arm_grab_demo.py          # 机械臂抓取
python examples\integrated_task_demo.py   # 综合任务
```

---

## 🎬 MVP 演示流程

1. 启动后端与前端。
2. 在 Web 控制台查看机器人状态、地图、障碍物与目标物体。
3. 点击底盘控制按钮，观察位置、朝向与日志变化。
4. 输入起点和终点，点击"生成路径"查看 BFS 规划结果。
5. 选择红/蓝方块，点击"模拟抓取"。
6. 在文字指令框输入"前进""后退""抓取红色方块""移动到 A 点""开始综合挑战"等。

---

## 📂 项目结构

```text
embodied-training-platform/
├── backend/      FastAPI 服务与机器人仿真模块（robot/）
├── frontend/     React + Vite Web 控制台
├── examples/     API 调用示例脚本（5 个）
├── docs/         项目说明、BOM、课程与实验文档
└── agent.md      统一接口与项目设计说明
```

---

## 📖 更多文档

| 主题 | 文档 |
|------|------|
| 项目总览与定位 | [`docs/project-overview.md`](./docs/project-overview.md) |
| 硬件方案与选型 | [`docs/hardware-guide.md`](./docs/hardware-guide.md) |
| 物料清单（BOM） | [`docs/bom.md`](./docs/bom.md) |
| 课程计划 | [`docs/course-plan.md`](./docs/course-plan.md) |
| 实验任务 | [`docs/experiments.md`](./docs/experiments.md) |
| 比赛材料 | [`docs/competition-package.md`](./docs/competition-package.md) |
| 答辩提纲 | [`docs/defense-outline.md`](./docs/defense-outline.md) |
| 路线图 | [`docs/roadmap.md`](./docs/roadmap.md) |
| 用户故事 | [`docs/user-story.md`](./docs/user-story.md) |

---

## 🚧 当前边界

本版本只做 **Mock / Simulator**，以"能演示、能教学、能复用"为目标：

- ✅ **已实现**：后端 API、Web 控制台、二维仿真、示例脚本。
- 🚫 **本阶段不做**：真实小车 / 机械臂 / 摄像头 / ROS / 云服务 / 大模型；复杂动力学仿真、SLAM、多机器人协作。

后续硬件联调、真实视觉、ROS 2 等规划见 [`docs/roadmap.md`](./docs/roadmap.md)。
