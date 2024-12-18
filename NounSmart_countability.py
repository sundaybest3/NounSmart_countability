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
    st.error(f"The following required columns are missing in the CSV: {', '.join(missing_columns)}")
    st.stop()

# Initialize game state in session state
if 'game_state' not in st.session_state:
    st.session_state.game_state = {
        "nickname": None,
        "page": None,
        "current_noun": None,
        "remaining_nouns": None,
        "score": 0,
        "trials": 0,
    }

game_state = st.session_state.game_state

# Function to filter nouns by page and prepare the list of nouns
def initialize_nouns(page):
    filtered_df = df[df["Page"] == page]
    if filtered_df.empty:
        return "No nouns available for this page. Please select a different page."
    game_state["remaining_nouns"] = filtered_df.sample(frac=1).to_dict(orient="records")
    return show_random_noun()

# Function to show a random noun
def show_random_noun():
    if not game_state["remaining_nouns"]:
        return f"\U0001F389 Great job, {game_state['nickname']}! All nouns have been answered correctly. (Score: {game_state['score']}/{game_state['trials']})"

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
        feedback = f"✅ Correct! {game_state['current_noun']['Word']} is {correct_answer} on page {game_state['page']}. Click 'Show the Noun' to continue."
    else:
        # Add the noun back to the remaining list for retry
        game_state["remaining_nouns"].insert(0, game_state["current_noun"])
        feedback = f"\u274C Incorrect. {game_state['current_noun']['Word']} is actually {correct_answer}. It will appear again."

    if not game_state["remaining_nouns"]:
        feedback = f"\U0001F389 Great job, {game_state['nickname']}! All nouns have been answered correctly. (Score: {game_state['score']}/{game_state['trials']})"

    return feedback

# Function to get page summary with noun count
def get_page_summary():
    summary = df.groupby("Page").size().reset_index(name="Total")
    summary["Display"] = summary["Page"].astype(str) + " (" + summary["Total"].astype(str) + " nouns)"
    return summary[["Page", "Display"]]

# Streamlit interface
st.title("NounSmart: Practice Singular and Plural Nouns")

# User input
nickname = st.text_input("Enter your nickname:", key="nickname_input")
page_summary = get_page_summary()
page_choices = page_summary.set_index("Page")["Display"].to_dict()
selected_page_display = st.selectbox("Select your page:", list(page_choices.values()), key="page_selector")

# Map display back to page
selected_page = next(page for page, display in page_choices.items() if display == selected_page_display)

# Show the noun button
if st.button("Show the Noun", key="show_noun_button"):
    if not game_state["nickname"] or game_state["nickname"] != nickname:
        game_state.update({
            "nickname": nickname,
            "page": selected_page,
            "current_noun": None,
            "remaining_nouns": None,
            "score": 0,
            "trials": 0,
        })
        st.write(initialize_nouns(selected_page))
    else:
        st.write(show_random_noun())

# Answer input
if game_state.get("current_noun"):
    user_choice = st.radio("Is the noun countable or uncountable?", ["Countable", "Uncountable"], key="user_choice_radio")
    if st.button("Submit Answer", key="submit_answer_button"):
        st.write(check_answer(user_choice))

# Display score
if game_state["trials"] > 0:
    st.write(f"Score: {game_state['score']} / {game_state['trials']}")
