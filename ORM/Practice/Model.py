class Model:
    def __init__(self):
        for key, value in self.__dict__.items():
            setattr(self, key, value)
