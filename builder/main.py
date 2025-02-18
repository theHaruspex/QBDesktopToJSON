from _archive.builder.json_sharder import JSONSharder
from _archive.builder.database_builder import DatabaseBuilder






# -------------------------------------------------------------------
# Main Workflow Function
# -------------------------------------------------------------------
def main_workflow(input_dir, output_dir):
    """
    High-level workflow function.

    Steps:
      1. Build aggregated customer data from all CSV files in input_dir.
      2. Finalize the aggregated records.
      3. Write each customer record to its own JSON file in output_dir.
    """
    db_builder = DatabaseBuilder(input_dir)
    aggregated = db_builder.build_from_directory()
    final_records = db_builder.finalize_records(aggregated)
    sharder = JSONSharder(output_dir)
    sharder.shard_all(final_records)


# -------------------------------------------------------------------
# Example Usage
# -------------------------------------------------------------------
if __name__ == '__main__':
    # Replace these with your actual paths.
    input_directory = "raw_sales_data"  # Directory containing CSV files.
    output_directory = "output"  # Directory for sharded JSON files.

    main_workflow(input_directory, output_directory)