"""OpenCV display helpers for the SafeDrive HUD."""

import cv2


def draw_alert_level(image, alert_level: str, color, y_offset: int = 30):
    cv2.putText(image, f"Niveau: {alert_level}", (10, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)


def draw_eye_timer(image, remaining: float, color, y_offset: int = 60):
    cv2.putText(image, f"Temps: {remaining:.1f}s", (10, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)


def draw_yawn(image, consecutive_yawns: int, y_offset: int = 90):
    cv2.putText(image, f"BAILLEMENT! ({consecutive_yawns})", (10, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)


def draw_head_state(image, head_state: dict, y_offset: int = 120):
    parts = []
    if head_state["turned"]:
        parts.append(f"Rotation: {head_state['direction_h']}")
    if head_state["tilted"]:
        parts.append(f"Inclinaison: {head_state['direction_v']}")
    if parts:
        cv2.putText(image, " + ".join(parts), (10, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)


def draw_yawn_total(image, yawn_count: int, y_offset: int = 150):
    cv2.putText(image, f"Total B\u00e2illements: {yawn_count}", (10, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)


def draw_phone_warning(image, phone_time: float, y_offset: int = 180):
    text = f"ATTENTION: T\u00e9l\u00e9phone d\u00e9tect\u00e9! ({phone_time:.1f}s)"
    cv2.putText(image, text, (10, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)


def draw_danger_border(image, width: int, height: int, color):
    cv2.rectangle(image, (0, 0), (width, height), color, 3)


def draw_no_face(image):
    cv2.putText(image, "Visage non d\u00e9tect\u00e9", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
