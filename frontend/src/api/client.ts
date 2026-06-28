import type { CommandResult, Point, RobotState } from "../types/robot";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail ?? `请求失败：${response.status}`);
  }

  return response.json() as Promise<T>;
}

export function fetchRobotState() {
  return request<RobotState>("/api/robot/state");
}

export function moveChassis(command: string, speed: number) {
  return request<RobotState>("/api/robot/chassis/move", {
    method: "POST",
    body: JSON.stringify({ command, speed }),
  });
}

export function planPath(start: Point, goal: Point, obstacles?: Point[]) {
  return request<{ path: Point[]; state: RobotState }>("/api/planner/path", {
    method: "POST",
    body: JSON.stringify({ start, goal, obstacles }),
  });
}

export function grabObject(objectId: string) {
  return request<{ result: unknown; state: RobotState }>("/api/robot/arm/grab", {
    method: "POST",
    body: JSON.stringify({ object_id: objectId }),
  });
}

export function executeCommand(text: string) {
  return request<CommandResult>("/api/task/command", {
    method: "POST",
    body: JSON.stringify({ text }),
  });
}

export function resetRobot() {
  return request<RobotState>("/api/robot/reset", { method: "POST" });
}

