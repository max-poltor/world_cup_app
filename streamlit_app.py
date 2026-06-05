import streamlit as st
<<<<<<< HEAD
from lists import TEAMS as TEAMS

st.title("This app is for logging the guesses of fifa world cup 2026 matches outcome")
st.write(
    "Log your score"
)

my_container = st.container(border=True)

col1, col2 = my_container.columns([0.8, 0.2])

with col1:
    team1_name = st.selectbox(
        'Select the team 1',
        options=TEAMS,
        index=None
    )

    team2_name = st.selectbox(
        'Select the team 2',
        options=TEAMS,
        index=None
    )


with col2:
    team1_score = st.number_input(key='team1_score', 
                                    label='',
                                    min_value=0,
                                    step=1
                                    )
    
    team2_score = st.number_input(key='team2_score', 
                                    label='',
                                    min_value=0,
                                    step=1
                                    )

=======

st.title("🎈 My new app")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)
>>>>>>> 28c9ea698bf00683fe78c40f65e0cb704de6a530
