import os
import re
import json

# -------------------------------------------------------------------
# JSONSharder
# -------------------------------------------------------------------
class JSONSharder:
    """
    Writes each aggregated customer record to its own JSON file.

    It sanitizes the customer name for a safe filename and writes the record
    to the designated output directory.
    """

    def __init__(self, output_dir):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def sanitize_filename(self, name):
        sanitized = re.sub(r'[^\w\-. ]', '_', name)
        return sanitized.strip().replace(" ", "_") + ".json"

    def write_customer_record(self, customer_record):
        filename = self.sanitize_filename(customer_record.get("customer", "unknown"))
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(customer_record, f, indent=4)
        print(f"Saved record for customer '{customer_record.get('customer')}' to {filepath}")

    def shard_all(self, aggregated_records):
        for record in aggregated_records:
            self.write_customer_record(record)

