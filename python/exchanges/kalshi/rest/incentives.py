from .basic_rest import BasicRest

class Incentive(BasicRest):
    def __init__(self):
        super().__init__()

    def get_incentives(self, limit: int = None) -> dict:
        url = f"{self.base_url}/incentive_programs"
        kwargs = self.drop_none(self.get_kwargs())
        return self.get(url, **kwargs)