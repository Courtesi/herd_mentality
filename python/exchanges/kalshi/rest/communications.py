from .basic_rest import BasicRest

#Most likely for market makers (advanced topic that we don't need for now)
class Communication(BasicRest):
    def __init__(self):
        super().__init__()

    def get_communications_id(self):
        url = f"{self.base_url}/communications/id"
        return self._authenticated_get_request(url)

    # Getting error:
    # {"error":{"code":"Either_creator_user_id_or_rfq_creator_user_id_must_be_filled.",
    # "message":"Either creator_user_id or rfq_creator_user_id must be filled."}}
    def get_quotes(self, cursor: str = None):
        url = f"{self.base_url}/communications/quotes"
        kwargs = self.get_kwargs()
        kwargs = self.drop_none(kwargs)
        return self._authenticated_get_request(url, **kwargs)