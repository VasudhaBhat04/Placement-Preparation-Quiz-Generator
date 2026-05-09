Inspired by a UPSC question generator logic seen on YouTube; adapted and extended it for placement prep quizzes with custom modules, difficulty levels, and  Pre- trained LLM (GROQ) integration.

Contains 2 modules:
Technical: Covers topics like Data Structures, Algorithms, DBMS, SQL, Operating Systems, OOPs, Computer Networks, etc.
Users can select from Easy, Medium, or Difficult levels.
Choose from 10, 15, or 20-question.
And a countdown timer of 10,15 & 20 minutes


Non-Technical: Includes Aptitude, Logical Reasoning & Verbal Ability .
Choose from 10, 15, or 20-question.
And a countdown timer of 10,15 & 20 minutes

Users submit answers and can anaylize their answers too...

Questions and options are generated in real-time using Groq-hosted LLaMA 3 models via LangChain.

app.py: Streamlit frontend that handles quiz flow, UI, timer, and result display.

utils.py: Backend logic for generating questions using Groq LLM and evaluating answers.

.env: Stores your generated Groq API key to load with dotenv.
