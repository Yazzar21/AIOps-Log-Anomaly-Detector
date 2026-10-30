def build_event_count_matrix(parsed_df):
    valid_df = parsed_df[parsed_df['BlockId'] != "UNKNOWN"]
    event_matrix = pd.crosstab(valid_df['BlockId'], valid_df['EventId'])
    return event_matrix