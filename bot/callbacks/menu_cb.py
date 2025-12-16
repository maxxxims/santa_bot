from aiogram.filters.callback_data import CallbackData


class InviteCallback(CallbackData, prefix="invite"):
    ...

class GetPairCallback(CallbackData, prefix="get_pair"):
    ...

class ShuffleCallback_1(CallbackData, prefix="shuffle_1"):
    ...

class ShuffleCallbackAccept(CallbackData, prefix="shuffle_accept"):
    ...

class ShuffleCallbackDecline(CallbackData, prefix="shuffle_decline"):
    ...
    
class ExitGroupCallback_1(CallbackData, prefix="exit_group"):
    ...
    
class ExitGroupCallbackAccept(CallbackData, prefix="exit_g_a"):
    ...
    
class ExitGroupCallbackDecline(CallbackData, prefix="exit_g_d"):
    ...
    
class CloseGroupCallback(CallbackData, prefix="close_group"):
    ...
    
class CloseEventCallback_1(CallbackData, prefix="close_event"):
    ...
        
class CloseEventCallbackAccept(CallbackData, prefix="close_ea"):
    ...
        
class CloseEventCallbackDecline(CallbackData, prefix="close_ed"):
    ...
    
class SetWishlistCallback(CallbackData, prefix="wishlist"):
    ...
    
class BackButtonCallback(CallbackData, prefix="back_menu"):
    ...
    
class MsgCallback(CallbackData, prefix="chatting"):
    send_to_santa: bool
    
class ExtendGroupCallback(CallbackData, prefix="extend_group"):
    ...
    
class RefreshPaymentCallback(CallbackData, prefix="refresh_pay"):
    payment_id: str
    
class NavigationGroupCallback(CallbackData, prefix="nav_group"):
    next_page: int