import os

def log_historical_extraction(record_count):
    log = open("historical_extraction_log.md", "w", encoding="utf-8")
    log.write("# Historical Extraction Log\n\n")
    log.write("This log file contains the details of the historical extraction process.\n\n")
    log.write(f"total records in df {record_count}\n")
