import os
import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest

def build_feature_matrix(parsed_df: pd.DataFrame) -> pd.DataFrame:
    valid_df = parsed_df[parsed_df['BlockId'] != "UNKNOWN"].copy()
    event_matrix = pd.crosstab(valid_df['BlockId'], valid_df['EventId'])

    level_counts = pd.crosstab(valid_df['BlockId'], valid_df['Level'])
    for level_col in ['WARN', 'ERROR', 'FATAL']:
        if level_col in level_counts.columns:
            event_matrix[f'Level_{level_col}'] = level_counts[level_col]
        else:
            event_matrix[f'Level_{level_col}'] = 0

    event_matrix['Total_Events'] = valid_df.groupby('BlockId').size()
    return event_matrix.fillna(0)

def train_and_detect(feature_matrix: pd.DataFrame, model_path: str, output_results_path: str, contamination: float = 0.05) -> pd.DataFrame:
    feature_cols = list(feature_matrix.columns)
    model = IsolationForest(
        n_estimators=200,
        contamination=contamination,
        random_state=42,
        n_jobs=-1
    )

    raw_preds = model.fit_predict(feature_matrix[feature_cols])
    scores = model.decision_function(feature_matrix[feature_cols])

    results_df = feature_matrix.copy()
    results_df['Anomaly_Flag'] = [1 if pred == -1 else 0 for pred in raw_preds]
    results_df['Anomaly_Score'] = scores
    results_df['Status'] = results_df['Anomaly_Flag'].map({1: 'ANOMALY', 0: 'NORMAL'})

    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump({'model': model, 'features': feature_cols}, model_path)

    results_df.reset_index().to_csv(output_results_path, index=False)
    return results_df.reset_index()