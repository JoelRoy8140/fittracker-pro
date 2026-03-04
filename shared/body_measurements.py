import cv2
import sys
import mediapipe as mp
import numpy as np
import math

class BodyMeasurementScanner:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
    
    def get_body_measurements(self, image):
        """Extract measurements from webcam image"""
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb_image)
        
        if not results.pose_landmarks:
            return None
            
        landmarks = results.pose_landmarks.landmark
        h, w = image.shape[:2]
        
        # Convert normalized coords to pixels
        def to_pixel(landmark):
            return int(landmark.x * w), int(landmark.y * h)
        
        # Key measurements
        measurements = {
            'shoulder_width': self._distance(
                to_pixel(landmarks[11]), to_pixel(landmarks[12])
            ),
            'torso_height': self._distance(
                to_pixel(landmarks[11]), to_pixel(landmarks[23])
            ),
            'hip_width': self._distance(
                to_pixel(landmarks[23]), to_pixel(landmarks[24])
            )
        }
        
        return measurements, results.pose_landmarks
    
    def _distance(self, p1, p2):
        return math.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)
    
    def calculate_bmi(self, weight_kg, height_cm):
        height_m = height_cm / 100
        return weight_kg / (height_m ** 2)
    
    def estimate_body_fat(self, bmi, age, gender):
        if gender.lower() == 'male':
            return (1.20 * bmi) + (0.23 * age) - 16.2
        else:
            return (1.20 * bmi) + (0.23 * age) - 5.4
