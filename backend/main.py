from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from robot.planner import PathNotFoundError
from robot.simulator import RobotSimulator
from robot.task_manager import TaskManager


app = FastAPI(title="桌面具身智能训练平台 MVP")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

simulator = RobotSimulator()
task_manager = TaskManager(simulator)


class Point(BaseModel):
    x: int
    y: int


class ChassisMoveRequest(BaseModel):
    command: str
    speed: float = Field(default=0.5, ge=0, le=1)


class PathRequest(BaseModel):
    start: Point
    goal: Point
    obstacles: list[Point] | None = None


class GrabRequest(BaseModel):
    object_id: str


class TextCommandRequest(BaseModel):
    text: str


@app.get("/health")
def health():
    return {"status": "ok", "service": "embodied-training-platform"}


@app.get("/api/robot/state")
def get_robot_state():
    return simulator.get_state()


@app.post("/api/robot/chassis/move")
def move_chassis(request: ChassisMoveRequest):
    try:
        return simulator.move_chassis(request.command, request.speed)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/planner/path")
def plan_path(request: PathRequest):
    try:
        path = simulator.plan_path(
            start=request.start.model_dump(),
            goal=request.goal.model_dump(),
            obstacles=[item.model_dump() for item in request.obstacles] if request.obstacles else None,
        )
        return {"path": path, "state": simulator.get_state()}
    except (ValueError, PathNotFoundError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/vision/objects")
def detect_objects():
    return {"objects": simulator.detect_objects()}


@app.post("/api/robot/arm/grab")
def grab_object(request: GrabRequest):
    result = simulator.grab_object(request.object_id)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["message"])
    return {"result": result, "state": simulator.get_state()}


@app.post("/api/task/command")
def execute_text_command(request: TextCommandRequest):
    try:
        return task_manager.execute_command(request.text)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/robot/reset")
def reset_robot():
    return simulator.reset()

