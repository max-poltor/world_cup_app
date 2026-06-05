import streamlit as st
from lists import TEAMS as TEAMS, USERS as USERS

st.write("This app is for logging the guesses of fifa world cup 2026 matches outcome")

# 1. Initialize the session state to track the current step
if 'step' not in st.session_state:
    st.session_state.step = 1

if st.session_state.step == 1:

    with st.form('user_form'):

        user_name = st.selectbox(
            'Select your name',
            options=USERS,
            index=None
        )

        submit_1 = st.form_submit_button('Next')
        
        if submit_1:
            st.session_state.user_name = user_name  # Save data
            st.session_state.step = 2     # Advance to next step
            st.rerun() 

elif st.session_state.step == 2:

    with st.form('score_log'):

        col1, col2 = st.columns([0.5, 0.5])

        with col1:

            team1_score = st.number_input('Input the score for the team1',
                                          min_value=0,
                                          step=1
                                        )
        
        with col2:

            team2_score = st.number_input('Input the score for the team2',
                                          min_value=0,
                                          step=1
                                        )

        submit_2 = st.form_submit_button('Submit')

        if submit_2:
            st.session_state.team1_score = team1_score  # Save data
            st.session_state.team2_score = team2_score  # Save data
            st.session_state.step = 3     # Advance to next step
            st.rerun()

elif st.session_state.step == 3:

    with st.form('results_display'):

        st.write(f'{st.session_state.user_name} chosen team1_name playing against team2_name\
                with the score {st.session_state.team1_score}:{st.session_state.team2_score}!')

        submit_3 = st.form_submit_button('Restart')

        if submit_3:
            st.session_state.step = 1     # Reset to first step
            st.rerun()