from robot.arm import SimulatedArm
from robot.chassis import SimulatedChassis
from robot.planner import GridPlanner
from robot.vision import SimpleVision


class RobotSimulator:
    def __init__(self, width: int = 10, height: int = 10):
        self.width = width
        self.height = height
        self.planner = GridPlanner(width=width, height=height)
        self.chassis = SimulatedChassis(self)
        self.arm_driver = SimulatedArm(self)
        self.vision = SimpleVision(self)
        self.reset()

    def reset(self) -> dict:
        self.position = {"x": 0.0, "y": 0.0}
        self.heading = 0
        self.current_task = "idle"
        self.arm = {"status": "ready", "gripper": "open", "holding": None}
        self.objects = [
            {"id": "red_cube", "name": "红色方块", "color": "red", "x": 6, "y": 2, "status": "available"},
            {"id": "blue_cube", "name": "蓝色方块", "color": "blue", "x": 8, "y": 7, "status": "available"},
        ]
        self.obstacles = [{"x": 3, "y": 3}, {"x": 3, "y": 4}, {"x": 4, "y": 4}]
        self.path: list[dict[str, int]] = []
        self.logs: list[str] = []
        self.add_log("仿真环境已重置")
        return self.get_state()

    def get_state(self) -> dict:
        return {
            "map": {"width": self.width, "height": self.height},
            "position": self.position.copy(),
            "heading": self.heading,
            "current_task": self.current_task,
            "arm": self.arm.copy(),
            "objects": [item.copy() for item in self.objects],
            "obstacles": [item.copy() for item in self.obstacles],
            "path": [item.copy() for item in self.path],
            "logs": list(self.logs[-30:]),
        }

    def move_chassis(self, command: str, speed: float = 0.5) -> dict:
        speed = max(0.0, min(float(speed), 1.0))
        actions = {
            "forward": self.chassis.move_forward,
            "backward": self.chassis.move_backward,
            "left": self.chassis.turn_left,
            "right": self.chassis.turn_right,
        }
        if command == "stop":
            self.chassis.stop()
        elif command in actions:
            actions[command](speed)
        else:
            raise ValueError(f"unsupported chassis command: {command}")
        return self.get_state()

    def plan_path(self, start: dict, goal: dict, obstacles: list[dict] | None = None) -> list[dict]:
        active_obstacles = obstacles if obstacles is not None else self.obstacles
        self.path = self.planner.plan_path(start=start, goal=goal, obstacles=active_obstacles)
        self.current_task = "planner:path"
        self.add_log(f"路径规划完成：{len(self.path)} 个点")
        return self.path

    def grab_object(self, object_id: str) -> dict:
        return self.arm_driver.grab(object_id)

    def detect_objects(self) -> list[dict]:
        return self.vision.detect_objects()

    def find_object(self, object_id: str) -> dict | None:
        return next((item for item in self.objects if item["id"] == object_id), None)

    def add_log(self, message: str) -> None:
        self.logs.append(message)

    def clamp(self, value: float, low: float, high: float) -> float:
        return max(low, min(value, high))

