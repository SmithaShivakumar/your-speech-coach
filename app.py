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
QUESTION_BANK = {
    "General Behavioral": [
        "Tell me about a time you handled a difficult conflict at work.",
        "What is your greatest professional achievement so far?",
        "How do you handle high-pressure situations and tight deadlines?",
        "Why should we hire you over other candidates with similar skills?",
        "Describe a complex project you led and the results you achieved.",
        "Tell me about a time you had to align multiple stakeholders with conflicting priorities.",
        "Describe a situation where you had to push back on a senior leader.",
        "Tell me about a time you changed someone's mind using data.",
        "How have you handled a situation where stakeholders kept changing requirements?",
        "Tell me about a time you went beyond your defined role to solve a problem.",
        "Describe a situation where there was no clear owner, and you stepped in.",
        "Tell me about a time you identified an opportunity others missed.",
        "Tell me about a time you had to deliver a project under tight deadlines.",
        "Describe a time when things didn't go according to plan. What did you do?",
        "Tell me about a time you had to manage multiple priorities simultaneously.",
        "Tell me about a time you failed. What did you learn?",
        "Describe a decision you made that you would approach differently today.",
        "Tell me about a time you had a disagreement with a cross-functional partner.",
        "Describe a situation where you had to deal with a difficult team member.",
        "Tell me about a time you uncovered a customer need that wasn't obvious.",
    ],
    "PM-Specific": [
        "How do you decide what to build next when everything feels urgent?",
        "Tell me about a time you had to kill a feature you personally believed in.",
        "How do you align engineering, design, and business stakeholders on a roadmap?",
        "Describe a time you shipped something that underperformed. What did you learn?",
        "How do you measure whether a product is successful?",
        "Tell me about a time you had to make a build vs. buy decision.",
        "How do you handle a situation where your data and your users' feedback conflict?",
        "Describe a time you had to influence a team you had no authority over.",
        "Tell me about a product you admire and how you would improve it.",
        "How do you write a PRD that engineers actually want to read?",
        "Tell me about a time you reduced scope without reducing value.",
        "How do you prioritize technical debt against new feature requests?",
        "Describe a time you had to represent the customer when the business pushed back.",
        "How do you run a discovery sprint? Walk me through your process.",
        "Tell me about a launch that didn't go as planned. What happened?",
        "How do you decide when a product is ready to ship?",
        "Describe a time you used an experiment to settle an internal debate.",
        "How do you handle feature requests from a very important customer?",
        "Tell me about a time you had to say no to a request from a VP.",
        "How do you keep a team motivated during a long, hard-to-measure project?",
    ],
    "Analyst / Finance": [
        "Tell me about a time your model was wrong. How did you discover it and what did you do?",
        "How do you explain a complex quantitative finding to a non-technical stakeholder?",
        "Describe a time you found an insight in data that changed a business decision.",
        "How do you handle a situation where the data is incomplete or unreliable?",
        "Tell me about the most complex financial model you've built.",
        "Describe a time you had to present a recommendation a client didn't want to hear.",
        "How do you validate assumptions in a financial model?",
        "Tell me about a time you worked under extreme time pressure to deliver an analysis.",
        "How do you decide what level of granularity to use in a model?",
        "Describe a situation where two analysts had conflicting conclusions from the same data.",
        "Tell me about a time you automated a manual reporting process.",
        "How do you think about risk when building a quantitative model?",
        "Describe a time you caught an error that would have had significant consequences.",
        "How do you keep up with changes in markets or regulation that affect your work?",
        "Tell me about a time you had to defend your methodology under scrutiny.",
        "How do you communicate uncertainty and confidence intervals to decision-makers?",
        "Describe a time you worked cross-functionally with a trading desk or portfolio manager.",
        "Tell me about a time you built something that was later adopted more broadly.",
        "How do you structure a client presentation for a complex investment thesis?",
        "Describe a time when quantitative analysis contradicted market intuition.",
    ],
    "Leadership & Conflict": [
        "Tell me about a time you led a team through significant uncertainty.",
        "Describe a time you had to give difficult feedback to someone more senior than you.",
        "How do you build trust with a new team quickly?",
        "Tell me about a time a direct report was underperforming. How did you handle it?",
        "Describe a time you had to make an unpopular decision and defend it.",
        "How do you manage conflict between two high-performing team members?",
        "Tell me about a time you had to advocate for a team member to leadership.",
        "Describe a time you inherited a broken team or process.",
        "How do you drive alignment when there is genuine disagreement on strategy?",
        "Tell me about a time you had to deliver bad news to a team.",
        "Describe a time you had to earn trust in a new organization.",
        "How do you keep a remote or distributed team cohesive?",
        "Tell me about a time you had to change course mid-project.",
        "Describe a situation where you had to balance speed and quality.",
        "How do you mentor someone who is more technically skilled than you?",
    ],
    "Data & Decisions": [
        "Tell me about a time you used data to change someone's strongly-held opinion.",
        "Describe a time you designed a metric that turned out to be misleading.",
        "How do you design an A/B test from scratch? Walk me through it.",
        "Tell me about a time the results of an experiment surprised you.",
        "How do you decide what to measure when the 'right' metric isn't obvious?",
        "Describe a time you had to make a decision with very little data.",
        "How do you distinguish between correlation and causation in practice?",
        "Tell me about a time a dashboard or report led to a wrong conclusion.",
        "How do you handle a situation where different teams are using different definitions of the same metric?",
        "Describe a time you built a data pipeline or reporting system from scratch.",
        "How do you communicate statistical significance to non-technical stakeholders?",
        "Tell me about a time you used qualitative data to complement quantitative analysis.",
        "Describe a time when you had to stop an experiment early.",
        "How do you decide when you have enough data to make a decision?",
        "Tell me about a time you caught a data quality issue before it caused harm.",
    ],
}

ALL_CATEGORIES = list(QUESTION_BANK.keys())

def get_all_questions():
    return [q for questions in QUESTION_BANK.values() for q in questions]

def get_new_question():
    cat = st.session_state.selected_category
    if cat == "All":
        pool = get_all_questions()
    else:
        pool = QUESTION_BANK[cat]
    st.session_state.current_question = random.choice(pool)
    st.session_state.think_start = None
    st.session_state.think_done = False
    st.session_state.start_time = None
    st.session_state.section_resets = {}

# --- SESSION STATE INIT ---
if 'selected_category' not in st.session_state:
    st.session_state.selected_category = "All"
if 'current_question' not in st.session_state:
    st.session_state.current_question = random.choice(get_all_questions())
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'history' not in st.session_state:
    st.session_state.history = []
if 'think_duration' not in st.session_state:
    st.session_state.think_duration = 30
if 'think_start' not in st.session_state:
    st.session_state.think_start = None
if 'think_done' not in st.session_state:
    st.session_state.think_done = False
if 'section_resets' not in st.session_state:
    st.session_state.section_resets = {}

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

# --- 3. MAIN INTERFACE ---
st.title("🎤 Psyc-Check: Speaking Mastery")
st.write("Master your pacing, track your framework, and stay on point.")

col_left, col_right = st.columns([1, 2])

with col_left:
    # Category filter
    category_options = ["All"] + ALL_CATEGORIES
    selected = st.selectbox(
        "Question category",
        category_options,
        index=category_options.index(st.session_state.selected_category),
        key="category_select"
    )
    if selected != st.session_state.selected_category:
        st.session_state.selected_category = selected
        get_new_question()
        st.rerun()

    st.info(f"**YOUR QUESTION:** {st.session_state.current_question}")

    if st.button("Next Question ↻"):
        get_new_question()
        st.rerun()

    # Think timer controls
    st.subheader("⏳ Think Time")
    think_options = {"15 seconds": 15, "30 seconds": 30, "60 seconds": 60}
    chosen_label = st.selectbox(
        "How long to think?",
        list(think_options.keys()),
        index=1
    )
    st.session_state.think_duration = think_options[chosen_label]

    col_think1, col_think2 = st.columns(2)
    with col_think1:
        if st.button("⏱ Start Think Timer", use_container_width=True):
            st.session_state.think_start = time.time()
            st.session_state.think_done = False
            st.rerun()
    with col_think2:
        if st.button("Skip → Start Now", use_container_width=True):
            st.session_state.think_done = True
            st.session_state.start_time = time.time()
            st.session_state.section_resets = {}
            st.rerun()

    # Think timer countdown
    if st.session_state.think_start and not st.session_state.think_done:
        elapsed_think = time.time() - st.session_state.think_start
        remaining_think = st.session_state.think_duration - elapsed_think
        if remaining_think > 0:
            st.markdown(f"### Think: `{remaining_think:.1f}s`")
            st.progress(min(elapsed_think / st.session_state.think_duration, 1.0))
            time.sleep(0.1)
            st.rerun()
        else:
            st.session_state.think_done = True
            st.session_state.start_time = time.time()
            st.session_state.section_resets = {}
            st.success("✅ Think time done — begin speaking!")
            time.sleep(0.1)
            st.rerun()

    st.subheader("🎥 Video Practice")
    html(record_js, height=400)
    st.caption("Video saves directly to your device to ensure privacy and zero lag.")

with col_right:
    st.subheader("⏱️ Live Framework Tracker")

    if not st.session_state.get('think_done') and not st.session_state.get('start_time'):
        st.info("Use the Think Timer on the left to begin, or click 'Skip → Start Now'.")

    if st.session_state.start_time:
        elapsed = time.time() - st.session_state.start_time
        cum_time = 0
        still_running = False

        for idx, (name, duration) in enumerate(SPEECH_STRUCTURE):
            section_key = f"reset_{idx}"
            reset_offset = st.session_state.section_resets.get(section_key, 0)
            section_start = cum_time
            section_end = cum_time + duration
            adjusted_elapsed = elapsed - reset_offset

            if adjusted_elapsed < section_start:
                st.markdown(f"⚪ **{name}** — {duration}s")
            elif adjusted_elapsed <= section_end:
                still_running = True
                section_elapsed = adjusted_elapsed - section_start
                remaining = duration - section_elapsed
                st.markdown(f"### 🔥 {name.upper()}")
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.progress(min(section_elapsed / duration, 1.0))
                    if remaining <= 5:
                        st.error(f"⚠️ Wrap up! `{remaining:.1f}s` left")
                    else:
                        st.markdown(f"`{remaining:.1f}s` remaining")
                with col_b:
                    if st.button("↺ Redo", key=f"redo_{idx}"):
                        st.session_state.section_resets[section_key] = (
                            st.session_state.section_resets.get(section_key, 0) + section_elapsed
                        )
                        st.rerun()
            else:
                st.markdown(f"✅ **{name}** — done")

            cum_time += duration

        if still_running:
            time.sleep(0.1)
            st.rerun()
        elif elapsed > TOTAL_TIME + sum(st.session_state.section_resets.values()):
            st.success("🎯 All sections complete!")
            if st.button("Reset Timer"):
                st.session_state.start_time = None
                st.session_state.think_start = None
                st.session_state.think_done = False
                st.session_state.section_resets = {}
                st.rerun()

# --- 4. POST-SESSION ANALYSIS ---
st.divider()
st.subheader("📝 Post-Session Analysis")
st.caption("Paste your transcript to get a full evaluation.")

user_text = st.text_area("Paste your transcript here:", height=150)

def analyze_transcript(text):
    words = text.lower().split()
    word_count = len(words)

    # 1. STAR Coverage
    star_keywords = {
        "Situation": ["situation", "context", "background", "when", "working at", "was at"],
        "Task": ["task", "responsibility", "goal", "objective", "needed to", "had to", "my role"],
        "Action": ["action", "i did", "i built", "i created", "i led", "i implemented",
                   "i decided", "i proposed", "i reached out", "i worked", "i ran", "i designed"],
        "Result": ["result", "outcome", "impact", "achieved", "increased", "decreased",
                   "reduced", "saved", "improved", "delivered", "shipped", "led to"],
    }
    star_found = {}
    for component, kws in star_keywords.items():
        star_found[component] = any(kw in text.lower() for kw in kws)
    star_score = int((sum(star_found.values()) / 4) * 100)

    # 2. Filler Words
    fillers = ["um", "uh", "like", "you know", "basically", "literally",
               "right?", "so yeah", "i mean", "sort of", "kind of"]
    filler_count = sum(text.lower().count(f) for f in fillers)
    if filler_count <= 3:
        filler_rating = "Low"
    elif filler_count <= 8:
        filler_rating = "Medium"
    else:
        filler_rating = "High"

    # 3. Answer Length
    if word_count < 80:
        length_rating = "Too Short"
    elif word_count <= 350:
        length_rating = "Ideal"
    else:
        length_rating = "Too Long"

    # 4. Confidence Markers (hedging language)
    hedges = ["i think maybe", "sort of", "kind of", "i'm not sure but",
              "i guess", "probably", "might have", "not really sure",
              "i hope", "i feel like maybe"]
    hedge_count = sum(text.lower().count(h) for h in hedges)
    if hedge_count == 0:
        hedge_flag = "None detected — strong"
    elif hedge_count <= 2:
        hedge_flag = f"{hedge_count} found — acceptable"
    else:
        hedge_flag = f"{hedge_count} found — reduce hedging"

    # Overall score
    score_points = (
        (star_score / 100) * 40 +
        (1 if filler_rating == "Low" else 0.5 if filler_rating == "Medium" else 0) * 20 +
        (1 if length_rating == "Ideal" else 0.5) * 20 +
        (1 if hedge_count == 0 else 0.5 if hedge_count <= 2 else 0) * 20
    )
    if score_points >= 75:
        overall = "Strong"
    elif score_points >= 50:
        overall = "Good"
    else:
        overall = "Needs Work"

    return {
        "star_score": star_score,
        "star_found": star_found,
        "filler_count": filler_count,
        "filler_rating": filler_rating,
        "word_count": word_count,
        "length_rating": length_rating,
        "hedge_count": hedge_count,
        "hedge_flag": hedge_flag,
        "overall": overall,
        "score_points": round(score_points),
    }

results = None
if user_text:
    results = analyze_transcript(user_text)

    st.markdown("### Scorecard")
    r1c1, r1c2 = st.columns(2)
    r2c1, r2c2 = st.columns(2)

    with r1c1:
        st.metric("STAR Coverage", f"{results['star_score']}%")
        found_labels = [k for k, v in results['star_found'].items() if v]
        missing_labels = [k for k, v in results['star_found'].items() if not v]
        if found_labels:
            st.caption(f"Found: {', '.join(found_labels)}")
        if missing_labels:
            st.warning(f"Missing: {', '.join(missing_labels)}")

    with r1c2:
        st.metric("Filler Words", results['filler_count'], help="um, uh, like, you know...")
        rating_map = {"Low": "success", "Medium": "warning", "High": "error"}
        getattr(st, rating_map[results['filler_rating']])(f"Rating: {results['filler_rating']}")

    with r2c1:
        st.metric("Answer Length", f"{results['word_count']} words")
        if results['length_rating'] == "Ideal":
            st.success("Length: Ideal")
        elif results['length_rating'] == "Too Short":
            st.warning("Too Short — aim for 150–300 words")
        else:
            st.warning("Too Long — tighten your answer")

    with r2c2:
        st.metric("Confidence Markers", results['hedge_count'], help="hedging phrases detected")
        if results['hedge_count'] == 0:
            st.success(results['hedge_flag'])
        elif results['hedge_count'] <= 2:
            st.warning(results['hedge_flag'])
        else:
            st.error(results['hedge_flag'])

    st.markdown("---")
    overall_colors = {"Strong": "success", "Good": "warning", "Needs Work": "error"}
    getattr(st, overall_colors[results['overall']])(
        f"**Overall: {results['overall']}** — score {results['score_points']}/100"
    )

if st.button("💾 Log This Session"):
    if results:
        st.session_state.history.append({
            "Session": len(st.session_state.history) + 1,
            "STAR Score": results['star_score'],
            "Filler Words": results['filler_count'],
            "Word Count": results['word_count'],
            "Hedge Count": results['hedge_count'],
            "Overall": results['overall'],
        })
    else:
        st.session_state.history.append({
            "Session": len(st.session_state.history) + 1,
            "STAR Score": 0,
            "Filler Words": 0,
            "Word Count": 0,
            "Hedge Count": 0,
            "Overall": "—",
        })
    st.toast("Session Saved!")

if st.session_state.history:
    df = pd.DataFrame(st.session_state.history)
    st.plotly_chart(
        px.line(
            df, x="Session",
            y=["STAR Score", "Filler Words", "Word Count"],
            markers=True,
            title="Your Progress Over Time"
        ),
        use_container_width=True
    )
