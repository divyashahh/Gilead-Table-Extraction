import csv
import re
from collections import Counter

# === CONFIG ===
input_csv = "outputs/gilead_digital.csv"
output_csv = "outputs/gilead_digital_structured.csv"
preview_limit = 5

# === STEP 1: Read blocks from original CSV ===
raw_blocks = []
with open(input_csv, "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    for row in reader:
        if row and row[0].lower() != "page":  # Skip header
            raw_blocks.append(row[1])  # Just the "Text" column

# === STEP 2: Parse and split each block into rows and cells ===
structured_rows = []
row_lengths = []

for block in raw_blocks:
    lines = block.split('\n')
    for line in lines:
        # Ignore decorative lines or short noise
        if len(line.strip()) < 3 or set(line.strip()) <= set("-_=*^# "):
            continue
        # Split line into cells using tabs, commas, or multi-spaces
        cells = re.split(r'\t|,{1}| {2,}', line)
        cleaned = [c.strip() for c in cells if c.strip()]
        if cleaned:
            structured_rows.append(cleaned)
            row_lengths.append(len(cleaned))

# === STEP 3: Preview few rows + log row shape info
print("\n📋 Preview of structured rows:")
for r in structured_rows[:preview_limit]:
    print(r)

print("\n🔍 Column count distribution across rows:")
length_counts = Counter(row_lengths)
for length, count in sorted(length_counts.items()):
    print(f"  {length} columns → {count} rows")

# === STEP 4: Write structured rows to new CSV
with open(output_csv, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    for row in structured_rows:
        writer.writerow(row)

print(f"\n✅ Structured output saved to: {output_csv}")
