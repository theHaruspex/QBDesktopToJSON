# -------------------------------------------------------------------
# CustomerGroup
# -------------------------------------------------------------------
class CustomerGroup:
    """
    Holds data for a single customer group extracted from one CSV file.

    Attributes:
      - customer_name: The customer's name.
      - contact_info: Dictionary of common contact and address fields.
      - invoices: Dictionary (keyed by invoice number) of lists of purchase line items.
      - total_sales: Total sales amount (float) for this group.
      - classes: List of all "Class" field values from invoice rows.
    """

    def __init__(self, customer_name, contact_info):
        self.customer_name = customer_name
        self.contact_info = contact_info  # Dict of contact fields.
        self.invoices = {}  # { invoice_number: [purchase_invoice, ...] }
        self.total_sales = 0.0
        self.classes = []  # List of class values.

    def add_invoice(self, invoice):
        inv_num = invoice.get("Num", "UNKNOWN")
        if inv_num not in self.invoices:
            self.invoices[inv_num] = []
        self.invoices[inv_num].append(invoice)

    def merge(self, other):
        """
        Merge another CustomerGroup (from another CSV file) into this one.
        This merges invoices (by appending line items for matching invoice numbers),
        sums total_sales, and extends the classes list.
        """
        for inv_num, items in other.invoices.items():
            if inv_num in self.invoices:
                self.invoices[inv_num].extend(items)
            else:
                self.invoices[inv_num] = items
        self.total_sales += other.total_sales
        self.classes.extend(other.classes)
