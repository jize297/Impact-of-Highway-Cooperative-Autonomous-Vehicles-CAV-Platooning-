#!/usr/bin/env python3
"""
tripinfo_analysis_fixed.py

Parse a fixed SUMO tripinfo.xml, extract key vehicle trip metrics,
aggregate by vehicle type (vType), and output summary statistics including
overall averages of means.
"""

import os
import xml.etree.ElementTree as ET
import pandas as pd

# Fixed parameters
INPUT_TRIPINFO = 'tripinfo.xml'
OUTPUT_DIR = 'analysis_output'
OUTPUT_CSV = os.path.join(OUTPUT_DIR, 'tripinfo_summary_by_vtype.csv')

# Fields to extract from each <tripinfo>
NUMERIC_FIELDS = [
     'waitingTime',  'timeLoss'
]
STRING_FIELDS = ['id', 'vType']


def parse_tripinfo(xml_path):
    """
    Parse tripinfo.xml and return a DataFrame.
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()
    records = []
    for trip in root.findall('tripinfo'):
        rec = {}
        for field in STRING_FIELDS:
            rec[field] = trip.get(field)
        for field in NUMERIC_FIELDS:
            val = trip.get(field)
            rec[field] = float(val) if val is not None else None
        records.append(rec)
    df = pd.DataFrame(records)
    return df


def summarize_by_vtype(df):
    """
    Group DataFrame by vType and compute mean and std for numeric metrics.
    """
    summary = df.groupby('vType')[NUMERIC_FIELDS].agg(['mean', 'std'])
    summary.columns = ['_'.join(col).strip() for col in summary.columns.values]
    return summary


def append_overall_averages(summary_df):
    """
    Compute the mean of each column in the summary (i.e., average of means/stds across vTypes)
    and append as a final row labeled 'overall_average'.
    """
    overall_avg = summary_df.mean(axis=0, numeric_only=True)
    overall_avg.name = 'overall_average'
    summary_with_avg = pd.concat([summary_df, pd.DataFrame([overall_avg])])
    return summary_with_avg


def main():
    # Ensure output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Parse tripinfo
    df = parse_tripinfo(INPUT_TRIPINFO)
    print(f"Parsed {len(df)} trips from {INPUT_TRIPINFO}")

    # Summarize by vehicle type
    summary = summarize_by_vtype(df)

    # Append overall average row
    summary_with_avg = append_overall_averages(summary)

    # Save to CSV
    summary_with_avg.to_csv(OUTPUT_CSV)
    print(f"Summary statistics (with overall averages) saved to {OUTPUT_CSV}")
    print(summary_with_avg)


if __name__ == '__main__':
    main()
