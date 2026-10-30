import os
import re
import pandas as pd
from drain3 import TemplateMiner
from drain3.template_miner_config import TemplateMinerConfig

def parse_hdfs_logs(raw_log_path: str, output_parsed_path: str, output_templates_path: str) -> pd.DataFrame:
    config = TemplateMinerConfig()
    config.profiling_enabled = False
    miner = TemplateMiner(config=config)

    log_pattern = re.compile(
        r'^(?P<Date>\d{6})\s+(?P<Time>\d{6})\s+(?P<PID>\d+)\s+'
        r'(?P<Level>\w+)\s+(?P<Component>[^:]+):\s+(?P<Content>.*)$'
    )
    blk_pattern = re.compile(r'(blk_-?\d+)')

    parsed_records = []
    with open(raw_log_path, 'r', encoding='utf-8', errors='replace') as file:
        for line_num, line in enumerate(file, start=1):
            match = log_pattern.match(line.strip())
            if not match:
                continue

            content = match.group('Content')
            blk_match = blk_pattern.search(content)
            block_id = blk_match.group(1) if blk_match else "UNKNOWN"

            result = miner.add_log_message(content)
            event_id = f"E{result['cluster_id']}"
            template = result['template_mined']

            parsed_records.append({
                'LineId': line_num,
                'Date': match.group('Date'),
                'Time': match.group('Time'),
                'PID': int(match.group('PID')),
                'Level': match.group('Level'),
                'Component': match.group('Component'),
                'BlockId': block_id,
                'EventId': event_id,
                'EventTemplate': template,
                'RawContent': content
            })

    parsed_df = pd.DataFrame(parsed_records)
    os.makedirs(os.path.dirname(output_parsed_path), exist_ok=True)
    parsed_df.to_csv(output_parsed_path, index=False)

    templates_df = (
        parsed_df.groupby(['EventId', 'EventTemplate'])
        .size()
        .reset_index(name='Occurrences')
        .sort_values(by='Occurrences', ascending=False)
    )
    templates_df.to_csv(output_templates_path, index=False)
    return parsed_df