import streamlit as st
import time
import random
import pandas as pd
import plotly.express as px
import numpy as np

# --- 1. SAFE IMPORTS FOR PRODUCTION ---
try:
    import cv2
    import mediapipe as mp
    VISION_ENGINE_LIVE = True
except ImportError:
    VISION_ENGINE_LIVE = False

from streamlit.components.v1 import html

# --- 2. CONFIG & FRAMEWORK ---
st.set_page_config(page_title="Psyc-Check Pro", layout="wide")

SPEECH_STRUCTURE = [
    ("Hook", 30), ("Handshake", 45), ("Problem", 30), ("Sub-Problem", 30),
    ("Action", 60), ("Sub-Result", 30), ("Result", 30), ("Lessons Learnt", 15)
]
TOTAL_TIME = sum(s[1] for s in SPEECH_STRUCTURE)

if 'start_time' not in st.session_state: st.session_state.start_time = None
if 'history' not in st.session_state: st.session_state.history = []

# --- 3. BROWSER-BASED VIDEO RECORDER ---
record_js = """
<div style="text-align: center; font-family: sans-serif; background: #111; padding: 15px; border-radius: 15px;">
    <video id="video" width="100%" height="auto" autoplay muted style="border-radius:10px;"></video><br>
    <button id="start" style="margin:10px; padding:12px 20px; background:#28a745; color:white; border:none; border-radius:5px; cursor:pointer;">⏺ RECORD SESSION</button>
    <button id="stop" style="margin:10px; padding:12px 20px; background:#dc3545; color:white; border:none; border-radius:5px; cursor:pointer;">⏹ STOP & DOWNLOAD</button>
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
            a.download = "practice_video.webm";
            a.click();
            chunks = [];
        };
        mediaRecorder.start();
    }
    b.onclick = () => { startRec(); b.disabled = true; };
    s.onclick = () => { mediaRecorder.stop(); v.srcObject.getTracks().forEach(t => t.stop()); b.disabled = false; };
</script>
"""

# --- 4. MAIN INTERFACE ---
st.title("🎤 Psyc-Check Speaking Mastery")

col_left, col_right = st.columns([1, 2])

with col_left:
    st.subheader("🎥 Video Practice")
    html(record_js, height=400)
    
    # Posture Logic
    st.divider()
    img_file = st.camera_input("Snapshot: Quick Posture Check")
    posture_score = 0
    if img_file and VISION_ENGINE_LIVE:
        try:
            bytes_data = img_file.getvalue()
            cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
            # Basic brightness/contrast check for 'Confidence'
            posture_score = int(np.mean(cv2_img) / 2.55) 
            st.metric("Lighting/Confidence", f"{posture_score}%")
        except:
            pass

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
                if rem <= 5: st.warning("WRAP UP SOON!")
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
if st.button("Log Stats"):
    st.session_state.history.append({"Session": len(st.session_state.history) + 1, "Score": posture_score})

if st.session_state.history:
    df = pd.DataFrame(st.session_state.history)
    st.plotly_chart(px.line(df, x="Session", y="Score", markers=True), use_container_width=True)
