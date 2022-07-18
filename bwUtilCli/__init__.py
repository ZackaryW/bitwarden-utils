import os
import click 
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bwUtil.caller import BwClient
from bwUtil.download import secureDownloadMethod

downloadtempFolder : str = None

@click.command()
@click.option("--runcmd", type=click.STRING, default=None, help="run a command")
@click.option('--bwpath', type=str, default=os.getcwd(), help='Path to BWUtil.exe')
@click.option('--username', type=str, required=False)
@click.option('--password', type=str, required=False)
@click.option('--totp', type=str, required=False)
@click.option('--downloadtemp', is_flag = True, default=False)
@click.option('--sync', is_flag = True, default=False)
@click.option('--dig', type=int, default=2)
@click.option('--export', type=str, required=False)
def clickMain(
    username, 
    password, 
    bwpath, 
    downloadtemp, 
    sync, 
    runcmd,
    dig,
    totp=None,
    export=None, 
):
    global downloadtempFolder

    print("Bitwarden Utils CLI")

    # init client
    bw = BwClient.resolve(bwpath)

    if bw is None and downloadtemp and (download := secureDownloadMethod()) is not None:
        print("Downloaded cli to {}".format(download))
        bw = BwClient.resolve(download)
        downloadtempFolder = download

    if bw is None:
        print("bw (cli) not found, please specify path")
        return

    # logged in
    loggedIn = bw.isLoggedIn
    if not loggedIn:
        print("Currently not logged in, will attempt to login if possible")
    else:
        print("Currently logged in as {}".format(bw.isLoggedIn))

    if not loggedIn and ( not username or not password):
        print("Please specify username and password")
        username = click.prompt("Username")
        password = click.prompt("Password", hide_input=True)
        hasTotp = click.confirm("Do you have a totp code?")
        if hasTotp:
            totp = click.prompt("Totp code")
        else:
            totp = None 

    if loggedIn:
        pass

    elif bw.login(username, password, totp):
        
        print("Logged in as {}".format(bw.isLoggedIn))
    else:
        print("Failed to login")
        return

    # unlock
    if bw.session is None:
        if not password:
            password = click.prompt("Password", hide_input=True)
        bw.unlock(password=password)
        print("Unlocked")

    if bw.session is None:
        print("No session found, login/unlock failed")
        return

    # sync if requested
    if sync:
        bw.sync()
        print("Synced")

    # run command if requested
    if runcmd:
        res= bw.runWithSession(*runcmd.split(" "))
        print("Ran command {}".format(runcmd))
        print(res)
        return

    # export
    if not export:
        export = click.prompt("Please specify export path", type=click.Path())

    if not os.path.exists(export):
        os.makedirs(export, exist_ok=True)

    export = os.path.abspath(export)

    if not os.path.isdir(export):
        print("Export path is not a directory")
        return

    # export
    items = bw.listItems()
    total_jobs = len(items)
    if total_jobs == 0:
        print("No attachments found")
        return

    for i in bw.export_attachments(export, items):
        if total_jobs != 0:
            print("working on {}/{}".format(i, total_jobs))

    print("Done")

def main():
    clickMain()
    if downloadtempFolder:
        os.remove(downloadtempFolder)


if __name__ == "__main__":
    main()
