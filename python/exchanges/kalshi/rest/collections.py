from .basic_rest import BasicRest
from .models.models import MarketSelection

class Collection(BasicRest):

    def __init__(self):
        super().__init__()

    def get_multivariate_event_collections(self, cursor: str = None):
        url = f"{self.base_url}/multivariate_event_collections"
        kwargs = self.drop_none(self.get_kwargs())
        return self.get(url, **kwargs)
    
    def get_multivariate_event_collection(self, collection_ticker: str):
        url = f"{self.base_url}/multivariate_event_collections/{collection_ticker}"
        return self.get(url)
    
    def create_market_in_mec(self,
                            collection_ticker: str,
                            selected_markets: list[MarketSelection]):
        url = f"{self.base_url}/multivariate_event_collections/{collection_ticker}"

        body = {"selected_markets": selected_markets}

        return self._authenticated_post_request(url, data=body)

    def get_mec_lookup_history(self, collection_ticker: str, lookback_seconds: int = None):
        url = f"{self.base_url}/multivariate_event_collections/{collection_ticker}/lookup"
        
        return self.get(url, lookback_seconds=lookback_seconds)
    
    def lookup_market_in_mec(self, collection_ticker: str, selected_markets):
        url = f"{self.base_url}/multivariate_event_collections/{collection_ticker}/lookup"

        body = {"selected_markets": selected_markets}

        return self._authenticated_put_request(url, data=body)