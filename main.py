"""SafeDrive — drowsiness and distraction detector.

This is the slim entry-point (~80 lines).  All logic lives in the
``safedrive`` package.
"""

import argparse
import logging
import time

import cv2
import mediapipe as mp

from safedrive.config import load_config
from safedrive.logger import setup_logging
from safedrive.alert_system import AlertSystem
from safedrive import display
from safedrive.detectors.eye_detector import detect_eyes_closed
from safedrive.detectors.mouth_detector import detect_yawning
from safedrive.detectors.head_detector import check_head_position
from safedrive.detectors.phone_detector import detect_phone_usage

logger = logging.getLogger(__name__)


def determine_alert_level(eyes_closed_time, is_yawning, head_state, phone_time, cfg):
    danger = 0
    if eyes_closed_time > cfg.eyes_closed_time_threshold * 0.8:
        danger += 2
    elif eyes_closed_time > cfg.eyes_closed_time_threshold * 0.5:
        danger += 1
    if is_yawning:
        danger += 1
    if head_state["turned"] and head_state["tilted"]:
        danger += 2
    elif head_state["turned"] or head_state["tilted"]:
        danger += 1
    if phone_time > cfg.phone_detection_threshold:
        danger += 3
    elif phone_time > 0:
        danger += 1
    if danger >= 3:
        return "DANGER"
    if danger >= 1:
        return "WARNING"
    return "NORMAL"


def main():
    parser = argparse.ArgumentParser(description="SafeDrive detector")
    parser.add_argument("--config", default=None, help="Path to config.yaml")
    args = parser.parse_args()

    cfg = load_config(args.config)
    setup_logging()
    det = cfg.detection

    face_mesh = mp.solutions.face_mesh.FaceMesh(
        max_num_faces=1, refine_landmarks=True,
        min_detection_confidence=0.5, min_tracking_confidence=0.5,
    )
    hands = mp.solutions.hands.Hands(
        max_num_hands=2, min_detection_confidence=0.7, min_tracking_confidence=0.5,
    )
    alert = AlertSystem(cfg.alert.alarm_path, cfg.alert.levels)
    alert.start()

    cap = cv2.VideoCapture(cfg.camera.index)
    if not cap.isOpened():
        logger.warning("Camera %d unavailable, trying index 0", cfg.camera.index)
        cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        logger.error("Cannot access any camera.")
        return

    logger.info("SafeDrive started")
    eyes_closed_start = None
    yawn_count = 0
    last_yawn_time = time.time()
    consecutive_yawns = 0
    phone_start = None

    try:
        while cap.isOpened():
            ok, image = cap.read()
            if not ok:
                break
            h, w = image.shape[:2]
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            face_res = face_mesh.process(rgb)
            hand_res = hands.process(rgb)
            now = time.time()

            phone_detected = False
            if hand_res.multi_hand_landmarks:
                for hl in hand_res.multi_hand_landmarks:
                    if detect_phone_usage(hl, h, w):
                        phone_detected = True
                        if phone_start is None:
                            phone_start = now
                        mp.solutions.drawing_utils.draw_landmarks(
                            image, hl, mp.solutions.hands.HAND_CONNECTIONS,
                            mp.solutions.drawing_utils.DrawingSpec(color=(255, 0, 0), thickness=2, circle_radius=2),
                            mp.solutions.drawing_utils.DrawingSpec(color=(0, 0, 255), thickness=2),
                        )
            if not phone_detected:
                phone_start = None
            phone_time = (now - phone_start) if phone_start else 0

            if face_res.multi_face_landmarks:
                lm = face_res.multi_face_landmarks[0].landmark
                eyes_closed = detect_eyes_closed(lm, det.eye_closed_threshold)
                is_yawning = detect_yawning(lm, det.mouth_aspect_ratio_threshold, det.mouth_open_threshold)
                head_state = check_head_position(lm, det.head_rotation_threshold, det.head_tilt_threshold)

                if is_yawning and now - last_yawn_time > 3.0:
                    yawn_count += 1
                    consecutive_yawns += 1
                    last_yawn_time = now
                elif not is_yawning and now - last_yawn_time > 10.0:
                    consecutive_yawns = 0

                if eyes_closed:
                    if eyes_closed_start is None:
                        eyes_closed_start = now
                    elapsed = now - eyes_closed_start
                else:
                    elapsed = 0
                    eyes_closed_start = None

                level = determine_alert_level(
                    elapsed if eyes_closed_start else 0,
                    consecutive_yawns >= 2, head_state, phone_time, det,
                )
                color = alert.get_color(level)
                alert.update(level)

                display.draw_alert_level(image, level, color)
                if eyes_closed:
                    display.draw_eye_timer(image, max(0, det.eyes_closed_time_threshold - elapsed), color)
                if is_yawning:
                    display.draw_yawn(image, consecutive_yawns)
                display.draw_head_state(image, head_state)
                display.draw_yawn_total(image, yawn_count)
                if phone_detected:
                    display.draw_phone_warning(image, phone_time)
                if level == "DANGER":
                    display.draw_danger_border(image, w, h, color)
            else:
                display.draw_no_face(image)
                eyes_closed_start = None

            cv2.imshow("SafeDrive", image)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()
        alert.stop()
        face_mesh.close()
        hands.close()
        logger.info("SafeDrive stopped")


if __name__ == "__main__":
    main()
