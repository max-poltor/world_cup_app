import streamlit as st
import pandas as pd
from lists import *

st.title("This app is for logging the guesses of fifa world cup 2026 matches outcome")
st.write(
    "Log your score"
)

my_container = st.container(border=True)

col1, col2 = my_container.columns([0.8, 0.2])

with col1:
    team1 = st.selectbox(
        'Select the team 1',
        options=TEAMS,
        index=None
    )
with col2:
    score_team1 = st.number_input(key='score_team1', 
                                    label='',
                                    min_value=0,
                                    step=1
                                    )
    
with col1:
    team2 = st.selectbox(
        'Select the team 2',
        options=TEAMS,
        index=None
    )
with col2:
    score_team2 = st.number_input(key='score_team2', 
                                    label='',
                                    min_value=0,
                                    step=1
                                    )

