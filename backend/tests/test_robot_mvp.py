import unittest

from robot.planner import GridPlanner, PathNotFoundError
from robot.simulator import RobotSimulator
from robot.task_manager import TaskManager


class GridPlannerTest(unittest.TestCase):
    def test_plans_path_around_obstacles(self):
        planner = GridPlanner(width=5, height=5)

        path = planner.plan_path(
            start={"x": 0, "y": 0},
            goal={"x": 4, "y": 4},
            obstacles=[{"x": 1, "y": 0}, {"x": 1, "y": 1}, {"x": 1, "y": 2}],
        )

        self.assertEqual(path[0], {"x": 0, "y": 0})
        self.assertEqual(path[-1], {"x": 4, "y": 4})
        self.assertNotIn({"x": 1, "y": 0}, path)

    def test_raises_clear_error_when_path_is_blocked(self):
        planner = GridPlanner(width=3, height=3)

        with self.assertRaises(PathNotFoundError):
            planner.plan_path(
                start={"x": 0, "y": 0},
                goal={"x": 2, "y": 2},
                obstacles=[{"x": 1, "y": 0}, {"x": 0, "y": 1}],
            )


class RobotSimulatorTest(unittest.TestCase):
    def test_chassis_command_changes_robot_state(self):
        simulator = RobotSimulator()

        before = simulator.get_state()["position"]
        state = simulator.move_chassis("forward", 1.0)

        self.assertGreater(state["position"]["y"], before["y"])
        self.assertEqual(state["current_task"], "chassis:forward")
        self.assertGreater(len(state["logs"]), 0)

    def test_arm_grab_marks_object_as_grabbed(self):
        simulator = RobotSimulator()

        result = simulator.grab_object("red_cube")
        state = simulator.get_state()

        self.assertTrue(result["success"])
        red_cube = next(item for item in state["objects"] if item["id"] == "red_cube")
        self.assertEqual(red_cube["status"], "grabbed")
        self.assertEqual(state["arm"]["holding"], "red_cube")


class TaskManagerTest(unittest.TestCase):
    def test_text_commands_trigger_supported_actions(self):
        simulator = RobotSimulator()
        manager = TaskManager(simulator)

        commands = ["前进", "后退", "左转", "右转", "停止", "抓取红色方块"]
        intents = [manager.execute_command(text)["intent"] for text in commands]

        self.assertEqual(
            intents,
            [
                "move_forward",
                "move_backward",
                "turn_left",
                "turn_right",
                "stop",
                "grab_red_cube",
            ],
        )


if __name__ == "__main__":
    unittest.main()
