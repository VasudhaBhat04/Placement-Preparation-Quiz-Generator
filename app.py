import streamlit as st
import time
from utils import QuestionGenerator

generator = QuestionGenerator()

st.title("🚀 Placement Preparation Quiz Generator")


module = st.sidebar.selectbox("Choose Module", ["Technical", "Non-Technical"])
difficulty = st.sidebar.selectbox("Select Difficulty", ["easy", "medium", "difficult"]) if module == "Technical" else None
n_questions = st.sidebar.slider("Number of Questions", 10, 15, 20,step=5)
topic = st.sidebar.selectbox("Select Topic", generator.technical_topics if module == "Technical" else generator.non_technical_topics)
timer_duration = st.sidebar.slider("Timer Duration (minutes)", 10, 15, 20,step=5)

if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}
if "questions" not in st.session_state:
    st.session_state.questions = []

if st.sidebar.button("Generate Questions"):
    st.session_state.start_time = time.time()
    st.session_state.user_answers = {}

    st.session_state.questions = [generator.generate_question(module, topic, difficulty) for _ in range(n_questions)]
    
    st.success("Questions generated! Timer started!")


if st.session_state.start_time:
    elapsed = time.time() - st.session_state.start_time
    remaining = int(timer_duration * 60 - elapsed)
    if remaining > 0:
        st.info(f"⏳ Time Remaining: {remaining // 60}:{remaining % 60:02d}")
    else:
        st.warning("⏰ Time's up! Submit your answers.")

   
    for idx, q in enumerate(st.session_state.questions, 1):
        st.write(f"**Q{idx}. {q.question}**")
        answer = st.radio(f"Choose your answer", options=q.options, key=f"ans_{idx}")
        st.session_state.user_answers[f"Q{idx}"] = answer

    if remaining <= 0 or st.button("Submit Answers"):
        correct = 0
        total = len(st.session_state.questions)
        st.subheader("📊 Results")

        for idx, q in enumerate(st.session_state.questions, 1):
            user_ans = st.session_state.user_answers.get(f"Q{idx}", "Not Answered")
            correct_ans = q.correct_answer
            st.write(f"**Q{idx}** - Your Answer: {user_ans} | Correct: {correct_ans}")
            st.write(f"Explanation: {q.explanation}")
            if user_ans == correct_ans:
                correct += 1

        st.success(f"You got {correct}/{total} correct!")