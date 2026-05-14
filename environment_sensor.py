import cv2
import numpy as np
import threading
import time
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
from enum import Enum

class ObstacleType(Enum):
    WALL = "wall"
    FLOOR = "floor"
    CEILING = "ceiling"
    OBJECT = "object"
    PERSON = "person"
    VEHICLE = "vehicle"
    STAIRS = "stairs"
    DOOR = "door"
    UNKNOWN = "unknown"

class DangerLevel(Enum):
    SAFE = 0
    CAUTION = 1
    WARNING = 2
    DANGER = 3

@dataclass
class Obstacle:
    #Obstacle information
    type: ObstacleType
    danger_level: DangerLevel
    distance: float  # meters
    direction: str  # left, right, center, etc.
    position: Tuple[int, int]  # (x, y) in frame
    size: Tuple[int, int]  # (width, height)
    confidence: float

@dataclass
class Path:
    """Navigation path information"""
    clear: bool
    direction: str
    width: float  # meters
    obstacles: List[Obstacle]
    recommended_action: str

class EnvironmentSensor:
    def __init__(self, camera_index: int = 0):

        self.camera_index = camera_index
        self.cap = None
        self.running = False
        self.thread = None

        self.current_frame = None
        self.frame_lock = threading.Lock()

        self.obstacles: List[Obstacle] = []
        self.obstacle_lock = threading.Lock()

        self.current_path: Optional[Path] = None
        self.path_lock = threading.Lock()

        self.focal_length = 500  # pixels
        self.real_object_width = 0.5  # meters (average object width)

        self.danger_thresholds = {
            DangerLevel.SAFE: 3.0,  # meters
            DangerLevel.CAUTION: 2.0,
            DangerLevel.WARNING: 1.0,
            DangerLevel.DANGER: 0.5
        }

    def start(self):
        if self.running:
            return

        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            if not self.cap.isOpened():
                print(" Failed to open camera")
                return

            self.running = True
            self.thread = threading.Thread(target=self._run_loop, daemon=True)
            self.thread.start()

            print(" Environment sensing started")

        except Exception as e:
            print(f" Failed to start environment sensing: {e}")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        if self.cap:
            self.cap.release()
        print(" Environment sensing stopped")

    def _run_loop(self):
        while self.running:
            try:
                ret, frame = self.cap.read()
                if not ret:
                    time.sleep(0.1)
                    continue

                with self.frame_lock:
                    self.current_frame = frame.copy()

                detected = self._detect_obstacles(frame)

                with self.obstacle_lock:
                    self.obstacles = detected

                path = self._analyze_path(frame, detected)

                with self.path_lock:
                    self.current_path = path

                time.sleep(0.05)

            except Exception as e:
                print(f" Sensing error: {e}")
                time.sleep(0.1)

    def _detect_obstacles(self, frame: np.ndarray) -> List[Obstacle]:

        obstacles = []

        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            edges = cv2.Canny(gray, 50, 150)

            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            height, width = frame.shape[:2]
            center_x = width // 2

            nav_zone_top = int(height * 0.15)
            nav_zone_bottom = int(height * 0.85)

            for contour in contours:
                area = cv2.contourArea(contour)
                if area < 1000:
                    continue

                x, y, w, h = cv2.boundingRect(contour)

                if y < nav_zone_top or (y + h) > nav_zone_bottom:
                    continue

                distance = self._estimate_distance(w)

                danger_level = self._get_danger_level(distance)

                if x + w < center_x - 50:
                    direction = "left"
                elif x > center_x + 50:
                    direction = "right"
                else:
                    direction = "center"

                obstacle_type = self._classify_obstacle(frame, x, y, w, h)

                obstacle = Obstacle(
                    type=obstacle_type,
                    danger_level=danger_level,
                    distance=distance,
                    direction=direction,
                    position=(x + w // 2, y + h // 2),
                    size=(w, h),
                    confidence=0.7
                )

                obstacles.append(obstacle)

            obstacles.sort(key=lambda o: o.distance)

            obstacles = obstacles[:10]

        except Exception as e:
            print(f" Obstacle detection error: {e}")

        return obstacles

    def _estimate_distance(self, pixel_width: int) -> float:

        if pixel_width <= 0:
            return 10.0  # Far away

        distance = (self.real_object_width * self.focal_length) / pixel_width

        return max(0.1, min(distance, 10.0))

    def _get_danger_level(self, distance: float) -> DangerLevel:
        if distance >= self.danger_thresholds[DangerLevel.SAFE]:
            return DangerLevel.SAFE
        elif distance >= self.danger_thresholds[DangerLevel.CAUTION]:
            return DangerLevel.CAUTION
        elif distance >= self.danger_thresholds[DangerLevel.WARNING]:
            return DangerLevel.WARNING
        else:
            return DangerLevel.DANGER

    def _classify_obstacle(self, frame: np.ndarray, x: int, y: int, w: int, h: int) -> ObstacleType:

        roi = frame[y:y+h, x:x+w]

        avg_color = np.mean(roi, axis=(0, 1))

        height, width = frame.shape[:2]

        if y + h > height * 0.8:
            return ObstacleType.FLOOR

        if y < height * 0.2:
            return ObstacleType.CEILING

        aspect_ratio = h / w if w > 0 else 0
        if aspect_ratio > 2.0:
            return ObstacleType.DOOR

        return ObstacleType.OBJECT

    def _analyze_path(self, frame: np.ndarray, obstacles: List[Obstacle]) -> Path:

        height, width = frame.shape[:2]

        center_obstacles = [o for o in obstacles if o.direction == "center" and o.danger_level in [DangerLevel.WARNING, DangerLevel.DANGER]]

        if center_obstacles:
            closest = center_obstacles[0]

            left_obstacles = [o for o in obstacles if o.direction == "left"]
            right_obstacles = [o for o in obstacles if o.direction == "right"]

            if len(left_obstacles) < len(right_obstacles):
                direction = "right"
                recommended_action = f"Obstacle ahead {closest.distance:.1f} meters. Turn right."
            else:
                direction = "left"
                recommended_action = f"Obstacle ahead {closest.distance:.1f} meters. Turn left."

            return Path(
                clear=False,
                direction=direction,
                width=0.0,
                obstacles=center_obstacles,
                recommended_action=recommended_action
            )

        caution_obstacles = [o for o in obstacles if o.danger_level == DangerLevel.CAUTION and o.direction == "center"]

        if caution_obstacles:
            closest = caution_obstacles[0]
            return Path(
                clear=True,
                direction="center",
                width=2.0,
                obstacles=caution_obstacles,
                recommended_action=f"Caution: Object {closest.distance:.1f} meters ahead."
            )

        return Path(
            clear=True,
            direction="center",
            width=3.0,
            obstacles=[],
            recommended_action="Path clear. Continue straight."
        )

    def get_current_frame(self) -> Optional[np.ndarray]:
        with self.frame_lock:
            return self.current_frame.copy() if self.current_frame is not None else None

    def get_obstacles(self) -> List[Obstacle]:
        with self.obstacle_lock:
            return list(self.obstacles)

    def get_path(self) -> Optional[Path]:
        with self.path_lock:
            return self.current_path

    def get_guidance(self) -> str:

        path = self.get_path()

        if not path:
            return "Unable to analyze path. Please check camera."

        if not path.clear:
            return path.recommended_action

        obstacles = self.get_obstacles()
        nearby = [o for o in obstacles if o.distance < 2.0]

        if nearby:
            closest = nearby[0]
            if closest.danger_level == DangerLevel.DANGER:
                return f"STOP! {closest.type.value} {closest.distance:.1f} meters to your {closest.direction}."
            elif closest.danger_level == DangerLevel.WARNING:
                return f"Warning: {closest.type.value} {closest.distance:.1f} meters to your {closest.direction}."

        return path.recommended_action

environment_sensor = EnvironmentSensor()
