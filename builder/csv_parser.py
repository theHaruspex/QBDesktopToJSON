import csv
from collections import defaultdict
from _archive.builder.customer_group import CustomerGroup

class CSVParser:
    """
    Reads a single CSV file and returns a list of CustomerGroup objects.

    It processes the CSV row-by-row:
      - A non-empty first cell (that does not start with "Invoice" or "Total")
        indicates a new customer group header.
      - Rows starting with "Invoice" represent individual purchase items.
        The "Num" field (invoice number) is used to group these items.
      - A row starting with "Total" provides the total sales for the group.
    """

    def __init__(self):
        pass

    def parse_file(self, filepath):
        customer_groups = []
        current_customer = None
        current_invoices = None
        current_total = 0.0
        current_classes = []
        contact_info = None

        with open(filepath, 'r', newline='', encoding='latin-1') as csvfile:
            reader = csv.reader(csvfile)
            try:
                header = next(reader)
            except StopIteration:
                return customer_groups  # Empty file

            # Remove a leading empty cell from the header, if it exists.
            if header and header[0].strip() == "":
                header = header[1:]

            # Process each row in the CSV.
            for row in reader:
                # If the row starts with an empty cell due to a leading comma, shift the row.
                if row and row[0].strip() == "" and len(row) > 1:
                    row = row[1:]
                if not any(cell.strip() for cell in row):
                    continue  # Skip completely empty rows

                first_cell = row[0].strip()
                # -- Customer Group Header Row --
                if first_cell and not first_cell.startswith("Invoice") and not first_cell.startswith("Total"):
                    # If we were processing a customer group, finalize it.
                    if current_customer is not None:
                        group = CustomerGroup(current_customer, contact_info)
                        group.invoices = current_invoices if current_invoices is not None else {}
                        group.total_sales = current_total
                        group.classes = current_classes
                        customer_groups.append(group)
                    # Start a new customer group.
                    current_customer = first_cell.strip('"')
                    current_invoices = defaultdict(list)
                    current_total = 0.0
                    current_classes = []
                    contact_info = {}
                # -- Invoice Row --
                elif first_cell.startswith("Invoice"):
                    # If no customer group is active, skip the invoice row.
                    if current_customer is None or current_invoices is None:
                        # Optionally, log a warning here.
                        # print("Warning: Invoice row encountered before any customer header. Skipping row.")
                        continue

                    # Build a dictionary for this invoice row.
                    invoice = {}
                    for i, col in enumerate(header):
                        invoice[col] = row[i].strip() if i < len(row) else ""
                    # Ensure contact_info is initialized.
                    if contact_info is None:
                        contact_info = {}
                    # Capture contact info from the first invoice row.
                    if not contact_info:
                        keys = [
                            "Source Name", "Name Address", "Name Street1", "Name Street2",
                            "Name City", "Name State", "Name Zip", "Name Contact", "Name Phone #",
                            "Name Fax #", "Name E-Mail", "Name", "Ship To Address 1",
                            "Ship To Address 2", "Ship To State", "Ship Zip", "Notes",
                            "Last Name", "First Name"
                        ]
                        for key in keys:
                            contact_info[key] = invoice.get(key, "")
                    # Create a copy for the purchase details and remove the contact-related fields.
                    purchase_invoice = invoice.copy()
                    for key in [
                        "Source Name", "Name Address", "Name Street1", "Name Street2",
                        "Name City", "Name State", "Name Zip", "Name Contact", "Name Phone #",
                        "Name Fax #", "Name E-Mail", "Name", "Ship To Address 1",
                        "Ship To Address 2", "Ship To State", "Ship Zip", "Notes",
                        "Last Name", "First Name", "Terms"
                    ]:
                        purchase_invoice.pop(key, None)
                    # Group this purchase by invoice number.
                    inv_num = invoice.get("Num", "UNKNOWN")
                    current_invoices[inv_num].append(purchase_invoice)
                    # Accumulate the "Class" value.
                    cls_val = invoice.get("Class", "").strip()
                    if cls_val:
                        current_classes.append(cls_val)
                # -- Total Row --
                elif first_cell.startswith("Total"):
                    # Extract the total sales value (assumed to be in the "Balance" column).
                    try:
                        balance_idx = header.index("Balance")
                        total_str = row[balance_idx].strip() if balance_idx < len(row) else "0"
                        total_value = float(total_str.replace(',', ''))
                    except (ValueError, IndexError):
                        total_value = 0.0
                    current_total = total_value
                    # Finalize the current customer group.
                    if current_customer is not None:
                        group = CustomerGroup(current_customer, contact_info)
                        group.invoices = current_invoices if current_invoices is not None else {}
                        group.total_sales = current_total
                        group.classes = current_classes
                        customer_groups.append(group)
                        current_customer = None
                        current_invoices = None
                        current_total = 0.0
                        current_classes = []
                        contact_info = None

            # End-of-file: if a group is still active, finalize it.
            if current_customer is not None:
                group = CustomerGroup(current_customer, contact_info)
                group.invoices = current_invoices if current_invoices is not None else {}
                group.total_sales = current_total
                group.classes = current_classes
                customer_groups.append(group)

        return customer_groups