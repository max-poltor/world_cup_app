import streamlit as st
import pandas as pd
from sqlalchemy import text

matches = pd.read_csv('data/world_cup_matches.csv') # table with match details and official scores

st.set_page_config(page_title='FIFA World Cup Score Logger App', page_icon=':soccer:', layout='wide')

# Initialize connection.
conn = st.connection('mysql', type='sql')
predictions = conn.query('SELECT * from user_predictions;', ttl=0) # table with user predictions

with st.sidebar:
    user_name = st.selectbox(
        'Choose your name',
        options=['Deborah', 'Bhavna', 'Max'],
        index=None
    )

if not user_name:
    st.warning('Please select your name from the sidebar to submit your score predictions.')
    st.stop()

main_col1, main_col2 = st.columns([0.6, 0.4])

with main_col1:
    with st.container(height=1500, border=False):
        for match in matches.itertuples():
            
            # Render only those forms that are for upcoming matches within a week from today.
            if pd.to_datetime(match.date, dayfirst=True) < pd.to_datetime('today') + pd.to_timedelta(7, unit='d'):

                key = f'submitted_{match.match_id}_{user_name}'

                in_db = user_name in predictions[predictions['match_id'] == match.match_id]['user_name'].values
                in_session = st.session_state.get(key, False)
                check = in_db or in_session

                with st.form(key=f'form_container_{match.match_id}_{user_name}', border=True):

                    st.write('Enter your score predictions for the match between **{}** and **{}** and press submit button'.format(match.team1, match.team2))

                    st.subheader('Match Details')

                    col1, col2, col3 = st.columns([0.3, 0.4, 0.3])
                    with col1:
                        st.image(f'https://flagcdn.com/{match.team1_code}.svg', width=50)
                        st.image(f'https://flagcdn.com/{match.team2_code}.svg', width=50)
                    with col2:
                        st.write(f'**{match.team1}**')
                        st.write(f'**{match.team2}**')
                    with col3:
                        st.text_input(key=f'{match.match_id}_team1_score', label='', label_visibility='collapsed', disabled=check)
                        st.text_input(key=f'{match.match_id}_team2_score', label='', label_visibility='collapsed', disabled=check)

                    st.write(f'**Date:** {match.date}')
                    
                    submitted = st.form_submit_button(
                        'Submit',
                        disabled=check,
                        type='primary'
                    )
                    
                    if submitted:

                        st.session_state[key] = True
                        
                        # Create a dictionary of the new data row to be added to the predictions DataFrame
                        new_row = {
                            'match_id': match.match_id,
                            'user_name': user_name,
                            'team1_score': st.session_state[f'{match.match_id}_team1_score'],
                            'team2_score': st.session_state[f'{match.match_id}_team2_score']
                        }
                        
                        # Convert the dictionary to a DataFrame
                        new_df = pd.DataFrame([new_row])

                        # Append the new DataFrame to the existing predictions DataFrame
                        predictions = pd.concat([predictions, new_df], ignore_index=True)

                        # update the database with the new predictions DataFrame
                        with conn.session as session:
                            session.execute(
                                text(
                                    "INSERT INTO user_predictions (match_id, user_name, team1_score, team2_score) "
                                    "VALUES (:match_id, :user_name, :team1_score, :team2_score)"
                                ),
                                params=new_row
                            )
                            session.commit()
                        
                        st.rerun()

                    else:
                        pass

with main_col2:
    st.table(predictions)