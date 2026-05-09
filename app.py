import time
import streamlit as st

try:
    from streamlit_autorefresh import st_autorefresh
    _HAS_AUTOREFRESH = True
except ImportError:
    _HAS_AUTOREFRESH = False

from utils import QuestionGenerator

st.set_page_config(
    page_title="Placement Quiz Generator",
    layout="wide",
)

st.title("Placement Preparation Quiz Generator")

generator = QuestionGenerator()

with st.sidebar:
    st.header("Quiz Settings")

    module = st.selectbox("Choose Module", ["Technical", "Non-Technical"])

    difficulty = (
        st.selectbox("Select Difficulty", ["easy", "medium", "difficult"])
        if module == "Technical"
        else None
    )

    n_questions = st.select_slider(
        "Number of Questions", options=[10, 15, 20], value=10
    )

    topic = st.selectbox(
        "Select Topic",
        generator.technical_topics
        if module == "Technical"
        else generator.non_technical_topics,
    )

    timer_minutes = st.select_slider(
        "Timer Duration (minutes)", options=[10, 15, 20], value=10
    )

    generate_btn = st.button("Generate Questions", use_container_width=True)

defaults = {
    "start_time": None,
    "user_answers": {},
    "questions": [],
    "submitted": False,
    "quiz_active": False,
    "score": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

if st.session_state.quiz_active and not st.session_state.submitted:
    if _HAS_AUTOREFRESH:
        st_autorefresh(interval=1_000, key="quiz_timer")
    else:
        st.caption(
            "Install streamlit-autorefresh for a live countdown: "
            "pip install streamlit-autorefresh"
        )

if generate_btn:
    progress_bar = st.progress(0, text="Generating questions...")
    seen: set = set()
    questions = []

    for i in range(n_questions):
        progress_bar.progress(
            (i + 1) / n_questions,
            text=f"Generating question {i + 1}/{n_questions}...",
        )
        q = generator.generate_question(
            module, topic, difficulty, seen_questions=seen
        )
        seen.add(q.question)
        questions.append(q)

    progress_bar.empty()

    st.session_state.questions = questions
    st.session_state.start_time = time.time()
    st.session_state.user_answers = {}
    st.session_state.submitted = False
    st.session_state.quiz_active = True
    st.session_state.score = None

    st.success(f"{n_questions} unique questions generated! Timer started.")

if st.session_state.start_time and st.session_state.questions:
    timer_seconds = timer_minutes * 60
    elapsed = time.time() - st.session_state.start_time
    remaining = int(timer_seconds - elapsed)

    timer_box = st.empty()
    if remaining > 0 and not st.session_state.submitted:
        mins, secs = divmod(remaining, 60)
        timer_box.info(f"Time Remaining: **{mins:02d}:{secs:02d}**")
    elif not st.session_state.submitted:
        timer_box.error("Time's up! Answers auto-submitted.")
        st.session_state.submitted = True
        st.session_state.quiz_active = False

    if not st.session_state.submitted:
        st.markdown("---")
        for idx, q in enumerate(st.session_state.questions, 1):
            with st.container():
                st.markdown(f"**Q{idx}. {q.question}**")
                chosen = st.radio(
                    f"q{idx}_label",
                    options=q.options,
                    key=f"ans_{idx}",
                    index=None,
                    label_visibility="collapsed",
                )
                st.session_state.user_answers[f"Q{idx}"] = chosen
                st.markdown("")

        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("Submit Answers", use_container_width=True):
                st.session_state.submitted = True
                st.session_state.quiz_active = False
                st.rerun()

    if st.session_state.submitted:
        questions = st.session_state.questions
        answers = st.session_state.user_answers
        correct_count = 0
        total = len(questions)

        st.markdown("---")
        st.subheader("Results")

        for idx, q in enumerate(questions, 1):
            user_ans = answers.get(f"Q{idx}") or "Not Answered"
            correct_ans = q.correct_answer
            is_correct = user_ans == correct_ans
            if is_correct:
                correct_count += 1

            status = "Correct" if is_correct else "Incorrect"
            with st.expander(f"[{status}] Q{idx}. {q.question}", expanded=False):
                st.write(f"**Your answer:** {user_ans}")
                st.write(f"**Correct answer:** {correct_ans}")
                st.info(q.explanation)

        pct = correct_count / total * 100
        st.markdown("---")
        if pct >= 80:
            st.success(f"Score: **{correct_count}/{total}** ({pct:.0f}%) - Excellent!")
        elif pct >= 50:
            st.warning(f"Score: **{correct_count}/{total}** ({pct:.0f}%) - Good effort!")
        else:
            st.error(f"Score: **{correct_count}/{total}** ({pct:.0f}%) - Keep practising!")

        st.markdown("")
        if st.button("Start a New Quiz"):
            for k, v in defaults.items():
                st.session_state[k] = v
            st.rerun()
