import streamlit as st
from lists import TEAMS as TEAMS, USERS as USERS

st.title("This app is for logging the guesses of fifa world cup 2026 matches outcome")
st.write(
    "Log your score"
)

with st.form('user_form', clear_on_submit=True):

    user_name = st.selectbox(
        'Select your name',
        options=USERS,
        index=None
    )

    col1, col2 = st.columns([0.8, 0.2])

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
                                        label='Input the score',
                                        min_value=0,
                                        step=1
                                        )
        
        team2_score = st.number_input(key='team2_score', 
                                        label='Input the score',
                                        min_value=0,
                                        step=1
                                        )

    submitted = st.form_submit_button()

if submitted:
    st.write(f'{user_name} chosen {team1_name} playing against {team2_name}\
              with the score {team1_score}:{team2_score}!')