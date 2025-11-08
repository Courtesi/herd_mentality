from .basic_rest import BasicRest

class Milestone(BasicRest):
    def __init__(self):
        super().__init__()

    def get_milestones(self,
                       limit: int,
                       minimum_start_date: str = None,
                       category: str = None,
                       competition: str = None,
                       type: str = None,
                       related_event_ticker: str = None,
                       cursor: str = None) -> dict:
        url = f"{self.base_url}/milestones"
        kwargs = self.drop_none(self.get_kwargs())
        print(kwargs)
        return self.get(url, **kwargs)
        
    def get_milestone(self, milestone_id: str) -> dict:
        url = f"{self.base_url}/milestones/{milestone_id}"
        return self.get(url)