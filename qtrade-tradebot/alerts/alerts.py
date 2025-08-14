from abc import ABC, abstractmethod

class BaseAlert(ABC):

    @abstractmethod
    def send_msg(self, msg:str,  recipient:str, subject:str):
        # handles the logic to connect to required resources then sends msg to recipient with subject
        pass

    

