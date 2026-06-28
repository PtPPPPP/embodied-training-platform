class SimulatedChassis:
    def __init__(self, simulator: "RobotSimulator"):
        self.simulator = simulator

    def move_forward(self, speed: float):
        self._move("forward", dy=1, speed=speed)

    def move_backward(self, speed: float):
        self._move("backward", dy=-1, speed=speed)

    def turn_left(self, speed: float):
        self.simulator.heading = (self.simulator.heading - 90) % 360
        self.simulator.current_task = "chassis:left"
        self.simulator.add_log(f"底盘左转，速度 {speed:.2f}")

    def turn_right(self, speed: float):
        self.simulator.heading = (self.simulator.heading + 90) % 360
        self.simulator.current_task = "chassis:right"
        self.simulator.add_log(f"底盘右转，速度 {speed:.2f}")

    def stop(self):
        self.simulator.current_task = "idle"
        self.simulator.add_log("底盘停止")

    def _move(self, command: str, dy: int, speed: float):
        step = max(0.1, min(float(speed), 1.0))
        position = self.simulator.position
        position["y"] = self.simulator.clamp(position["y"] + dy * step, 0, self.simulator.height - 1)
        self.simulator.current_task = f"chassis:{command}"
        self.simulator.add_log(f"底盘{self._label(command)}，速度 {speed:.2f}")

    def _label(self, command: str) -> str:
        return {"forward": "前进", "backward": "后退"}[command]


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from robot.simulator import RobotSimulator

