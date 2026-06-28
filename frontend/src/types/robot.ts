export type Point = {
  x: number;
  y: number;
};

export type SimObject = Point & {
  id: string;
  name: string;
  color: "red" | "blue" | string;
  status: string;
};

export type RobotState = {
  map: {
    width: number;
    height: number;
  };
  position: Point;
  heading: number;
  current_task: string;
  arm: {
    status: string;
    gripper: string;
    holding: string | null;
  };
  objects: SimObject[];
  obstacles: Point[];
  path: Point[];
  logs: string[];
};

export type CommandResult = {
  intent: string;
  result: unknown;
  state?: RobotState;
};

