class AppException(Exception):
    def __init__(self, category, error, message):
        super().__init__(message)
        self.category = category
        self.error = error
