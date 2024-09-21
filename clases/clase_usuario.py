class Usuario(object):
    def __init__(self, id, dni, password):
        self.id = id
        self.dni = dni
        self.password = password

    def __str__(self):
        return "User(id='%s')" % self.id
