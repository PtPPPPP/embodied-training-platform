# 5 个实验任务（Experiment Manual）

> 本文档是社团训练营的"实验手册"。5 个实验由浅入深，串成
> **"控制 → 规划 → 感知 → 执行 → 综合"** 的完整具身智能闭环。
>
> 所有实验都可在 **A 档（纯仿真）** 下完成——**当前 MVP 无需任何真实硬件**。
> 每个实验给出真实 API 端点、请求体、返回字段，可直接对照 `examples/` 运行。
>
> ⚠️ 实验基于当前 MVP 的真实实现，以下边界请先了解（诚实说明，避免误解）：
> - **路径规划当前是 BFS（4 邻域）**，A* 作为拓展/后续；
> - **视觉当前是 `SimpleVision` 模拟目标列表**，真实 OpenCV 接入为后续/B 档；
> - **机械臂当前只有 `grab`（抓取）和 `reset`（复位/释放）**，"放置到指定区域"为后续扩展；
> - **小车前进/后退只改变 y 坐标，左转/右转只改变朝向 heading**（仿真简化）。

---

## 阅读约定

- **前置准备**：先启动后端（`python -m uvicorn main:app --app-dir backend --reload`），
  再启动前端（`cd frontend && npm run dev`），浏览器打开 `http://127.0.0.1:5173`。
- **示例脚本**：每个实验都有对应 `examples/*.py`，可直接 `python examples/xxx.py` 运行。
- **验收标准**：实验完成的最低门槛，也是训练营考核依据。
- **API 基址**：`http://127.0.0.1:8000`（可用环境变量 `MVP_API_BASE_URL` 覆盖）。

---

## 实验 1：机器人基础控制

> 对应课程：lesson-01、lesson-02 / 训练营第 1 周 / 示例：`examples/simple_move.py`

### 实验目标
让新人理解机器人运动控制基础：前进、后退、左转、右转、停止、调速，
并体会"一次 API 调用如何变成机器人的一次动作"。

### 前置知识
- Python 基本语法（变量、函数、调用）；
- 会启动项目、打开 Web 控制台；
- （可选）HTTP 请求的概念。

### 所需硬件
- **A 档即可**：一台装了 Python 的电脑 + 浏览器。无需任何硬件。

### 所需软件
- Web 控制台、FastAPI 后端、`RobotSimulator`（含 `SimulatedChassis`）。

### 实验步骤
1. 启动后端与前端，浏览器打开控制台；
2. 在"机器人状态"面板确认初始值：位置 `(0.0, 0.0)`、朝向 `0°`、当前任务 `idle`；
3. 调节速度滑块，依次点击"前进 / 后退 / 左转 / 右转 / 停止"，观察状态与地图变化；
4. 用 Python 直接调用 API 复现：
   ```python
   # examples/simple_move.py 的核心
   from api_client import post, print_json
   state = post("/api/robot/chassis/move", {"command": "forward", "speed": 0.6})
   print_json("小车前进后的状态", state)
   ```
5. 观察返回的 `position.y` 增大（前进）、`heading` 变化（转向）、`current_task` 变为 `chassis:forward` 等；
6. 进阶：连续调用组合指令，让小车"前进两步、右转、再前进"。

### 核心代码模块
- API：`POST /api/robot/chassis/move`，请求体 `{command, speed}`；
- `command` 取值：`forward` / `backward` / `left` / `right` / `stop`；
- `speed`：浮点数，默认 `0.5`，范围 `0~1`（后端会 clamp 到 `[0.1, 1.0]` 作为步长）；
- 实现：`Simulator.move_chassis` → `SimulatedChassis.move_forward / ...`；
- 行为（仿真简化）：
  - `forward`：`position.y += speed`；`current_task = "chassis:forward"`
  - `backward`：`position.y -= speed`
  - `left`：`heading = (heading - 90) % 360`
  - `right`：`heading = (heading + 90) % 360`
  - `stop`：`current_task = "idle"`

### 预期现象
- 点击按钮后，状态面板的位置/朝向/当前任务立即更新；
- 地图上代表小车的"车"字位置随之移动（前进向上）；
- 日志区出现"底盘前进，速度 0.6"等记录。

### 常见问题
| 问题 | 原因 | 解决 |
|------|------|------|
| 点按钮小车不动 | 后端未启动 / 跨域被拦 | 确认后端在 8000 端口、CORS 已配置 |
| 前进后 x 没变 | 仿真里前进只改 y（设计如此） | 要改 x 需先转向再前进（教学点：朝向与移动分离） |
| 转向后位置没变 | 转向只改朝向，不移动（设计如此） | 转向后再调用前进 |
| 真实小车（B 档）方向反了 | 电机接线极性 | 交换电机两根线或软件取反 |
| speed 设很大没效果 | 后端 clamp 到 1.0 | 步长上限就是 1.0 |

### 拓展任务
- 用脚本连续调用实现"走一个正方形"轨迹（前进→右转→前进→右转…）；
- 用键盘 WASD 通过脚本实时控制小车；
- 给小车加"接近地图边界自动停止"的逻辑（读 `position` 判断）。

### 验收标准
- [ ] Web 控制台能发送 5 种控制指令；
- [ ] 仿真小车状态（位置/朝向/任务）能正确响应；
- [ ] 能用 Python 脚本调用 `/api/robot/chassis/move` 复现控制；
- [ ] （B 档）真实小车能按指令运动，方向正确。

---

## 实验 2：桌面地图路径规划

> 对应课程：lesson-06 / 训练营第 2 周 / 示例：`examples/path_planning_demo.py`

### 实验目标
让新人理解栅格地图、坐标系、障碍物，并用 **BFS** 规划一条从起点到终点的无碰撞路径。
（A* 作为本实验的拓展任务和后续升级。）

### 前置知识
- 实验 1；
- 二维坐标、栅格地图概念；
- （可选）队列数据结构基础。

### 所需硬件
- **A 档即可**（仿真地图完全够用）。

### 所需软件
- Web 控制台（地图可视化）、`GridPlanner`（BFS）。

### 实验步骤
1. 在控制台"路径规划"面板，确认默认起点 `(0,0)`、终点 `(8,8)`；
2. 地图上已有障碍 `{3,3}、{3,4}、{4,4}`，点击"生成路径"；
3. 观察地图上高亮显示的路径点；
4. 用 Python 调用 API 复现：
   ```python
   # examples/path_planning_demo.py 的核心
   result = post("/api/planner/path", {
       "start": {"x": 0, "y": 0},
       "goal": {"x": 8, "y": 8},
       "obstacles": [{"x": 3, "y": 3}, {"x": 3, "y": 4}, {"x": 4, "y": 4}],
   })
   print(result["path"])   # 一串 {x,y} 路径点
   ```
5. 改变起点/终点或增减障碍，观察路径变化；
6. 故意把终点用障碍围死，观察返回的 `400` 错误（`PathNotFoundError`）。

### 核心代码模块
- API：`POST /api/planner/path`，请求体 `{start:{x,y}, goal:{x,y}, obstacles?:[{x,y}]}`；
- 返回：`{path: [{x,y}, ...], state}`；
- 实现：`Simulator.plan_path` → `GridPlanner.plan_path`（**BFS，4 邻域**）；
- 边界：起/终点越界报 `400`；起/终点被阻挡或无路径报 `400`（`PathNotFoundError`）；
- 坐标范围：`0 <= x,y <= 9`（10×10 地图）。

### 预期现象
- 路径能绕开障碍连接起点与终点；
- 地图上路径格子被高亮；
- 把终点围死后，前端显示错误提示，后端返回 400。

### 常见问题
| 问题 | 原因 | 解决 |
|------|------|------|
| 规划不出路径（400） | 起终点被障碍包围或不可达 | 检查地图连通性，留出通道 |
| 路径"贴墙"不安全 | 没有膨胀（inflation） | 给障碍加一层安全边距（拓展） |
| 坐标超 9 报错 | 越出 10×10 地图 | x、y 限制在 0~9 |
| 想要更"直"的路径 | BFS 转角多 | 实现 A*（拓展任务） |

### 拓展任务
- **实现 A\***：在 `GridPlanner` 基础上加入启发函数（曼哈顿距离）与优先队列，对比路径差异；
- 给路径做"平滑"（减少转角）；
- 实现动态障碍（规划途中出现新障碍需重规划）。

### 验收标准
- [ ] 能在地图上设置起点、终点并使用默认障碍；
- [ ] 系统能输出一条无碰撞路径并在地图高亮；
- [ ] 终点不可达时能正确报错而非崩溃；
- [ ] 理解当前是 BFS，并能讲出 A* 的改进方向。

---

## 实验 3：视觉目标识别

> 对应课程：lesson-04、lesson-05 / 训练营第 2 周 / 示例：`examples/vision_demo.py`

### 实验目标
让新人理解"视觉识别"在机器人系统中的角色：把图像/场景变成**带坐标的目标列表**，
供下游（规划、抓取）使用。

> ⚠️ **当前 MVP 的视觉是 `SimpleVision`**：它直接返回仿真里预设的目标列表
>（`red_cube`、`blue_cube` 的颜色与坐标），用于打通"感知→下游"的数据流。
> 真实的 OpenCV（HSV 颜色分割、轮廓检测）作为教学概念讲解，并在后续/B 档接入真实摄像头。

### 前置知识
- Python 基础；
- 坐标系基础；
- （概念）图像就是像素矩阵、HSV 颜色空间。

### 所需硬件
- **A 档**：无摄像头，用 `SimpleVision` 模拟；
- **B 档**：USB 摄像头 + 彩色目标块（后续接入真实 OpenCV）。

### 所需软件
- `SimpleVision`（当前）、OpenCV（后续/B 档）。

### 实验步骤
1. 调用视觉 API，获取当前目标列表：
   ```python
   # examples/vision_demo.py 的核心
   from api_client import get, print_json
   result = get("/api/vision/objects")
   print_json("模拟视觉识别结果", result)
   ```
2. 观察返回的目标：每个目标含 `id / name / color / x / y / status`；
3. 在控制台地图上对照目标位置（红色方块在 6,2；蓝色方块在 8,7）；
4. 抓取某个目标后（实验 4），再次调用视觉 API，观察其 `status` 从 `available` 变为 `grabbed`；
5. （概念讲解）讨论真实摄像头场景下，如何用 OpenCV 的 HSV 分割 + 轮廓检测得到同样的 `{color, x, y}`。

### 核心代码模块
- API：`GET /api/vision/objects`，返回 `{objects: [{id,name,color,x,y,status}, ...]}`；
- 实现：`Simulator.detect_objects` → `SimpleVision.detect_objects`（返回 `objects` 副本）；
- 目标字段：`status ∈ {available, grabbed}`；
- （后续）真实实现：`cv2.cvtColor → inRange → findContours → moments`，输出与当前同结构的坐标。

### 预期现象
- 返回红、蓝两个目标及其坐标；
- 抓取后该目标 `status` 变为 `grabbed`；
- 控制台地图上目标位置与坐标一致。

### 常见问题
| 问题 | 原因 | 解决 |
|------|------|------|
| 想接真实摄像头但没接口 | MVP 仅模拟 | 第二阶段实现真实 `Vision` 后端，接口不变 |
| 目标坐标和地图对不上 | 地图 y 轴从下往上渲染 | 注意地图渲染 y 从高到低，逻辑坐标 y 向上为正 |
| 不理解为什么要"模拟视觉" | 为了先打通数据流 | 先用模拟跑通全链路，再替换为真实算法 |

### 拓展任务
- 实现一个真实 OpenCV 版 `Vision`：USB 摄像头读图 → HSV 分割 → 输出 `{color,x,y}`；
- 估计目标大小（像素面积 → 距离粗估）；
- 同时识别多种颜色。

### 验收标准
- [ ] 能调用 `/api/vision/objects` 获取目标列表；
- [ ] 能在控制台/地图上看到目标位置与颜色；
- [ ] 抓取后能观察到 `status` 变化；
- [ ] 能讲清"模拟视觉"与"真实 OpenCV"的关系和替换方式。

---

## 实验 4：机械臂目标抓取

> 对应课程：lesson-07 / 训练营第 3 周 / 示例：`examples/arm_grab_demo.py`

### 实验目标
让新人理解机械臂控制与任务执行：通过统一接口抓取目标，观察机械臂状态与目标状态的变化。

> ⚠️ **当前 MVP 的机械臂只有 `grab(object_id)` 和 `reset()` 两个动作**：
> - `grab`：夹爪闭合、`holding` 设为目标、目标 `status` 变为 `grabbed`；
> - `reset`：机械臂复位、夹爪张开、释放持有物。
> "放置到指定区域""按关节角度运动"等为后续扩展（见 lesson-07）。

### 前置知识
- 实验 1（控制概念）；
- 坐标系基础；
- （可选）舵机/角度的概念。

### 所需硬件
- **A 档**：仿真机械臂即可；
- **B 档**：4 自由度舵机机械臂（后续接入）。

### 所需软件
- `SimulatedArm`（当前）、舵机控制（B 档后续）。

### 实验步骤
1. 在控制台"机械臂任务"面板，下拉选择目标（默认 `red_cube`），点击"模拟抓取"；
2. 观察状态面板：`机械臂` 变为 `holding / closed`，目标 `status` 变为 `grabbed`；
3. 用 Python 调用 API 复现：
   ```python
   # examples/arm_grab_demo.py 的核心
   result = post("/api/robot/arm/grab", {"object_id": "red_cube"})
   print_json("机械臂抓取结果", result)
   ```
4. 对同一目标再次抓取，观察返回"目标已被抓取"（404）；
5. 调用 `/api/robot/reset` 复位，观察机械臂回到 `ready / open`、`holding` 清空；
6. （进阶）结合实验 3，先识别目标再抓取（见综合实验）。

### 核心代码模块
- API：
  - `POST /api/robot/arm/grab`，请求体 `{object_id}`，成功返回 `{result, state}`，失败 404；
  - `POST /api/robot/reset`，复位整个仿真；
- 实现：`Simulator.grab_object` → `SimulatedArm.grab`；
- 状态变化：
  - 成功：`arm.status = holding`、`arm.gripper = closed`、`arm.holding = object_id`、`object.status = grabbed`、`current_task = arm:grab:{id}`；
  - 失败原因：目标不存在 / 目标已被抓取。

### 预期现象
- 抓取成功后状态面板与地图目标状态同步更新；
- 重复抓取同一目标会被拒绝；
- 复位后一切回到初始。

### 常见问题
| 问题 | 原因 | 解决 |
|------|------|------|
| 抓取返回 404 | 目标已被抓取或 id 错误 | 先 reset 或检查 object_id |
| 想要"放置"功能 | MVP 未实现 | 当前用 reset 释放；放置到指定区域为后续扩展 |
| 真实舵机臂抓不稳（B 档） | 实物精度不足 | 用预设动作 + 固定目标点规避（见风险文档） |

### 拓展任务
- 给 `Arm` 增加 `place(zone)` / `open_gripper()` 方法（需改后端，属功能扩展）；
- 实现按关节角度控制（B 档舵机）；
- 连续抓取红、蓝两个目标。

### 验收标准
- [ ] 能通过 `/api/robot/arm/grab` 抓取红/蓝方块；
- [ ] 抓取后 `arm.holding` 与目标 `status` 正确更新；
- [ ] 重复抓取与不存在目标能被正确拒绝；
- [ ] 能用 `/api/robot/reset` 复位。

---

## 实验 5：文字指令综合任务

> 对应课程：lesson-08、lesson-09、lesson-10 / 训练营第 4 周 / 示例：`examples/integrated_task_demo.py`

### 实验目标
让新人理解多模态交互与任务编排：把一段文字，
拆解为"感知 + 规划 + 执行"的完整具身智能任务。

> 当前 MVP 用**规则匹配**解析指令（关键词包含），不依赖大模型；后续可替换为 ASR / LLM。

### 前置知识
- 实验 1~4；
- 简单任务状态机概念（lesson-08）；
- 指令解析的概念（lesson-09）。

### 所需硬件
- **A 档**：仿真即可完成全部综合任务。

### 所需软件
- `TaskManager`（指令解析）、前 4 个实验的全部模块、控制台文字输入框。

### 实验步骤
1. 在控制台"文字指令"输入框输入指令，点"执行"，例如：
   - `前进` / `后退` / `左转` / `右转` / `停止`
   - `抓取红色方块` / `抓取蓝色方块`
   - `移动到 A 点`
   - `开始综合挑战`
2. 观察返回的 `intent`（意图标签）与状态变化；
3. 用 Python 调用 API 复现：
   ```python
   result = post("/api/task/command", {"text": "开始综合挑战"})
   print(result["intent"])   # integrated_challenge
   ```
4. 查看 `综合挑战` 的内部流程：规划路径 `(0,0)→(6,2)`（到红色方块）+ 抓取 `red_cube`；
5. 输入不支持的指令（如"飞起来"），观察返回 `400`（`unsupported command text`）。

### 核心代码模块
- API：`POST /api/task/command`，请求体 `{text}`，返回 `{intent, result, state?}`；
- 实现：`TaskManager.execute_command`（关键词匹配 → 意图 → 调用对应模块）；
- 支持的指令与意图（**当前真实支持集**）：

| 文字关键词（中/英） | intent | 实际动作 |
|--------------------|--------|----------|
| 前进 / forward | `move_forward` | 底盘前进 |
| 后退 / backward | `move_backward` | 底盘后退 |
| 左转 / left | `turn_left` | 底盘左转 |
| 右转 / right | `turn_right` | 底盘右转 |
| 停止 / stop | `stop` | 底盘停止 |
| 红色 / 红方块 / red | `grab_red_cube` | 抓取 red_cube |
| 蓝色 / 蓝方块 / blue | `grab_blue_cube` | 抓取 blue_cube |
| 移动到 / 目标点 / a点 / move | `move_to_goal` | 规划 (0,0)→(8,8) |
| 综合挑战 / challenge | `integrated_challenge` | 规划 (0,0)→(6,2) + 抓 red_cube |

### 预期现象
- 输入一句文字，系统返回对应 `intent` 并执行动作；
- `综合挑战` 一次性完成"规划到红色方块 + 抓取"；
- 不支持的指令返回 400 而非崩溃。

### 常见问题
| 问题 | 原因 | 解决 |
|------|------|------|
| 指令解析不出来 | 关键词未命中 | 用上表的关键词；扩展可改 `TaskManager` 规则 |
| 综合挑战没"走过去" | 当前只规划路径+抓取，未自动行驶 | 拓展：拿到 path 后循环调用底盘移动 |
| 想要语音输入 | MVP 仅文字 | 后续接入 ASR（Whisper 等） |

### 拓展任务
- 拿到 `综合挑战` 的 `path` 后，循环调用底盘移动让小车真正沿路径走完；
- 支持组合指令（"先抓红色，再抓蓝色"）；
- 接入真实语音输入（后续阶段）。

### 验收标准
- [ ] 控制台支持文字指令输入；
- [ ] 至少能正确执行上表 9 类指令并返回正确 `intent`；
- [ ] 不支持的指令能被友好拒绝（400）；
- [ ] `综合挑战` 能完成"规划 + 抓取"。

---

## 实验全景与依赖关系

```
实验1 基础控制 ──┐
                ├──▶ 实验2 路径规划(BFS) ──┐
实验3 视觉识别 ──┤                          ├──▶ 实验5 综合指令任务
                ├──▶ 实验4 机械臂抓取 ──────┘
        （统一 API + RobotSimulator 贯穿全部实验）
```

- 实验 1 是地基（控制）；
- 实验 2、3、4 是三条能力线（规划 / 感知 / 执行）；
- 实验 5 把三条线收口成完整的具身智能任务。

## 验收汇总（对应 `agent.md` 第 15 节 MVP 验收）

| 验收项 | 对应实验 | API |
|--------|----------|-----|
| 控制台可见状态、能控制小车 | 实验 1 | `/api/robot/chassis/move` |
| 地图设点生成路径 | 实验 2 | `/api/planner/path` |
| 跑通视觉识别 demo | 实验 3 | `/api/vision/objects` |
| 跑通机械臂抓取模拟 | 实验 4 | `/api/robot/arm/grab` |
| 输入文字指令触发任务 | 实验 5 | `/api/task/command` |

> 完成 5 个实验，即满足 MVP"能演示"的全部验收点。当前 MVP 已实现上述全部 API。
