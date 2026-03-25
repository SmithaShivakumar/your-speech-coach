import streamlit as st
import cv2
import time
import numpy as np
import pandas as pd
import plotly.express as px
import random

# --- 1. ROBUST VISION ENGINE INITIALIZATION ---
# We wrap this in a try-except at the very top to prevent the app from crashing on boot.
try:
    import mediapipe as mp
    mp_pose = mp.solutions.pose
    # Initialize the pose detector once and cache it
    pose_detector = mp_pose.Pose(
        static_image_mode=False, 
        model_complexity=1, 
        min_detection_confidence=0.5
    )
    VISION_ENGINE_LIVE = True
except Exception as e:
    VISION_ENGINE_LIVE = False
    VISION_ERROR = str(e)

# --- 2. CONFIG & DATA ---
st.set_page_config(page_title="Psyc-Check: AI Speaking Coach", layout="wide")

QUESTIONS = [
    "Tell me about a time you handled a difficult conflict at work.",
    "What is your greatest professional achievement so far?",
    "How do you handle high-pressure situations and tight deadlines?",
    "Why should we hire you over other candidates with similar skills?",
    "Describe a complex project you led and the results you achieved.",
    "Tell me about a time you had to align multiple stakeholders.",
    "Describe a situation where you had to push back on a senior leader.",
    "Tell me about a time you failed. What did you learn?",
    "How do you handle a situation where stakeholders keep changing requirements?",
    "Tell me about a time you had to align multiple stakeholders with conflicting priorities.",
    "Tell me about a time you changed someone’s mind using data.",
    "Tell me about a time you went beyond your defined role to solve a problem.",
    "Describe a situation where there was no clear owner, and you stepped in.",
    "Tell me about a time you identified an opportunity others missed.",
    "Tell me about a time you had to deliver a project under tight deadlines.",
    "Describe a time when things didn’t go according to plan. What did you do?",
    "Tell me about a time you had to manage multiple priorities simultaneously.",
    "Describe a decision you made that you would approach differently today.",
    "Tell me about a time you had a disagreement with a cross-functional partner.",
    "Describe a situation where you had to deal with a difficult team member.",
    "Tell me about a time you uncovered a customer need that wasn’t obvious."
]

# Initialize Session States for Gamification
if 'history' not in st.session_state: st.session_state.history = []
if 'current_q' not in st.session_state: st.session_state.current_q = random.choice(QUESTIONS)
if 'start_time' not in st.session_state: st.session_state.start_time = None
if 'elapsed' not in st.session_state: st.session_state.elapsed = 0

# --- 3. LOGIC FUNCTIONS ---

def get_new_question():
    st.session_state.current_q = random.choice(QUESTIONS)
    st.session_state.start_time = None
    st.session_state.elapsed = 0

def calculate_coherence(question, answer):
    if not answer: return 0
    stop_words = {'a', 'the', 'is', 'at', 'which', 'on', 'and', 'i', 'me', 'to', 'of', 'in', 'that'}
    q_keywords = set([w.lower().strip('?.!,') for w in question.split() if w.lower() not in stop_words])
    a_words = set([w.lower().strip('?.!,') for w in answer.split()])
    overlap = q_keywords.intersection(a_words)
    return round((len(overlap) / len(q_keywords)) * 100, 2) if q_keywords else 0

def analyze_posture(frame):
    """Calculates a confidence score based on shoulder alignment."""
    if not VISION_ENGINE_LIVE:
        return 0
    try:
        # Convert BGR to RGB for MediaPipe
        results = pose_detector.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        if results.pose_landmarks:
            lm = results.pose_landmarks.landmark
            # Get Y-coordinates of shoulders (0 is top, 1 is bottom)
            left_y = lm[mp_pose.PoseLandmark.LEFT_SHOULDER].y
            right_y = lm[mp_pose.PoseLandmark.RIGHT_SHOULDER].y
            
            # The closer to 0 the difference, the straighter the posture
            diff = abs(left_y - right_y)
            score = max(0, 100 - (diff * 1000)) 
            return int(score)
    except:
        return 0
    return 0

# --- 4. THE USER INTERFACE ---

st.title("🎤 Psyc-Check: Your AI Speaking Coach")

# Global Error Warning if MediaPipe fails (helps with debugging)
if not VISION_ENGINE_LIVE:
    st.warning(f"⚠️ Vision Engine (MediaPipe) is unavailable in this environment. Focus on Tone & Coherence!")

col1, col2 = st.columns([2, 1])

with col1:
    # --- Question Area ---
    st.info(f"**YOUR QUESTION:** {st.session_state.current_q}")
    if st.button("New Question ↻"):
        get_new_question()
        st.rerun()

    # --- Camera Input (Posture Check) ---
    img_file = st.camera_input("Snapshot: Check your posture & eye contact")
    current_posture_score = 0
    
    if img_file:
        bytes_data = img_file.getvalue()
        cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
        current_posture_score = analyze_posture(cv2_img)
        
        st.metric("Posture Confidence", f"{current_posture_score}%")
        if current_posture_score > 85:
            st.success("Perfect alignment! You look authoritative.")
        else:
            st.warning("Try to level your shoulders and sit up straighter.")

    st.divider()
    
    # --- Stopwatch & Scoring ---
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        if st.button("🚀 START ANSWERING"):
            st.session_state.start_time = time.time()
            st.toast("Clock is ticking! Stay concise.")
    with c2:
        if st.button("🛑 STOP"):
            if st.session_state.start_time:
                st.session_state.elapsed = round(time.time() - st.session_state.start_time, 2)
    with c3:
        st.subheader(f"⏱️ {st.session_state.elapsed}s")

    user_text = st.text_area("Paste your transcript here to analyze coherence:", placeholder="I handled the conflict by...", height=150)
    
    if user_text:
        rel_score = calculate_coherence(st.session_state.current_q, user_text)
        st.metric("Relevance Score", f"{rel_score}%")
        
        if rel_score > 40:
            st.success("Direct & To the point!")
        else:
            st.error("Rambling alert: Try to use more keywords from the question.")

with col2:
    st.sidebar.header("Target Metrics")
    timer_goal = st.sidebar.slider("Time Limit (s)", 30, 180, 60)
    
    st.subheader("📊 Session History")
    
    # Log Session Button
    if st.button("💾 Save Session Metrics"):
        # We calculate the final score for the graph
        final_rel = rel_score if 'rel_score' in locals() else 0
        st.session_state.history.append({
            "Session": len(st.session_state.history) + 1,
            "Posture": current_posture_score,
            "Coherence": final_rel
        })
        st.success("Session Logged!")

    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        fig = px.line(df, x="Session", y=["Posture", "Coherence"], markers=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("No sessions logged yet. Start practicing!")
