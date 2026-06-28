# 桌面具身智能训练平台 MVP

这是一个不依赖真实硬件的桌面具身智能训练平台 Demo。它用 FastAPI 提供机器人控制服务，用 React/Vite 提供 Web 控制台，用二维网格模拟小车、障碍物、目标物体、路径规划和机械臂抓取。

## 已包含功能

- 后端机器人控制 API。
- Web 控制台。
- 二维桌面地图。
- 小车前进、后退、左转、右转、停止。
- BFS 路径规划。
- 模拟视觉目标列表。
- 模拟机械臂抓取红色/蓝色方块。
- 文字指令触发任务。
- 5 个示例脚本。
- 基础项目文档、BOM、课程计划和实验说明。

## 后端启动

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
python -m uvicorn main:app --app-dir backend --reload
```

打开健康检查：

```text
http://127.0.0.1:8000/health
```

## 前端启动

另开一个终端：

```powershell
cd frontend
npm install
npm run dev
```

默认访问：

```text
http://127.0.0.1:5173
```

## MVP 演示流程

1. 启动后端。
2. 启动前端。
3. 在 Web 控制台查看机器人状态、地图、障碍物和目标物体。
4. 点击小车控制按钮，观察位置、朝向和日志变化。
5. 输入起点和终点，点击“生成路径”。
6. 选择红色方块或蓝色方块，点击“模拟抓取”。
7. 输入“前进”“后退”“抓取红色方块”“移动到 A 点”“开始综合挑战”等文字指令。

## 示例脚本

后端启动后可运行：

```powershell
python examples\simple_move.py
python examples\path_planning_demo.py
python examples\vision_demo.py
python examples\arm_grab_demo.py
python examples\integrated_task_demo.py
```

## 项目结构

```text
backend/      FastAPI 服务和机器人仿真模块
frontend/     React/Vite Web 控制台
docs/         项目说明、BOM、课程和实验文档
examples/     API 调用示例脚本
```

## 当前边界

本版本只做 Mock / Simulator，不接真实小车、机械臂、摄像头、ROS、云服务或大模型。

