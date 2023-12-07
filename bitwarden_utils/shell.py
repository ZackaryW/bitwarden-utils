import argparse
import json
import os
from pprint import pprint
import sys
import click
import parse

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from bitwarden_utils.core.proc import BwProc # noqa
from bitwarden_utils.com.attachment import AttachmentManager # noqa

"""
ignore all args first
"""
arg_parse = argparse.ArgumentParser()
# path
arg_parse.add_argument("--path", type=str, default="bw")
arg_parse.add_argument("--stateful-session", "-ss", action='store_true')

def env_key_replace(raw : str, envs):
    if "%" not in raw:
        return raw
    for key in envs:
        if f"%{key}%" not in raw:
            continue

        raw = raw.replace(f"%{key}%", envs[key])
    return raw

# allow extra
com_arg = argparse.ArgumentParser()
com_arg.add_argument("--limit", type=int, default=-1)

def handle_keyring(proc : BwProc):
    import keyring
    if proc.isLocked:
        session = keyring.get_password("BW_UTILS","BW_SESSION")
        if session is None or len(session) == 0:
            print("no session")
        else:
            proc.session = session

    elif proc.session is not None:
        keyring.set_password("BW_UTILS",username="BW_SESSION", password=proc.session)
    else:
        print("no session")

def handle_com(cmd : list, proc : BwProc):
    # determines where options starts
    args = cmd[1:]
    cmd = cmd[0]
    index = -1
    for i in range(len(args)):
        index = i

        if args[i].startswith("-") and not args[i].endswith("-"):
            break

    index = index + 1

    if len(args) > index:
        cargs = vars(com_arg.parse_args(args[index:]))
    else:
        cargs = {}

    if cmd == "attexport":
        com = AttachmentManager(proc)
        com.export(*args[:index], **cargs)
    elif cmd == "attsync":
        com = AttachmentManager(proc)
        com.sync(*args[:index],  **cargs)
    elif cmd == "keyring":
        handle_keyring(proc)
    print("done")

def prep_unlock(cmd : list):
    if len(cmd) == 1:
        return click.prompt("enter password", type=str, hide_input=True)
    else:
        return cmd[1]


def shell_entry():
    print(
        "welcome to bitwarden quicker shell, same use case as bw-cli with session key stored for the instance"
    )

    arg_dict = vars(arg_parse.parse_args())

    proc = BwProc(path=arg_dict["path"])
    
    envs = os.environ.copy()

    if arg_dict["stateful_session"]:
        handle_keyring(proc)

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
            handle_com(cmd[1:], proc)
            continue

        if cmd[0] == "login":
            u, p, *args = cmd[1:]
            proc = proc.login(proc.path, u, p, *args)
            del u, p, args
            continue

        if cmd[0] == "unlock":
            proc = proc.unlock(prep_unlock(cmd))
            continue

        try:
            res = proc.exec(*cmd)
            raw = json.loads(res)
            pprint(raw, indent=4)
        except Exception as e: # noqa
            print(e)

def main_loop():
    try:
        shell_entry()
    except* (KeyboardInterrupt, EOFError):
        print("\nbye")

if __name__ == "__main__":
    main_loop()