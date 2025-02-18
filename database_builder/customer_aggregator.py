# -------------------------------------------------------------------
# CustomerAggregator
# -------------------------------------------------------------------
class CustomerAggregator:
    """
    Aggregates multiple CustomerGroup objects for the same customer.

    The aggregated data is stored in a dictionary keyed by customer name.
    """

    def __init__(self):
        self.aggregated = {}

    def aggregate(self, groups):
        for group in groups:
            name = group.customer_name
            if name in self.aggregated:
                self.aggregated[name].merge(group)
            else:
                self.aggregated[name] = group

    def get_aggregated(self):
        return self.aggregated


