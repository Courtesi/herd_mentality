from dataclasses import dataclass
from enum import Enum
from typing import Optional, TypedDict

class Action(Enum):
    BUY = "buy"
    SELL = "sell"

class Side(Enum):
    YES = "yes"
    NO = "no"

class TimeInForce(Enum):
    FOK = "fill_or_kill"
    IOC = "immediate_or_cancel"

class CountFilter(Enum):
    position = "position"
    total_traded = "total_traded"
    resting_order_count = "resting_order_count"

@dataclass
class MarketSelection():
    event_ticker: str
    market_ticker: str
    side: Side

    def to_dict(self) -> dict:
        result = {}
        for key, value in self.__dict__.items():
            if value is not None:
                # Convert enums to their string values
                if isinstance(value, Enum):
                    result[key] = value.value
                else:
                    result[key] = value
        return result

@dataclass
class OrderParameters:
    
    # REQUIRED PARAMETERS
    action: Action
    side: Side
    ticker: str
    count: int
    client_order_id: str
    
    # PRICE PARAMETERS (exactly ONE required)
    yes_price: Optional[int] = None
    no_price: Optional[int] = None
    yes_price_dollars: Optional[str] = None
    no_price_dollars: Optional[str] = None
    
    # OPTIONAL PARAMETERS
    buy_max_cost: Optional[int] = None
    cancel_order_on_pause: Optional[bool] = None
    
    expiration_ts: Optional[int] = None
    order_group_id: Optional[str] = None
    post_only: Optional[bool] = None
    self_trade_prevention_type: Optional[str] = None
    sell_position_capped: Optional[bool] = None
    sell_position_floor: Optional[int] = None
    time_in_force: Optional[TimeInForce] = None

    #FOR AMENDING ORDERS
    updated_client_order_id: Optional[str] = None
    
    def __post_init__(self):
        if self.client_order_id == None:
            raise ValueError("client_order_id is required")
        
        """Validate that exactly one price parameter is set."""
        price_params = [
            self.yes_price,
            self.no_price,
            self.yes_price_dollars,
            self.no_price_dollars
        ]
        
        if sum(p is not None for p in price_params) != 1:
            raise ValueError(
                "Exactly one of yes_price, no_price, yes_price_dollars, "
                "or no_price_dollars must be provided"
            )
        
        # Validate client_order_id format if provided
        if self.client_order_id:
            if len(self.client_order_id) > 64:
                raise ValueError("client_order_id must be 64 characters or less")
            if not all(c.isalnum() or c in '_-' for c in self.client_order_id):
                raise ValueError(
                    "client_order_id can only contain alphanumeric characters, '_', and '-'"
                )
    
    def to_dict(self) -> dict:
        """Convert to dictionary, excluding None values."""
        result = {}
        for key, value in self.__dict__.items():
            if value is not None:
                # Convert enums to their string values
                if isinstance(value, Enum):
                    result[key] = value.value
                else:
                    result[key] = value
        return result
    
    def update_count(self, new_count):
        self.count = new_count

    def set_updated_client_order_id(self, updated_client_order_id):
        self.updated_client_order_id = updated_client_order_id

    def amend_order(self, new_count: int, updated_client_order_id: str):
        self.count = new_count
        self.updated_client_order_id = updated_client_order_id

# @dataclass
# class AmendOrderParameters:
    
#     # REQUIRED - identifies the order to amend
#     client_order_id: str
    
#     # REQUIRED FOR VALIDATION - cannot be amended but must match original
#     action: Action
#     side: Side
#     ticker: str
    
#     # AMENDABLE - at least one price parameter required
#     yes_price: Optional[int] = None
#     no_price: Optional[int] = None
#     yes_price_dollars: Optional[str] = None
#     no_price_dollars: Optional[str] = None
    
#     # AMENDABLE - optional
#     count: Optional[int] = None
#     updated_client_order_id: Optional[str] = None
    
#     def __post_init__(self):
#         """Validate amend order parameters."""
        
#         # Validate client_order_id format
#         if self.client_order_id == None:
#             raise ValueError("client_order_id is required")
        
#         if self.client_order_id and len(self.client_order_id) > 64:
#             raise ValueError("client_order_id must be 64 characters or less")
        
#         if self.client_order_id and not all(c.isalnum() or c in '_-' for c in self.client_order_id):
#             raise ValueError(
#                 "client_order_id can only contain alphanumeric characters, '_', and '-'"
#             )
        
#         # Validate updated_client_order_id format if provided
#         if self.updated_client_order_id:
#             if len(self.updated_client_order_id) > 64:
#                 raise ValueError("updated_client_order_id must be 64 characters or less")
            
#             if not all(c.isalnum() or c in '_-' for c in self.updated_client_order_id):
#                 raise ValueError(
#                     "updated_client_order_id can only contain alphanumeric characters, '_', and '-'"
#                 )
        
#         # Validate count if provided
#         if self.count is not None and self.count < 1:
#             raise ValueError("count must be >= 1")
        
#         # Validate exactly one price parameter is provided
#         price_params = [
#             self.yes_price,
#             self.no_price,
#             self.yes_price_dollars,
#             self.no_price_dollars
#         ]
#         price_count = sum(p is not None for p in price_params)
        
#         if price_count != 1:
#             raise ValueError(
#                 "Exactly one of yes_price, no_price, yes_price_dollars, "
#                 "or no_price_dollars must be provided"
#             )
        
#         # Validate price matches side
#         if self.side == Side.YES:
#             if self.no_price is not None or self.no_price_dollars is not None:
#                 raise ValueError(
#                     "For 'yes' side orders, must use yes_price or yes_price_dollars"
#                 )
#         elif self.side == Side.NO:
#             if self.yes_price is not None or self.yes_price_dollars is not None:
#                 raise ValueError(
#                     "For 'no' side orders, must use no_price or no_price_dollars"
#                 )
        
#         # Validate price ranges for cent-based prices
#         if self.yes_price is not None and not (0 <= self.yes_price <= 100):
#             raise ValueError("yes_price must be between 0 and 100 cents")
        
#         if self.no_price is not None and not (0 <= self.no_price <= 100):
#             raise ValueError("no_price must be between 0 and 100 cents")
        
#         # Validate at least one amendable field is being changed
#         amendable_fields = [
#             self.count,
#             self.yes_price,
#             self.no_price,
#             self.yes_price_dollars,
#             self.no_price_dollars,
#             self.updated_client_order_id,
#         ]
        
#         if all(field is None for field in amendable_fields):
#             raise ValueError(
#                 "At least one amendable field must be provided "
#                 "(count, price, or updated_client_order_id)"
#             )
    
#     def to_dict(self) -> dict:
#         """Convert to dictionary, excluding None values."""
#         result = {}
#         for key, value in self.__dict__.items():
#             if value is not None:
#                 # Convert enums to their string values
#                 if isinstance(value, Enum):
#                     result[key] = value.value
#                 else:
#                     result[key] = value
#         return result