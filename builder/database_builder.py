from _archive.builder.csv_parser import CSVParser
from _archive.builder.customer_aggregator import CustomerAggregator
from collections import Counter


import os


# -------------------------------------------------------------------
# DatabaseBuilder
# -------------------------------------------------------------------
class DatabaseBuilder:
    """
    Orchestrates the workflow to build the customer database.

    It reads CSV files from an input directory, uses CSVParser to extract CustomerGroup
    objects, aggregates them using CustomerAggregator, and then finalizes the records.
    """

    def __init__(self, input_dir):
        self.input_dir = input_dir
        self.parser = CSVParser()
        self.aggregator = CustomerAggregator()

    def build_from_directory(self):
        all_groups = []
        for filename in os.listdir(self.input_dir):
            if filename.lower().endswith('.csv'):
                filepath = os.path.join(self.input_dir, filename)
                groups = self.parser.parse_file(filepath)
                all_groups.extend(groups)
        self.aggregator.aggregate(all_groups)
        return self.aggregator.get_aggregated()

    def finalize_records(self, aggregated):
        """
        Finalize each customer record:
          - Compute "Customer Class" as the most common class value.
          - Convert the invoices dictionary into a list of grouped purchases.
          - Merge the contact_info to the top level.
          - Format total_sales as a string with two decimals.
        """
        final_records = []
        for customer, group in aggregated.items():
            counter = Counter(group.classes)
            customer_class = counter.most_common(1)[0][0] if counter else ""
            purchases = []
            for inv_num, items in group.invoices.items():
                purchases.append({
                    "Num": inv_num,
                    "invoices": items
                })
            record = {
                "customer": customer,
                **group.contact_info,  # Unpack contact info into the top level.
                "Customer Class": customer_class,
                "total_sales": f"{group.total_sales:.2f}",
                "purchases": purchases
            }
            final_records.append(record)
        return final_records
