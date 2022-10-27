from invoke import task
from task.common import run_cdk, help

VERSION = {
    'version': 'The version of the application to be deployed. Default: 1'
}
deploy_task = task(help=help(VERSION))

@deploy_task
def cloudxiam(c, profile=None, version=1):
    run_cdk(c, command='deploy', stack='cloudxiam', profile=profile, context={
        'version': version
    })
    
@deploy_task
def cloudxinfo(c, profile=None, version=1):
    run_cdk(c, command='deploy', stack='cloudxinfo', profile=profile, context={
        'version': version
    })

@deploy_task
def cloudximage(c, profile=None, version=1):
    run_cdk(c, command='deploy', stack='cloudximage', profile=profile, context={
        'version': version
    })

@deploy_task
def cloudxserverless(c, profile=None, version=1):
    run_cdk(c, command='deploy', stack='cloudxserverless', profile=profile, context={
        'version': version
    })