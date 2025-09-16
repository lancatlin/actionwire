#!/usr/bin/env python3
"""
CSV Comparison Tool for detections.csv and script.csv

This program compares two CSV files:
- detections.csv: Contains timecode and keyword pairs (voice detection results)
- script.csv: Contains timecode, keyword, event, action, and other columns (script with actions)

The comparison provides various analyses including:
- Timecode matching
- Keyword frequency analysis
- Missing entries
- Timing differences
- Statistical summaries
"""

import csv
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import argparse
import sys
from pathlib import Path


def parse_timecode(timecode_str):
    """Convert timecode string (MM:SS) to seconds for easier comparison."""
    try:
        parts = timecode_str.split(':')
        if len(parts) == 2:
            minutes, seconds = map(int, parts)
            return minutes * 60 + seconds
        return 0
    except (ValueError, AttributeError):
        return 0


def format_timecode(seconds):
    """Convert seconds back to MM:SS format."""
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes:02d}:{seconds:02d}"


def load_detections(file_path):
    """Load detections.csv file."""
    detections = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['timecode'] and row['keyword']:  # Skip empty rows
                    detections.append({
                        'timecode': row['timecode'],
                        'keyword': row['keyword'],
                        'seconds': parse_timecode(row['timecode'])
                    })
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        sys.exit(1)

    return detections


def load_script(file_path):
    """Load script.csv file."""
    script = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['timecode'] and row['keyword']:  # Skip empty rows
                    script.append({
                        'timecode': row['timecode'],
                        'keyword': row['keyword'],
                        'event': row.get('event', ''),
                        'action': row.get('action', ''),
                        'p_area': row.get('P area (1)', ''),
                        'w_area': row.get('W area (3)', ''),
                        'seconds': parse_timecode(row['timecode'])
                    })
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        sys.exit(1)

    return script


def find_closest_match(target_seconds, source_list, tolerance=5):
    """Find the closest match within tolerance seconds."""
    closest = None
    min_diff = float('inf')

    for item in source_list:
        diff = abs(item['seconds'] - target_seconds)
        if diff <= tolerance and diff < min_diff:
            min_diff = diff
            closest = item

    return closest, min_diff


def compare_files(detections, script):
    """Compare the two CSV files and generate analysis."""

    print("=" * 80)
    print("CSV FILES COMPARISON ANALYSIS")
    print("=" * 80)

    # Basic statistics
    print(f"\n📊 BASIC STATISTICS")
    print(f"Detections file: {len(detections)} entries")
    print(f"Script file: {len(script)} entries")

    # Time range analysis
    det_times = [d['seconds'] for d in detections]
    script_times = [s['seconds'] for s in script]

    if det_times and script_times:
        print(f"\n⏰ TIME RANGE")
        print(f"Detections: {format_timecode(min(det_times))} - {format_timecode(max(det_times))}")
        print(f"Script: {format_timecode(min(script_times))} - {format_timecode(max(script_times))}")

    # Keyword frequency analysis
    print(f"\n🔤 KEYWORD FREQUENCY ANALYSIS")

    det_keywords = Counter([d['keyword'] for d in detections])
    script_keywords = Counter([s['keyword'] for s in script])

    print(f"\nTop keywords in detections:")
    for keyword, count in det_keywords.most_common(10):
        print(f"  {keyword}: {count}")

    print(f"\nTop keywords in script:")
    for keyword, count in script_keywords.most_common(10):
        print(f"  {keyword}: {count}")

    # Common keywords
    common_keywords = set(det_keywords.keys()) & set(script_keywords.keys())
    print(f"\nCommon keywords ({len(common_keywords)}): {', '.join(sorted(common_keywords))}")

    # Keywords only in detections
    det_only = set(det_keywords.keys()) - set(script_keywords.keys())
    print(f"\nKeywords only in detections ({len(det_only)}): {', '.join(sorted(det_only))}")

    # Keywords only in script
    script_only = set(script_keywords.keys()) - set(det_keywords.keys())
    print(f"\nKeywords only in script ({len(script_only)}): {', '.join(sorted(script_only))}")

    # Timecode matching analysis
    print(f"\n🎯 TIMECODE MATCHING ANALYSIS")

    matches = []
    detections_without_match = []
    script_without_match = []

    # Find matches for detections
    for det in detections:
        closest, diff = find_closest_match(det['seconds'], script, tolerance=10)
        if closest:
            matches.append({
                'detection': det,
                'script': closest,
                'time_diff': diff
            })
        else:
            detections_without_match.append(det)

    # Find script entries without matches
    matched_script_seconds = {m['script']['seconds'] for m in matches}
    for script_item in script:
        if script_item['seconds'] not in matched_script_seconds:
            script_without_match.append(script_item)

    print(f"Matched entries: {len(matches)}")
    print(f"Detections without match: {len(detections_without_match)}")
    print(f"Script entries without match: {len(script_without_match)}")

    # Show some example matches
    if matches:
        print(f"\n📋 SAMPLE MATCHES:")
        for i, match in enumerate(matches):
            det = match['detection']
            script_item = match['script']
            print(f"  {i+1}. {det['timecode']} '{det['keyword']}' ↔ {script_item['timecode']} '{script_item['keyword']}' (diff: {match['time_diff']}s)")

    # Show unmatched detections
    if detections_without_match:
        print(f"\n❌ DETECTIONS WITHOUT MATCH:")
        for i, det in enumerate(detections_without_match):
            print(f"  {i+1}. {det['timecode']} '{det['keyword']}'")

    # Show unmatched script entries
    if script_without_match:
        print(f"\n❌ SCRIPT ENTRIES WITHOUT MATCH:")
        for i, script_item in enumerate(script_without_match):
            print(f"  {i+1}. {script_item['timecode']} '{script_item['keyword']}' ({script_item['event']})")

    # Event type analysis for script
    if script:
        print(f"\n🎭 SCRIPT EVENT ANALYSIS")
        events = Counter([s['event'] for s in script if s['event']])
        print(f"Event types:")
        for event, count in events.most_common():
            print(f"  {event}: {count}")

    # Action analysis for script
    # if script:
    #     print(f"\n⚡ SCRIPT ACTION ANALYSIS")
    #     actions = Counter([s['action'] for s in script if s['action']])
    #     print(f"Action types:")
    #     for action, count in actions.most_common():
    #         print(f"  {action}: {count}")

    # Timing analysis
    if matches:
        print(f"\n⏱️ TIMING ANALYSIS")
        time_diffs = [m['time_diff'] for m in matches]
        avg_diff = sum(time_diffs) / len(time_diffs)
        max_diff = max(time_diffs)
        min_diff = min(time_diffs)

        print(f"Average time difference: {avg_diff:.2f} seconds")
        print(f"Maximum time difference: {max_diff} seconds")
        print(f"Minimum time difference: {min_diff} seconds")

        # Distribution of time differences
        diff_ranges = {
            "0-1s": len([d for d in time_diffs if d <= 1]),
            "1-3s": len([d for d in time_diffs if 1 < d <= 3]),
            "3-5s": len([d for d in time_diffs if 3 < d <= 5]),
            "5-10s": len([d for d in time_diffs if 5 < d <= 10]),
            ">10s": len([d for d in time_diffs if d > 10])
        }

        print(f"\nTime difference distribution:")
        for range_name, count in diff_ranges.items():
            percentage = (count / len(time_diffs)) * 100
            print(f"  {range_name}: {count} ({percentage:.1f}%)")

    return {
        'matches': matches,
        'detections_without_match': detections_without_match,
        'script_without_match': script_without_match,
        'det_keywords': det_keywords,
        'script_keywords': script_keywords
    }


def export_detailed_report(comparison_data, output_file):
    """Export detailed comparison report to CSV."""
    matches = comparison_data['matches']

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Detection Timecode', 'Detection Keyword', 'Script Timecode', 'Script Keyword',
            'Time Difference (s)', 'Script Event', 'Script Action'
        ])

        for match in matches:
            det = match['detection']
            script_item = match['script']
            writer.writerow([
                det['timecode'],
                det['keyword'],
                script_item['timecode'],
                script_item['keyword'],
                match['time_diff'],
                script_item['event'],
                script_item['action']
            ])

    print(f"\n💾 Detailed report exported to: {output_file}")


def main():
    parser = argparse.ArgumentParser(description='Compare detections.csv and script.csv files')
    parser.add_argument('--detections', default='data/detections.csv',
                       help='Path to detections.csv file')
    parser.add_argument('--script', default='data/script.csv',
                       help='Path to script.csv file')
    parser.add_argument('--output', default='comparison_report.csv',
                       help='Output file for detailed report')
    parser.add_argument('--tolerance', type=int, default=10,
                       help='Time tolerance in seconds for matching (default: 10)')

    args = parser.parse_args()

    print("Loading files...")
    detections = load_detections(args.detections)
    script = load_script(args.script)

    print("Performing comparison analysis...")
    comparison_data = compare_files(detections, script)

    print("\nExporting detailed report...")
    export_detailed_report(comparison_data, args.output)

    print(f"\n✅ Comparison complete! Check {args.output} for detailed results.")


if __name__ == "__main__":
    main()
