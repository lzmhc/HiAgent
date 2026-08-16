from tools.execute_shell.shell_manager import manager


def execute_shell(command: str):

    try:

        output = manager.execute(command)

        return {
            "success": True,
            "stdout": output,
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    print(execute_shell("pwd"))
    print(execute_shell("cd ~"))
    print(execute_shell("pwd"))
    print(execute_shell("ls"))
