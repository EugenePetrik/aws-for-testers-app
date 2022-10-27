from invoke import task
from task.common import run_cdk, help, run_command
import platform

destroy_task = task(help=help())

FORCE = platform.system() == 'Windows'

@destroy_task
def cloudxiam(c, profile=None, force=FORCE):
    run_cdk(c, command='destroy', stack='cloudxiam', profile=profile, force=force or FORCE)

@destroy_task
def cloudxinfo(c, profile=None, force=FORCE):
    run_cdk(c, command='destroy', stack='cloudxinfo', profile=profile, force=force or FORCE)

@destroy_task
def cloudximage(c, profile=None, force=FORCE):
    run_cdk(c, command='destroy', stack='cloudximage', profile=profile, force=force or FORCE)

@destroy_task
def cloudxserverless(c, profile=None, force=FORCE):
    run_cdk(c, command='destroy', stack='cloudxserverless', profile=profile, force=force or FORCE)
    
@destroy_task
def all(c, profile=None, force=FORCE):
    cmd = ["cdk"]
    if profile:
        cmd.append(f"--profile {profile}")
    cmd.append("destroy")
    cmd.append("--all")
    if force or FORCE:
        cmd.append("--force")
    run_command(c, cmd)