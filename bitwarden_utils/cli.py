import logging
import click
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from bitwarden_utils.core.proc import BwProc, BwProcInfo# noqa
from bitwarden_utils.core.python_client import BwPyClient# noqa
from bitwarden_utils import download_all_attachments_in_one_go # noqa

@click.group(invoke_without_command=True, no_args_is_help=True)
@click.option("--debug", is_flag=True, help="Print debug messages")
@click.option("--credential","-c", help="username, password, totp", multiple=True)
def cli(debug, credential):
    if debug:
        logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
        
    match len(credential), BwProcInfo.notLoggedIn:
        case 0, True:
            return click.echo("Please login first")
        case 0, False:
            pass
        
        case 1, True:
            return click.echo("Please login first")
        case 1, False:
            password = credential[0]
            BwProc.unlock(password)
        case 2, _:
            username, password = credential
            BwProc.login(username, password)
        case 3, _:
            username, password, totp = credential
            BwProc.login(username, password, totp)
        case _:
            logging.debug(credential)
            raise Exception("Invalid credential")

    logging.debug(BwPyClient.sync())
    
@cli.command("downall")
@click.argument("targetFolder")
def download_all(targetFolder):
    download_all_attachments_in_one_go(targetFolder)
    
def cli_main():
    cli()
    
if __name__ == "__main__":
    cli()

