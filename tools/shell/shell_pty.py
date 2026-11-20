import os
import pty
import select
import subprocess
import termios
import time


class ShellSession:
    def __init__(self):
        self.master, slave = pty.openpty()
        env = os.environ.copy()
        env["TERM"] = "dumb"
        env["PS1"] = ""
        env["PROMPT_COMMAND"] = ""
        attr = termios.tcgetattr(slave)
        attr[1] &= ~termios.ONLCR
        attr[3] &= ~termios.ECHO
        termios.tcsetattr(slave, termios.TCSANOW, attr)
        self.proc = subprocess.Popen(
            ["/bin/bash", "--norc", "+m"],
            stdin=slave,
            stdout=slave,
            stderr=slave,
            close_fds=True,
            preexec_fn=os.setsid,
            env=env,
        )
        os.close(slave)
    def execute(self, command: str):
        send = (command + "\n").encode("utf-8")
        os.write(self.master, send)
        while True:
            r, _, _ = select.select([self.master], [], [], 10)
            if not r:
                break
            chunk = os.read(self.master, 4096)
            if not chunk:
                break
            yield chunk.decode("utf-8")
class ShellManager:
    def __init__(self):
        self.session = ShellSession()
    def execute_shell(self, command: str):
        return self.session.execute(command)

shell_manager = ShellManager()
def execute_pty(command: str):
    return shell_manager.execute_shell(command)

if __name__ == "__main__":
    for output in execute_pty("""{"command": "fastfetch"}"""):
        print(output)
    print(str(time.time()))
