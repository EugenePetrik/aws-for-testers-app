# IAM Stack

The stack contains IAM Policies, Roles, and Groups to handle EC2 Instance access to S3 and EC2.

Policies:
 - `FullAccessPolicyEC2`
 - `FullAccessPolicyS3`
 - `ReadAccessPolicyS3`

Roles:
 - `FullAccessRoleEC2`
 - `FullAccessRoleS3`
 - `ReadAccessRoleS3`

Groups:
 - `FullAccessGroupEC2`
 - `FullAccessGroupS3`
 - `ReadAccessGroupS3`

## Prerequisites

1. Make sure that the [Initialization](../README.md) is done and **virtual env** is enabled.
   
## Deploying

1. Execute the following command to deploy the `cloudxiam` stack (in the folder of the main [README](../README.md)):
   ```shell
   invoke deploy.cloudxiam
   ```
   - To deploy other version of the stack, execute the deploy comment with `--version`, e.g.:
     ```shell
     invoke deploy.cloudxiam --version=2
     ```
2. If the script ask for confirmation to deploy the changes, then input a `y` and ht **Enter**:
   ```
   Do you wish to deploy these changes (y/n)? 
   ```
3. Wait for the process to finish.
4. At the end the command will provide you a number of output data that will be useful for testing:
   - The final name of the `FullAccessPolicyEC2`
   - The final name of the `FullAccessPolicyS3`
   - The final name of the `ReadAccessPolicyS3`

This command should be used for first and all consequitive deployments/updates.

## Destroying

1. Execute the following command to destroy the alreay deployed `cloudxiam` stack (in the folder of the main [README](../README.md)):
   ```shell
   invoke destroy.cloudxiam
   ```
2. If the script ask for confirmation to destroy the stack, then input a `y` and hit **Enter**:
   ```
   Are you sure you want to delete: cloudxiam (y/n)? 
   ```
3. Wait for the process to finish.