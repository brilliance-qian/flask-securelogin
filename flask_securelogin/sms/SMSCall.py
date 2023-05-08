from abc import ABCMeta, abstractmethod


class SMSCall:
    __metaclass__ = ABCMeta

    @abstractmethod
    def send_sms(self, phone) -> bool:
        pass

    @abstractmethod
    def verify_sms(self, phone) -> bool:
        pass

    @abstractmethod
    def get_errors(self) -> Exception:
        pass
