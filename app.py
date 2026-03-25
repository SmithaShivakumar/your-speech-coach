import streamlit as st
import mediapipe as mp
import cv2
import time
import numpy as np
import pandas as pd
import plotly.express as px
import random

# --- 1. CONFIG & SESSION STATE ---
st.set_page_config(page_title="Psyc-Check: AI Speaking Coach", layout="wide")

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

# Initialize Session States
if 'history' not in st.session_state: st.session_state.history = []
if 'current_q' not in st.session_state: st.session_state.current_q = random.choice(QUESTIONS)
if 'start_time' not in st.session_state: st.session_state.start_time = None
if 'elapsed' not in st.session_state: st.session_state.elapsed = 0

# --- 2. CORE LOGIC FUNCTIONS ---

def get_new_question():
    st.session_state.current_q = random.choice(QUESTIONS)
    st.session_state.start_time = None
    st.session_state.elapsed = 0

def calculate_coherence(question, answer):
    stop_words = {'a', 'the', 'is', 'at', 'which', 'on', 'and', 'i', 'me', 'to', 'of'}
    q_keywords = set([w.lower() for w in question.split() if w.lower() not in stop_words])
    a_words = set([w.lower() for w in answer.split()])
    overlap = q_keywords.intersection(a_words)
    return round((len(overlap) / len(q_keywords)) * 100, 2) if q_keywords else 0

# MediaPipe Initialization
try:
    mp_pose = mp.solutions.pose
    pose_detector = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
except Exception:
    st.error("MediaPipe initialization failed. Check packages.txt for libGL.so.1")

def analyze_posture(frame):
    results = pose_detector.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    if results.pose_landmarks:
        lm = results.pose_landmarks.landmark
        # Calculate shoulder tilt
        diff = abs(lm[mp_pose.PoseLandmark.LEFT_SHOULDER].y - lm[mp_pose.PoseLandmark.RIGHT_SHOULDER].y)
        return int(max(0, 100 - (diff * 1000)))
    return 0

# --- 3. UI LAYOUT ---

st.title("🎤 Psyc-Check: Your AI Speaking Coach")

col1, col2 = st.columns([2, 1])

with col1:
    st.info(f"**CURRENT CHALLENGE:** {st.session_state.current_q}")
    if st.button("New Question ↻"):
        get_new_question()
        st.rerun()

    # Camera Input
    img_file = st.camera_input("Take a posture check snapshot")
    current_posture_score = 0
    if img_file:
        bytes_data = img_file.getvalue()
        cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
        current_posture_score = analyze_posture(cv2_img)
        st.metric("Posture Confidence", f"{current_posture_score}%")

    st.divider()
    
    # Timing & Answer Section
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        if st.button("🚀 START TIMER"):
            st.session_state.start_time = time.time()
    with c2:
        if st.button("🛑 STOP TIMER"):
            if st.session_state.start_time:
                st.session_state.elapsed = round(time.time() - st.session_state.start_time, 2)
    with c3:
        st.subheader(f"⏱️ {st.session_state.elapsed}s")

    user_text = st.text_area("Paste your transcript here to analyze coherence:", height=150)
    
    if user_text:
        rel_score = calculate_coherence(st.session_state.current_q, user_text)
        st.metric("Relevance Score", f"{rel_score}%")
        
        if rel_score > 50:
            st.success("Great job! You stayed on topic.")
        else:
            st.warning("Try to use more keywords from the question to stay focused.")

with col2:
    st.sidebar.header("Settings")
    timer_goal = st.sidebar.slider("Target Time (s)", 30, 180, 60)
    
    st.subheader("📈 Progress Tracking")
    if st.button("Log Session Data"):
        st.session_state.history.append({
            "Session": len(st.session_state.history) + 1,
            "PostScore": current_posture_score,
            "RelScore": rel_score if 'rel_score' in locals() else 0
        })
        st.toast("Progress Saved!")

    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        fig = px.line(df, x="Session", y=["PostScore", "RelScore"], markers=True, title="Improvement Over Time")
        st.plotly_chart(fig, use_container_width=True)
        
