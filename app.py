import streamlit as st
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import cv2
import time
import numpy as np
import pandas as pd
import plotly.express as px


# --- INITIALIZATION ---
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
st.set_page_config(page_title="Video Skill Coach", layout="wide")

# --- SESSION STATE (The Database) ---
if 'history' not in st.session_state:
    st.session_state.history = []

## UI Header
st.title("Psyc-Check: Your AI Speaking Coach")
st.sidebar.header("Target Metrics")
timer_goal = st.sidebar.slider("Target Duration (Seconds)", 30, 180, 60)

# --- THE COACHING ENGINE ---
def analyze_frame(frame):
    # This simulates body language tracking using MediaPipe
    results = pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    confidence_score = 0
    
    if results.pose_landmarks:
        # Check if shoulders are level (Posture)
        lm = results.pose_landmarks.landmark
        left_shoulder = lm[mp_pose.PoseLandmark.LEFT_SHOULDER].y
        right_shoulder = lm[mp_pose.PoseLandmark.RIGHT_SHOULDER].y
        
        # Calculation: Lower difference = Better posture
        posture_gap = abs(left_shoulder - right_shoulder)
        confidence_score = max(0, 100 - (posture_gap * 1000))
        
    return int(confidence_score)

# --- NEW TASK-BASED INITIALIZATION ---
# 1. Download the model file (pose_landmarker.task) and put it in your repo
# Or use this code to set up the detector
def create_detector():
    base_options = python.BaseOptions(model_asset_path='pose_landmarker.task')
    options = vision.PoseLandmarkerOptions(
        base_options=base_options,
        output_segmentation_masks=True
    )
    return vision.PoseLandmarker.create_from_options(options)

# Use a try-except block to handle the attribute error gracefully
try:
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(min_detection_confidence=0.5)
except AttributeError:
    st.error("MediaPipe version mismatch. Please use 'pip install mediapipe==0.10.14' or migrate to Tasks API.")


# --- MAIN INTERFACE ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Live Practice Feed")
    # Note: In a production web environment, we use st.camera_input 
    # for security and browser compatibility.
    img_file = st.camera_input("Record a snapshot of your answer")
    
    if img_file:
        bytes_data = img_file.getvalue()
        cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
        score = analyze_frame(cv2_img)
        
        st.metric(label="Current Confidence Score", value=f"{score}%")
        if score > 80:
            st.success("Great Posture! You look authoritative.")
        else:
            st.warning("Try to sit up straighter to project more confidence.")

with col2:
    st.subheader("Gamified Progress")
    if st.button("Log This Session"):
        new_data = {"Session": len(st.session_state.history) + 1, "Score": score}
        st.session_state.history.append(new_data)
    
    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        fig = px.line(df, x="Session", y="Score", title="Your Growth Curve")
        st.plotly_chart(fig)
        
