import { useEffect, useMemo, useState } from "react";
import {
  executeCommand,
  fetchRobotState,
  grabObject,
  moveChassis,
  planPath,
  resetRobot,
} from "./api/client";
import type { Point, RobotState, SimObject } from "./types/robot";

const DEFAULT_START = { x: 0, y: 0 };
const DEFAULT_GOAL = { x: 8, y: 8 };

function App() {
  const [state, setState] = useState<RobotState | null>(null);
  const [speed, setSpeed] = useState(0.5);
  const [start, setStart] = useState<Point>(DEFAULT_START);
  const [goal, setGoal] = useState<Point>(DEFAULT_GOAL);
  const [targetId, setTargetId] = useState("red_cube");
  const [commandText, setCommandText] = useState("抓取红色方块");
  const [commandResult, setCommandResult] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    runAction(() => fetchRobotState());
  }, []);

  async function runAction(action: () => Promise<RobotState>) {
    setLoading(true);
    setError("");
    try {
      const nextState = await action();
      setState(nextState);
    } catch (err) {
      setError(err instanceof Error ? err.message : "操作失败");
    } finally {
      setLoading(false);
    }
  }

  async function handlePlanPath() {
    await runAction(async () => {
      const response = await planPath(start, goal, state?.obstacles);
      return response.state;
    });
  }

  async function handleGrab() {
    await runAction(async () => {
      const response = await grabObject(targetId);
      return response.state;
    });
  }

  async function handleCommand() {
    setLoading(true);
    setError("");
    try {
      const response = await executeCommand(commandText);
      setCommandResult(`intent: ${response.intent}`);
      if (response.state) {
        setState(response.state);
      } else {
        const maybeState = response.result as RobotState;
        if (maybeState?.map) {
          setState(maybeState);
        } else {
          setState(await fetchRobotState());
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "指令执行失败");
    } finally {
      setLoading(false);
    }
  }

  const objects = state?.objects ?? [];

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <h1>桌面具身智能训练平台</h1>
          <p>无真实硬件也能演示的小车、路径规划、目标识别和机械臂抓取闭环。</p>
        </div>
        <button className="secondary-button" onClick={() => runAction(resetRobot)} disabled={loading}>
          重置仿真
        </button>
      </header>

      {error && <div className="error-banner">{error}</div>}

      <section className="workspace">
        <div className="left-column">
          <StatusPanel state={state} loading={loading} />

          <section className="panel">
            <h2>小车控制</h2>
            <label className="field">
              速度
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={speed}
                onChange={(event) => setSpeed(Number(event.target.value))}
              />
              <span>{speed.toFixed(1)}</span>
            </label>
            <div className="control-grid">
              <button onClick={() => runAction(() => moveChassis("forward", speed))}>前进</button>
              <button onClick={() => runAction(() => moveChassis("left", speed))}>左转</button>
              <button className="stop-button" onClick={() => runAction(() => moveChassis("stop", 0))}>
                停止
              </button>
              <button onClick={() => runAction(() => moveChassis("right", speed))}>右转</button>
              <button onClick={() => runAction(() => moveChassis("backward", speed))}>后退</button>
            </div>
          </section>

          <section className="panel">
            <h2>路径规划</h2>
            <div className="two-column-form">
              <PointInputs label="起点" value={start} onChange={setStart} />
              <PointInputs label="终点" value={goal} onChange={setGoal} />
            </div>
            <button onClick={handlePlanPath}>生成路径</button>
          </section>

          <section className="panel">
            <h2>机械臂任务</h2>
            <select value={targetId} onChange={(event) => setTargetId(event.target.value)}>
              {objects.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name}（{item.status}）
                </option>
              ))}
            </select>
            <button onClick={handleGrab}>模拟抓取</button>
          </section>

          <section className="panel">
            <h2>文字指令</h2>
            <div className="command-row">
              <input value={commandText} onChange={(event) => setCommandText(event.target.value)} />
              <button onClick={handleCommand}>执行</button>
            </div>
            {commandResult && <p className="result-text">{commandResult}</p>}
          </section>
        </div>

        <div className="right-column">
          <section className="panel map-panel">
            <h2>二维桌面地图</h2>
            {state ? <MapView state={state} /> : <div className="empty">等待后端状态...</div>}
          </section>
          <section className="panel">
            <h2>最近日志</h2>
            <ul className="log-list">
              {(state?.logs ?? []).slice().reverse().map((item, index) => (
                <li key={`${item}-${index}`}>{item}</li>
              ))}
            </ul>
          </section>
        </div>
      </section>
    </main>
  );
}

function StatusPanel({ state, loading }: { state: RobotState | null; loading: boolean }) {
  return (
    <section className="panel status-panel">
      <h2>机器人状态</h2>
      <div className="status-grid">
        <span>服务</span>
        <strong>{loading ? "处理中" : "就绪"}</strong>
        <span>位置</span>
        <strong>{state ? `${state.position.x.toFixed(1)}, ${state.position.y.toFixed(1)}` : "-"}</strong>
        <span>朝向</span>
        <strong>{state ? `${state.heading}°` : "-"}</strong>
        <span>当前任务</span>
        <strong>{state?.current_task ?? "-"}</strong>
        <span>机械臂</span>
        <strong>{state ? `${state.arm.status} / ${state.arm.gripper}` : "-"}</strong>
      </div>
    </section>
  );
}

function PointInputs({
  label,
  value,
  onChange,
}: {
  label: string;
  value: Point;
  onChange: (value: Point) => void;
}) {
  return (
    <fieldset className="point-fieldset">
      <legend>{label}</legend>
      <label>
        x
        <input
          type="number"
          min="0"
          max="9"
          value={value.x}
          onChange={(event) => onChange({ ...value, x: Number(event.target.value) })}
        />
      </label>
      <label>
        y
        <input
          type="number"
          min="0"
          max="9"
          value={value.y}
          onChange={(event) => onChange({ ...value, y: Number(event.target.value) })}
        />
      </label>
    </fieldset>
  );
}

function MapView({ state }: { state: RobotState }) {
  const obstacleKeys = useMemo(() => new Set(state.obstacles.map(pointKey)), [state.obstacles]);
  const pathKeys = useMemo(() => new Set(state.path.map(pointKey)), [state.path]);
  const objectByKey = useMemo(() => {
    const map = new Map<string, SimObject>();
    state.objects.forEach((item) => map.set(pointKey(item), item));
    return map;
  }, [state.objects]);
  const robotKey = pointKey({
    x: Math.round(state.position.x),
    y: Math.round(state.position.y),
  });

  const rows = [];
  for (let y = state.map.height - 1; y >= 0; y -= 1) {
    for (let x = 0; x < state.map.width; x += 1) {
      const key = `${x},${y}`;
      const object = objectByKey.get(key);
      rows.push(
        <div
          key={key}
          className={[
            "map-cell",
            obstacleKeys.has(key) ? "obstacle-cell" : "",
            pathKeys.has(key) ? "path-cell" : "",
            object ? `object-cell ${object.color}` : "",
            robotKey === key ? "robot-cell" : "",
          ].join(" ")}
          title={`${x},${y}`}
        >
          {robotKey === key ? "车" : object ? object.name.slice(0, 1) : ""}
        </div>,
      );
    }
  }

  return (
    <div
      className="map-grid"
      style={{
        gridTemplateColumns: `repeat(${state.map.width}, minmax(28px, 1fr))`,
      }}
    >
      {rows}
    </div>
  );
}

function pointKey(point: Point) {
  return `${point.x},${point.y}`;
}

export default App;

