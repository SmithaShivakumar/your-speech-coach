import streamlit as st
import time
import random
import pandas as pd
import plotly.express as px
import numpy as np
import cv2
from streamlit.components.v1 import html

# --- 1. CONFIG & SESSION STATE ---
st.set_page_config(page_title="Psyc-Check Pro", layout="wide")

# Your specific 8-stage framework
SPEECH_STRUCTURE = [
    ("Hook", 30),
    ("Handshake", 45),
    ("Problem", 30),
    ("Sub-Problem", 30),
    ("Action", 60),
    ("Sub-Result", 30),
    ("Result", 30),
    ("Lessons Learnt", 15)
]
TOTAL_TIME = sum(s[1] for s in SPEECH_STRUCTURE)

if 'start_time' not in st.session_state: st.session_state.start_time = None
if 'history' not in st.session_state: st.session_state.history = []

# --- 2. VISION ENGINE (SAFE LOAD) ---
try:
    import mediapipe as mp
    mp_pose = mp.solutions.pose
    pose_detector = mp_pose.Pose(min_detection_confidence=0.5)
    VISION_READY = True
except Exception:
    VISION_READY = False

# --- 3. VIDEO RECORDER (BROWSER-BASED) ---
# This bypasses the need for server-side video drivers
record_js = """
<div style="text-align: center; font-family: sans-serif;">
    <video id="video" width="320" height="240" autoplay muted style="border:3px solid #4A90E2; border-radius:15px; background:#000;"></video><br>
    <button id="start" style="margin:10px; padding:12px 24px; background:#28a745; color:white; border:none; border-radius:8px; cursor:pointer; font-weight:bold;">⏺ RECORD</button>
    <button id="stop" style="margin:10px; padding:12px 24px; background:#dc3545; color:white; border:none; border-radius:8px; cursor:pointer; font-weight:bold;">⏹ STOP & SAVE</button>
</div>
<script>
    let b = document.getElementById("start");
    let s = document.getElementById("stop");
    let v = document.getElementById("video");
    let mediaRecorder;
    let chunks = [];

    async function startRec() {
        const stream = await navigator.mediaDevices.getUserMedia({video: true, audio: true});
        v.srcObject = stream;
        mediaRecorder = new MediaRecorder(stream);
        mediaRecorder.ondataavailable = e => chunks.push(e.data);
        mediaRecorder.onstop = e => {
            const blob = new Blob(chunks, {type: "video/webm"});
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = "speaking_practice.webm";
            a.click();
            chunks = [];
        };
        mediaRecorder.start();
    }
    b.onclick = () => { startRec(); b.disabled = true; b.innerText = "RECORDING..."; };
    s.onclick = () => { mediaRecorder.stop(); v.srcObject.getTracks().forEach(t => t.stop()); b.disabled = false; b.innerText = "⏺ RECORD"; };
</script>
"""

# --- 4. MAIN INTERFACE ---
st.title("🎤 Psyc-Check: Speaking Mastery")

col_left, col_right = st.columns([1, 2])

with col_left:
    st.subheader("🎥 Session Recording")
    html(record_js, height=380)
    
    # Posture Check Component
    img_file = st.camera_input("Quick Posture Check")
    posture_score = 0
    if img_file and VISION_READY:
        bytes_data = img_file.getvalue()
        cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
        results = pose_detector.process(cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB))
        if results.pose_landmarks:
            lm = results.pose_landmarks.landmark
            diff = abs(lm[mp_pose.PoseLandmark.LEFT_SHOULDER].y - lm[mp_pose.PoseLandmark.RIGHT_SHOULDER].y)
            posture_score = int(max(0, 100 - (diff * 1000)))
            st.metric("Posture Score", f"{posture_score}%")

with col_right:
    st.subheader("⏱️ Framework Timer")
    
    if st.button("🚀 BEGIN FLOW", use_container_width=True):
        st.session_state.start_time = time.time()

    if st.session_state.start_time:
        elapsed = time.time() - st.session_state.start_time
        cum_time = 0
        
        for name, duration in SPEECH_STRUCTURE:
            cum_time += duration
            if elapsed < (cum_time - duration):
                st.text(f"⚪ {name} ({duration}s)")
            elif elapsed <= cum_time:
                rem = round(cum_time - elapsed, 1)
                st.markdown(f"### 🔥 CURRENT PHASE: **{name.upper()}**")
                st.markdown(f"## Remaining: `{rem}s`")
                # Visual Alert for last 5 seconds
                if rem <= 5: st.error("WRAP UP THIS SECTION!")
                st.progress(min((elapsed - (cum_time - duration)) / duration, 1.0))
            else:
                st.text(f"✅ {name} (Completed)")
        
        if elapsed > TOTAL_TIME:
            st.success("🎯 Framework Complete!")
            if st.button("Reset Timer"):
                st.session_state.start_time = None
                st.rerun()
        else:
            time.sleep(0.1)
            st.rerun()

# --- 5. PROGRESS TRACKING ---
st.divider()
st.subheader("📊 Improvement Tracker")
if st.button("Log Current Stats"):
    st.session_state.history.append({
        "Session": len(st.session_state.history) + 1,
        "Posture": posture_score
    })

if st.session_state.history:
    df = pd.DataFrame(st.session_state.history)
    fig = px.line(df, x="Session", y="Posture", markers=True, title="Confidence Over Time")
    st.plotly_chart(fig, use_container_width=True)
