import pandas as pd
import numpy as np

def get_upcoming_matches(matches, days=7):
    start_date = pd.to_datetime('today').normalize()
    end_date = start_date + pd.Timedelta(days, unit='d')
    mask = (matches['date'] >= start_date) & (matches['date'] <= end_date)
    return matches.loc[mask]


def calculate_precision(scored, played_matches):
    """Correlation-based precision score (0-100, floored at 0.01) per user."""
    precision = []
    y_true = played_matches[['team1_score', 'team2_score']].values.flatten()

    for user in scored.user_name.unique():
        y_pred = []
        for match in played_matches.match_id.values:
            row = scored[(scored.match_id == match) & (scored.user_name == user)]
            y_pred.extend([np.nan, np.nan] if row.empty else row.iloc[0][['team1_score', 'team2_score']].to_list())
        corr_df = pd.DataFrame({'y_true': y_true, 'y_pred': y_pred})
        precision.append([user, max(corr_df.y_true.corr(corr_df.y_pred) * 100, 0.01)])

    return pd.DataFrame(precision, columns=['user_name', 'precision'])


def pd_weighted_median(df, val_col, weight_col):
    """
    Computes the weighted median for a specific column in a Pandas DataFrame.
    """
    # Sort the dataframe by the target value column
    df_sorted = df.sort_values(by=val_col)
    
    # Calculate the cumulative weight sum
    cumsum = df_sorted[weight_col].cumsum()
    cutoff = df_sorted[weight_col].sum() / 2.0
    
    # Filter for values above the threshold and return the first element
    return df_sorted[cumsum >= cutoff][val_col].iloc[0]


def score_prediction(row, played_matches):
    """
    Award points per prediction row:
        3 pts — exact scoreline
        1 pt  — correct outcome (win/draw/loss) but wrong score
        0 pts — wrong outcome
    """
    official = played_matches[played_matches['match_id'] == row['match_id']]
    if official.empty:
        return 0

    o = official.iloc[0]
    if row['team1_score'] == o['team1_score'] and row['team2_score'] == o['team2_score']:
        return 3  # exact scoreline

    # Compare outcomes: +1 / 0 / -1
    pred_outcome = [row['team1_score'] > row['team2_score'], row['team1_score'] < row['team2_score']]
    real_outcome = [o['team1_score'] > o['team2_score'], o['team1_score'] < o['team2_score']]
    return 1 if pred_outcome == real_outcome else 0