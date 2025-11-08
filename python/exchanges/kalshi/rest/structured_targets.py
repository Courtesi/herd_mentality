from .basic_rest import BasicRest

class StructuredTarget(BasicRest):
    def __init__(self):
        super().__init__()

    def get_structured_targets(self,
                               type: str = None,
                               competition: str = None,
                               page_size: int = None,
                               cursor: str = None):
        
        url = f"{self.base_url}/structured_targets"
        return self.get(url)
    
    def get_structured_target(self, structured_target_id: str = None):
        url = f"{self.base_url}/structured_targets/{structured_target_id}"
        return self.get(url)