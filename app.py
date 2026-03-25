import streamlit as st
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import cv2
import time
import numpy as np
import pandas as pd
import plotly.express as px
import random

# --- QUESTION BANK ---
QUESTIONS = [
    "Tell me about a time you handled a difficult conflict at work.",
    "What is your greatest professional achievement so far?",
    "How do you handle high-pressure situations and tight deadlines?",
    "Why should we hire you over other candidates with similar skills?",
    "Describe a complex project you led and the results you achieved.",
    "Tell me about a time you had to align multiple stakeholders with conflicting priorities.",
    "Describe a situation where you had to push back on a senior leader.",
    "Tell me about a time you changed someone’s mind using data.",
    "How have you handled a situation where stakeholders kept changing requirements?",
    "Tell me about a time you went beyond your defined role to solve a problem.",
    "Describe a situation where there was no clear owner, and you stepped in.",
    "Tell me about a time you identified an opportunity others missed.",
    "Tell me about a time you had to deliver a project under tight deadlines.",
    "Describe a time when things didn’t go according to plan. What did you do?",
    "Tell me about a time you had to manage multiple priorities simultaneously.",
    "Tell me about a time you failed. What did you learn?",
    "Describe a decision you made that you would approach differently today.",
    "Tell me about a time you had a disagreement with a cross-functional partner.",
    "Describe a situation where you had to deal with a difficult team member.",
    "Tell me about a time you uncovered a customer need that wasn’t obvious."
]

if 'current_question' not in st.session_state:
    st.session_state.current_question = random.choice(QUESTIONS)

def get_new_question():
    st.session_state.current_question = random.choice(QUESTIONS)

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

def check_relevance(question, answer):
    # Basic production-level check: Keyword Overlap
    q_set = set(question.lower().split())
    a_set = set(answer.lower().split())
    
    # Common "stop words" to ignore
    stop_words = {'a', 'the', 'is', 'at', 'which', 'on', 'and', 'i', 'me'}
    q_keywords = q_set - stop_words
    
    overlap = q_keywords.intersection(a_set)
    relevance_score = (len(overlap) / len(q_keywords)) * 100
    return round(relevance_score, 2)

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
with col1:
    st.info(f"**YOUR QUESTION:** {st.session_state.current_question}")
    if st.button("Next Question ↻"):
        get_new_question()
        st.rerun()

    # --- THE STOPWATCH ---
    if 'start_time' not in st.session_state:
        st.session_state.start_time = None

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🚀 START ANSWERING"):
            st.session_state.start_time = time.time()
    with c2:
        if st.button("🛑 STOP"):
            elapsed = time.time() - st.session_state.start_time
            st.session_state.elapsed = round(elapsed, 2)

    # --- INPUT FOR ANALYSIS ---
    user_answer = st.text_area("Paste your transcript here (or use Voice-to-Text):")
    
    if user_answer and st.session_state.get('elapsed'):
        rel_score = check_relevance(st.session_state.current_question, user_answer)
        
        # Gamified Feedback
        st.metric("Relevance Score", f"{rel_score}%")
        st.metric("Time Taken", f"{st.session_state.elapsed}s")
        
        if st.session_state.elapsed > timer_goal:
            st.error("Too long! You lost the 'Brevity Bonus'.")
        elif rel_score < 20:
            st.warning("You might be rambling. Try to use keywords from the question.")
        else:
            st.success("Sharp and Concise! Point awarded.")

with col2:
    st.subheader("Gamified Progress")
    if st.button("Log This Session"):
        new_data = {"Session": len(st.session_state.history) + 1, "Score": score}
        st.session_state.history.append(new_data)
    
    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        fig = px.line(df, x="Session", y="Score", title="Your Growth Curve")
        st.plotly_chart(fig)
        
