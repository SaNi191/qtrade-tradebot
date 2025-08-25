from abc import ABC, abstractmethod

class BaseAlert(ABC):

    @abstractmethod
    def send_msg(self, msg: str, recipient: str, subject: str) -> bool:
        # handles the logic to connect to required resources then 
        # sends msg to recipient with subject
        # returns whether message being sent was successful
        pass

    

