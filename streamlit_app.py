import streamlit as st
import pandas as pd
import numpy as np
from utils.helpers import get_upcoming_matches, calculate_precision, pd_weighted_median, score_prediction
from st_supabase_connection import SupabaseConnection, execute_query

matches = pd.read_csv('data/world_cup_matches.csv') # table with match details and official scores
matches['date'] = pd.to_datetime(matches['date'], dayfirst=True)

st.set_page_config(page_title='FIFA World Cup Score Logger App', page_icon=':soccer:', layout='centered')
st.html('assets/style.css')

# Initialize supabase connection
conn = st.connection(name='supabase', type=SupabaseConnection, ttl=0)
query = conn.table('user_predictions').select('*')
response = execute_query(query, ttl=0)

predictions = pd.DataFrame(pd.json_normalize(response.data))
predictions['time_logged'] = pd.to_datetime(predictions['time_logged'], format='ISO8601', utc=True)
predictions['time_logged'] = predictions['time_logged'].dt.tz_convert('Indian/Mauritius')

with st.sidebar:
    user_name = st.selectbox(
        'Choose your name',
        options=['Deborah', 'Bhavna', 'Max', 'Dmitry', 'Michael', 'Andrey', 'Viewer'],
        index=None
    )

if not user_name:
    st.warning('Please select your name from the sidebar to submit your score predictions.')
    st.stop()

# --- Pre-filter matches ---
upcoming_matches = get_upcoming_matches(matches)

tab1, tab2, tab3, tab4 = st.tabs(['Log scores', 'Group results', 'Leader board', 'All logs'])

with tab1: 

    with st.container(height=1500, border=False):
        for match in upcoming_matches.itertuples():
            
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
                    st.number_input(key=f'{match.match_id}_team1_score', 
                                    label=f'{match.team1} score', 
                                    label_visibility='collapsed', 
                                    disabled=check,
                                    value=None,
                                    min_value=0,
                                    step=1)
                    
                    st.number_input(key=f'{match.match_id}_team2_score', 
                                    label=f'{match.team2} score', 
                                    label_visibility='collapsed', 
                                    disabled=check,
                                    value=None,
                                    min_value=0,
                                    step=1)

                st.write(f'**Date:** {match.date:%d/%m/%Y}')
                
                submitted = st.form_submit_button(
                    'Submit',
                    disabled=check,
                    type='primary'
                )
                
                if submitted:
                    
                    if st.session_state[f'{match.match_id}_team1_score'] is None or st.session_state[f'{match.match_id}_team2_score'] is None:
                        st.warning('Please enter valid scores for both teams before submitting your prediction.')
                        st.stop()

                    st.session_state[key] = True
                    
                    # Create a dictionary of the new data row to be added to the predictions DataFrame
                    new_row = {
                        'match_id': match.match_id,
                        'user_name': user_name,
                        'team1_score': st.session_state[f'{match.match_id}_team1_score'],
                        'team2_score': st.session_state[f'{match.match_id}_team2_score'],
                        'time_logged': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    # update the database with the new predictions DataFrame
                    insert_query = conn.table('user_predictions').insert(new_row)
                    execute_query(insert_query)
                    
                    st.rerun()

with tab2:
    st.subheader('Group results')
    st.write('This section shows the group guess of the matches outcome.')

    # Calculate weights for user predictions based on prediction precision statistics
    played_matches = matches.dropna(subset=['team1_score', 'team2_score'])
 
    if played_matches.empty:
        
        # Calculate medium score predictions for each team in each match
        weighted_predictions = predictions.groupby('match_id').agg(
            team1_score_predicted=('team1_score', 'median'),
            team2_score_predicted=('team2_score', 'median')
        ).reset_index()

    else:
        
        scored = predictions[predictions['match_id'].isin(played_matches['match_id'])].copy()

        # Calculate the precision of predictions by user
        precision_df = calculate_precision(scored, played_matches)
        merged_df = pd.merge(predictions, precision_df, how='left')

        weighted_predictions = merged_df.groupby('match_id').apply(
                lambda x: pd_weighted_median(x, 'team1_score', 'precision')
            ).to_frame('team1_score_predicted').reset_index()

        weighted_predictions['team2_score_predicted'] = merged_df.groupby('match_id').apply(
                lambda x: pd_weighted_median(x, 'team2_score', 'precision')
            ).values 
    
    # Filter to matches that have at least one prediction, then merge
    matches_with_predictions = upcoming_matches[upcoming_matches['match_id'].isin(predictions['match_id'].unique())].merge(weighted_predictions, on='match_id')

    for match in matches_with_predictions.itertuples():

        with st.container(border=True):
            
            # define the winner or the draw
            scores = [match.team1_score_predicted, match.team2_score_predicted]
            win_index = scores.index(max(scores))
            lose_index = scores.index(min(scores))

            if win_index != lose_index:
                st.write('We predict that **{}** will win'.format([match.team1, match.team2][win_index]))
            else:
                st.write('We predict draw')

            st.subheader('Our Score Guess')

            col1, col2, col3 = st.columns([0.3, 0.4, 0.3])
            with col1:
                st.image(f'https://flagcdn.com/{match.team1_code}.svg', width=50)
                st.image(f'https://flagcdn.com/{match.team2_code}.svg', width=50)
            with col2:
                st.write(f'**{match.team1}**')
                st.write(f'**{match.team2}**')
            with col3:
                st.write(f'**{round(match.team1_score_predicted)}**')
                st.write(f'**{round(match.team2_score_predicted)}**')

            st.write(f'**Date:** {match.date:%d/%m/%Y}')


with tab3:
    st.subheader('Leader board')
    # Only score predictions for matches that have official results
 
    if played_matches.empty:
        st.info('The leaderboard will appear here once matches have been played.')
    else:
        scored['points'] = scored.apply(lambda x: score_prediction(x, played_matches), axis=1)

        leaderboard = (
            scored.groupby('user_name')['points']
            .sum()
            .reset_index()
            .rename(columns={'points': 'total_points'})
        )

        leaderboard = pd.merge(leaderboard, precision_df, how='left').sort_values(['total_points', 'precision'], ascending=False).reset_index(drop=True)

        leaderboard.index += 1  # rank starts at 1
        st.dataframe(leaderboard, 
                     column_config={
                         'precision': st.column_config.NumberColumn(
                            format='%.0f %%',
                         )
                     },
                     width='stretch')

with tab4:
    st.subheader('All entries')
    st.dataframe(
        pd.merge(matches[['match_id', 'team1', 'team2']], predictions, on='match_id', how='right'),
        column_config={
            'time_logged': st.column_config.DatetimeColumn(
                format='DD/MM/YYYY HH:mm'
            ),
            'match_id': None,
            'key': None,
        },
        hide_index=True
    )
