#!/usr/bin/env python3

import os

import yaml
import aws_cdk as cdk

from cdk.stack.iam import CloudXIAMStack
from cdk.stack.image import CloudXImageStack
from cdk.stack.info import CloudXInfoStack
from cdk.stack.serverless import CloudXServerlessStack

env = cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'),
                      region=os.getenv('CDK_DEFAULT_REGION'))
app = cdk.App()

with open('config.yml') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

    stack = app.node.try_get_context('stack')

    if not stack or stack == 'cloudxiam':
        CloudXIAMStack(app, 'cloudxiam',
                       env=env)
        
    if not stack or stack == 'cloudxinfo':
        CloudXInfoStack(app, 'cloudxinfo',
                        env=env,
                        key=config['key'])
        
    if not stack or stack == 'cloudximage':
        CloudXImageStack(app, 'cloudximage',
                         env=env,
                         key=config['key'],
                         application='image')
        
    if not stack or stack == 'cloudxserverless':
        CloudXServerlessStack(app, 'cloudxserverless',
                              env=env,
                              key=config['key'],
                              application='serverless')

app.synth()
