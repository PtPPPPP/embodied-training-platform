class TaskManager:
    def __init__(self, simulator: "RobotSimulator"):
        self.simulator = simulator

    def execute_command(self, text: str) -> dict:
        command = text.strip().lower()
        if not command:
            raise ValueError("command text is empty")

        if self._contains(command, ["前进", "forward"]):
            state = self.simulator.move_chassis("forward", 0.5)
            return {"intent": "move_forward", "result": state}
        if self._contains(command, ["后退", "backward"]):
            state = self.simulator.move_chassis("backward", 0.5)
            return {"intent": "move_backward", "result": state}
        if self._contains(command, ["左转", "left"]):
            state = self.simulator.move_chassis("left", 0.5)
            return {"intent": "turn_left", "result": state}
        if self._contains(command, ["右转", "right"]):
            state = self.simulator.move_chassis("right", 0.5)
            return {"intent": "turn_right", "result": state}
        if self._contains(command, ["停止", "stop"]):
            state = self.simulator.move_chassis("stop", 0)
            return {"intent": "stop", "result": state}
        if self._contains(command, ["红色", "红方块", "red"]):
            result = self.simulator.grab_object("red_cube")
            return {"intent": "grab_red_cube", "result": result, "state": self.simulator.get_state()}
        if self._contains(command, ["蓝色", "蓝方块", "blue"]):
            result = self.simulator.grab_object("blue_cube")
            return {"intent": "grab_blue_cube", "result": result, "state": self.simulator.get_state()}
        if self._contains(command, ["移动到", "目标点", "a点", "a 点", "move"]):
            path = self.simulator.plan_path({"x": 0, "y": 0}, {"x": 8, "y": 8})
            return {"intent": "move_to_goal", "result": {"path": path}, "state": self.simulator.get_state()}
        if self._contains(command, ["综合挑战", "challenge"]):
            path = self.simulator.plan_path({"x": 0, "y": 0}, {"x": 6, "y": 2})
            grab = self.simulator.grab_object("red_cube")
            return {
                "intent": "integrated_challenge",
                "result": {"path": path, "grab": grab},
                "state": self.simulator.get_state(),
            }

        raise ValueError("unsupported command text")

    def _contains(self, text: str, keywords: list[str]) -> bool:
        return any(keyword in text for keyword in keywords)


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from robot.simulator import RobotSimulator

