import os
import pty
import select
import subprocess
import time


class ShellSession:
    def __init__(self):
        self.master, slave = pty.openpty()

        self.proc = subprocess.Popen(
            ["/bin/bash", "-i"],
            stdin=slave,
            stdout=slave,
            stderr=slave,
            close_fds=True,
        )

        time.sleep(0.2)
        self.read()  # 清掉启动时的 Prompt

    def execute(self, command: str):
        os.write(self.master, (command + "\n").encode())

    def read(self):
        output = ""

        while True:
            ready, _, _ = select.select([self.master], [], [], 0.1)

            if not ready:
                break

            output += os.read(self.master, 4096).decode(errors="ignore")

        return output

    def close(self):
        self.proc.kill()

if __name__ == "__main__":
    shell = ShellSession()
    shell.execute("echo hello")
    shell.execute("echo world")
    shell.execute("pwd")
    time.sleep(0.2)
    print(shell.read())