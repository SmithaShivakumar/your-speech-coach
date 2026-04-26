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
        "Tell me about the most complex financial model you have built.",
        "Describe a time you had to present a recommendation a client did not want to hear.",
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
        "How do you decide what to measure when the right metric is not obvious?",
        "Describe a time you had to make a decision with very little data.",
        "How do you distinguish between correlation and causation in practice?",
        "Tell me about a time a dashboard or report led to a wrong conclusion.",
        "How do you handle a situation where different teams use different definitions of the same metric?",
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
    return [q for qs in QUESTION_BANK.values() for q in qs]

def get_new_question():
    """Pick a new question. Never touches timer state."""
    cat  = st.session_state.selected_category
    pool = get_all_questions() if cat == "All" else QUESTION_BANK[cat]
    st.session_state.current_question = random.choice(pool)

def reset_timer_only():
    """Reset timer state only. Current question is intentionally preserved."""
    st.session_state.think_start    = None
    st.session_state.think_done     = False
    st.session_state.start_time     = None
    st.session_state.section_resets = {}
    st.session_state.paused         = False
    st.session_state.paused_at      = None

# --- SESSION STATE INIT ---
_defaults = {
    "selected_category": "All",
    "think_start":       None,
    "think_done":        False,
    "think_duration":    30,
    "start_time":        None,
    "paused":            False,
    "paused_at":         None,
    "section_resets":    {},
    "history":           [],
}
for _k, _v in _defaults.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# current_question in its own block so it is never clobbered by defaults loop
if "current_question" not in st.session_state:
    st.session_state.current_question = random.choice(get_all_questions())


# --- 2. VIDEO RECORDER ---
def make_recorder_html(autostart: bool) -> str:
    flag = "true" if autostart else "false"
    hint = "Recording will start automatically..." if autostart else "Press RECORD to begin."
    return f"""
<div style="text-align:center;font-family:sans-serif;background:#111;
            padding:15px;border-radius:15px;">
  <video id="vid" width="100%" autoplay muted
         style="border-radius:10px;border:2px solid #333;"></video>
  <div id="hint" style="color:#aaa;font-size:12px;margin:6px 0;">{hint}</div>
  <button id="recBtn"
    style="margin:6px;padding:10px 18px;background:#28a745;color:#fff;
           border:none;border-radius:5px;cursor:pointer;font-weight:bold;">
    RECORD
  </button>
  <button id="stopBtn"
    style="margin:6px;padding:10px 18px;background:#dc3545;color:#fff;
           border:none;border-radius:5px;cursor:pointer;font-weight:bold;">
    STOP & SAVE
  </button>
</div>
<script>
(function(){{
  var autostart = {flag};
  var recBtn  = document.getElementById('recBtn');
  var stopBtn = document.getElementById('stopBtn');
  var vid     = document.getElementById('vid');
  var hint    = document.getElementById('hint');
  var mr, chunks=[], stream;

  async function startRec(){{
    try{{
      stream = await navigator.mediaDevices.getUserMedia({{video:true,audio:true}});
      vid.srcObject = stream;
      mr = new MediaRecorder(stream);
      mr.ondataavailable = function(e){{ chunks.push(e.data); }};
      mr.onstop = function(){{
        var blob = new Blob(chunks,{{type:'video/webm'}});
        var url  = URL.createObjectURL(blob);
        var a    = document.createElement('a');
        a.href=url; a.download='speech_practice.webm'; a.click();
        chunks=[];
      }};
      mr.start();
      recBtn.disabled=true;
      hint.textContent='Recording...';
      hint.style.color='#ff4444';
    }}catch(e){{
      hint.textContent='Camera/mic access denied.';
    }}
  }}

  recBtn.onclick  = startRec;
  stopBtn.onclick = function(){{
    if(mr && mr.state!=='inactive'){{
      mr.stop();
      if(stream) stream.getTracks().forEach(function(t){{t.stop();}});
      recBtn.disabled=false;
      hint.textContent='Saved to your device.';
      hint.style.color='#44ff88';
    }}
  }};

  if(autostart){{ setTimeout(startRec, 500); }}
}})();
</script>
"""


# --- 3. MAIN INTERFACE ---
st.title("Psyc-Check: Speaking Mastery")
st.write("Master your pacing, track your framework, and stay on point.")

col_left, col_right = st.columns([1, 2])

with col_left:
    # Category filter
    cat_options = ["All"] + ALL_CATEGORIES
    selected = st.selectbox(
        "Question category", cat_options,
        index=cat_options.index(st.session_state.selected_category),
        key="category_select"
    )
    if selected != st.session_state.selected_category:
        st.session_state.selected_category = selected
        get_new_question()
        st.rerun()

    st.info(f"**YOUR QUESTION:** {st.session_state.current_question}")

    if st.button("Next Question"):
        get_new_question()
        st.rerun()

    # Think timer
    st.subheader("Think Time")
    think_map = {"15 seconds": 15, "30 seconds": 30, "60 seconds": 60}
    chosen = st.selectbox("How long to think?", list(think_map.keys()), index=1)
    st.session_state.think_duration = think_map[chosen]

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Start Think Timer", use_container_width=True):
            st.session_state.think_start = time.time()
            st.session_state.think_done  = False
            st.rerun()
    with c2:
        if st.button("Skip, Start Now", use_container_width=True):
            st.session_state.think_done     = True
            st.session_state.start_time     = time.time()
            st.session_state.section_resets = {}
            st.session_state.paused         = False
            st.session_state.paused_at      = None
            st.rerun()

    # Think timer countdown
    if st.session_state.think_start and not st.session_state.think_done:
        et = time.time() - st.session_state.think_start
        rt = st.session_state.think_duration - et
        if rt > 0:
            st.markdown(f"### Think: `{rt:.1f}s`")
            st.progress(min(et / st.session_state.think_duration, 1.0))
            time.sleep(0.1)
            st.rerun()
        else:
            st.session_state.think_done     = True
            st.session_state.start_time     = time.time()
            st.session_state.section_resets = {}
            st.session_state.paused         = False
            st.session_state.paused_at      = None
            st.success("Think time done. Begin speaking!")
            time.sleep(0.1)
            st.rerun()

    # Video — auto-starts once speaking timer is live and not paused
    autostart_rec = (
        st.session_state.think_done and
        st.session_state.start_time is not None and
        not st.session_state.paused
    )
    st.subheader("Video Practice")
    html(make_recorder_html(autostart=autostart_rec), height=430)
    st.caption("Video saves directly to your device — nothing is uploaded.")

with col_right:
    st.subheader("Live Framework Tracker")

    if not st.session_state.start_time and not st.session_state.think_start:
        st.info("Start the Think Timer or click 'Skip, Start Now' to begin.")

    if st.session_state.start_time:
        # Elapsed: frozen when paused
        if st.session_state.paused:
            elapsed = st.session_state.paused_at
        else:
            elapsed = time.time() - st.session_state.start_time

        # Control buttons
        bc1, bc2 = st.columns(2)
        with bc1:
            if st.session_state.paused:
                if st.button("Resume", use_container_width=True):
                    st.session_state.start_time = time.time() - st.session_state.paused_at
                    st.session_state.paused     = False
                    st.session_state.paused_at  = None
                    st.rerun()
            else:
                if st.button("Pause", use_container_width=True):
                    st.session_state.paused_at = time.time() - st.session_state.start_time
                    st.session_state.paused    = True
                    st.rerun()
        with bc2:
            if st.button("Reset Timer", use_container_width=True):
                reset_timer_only()   # question is NOT changed
                st.rerun()

        if st.session_state.paused:
            st.warning("Paused. Press Resume to continue.")

        # Section-by-section display
        cum_time      = 0
        still_running = False

        for idx, (name, duration) in enumerate(SPEECH_STRUCTURE):
            section_key   = f"reset_{idx}"
            reset_offset  = st.session_state.section_resets.get(section_key, 0)
            adjusted      = elapsed - reset_offset

            if adjusted < cum_time:
                st.markdown(f"- {name} ({duration}s)")
            elif adjusted <= cum_time + duration:
                if not st.session_state.paused:
                    still_running = True
                sec_elapsed = adjusted - cum_time
                remaining   = duration - sec_elapsed
                st.markdown(f"### {name.upper()}")
                ca, cb = st.columns([3, 1])
                with ca:
                    st.progress(min(sec_elapsed / duration, 1.0))
                    if remaining <= 5:
                        st.error(f"Wrap up! {remaining:.1f}s left")
                    else:
                        st.markdown(f"`{remaining:.1f}s` remaining")
                with cb:
                    if st.button("Redo", key=f"redo_{idx}"):
                        st.session_state.section_resets[section_key] = (
                            st.session_state.section_resets.get(section_key, 0) + sec_elapsed
                        )
                        st.rerun()
            else:
                st.markdown(f"- ~~{name}~~ done")

            cum_time += duration

        total_with_redos = TOTAL_TIME + sum(st.session_state.section_resets.values())
        if still_running:
            time.sleep(0.1)
            st.rerun()
        elif elapsed >= total_with_redos:
            st.success("All sections complete!")


# --- 4. POST-SESSION ANALYSIS ---
st.divider()
st.subheader("Post-Session Analysis")
st.caption("Paste your transcript for a full evaluation.")

user_text = st.text_area("Paste transcript here:", height=150)

def analyze_transcript(text):
    wc = len(text.lower().split())

    star_kw = {
        "Situation": ["situation", "context", "background", "when", "working at", "was at"],
        "Task":      ["task", "responsibility", "goal", "objective", "needed to", "had to", "my role"],
        "Action":    ["action", "i did", "i built", "i created", "i led", "i implemented",
                      "i decided", "i proposed", "i reached out", "i worked", "i ran", "i designed"],
        "Result":    ["result", "outcome", "impact", "achieved", "increased", "decreased",
                      "reduced", "saved", "improved", "delivered", "shipped", "led to"],
    }
    star_found = {c: any(kw in text.lower() for kw in kws) for c, kws in star_kw.items()}
    star_score = int((sum(star_found.values()) / 4) * 100)

    fillers      = ["um", "uh", "like", "you know", "basically", "literally",
                    "right?", "so yeah", "i mean", "sort of", "kind of"]
    filler_count = sum(text.lower().count(f) for f in fillers)
    filler_rating = "Low" if filler_count <= 3 else "Medium" if filler_count <= 8 else "High"

    length_rating = "Too Short" if wc < 80 else "Ideal" if wc <= 350 else "Too Long"

    hedges      = ["i think maybe", "sort of", "kind of", "i'm not sure but",
                   "i guess", "probably", "might have", "not really sure",
                   "i hope", "i feel like maybe"]
    hedge_count = sum(text.lower().count(h) for h in hedges)
    hedge_flag  = ("None detected" if hedge_count == 0
                   else f"{hedge_count} found - acceptable" if hedge_count <= 2
                   else f"{hedge_count} found - reduce hedging")

    pts = (
        (star_score / 100) * 40 +
        (1 if filler_rating == "Low" else 0.5 if filler_rating == "Medium" else 0) * 20 +
        (1 if length_rating == "Ideal" else 0.5) * 20 +
        (1 if hedge_count == 0 else 0.5 if hedge_count <= 2 else 0) * 20
    )
    overall = "Strong" if pts >= 75 else "Good" if pts >= 50 else "Needs Work"

    return dict(star_score=star_score, star_found=star_found,
                filler_count=filler_count, filler_rating=filler_rating,
                word_count=wc, length_rating=length_rating,
                hedge_count=hedge_count, hedge_flag=hedge_flag,
                overall=overall, score_points=round(pts))

results = None
if user_text:
    results = analyze_transcript(user_text)
    st.markdown("### Scorecard")
    r1c1, r1c2 = st.columns(2)
    r2c1, r2c2 = st.columns(2)

    with r1c1:
        st.metric("STAR Coverage", f"{results['star_score']}%")
        found   = [k for k, v in results['star_found'].items() if v]
        missing = [k for k, v in results['star_found'].items() if not v]
        if found:   st.caption(f"Found: {', '.join(found)}")
        if missing: st.warning(f"Missing: {', '.join(missing)}")

    with r1c2:
        st.metric("Filler Words", results['filler_count'])
        {"Low": st.success, "Medium": st.warning, "High": st.error}[results['filler_rating']](
            f"Rating: {results['filler_rating']}")

    with r2c1:
        st.metric("Answer Length", f"{results['word_count']} words")
        if   results['length_rating'] == "Ideal":     st.success("Ideal length")
        elif results['length_rating'] == "Too Short": st.warning("Too short — aim for 150-300 words")
        else:                                         st.warning("Too long — tighten your answer")

    with r2c2:
        st.metric("Confidence Markers", results['hedge_count'])
        if   results['hedge_count'] == 0:  st.success(results['hedge_flag'])
        elif results['hedge_count'] <= 2:  st.warning(results['hedge_flag'])
        else:                              st.error(results['hedge_flag'])

    st.markdown("---")
    {"Strong": st.success, "Good": st.warning, "Needs Work": st.error}[results['overall']](
        f"**Overall: {results['overall']}** — {results['score_points']}/100")

if st.button("Log This Session"):
    st.session_state.history.append({
        "Session":      len(st.session_state.history) + 1,
        "STAR Score":   results['star_score']   if results else 0,
        "Filler Words": results['filler_count'] if results else 0,
        "Word Count":   results['word_count']   if results else 0,
        "Hedge Count":  results['hedge_count']  if results else 0,
        "Overall":      results['overall']      if results else "--",
    })
    st.toast("Session Saved!")

if st.session_state.history:
    df = pd.DataFrame(st.session_state.history)
    st.plotly_chart(
        px.line(df, x="Session", y=["STAR Score", "Filler Words", "Word Count"],
                markers=True, title="Your Progress Over Time"),
        use_container_width=True
    )
