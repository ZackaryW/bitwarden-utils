import argparse
import json
import os
from pprint import pprint
import sys
import parse

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from bitwarden_utils.core.proc import BwProc # noqa

"""
ignore all args first
"""
arg_parse = argparse.ArgumentParser()
# path
arg_parse.add_argument("--path", type=str, default="bw")

def env_key_replace(raw : str, envs):
    if "%" not in raw:
        return raw
    for key in envs:
        if f"%{key}%" not in raw:
            continue

        raw = raw.replace(f"%{key}%", envs[key])
    return raw

def handle_com(cmd : list):
    pass

def shell_entry():
    print(
        "welcome to bitwarden quicker shell, same use case as bw-cli with session key stored for the instance"
    )

    arg_dict = vars(arg_parse.parse_args())

    proc = BwProc(path=arg_dict["path"])
    
    envs = os.environ.copy()

    while True:
        cmd = input("> ")

        if cmd.startswith("set ") and "=" in cmd:
            match = parse.parse("set {key}={value}", cmd)
            envs[match["key"]] = match["value"]
            print(f"set {match['key']} to {match['value']}")
            continue

        # find all envs, then replace them
        # env keys are represented via %{key}%
        cmd = env_key_replace(cmd, envs)

        if cmd == "exit":
            break
        
        cmd = cmd.split()

        if cmd[0] == "com":
            handle_com(cmd)
            continue

        if cmd[0] == "login":
            u, p, *args = cmd[1:]
            proc = proc.login(proc.path, u, p, *args)
            continue

        if cmd[0] == "unlock":
            proc = proc.unlock(cmd[1])
            continue

        res = proc.exec(*cmd)
        try:
            raw = json.loads(res)
            pprint(raw, indent=4)
        except: # noqa
            print(res)

def main_loop():
    try:
        shell_entry()
    except* (KeyboardInterrupt, EOFError):
        print("\nbye")

if __name__ == "__main__":
    main_loop()