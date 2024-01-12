
class SessionRetainInterface:
    def __init__(self, session):
        self.session = session
        
    def __call__(self):
        return self.session

class InMemorySR(SessionRetainInterface):
    pass
