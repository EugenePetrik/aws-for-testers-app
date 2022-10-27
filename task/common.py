from typing import List, Literal, Optional
import platform
import sys

CDKCommand = Literal["deploy", "destroy"]

STACKS = ['cloudxiam', 'cloudxinfo', 'cloudximage', 'cloudxserverless']

PYTHON_MAJOR = 3
PYTHON_MIN_MINOR = 8
PYTHON_MAX_MINOR = 10
if sys.version_info[0] != PYTHON_MAJOR or sys.version_info[1] < PYTHON_MIN_MINOR or sys.version_info[1] > PYTHON_MAX_MINOR:
    sys.exit((
        f"Python {sys.version_info.major}.{sys.version_info.minor} is not supported.\n"
        f"Python required: {PYTHON_MAJOR}.{PYTHON_MIN_MINOR} <= Python <= {PYTHON_MAJOR}.{PYTHON_MAX_MINOR}.\n"
    ))


def _validate_stack(stack: str):
    if stack not in STACKS:
        raise ValueError(
            "There is no stack like '{}', possible stack: {}".format(stack, ", ".join(STACKS)))


def run_command(c, cmd: List[str]):
    c.run(" ".join(cmd), pty=platform.system() != 'Windows', echo=True)


def run_cdk(c, command: CDKCommand, stack: str, profile: Optional[str] = None, context: Optional[dict] = None, force: Optional[bool] = False):
    _validate_stack(stack)
    cmd = ["cdk"]
    if profile:
        cmd.append(f"--profile {profile}")
    cmd.append(command)
    cmd.append(stack)
    if force:
        cmd.append("--force")

    if not context:
        context = {}
    context['stack'] = stack
    cmd.append(" ".join([f"--context {k}={v}" for k, v in context.items()]))
    run_command(c, cmd)


def help(commands: Optional[dict] = {}):
    return {
        'profile': 'The AWS profile to use, the default one will be used if empty.',
        **commands
    }
