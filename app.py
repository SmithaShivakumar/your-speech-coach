import streamlit as st
import time
import random
import pandas as pd
import plotly.express as px
from streamlit.components.v1 import html

# --- 1. CONFIG & SESSION STATE ---
st.set_page_config(page_title="Psyc-Check Pro", layout="wide")

# The precise timing structure you requested
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
TOTAL_TIME = sum(s[1] for s in SPEECH_STRUCTURE) # 270 seconds (4.5 mins)

if 'start_time' not in st.session_state: st.session_state.start_time = None
if 'history' not in st.session_state: st.session_state.history = []

# --- 2. VIDEO RECORDING INJECTION (JavaScript) ---
# This allows us to record real video in the browser since Streamlit doesn't do it natively.
st.sidebar.title("Video Controls")
record_code = """
<div style="text-align: center;">
    <video id="video" width="320" height="240" autoplay muted style="border:2px solid #555; border-radius:10px;"></video><br>
    <button id="start" style="padding:10px; background-color:#28a745; color:white; border:none; border-radius:5px; cursor:pointer;">⏺ Start Recording</button>
    <button id="stop" style="padding:10px; background-color:#dc3545; color:white; border:none; border-radius:5px; cursor:pointer;">⏹ Stop & Download</button>
</div>
<script>
    let b = document.getElementById("start");
    let s = document.getElementById("stop");
    let v = document.getElementById("video");
    let mediaRecorder;
    let chunks = [];

    async function start() {
        let stream = await navigator.mediaDevices.getUserMedia({video: true, audio: true});
        v.srcObject = stream;
        mediaRecorder = new MediaRecorder(stream);
        mediaRecorder.ondataavailable = e => chunks.push(e.data);
        mediaRecorder.onstop = e => {
            let blob = new Blob(chunks, {type: "video/webm"});
            let url = URL.createObjectURL(blob);
            let a = document.createElement("a");
            a.href = url;
            a.download = "my_practice_session.webm";
            a.click();
        };
        mediaRecorder.start();
    }
    b.onclick = () => { start(); b.disabled = true; };
    s.onclick = () => { mediaRecorder.stop(); v.srcObject.getTracks().forEach(t => t.stop()); b.disabled = false; };
</script>
"""

# --- 3. THE UI LAYOUT ---
st.title("🎤 Psyc-Check: Master the Framework")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("🎥 Video Recorder")
    html(record_code, height=350)
    st.caption("Note: Video downloads locally to your computer once stopped.")
    
    if st.button("🚀 Start Timer Framework"):
        st.session_state.start_time = time.time()

with col2:
    st.subheader("⏱️ Live Framework Tracker")
    
    if st.session_state.start_time:
        elapsed = time.time() - st.session_state.start_time
        current_cumulative = 0
        
        # Display Progress Bars for each segment
        for name, duration in SPEECH_STRUCTURE:
            current_cumulative += duration
            remaining_for_segment = current_cumulative - elapsed
            
            if elapsed < (current_cumulative - duration):
                # Future segment
                st.text(f"⚪ {name} ({duration}s)")
            elif elapsed <= current_cumulative:
                # Active segment
                st.subheader(f"🔥 CURRENT: {name.upper()}")
                st.write(f"Remaining: **{round(remaining_for_segment, 1)}s**")
                progress = (elapsed - (current_cumulative - duration)) / duration
                st.progress(min(progress, 1.0))
            else:
                # Past segment
                st.text(f"✅ {name} (Completed)")
        
        if elapsed > TOTAL_TIME:
            st.success("🎉 Session Complete!")
            if st.button("Reset Timer"):
                st.session_state.start_time = None
                st.rerun()
        
        # Auto-refresh the UI every 1 second
        time.sleep(1)
        st.rerun()
    else:
        st.warning("Click 'Start Timer Framework' to begin your structured practice.")

# --- 4. COHERENCE ANALYSIS ---
st.divider()
st.subheader("📝 Post-Session Analysis")
user_text = st.text_area("Paste your transcript here to check if you stayed 'To the Point':", height=150)

if user_text:
    # Basic relevance check against the 'Problem' and 'Action' keywords
    keywords = ["problem", "solution", "action", "result", "learned"]
    found = [w for w in keywords if w in user_text.lower()]
    score = (len(found) / len(keywords)) * 100
    st.metric("Structure Coverage", f"{score}%")
    if score < 60:
        st.error("You missed some key structural phases in your speech.")
    else:
        st.success("Great structural integrity!")
