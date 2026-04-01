import streamlit as st
import time
import pandas as pd
import plotly.express as px
from streamlit.components.v1 import html
import random

# --- 1. CONFIG & FRAMEWORK ---
st.set_page_config(page_title="Psyc-Check Core", layout="wide")

SPEECH_STRUCTURE = [
    ("Hook", 30), ("Handshake", 45), ("Problem", 30), ("Sub-Problem", 30),
    ("Action", 60), ("Sub-Result", 30), ("Result", 30), ("Lessons Learnt", 15)
]
TOTAL_TIME = sum(s[1] for s in SPEECH_STRUCTURE)

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

if 'start_time' not in st.session_state: 
    st.session_state.start_time = None
if 'history' not in st.session_state: 
    st.session_state.history = []

# --- 2. BROWSER-BASED VIDEO RECORDER ---
record_js = """
<div style="text-align: center; font-family: sans-serif; background: #111; padding: 15px; border-radius: 15px;">
    <video id="video" width="100%" height="auto" autoplay muted style="border-radius:10px; border: 2px solid #333;"></video><br>
    <button id="start" style="margin:10px; padding:12px 20px; background:#28a745; color:white; border:none; border-radius:5px; cursor:pointer; font-weight:bold;">⏺ RECORD SESSION</button>
    <button id="stop" style="margin:10px; padding:12px 20px; background:#dc3545; color:white; border:none; border-radius:5px; cursor:pointer; font-weight:bold;">⏹ STOP & SAVE</button>
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
            a.download = "speech_practice.webm";
            a.click();
            chunks = [];
        };
        mediaRecorder.start();
    }
    b.onclick = () => { startRec(); b.disabled = true; };
    s.onclick = () => { mediaRecorder.stop(); v.srcObject.getTracks().forEach(t => t.stop()); b.disabled = false; };
</script>
"""
def get_new_question():
    st.session_state.current_question = random.choice(QUESTIONS)

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
    
# --- 3. MAIN INTERFACE ---
st.title("🎤 Psyc-Check: Speaking Mastery")
st.write("Master your pacing, track your framework, and stay on point.")

col_left, col_right = st.columns([1, 2])

with col_left:
    st.info(f"**YOUR QUESTION:** {st.session_state.current_question}")
    if st.button("Next Question ↻"):
        get_new_question()
        st.rerun()
    st.subheader("🎥 Video Practice")
    html(record_js, height=400)
    st.caption("Video saves directly to your device to ensure privacy and zero lag.")

with col_right:
    st.subheader("⏱️ Live Framework Tracker")
    
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
                if rem <= 5: 
                    st.error("WRAP UP THIS SECTION!")
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

# --- 4. COHERENCE & PROGRESS ---
st.divider()
st.subheader("📝 Post-Session Analysis")

user_text = st.text_area("Paste your transcript here to check structure coverage:", height=150)
score = 0

if user_text:
    keywords = ["problem", "solution", "action", "result", "learned", "because", "impact"]
    found = [w for w in keywords if w in user_text.lower()]
    score = int((len(found) / len(keywords)) * 100)
    
    st.metric("Structure Coverage Score", f"{score}%")
    if score < 50:
        st.warning("You missed some key structural keywords. Make sure to clearly state the problem and the impact.")
    else:
        st.success("Great structural integrity! You hit the major points.")

if st.button("💾 Log This Session"):
    st.session_state.history.append({
        "Session": len(st.session_state.history) + 1, 
        "Coherence Score": score
    })
    st.toast("Session Saved!")

if st.session_state.history:
    df = pd.DataFrame(st.session_state.history)
    st.plotly_chart(px.line(df, x="Session", y="Coherence Score", markers=True, title="Your Growth Over Time"), use_container_width=True)
