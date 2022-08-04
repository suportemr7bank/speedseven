from enum import Enum

class ApplicationFormType(Enum):
    """
    Application forms
    """
    APPLICATION_SETTINGS = 1
    ACCOUNT_SETTINGS = 2
    APPLICATION_OPERATION = 3
    APPLICATION_PURCHASE = 4
    DEPOSIT = 5
    WITHDRAW = 6
    OPERATION_APPROVAL = 7
    OPERATION_COMPLETION = 8


class PostCreateState(Enum):
    """
    State after creaation
    Created means the application was created
    Scheduled means the creation process depends on externa factor and
    may be executed in a backgroud task. (Ex: creating an account in a broker)
    In the scheduled case, the implementation should finalize application creation
    settint its date_activated
    """
    CREATED = 1
    SCHEDULED = 2
    RUNNING = 3
