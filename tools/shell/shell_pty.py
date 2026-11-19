import os
import pty
import re
import select
import subprocess
import termios

PREFIX = "===start==="
SUFFIX_PATTERN = re.compile(r"===end (\d+)===")

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
        send = ("echo "+PREFIX+"\n").encode() + (command + "\n").encode("utf-8") + ("echo ===end $?===\n").encode()
        os.write(self.master, send)
        buffer = b""
        while True:
            r, _, _ = select.select([self.master], [], [], 10)
            if not r:
                break
            chunk = os.read(self.master, 4096)
            if not chunk:
                break
            buffer += chunk
            if SUFFIX_PATTERN.search(buffer.decode("utf-8", errors="ignore")):
                break
        raw_result = buffer.decode("utf-8", errors="ignore")
        idx_start = raw_result.find(PREFIX)
        suffix_match = SUFFIX_PATTERN.search(raw_result, idx_start + len(PREFIX))
        if idx_start != -1 and suffix_match:
            stdout = raw_result[idx_start + len(PREFIX): suffix_match.start()]
            stdout = stdout.removeprefix("\n").removesuffix("\n")
            exit_code = int(suffix_match.group(1))
        else:
            stdout = raw_result
            exit_code = -1
        return {
            "stdout": stdout,
            "exit_code": exit_code
        }
class ShellManager:
    def __init__(self):
        self.session = ShellSession()
    def execute_shell(self, command: str):
        try:
            output = self.session.execute(command)
            return {
                "success": True,
                "stdout": output["stdout"],
                "exit_code": output["exit_code"]
            }
        except Exception as e:
            return {
                "success": False,
                "stderr": str(e)
            }

shell_manager = ShellManager()
def execute_pty(command: str):
    return shell_manager.execute_shell(command)

if __name__ == "__main__":
    # print(execute_pty("""echo OK"""))
    print(execute_pty("tmux ls"))
    # print(shell_manager.execute_shell("ls"))
    # print(shell_manager.execute_shell("cd ~"))
    # print(shell_manager.execute_shell("pwd"))
    # print(shell_manager.execute_shell("ls"))
