from tools.shell.shell_session import ShellSession

class ShellManager:

    def __init__(self):
        self.session = ShellSession()

    def execute(self, command):

        self.session.execute(command)

        import time
        time.sleep(0.2)

        return self.session.read()


manager = ShellManager()