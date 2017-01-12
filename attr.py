class Bug(object):
    pass
    


class Attribute(object):

    def __init__(self, name):
        print "__init__"
        self.name = name

    def __set__(self, instance, value):
        print "__set__"
        instance.__dict__[self.name] = value
        
    def __get__(self, instance, owner):
        if instance is None:
            return self
        print "__get__"
        return instance.__dict__[self.name]
        
setattr(Bug, 'wings', Attribute('wings'))

bug=Bug()

bug.wings = [2,3]

print bug.wings

