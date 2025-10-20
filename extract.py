import re
import csv
from datetime import datetime, timedelta
import argparse


parser = argparse.ArgumentParser(description="Specify log directory with parsed values")
parser.add_argument('--log', required=True, help="Input directory")
parser.add_argument('--output', required=True, help="Output file name")
args = parser.parse_args()

log_file = args.log
out_file = args.output

# regex
pattern_start = re.compile(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+): I tensorflow")
# pattern_line = re.compile(
#     r"\((\d{2}-\d{2})\) (\d{2}:\d{2}:\d{2}) INFO\s+\[.*\] FL Testing in round: (\d+).*'top_1': ([0-9.]+)"
# )
pattern_line = re.compile(
    r"\((\d{2}-\d{2})\)\s+(\d{2}:\d{2}:\d{2}).*FL Testing in round: (\d+).*'top_1': ([0-9.]+).*'loss': ([0-9.]+)"
)

results = []
start_time = None
prev_time = None
base_year = None

with open(log_file, "r") as f:
    for line in f:
        # dòng đầu tiên (thời gian bắt đầu training)
        if start_time is None:
            match_start = pattern_start.search(line)
            if match_start:
                start_time = datetime.strptime(match_start.group(1), "%Y-%m-%d %H:%M:%S.%f")
                prev_time = start_time
                base_year = start_time.year
                continue

        # các dòng kết quả round
        match_round = pattern_line.search(line)
        if match_round:
            date_str = match_round.group(1)  # MM-DD
            time_str = match_round.group(2)  # HH:MM:SS
            round_id = int(match_round.group(3))
            acc = float(match_round.group(4))
            loss = float(match_round.group(5))

            # giả định cùng năm với start_time
            timestamp = datetime.strptime(f"{base_year}-{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")

            # nếu timestamp < prev_time -> tức là qua năm mới
            if timestamp < prev_time:
                base_year += 1
                timestamp = datetime.strptime(f"{base_year}-{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")

            # thời gian round = timestamp hiện tại - prev_time
            elapsed = (timestamp - prev_time).total_seconds()
            prev_time = timestamp

            results.append((round_id, elapsed, acc, loss))

# Ghi CSV
with open(out_file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["round", "time", "accuracy", "loss"])
    writer.writerows(results)

print(f"Saved {len(results)} rounds to {out_file}")
