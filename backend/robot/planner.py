from collections import deque
from typing import Iterable


Point = dict[str, int]


class PathNotFoundError(ValueError):
    """Raised when no valid grid path exists."""


class GridPlanner:
    def __init__(self, width: int = 10, height: int = 10):
        self.width = width
        self.height = height

    def plan_path(
        self,
        start: Point,
        goal: Point,
        obstacles: Iterable[Point] | None = None,
    ) -> list[Point]:
        start_key = self._to_key(start)
        goal_key = self._to_key(goal)
        blocked = {self._to_key(item) for item in obstacles or []}

        self._validate_point(start_key, "start")
        self._validate_point(goal_key, "goal")

        if start_key in blocked:
            raise PathNotFoundError("start point is blocked")
        if goal_key in blocked:
            raise PathNotFoundError("goal point is blocked")

        queue: deque[tuple[int, int]] = deque([start_key])
        came_from: dict[tuple[int, int], tuple[int, int] | None] = {start_key: None}

        while queue:
            current = queue.popleft()
            if current == goal_key:
                return self._build_path(came_from, current)

            for neighbor in self._neighbors(current):
                if neighbor in blocked or neighbor in came_from:
                    continue
                came_from[neighbor] = current
                queue.append(neighbor)

        raise PathNotFoundError("no path found")

    def _neighbors(self, point: tuple[int, int]) -> list[tuple[int, int]]:
        x, y = point
        candidates = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        return [item for item in candidates if self._in_bounds(item)]

    def _in_bounds(self, point: tuple[int, int]) -> bool:
        x, y = point
        return 0 <= x < self.width and 0 <= y < self.height

    def _validate_point(self, point: tuple[int, int], name: str) -> None:
        if not self._in_bounds(point):
            raise ValueError(f"{name} point is outside map bounds")

    def _build_path(
        self,
        came_from: dict[tuple[int, int], tuple[int, int] | None],
        current: tuple[int, int],
    ) -> list[Point]:
        path: list[tuple[int, int]] = []
        while current is not None:
            path.append(current)
            current = came_from[current]
        path.reverse()
        return [{"x": x, "y": y} for x, y in path]

    def _to_key(self, point: Point) -> tuple[int, int]:
        return int(point["x"]), int(point["y"])

