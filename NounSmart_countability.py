import streamlit as st
import pandas as pd
import random

# Load the CSV file
csv_url = "https://raw.githubusercontent.com/sundaybest3/NounSmart_countability/refs/heads/main/nouns_CE_visang.csv"
df = pd.read_csv(csv_url)

# Inspect the columns
expected_columns = ["Page", "Word", "Countability"]
missing_columns = [col for col in expected_columns if col not in df.columns]
if missing_columns:
    raise ValueError(f"The following required columns are missing in the CSV: {', '.join(missing_columns)}")

# Initialize game state
game_state = {
    "nickname": None,
    "page": None,
    "current_noun": None,
    "remaining_nouns": None,
    "total_nouns": 0,
    "score": 0,
    "trials": 0,
}

# Function to filter nouns by page and prepare the list of nouns
def initialize_nouns(page):
    filtered_df = df[df["Page"] == page]
    if filtered_df.empty:
        return "No nouns available for this page. Please select a different page.", ""
    game_state["remaining_nouns"] = filtered_df.sample(frac=1).to_dict(orient="records")
    game_state["total_nouns"] = len(game_state["remaining_nouns"])
    game_state["score"] = 0
    game_state["trials"] = 0
    return show_random_noun(), "Ready to start!"

# Function to reset the game state when a new page is chosen
def reset_game_state():
    game_state["current_noun"] = None
    game_state["remaining_nouns"] = None
    game_state["total_nouns"] = 0
    game_state["score"] = 0
    game_state["trials"] = 0

# Function to show a random noun
def show_random_noun():
    if not game_state["remaining_nouns"]:
        return "No more nouns available. Click 'Submit Answer' to see your final feedback."

    game_state["current_noun"] = game_state["remaining_nouns"].pop()
    return game_state["current_noun"]["Word"]

# Function to check user's answer
def check_answer(user_choice):
    if not game_state.get("current_noun"):
        return "Please click 'Show the Noun' first."

    correct_answer = game_state["current_noun"]["Countability"].strip().lower()
    game_state["trials"] += 1

    if user_choice.lower() == correct_answer:
        game_state["score"] += 1
        feedback = f"✅ Correct! {game_state['current_noun']['Word']} is {correct_answer}. Click 'Show the Noun' to continue."
    else:
        game_state["remaining_nouns"].insert(0, game_state["current_noun"])
        feedback = f"❌ Incorrect. {game_state['current_noun']['Word']} is actually {correct_answer}. It will appear again. Click 'Show the Noun' to continue."

    # Check if all nouns are processed correctly
    if game_state["score"] == game_state["total_nouns"]:
        feedback += f"\n🎉 Great job, {game_state['nickname']}! All nouns have been answered correctly. Final Score: {game_state['score']} / {game_state['trials']} Choose another page for more practice."
    else:
        feedback += f"\nCurrent Score: {game_state['score']} / {game_state['trials']}"

    return feedback

# Function to get page summary with noun count
def get_page_summary():
    summary = df.groupby("Page").size().reset_index(name="Total")
    summary["Display"] = summary["Page"].astype(str) + " (" + summary["Total"].astype(str) + " nouns)"
    return summary["Display"].to_list()

# Streamlit interface
st.title("NounSmart: Countability")
st.write("### Look at the textbook page you selected and find out whether the noun is countable or not.")

# Input fields
nickname = st.text_input("Enter your nickname:", key="nickname")
page_choices = get_page_summary()
page = st.selectbox("Select a page:", options=["Select a page..."] + page_choices, key="page")

if st.button("Start Game"):
    if not nickname:
        st.write("⛔ Please enter your nickname to start.")
    elif page == "Select a page...":
        st.write("⛔ Please select a page to start.")
    else:
        selected_page = int(page.split(" (")[0])  # Extract the page number
        if game_state["nickname"] != nickname or game_state["page"] != selected_page:
            reset_game_state()
            game_state["nickname"] = nickname
            game_state["page"] = selected_page
            noun, feedback = initialize_nouns(selected_page)
        else:
            noun = show_random_noun()
            feedback = "Ready to continue!"
        st.write("### Noun:")
        st.write(noun)
        st.write("### Feedback and Score:")
        st.write(feedback)

    user_choice = st.radio("Your answer:", options=["Countable", "Uncountable"], key="user_choice")
    if st.button("Submit Answer"):
        feedback = check_answer(user_choice)
        noun = game_state["current_noun"]["Word"] if game_state["current_noun"] else ""
        st.write("### Noun:")
        st.write(noun)
        st.write("### Feedback and Score:")
        st.write(feedback)

