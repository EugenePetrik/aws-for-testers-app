# CloudX Associate QA - Test Application

This project contains the test applications used during the **CloudX Associate QA** course.

The project is based on **Python** and the **AWS CDK**.

## Prerequisites

These need to be done once, you set up the project.

1. **AWS Account** is created (see Module 2: Create AWS Account)
2. **Python** is installed (>=3.8, <=3.10): [Guide](https://wiki.python.org/moin/BeginnersGuide/Download)
3. **AWS CLI** is installed and
   configured: [Guide](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html)
4. **Node.js LTS** is installed (for AWS CDK): [Homepage](https://nodejs.org/en/)
5. **AWS CDK** is
   installed: [Guide](https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html?refid=33ffcbe8-beac-4ead-b902-a91ced7f226f#getting_started_install)

## Usage

### Initializing

To use the project and deploy/destroy the stacks and application, the following initialization is required (besides the
previously listed prerequisites).

Execute the following commands in the main directory of the project (where this README is located):

1. Create a Python virtual environment _(this needs to be executed once)_:
   ```shell
   python -m venv .venv
   ```
2. After the init process completes and the virtual environment is created, activate the virtual environment with the following
   command _(this needs to be executed every time the command line session is opened)_:
    - In any Unix/Mac (like) terminal (including Git Bash, Mingw, etc):
      ```shell
      source .venv/bin/activate
      ```
    - In Windows Command line:
      ```cmd
      .venv\Scripts\activate.bat
      ```
    - In Windows PowerShell:
      ```shell
      & .\.venv\Scripts\Activate.ps1
      ```
   Note, that, depending on the version of `venv` and the platform, the `.venv` folder structure can be different, the scripts can be either in the `bin` or the `Scripts` folder.
3. Once the virtual environment is activated, install the required dependencies _(no need to execute this often, at least once when the virtual environment is created)_:
   ```shell
   pip install -r requirements.txt --upgrade
   ```
4. Most of the stacks will require having an **EC2 Key Pair** set up on your local machine. To set it up, follow these steps:
   1. Open **AWS Console**
   2. In the **Services** menu, select **EC2**
   3. In the **Network & Security** menu, select **Key Pairs**.
   4. Select the same region on the top-right corner as you will use during the course.
   5. Click on **Create Key Pair** and provide the `cloudx` name for this new Key Pair.
   6. Click on **Create**
   7. Download the Key Pair provided in PEM format and store it in the `<USER_HOME>/.aws/pems` folder
    as `cloudx.pem` (`C:\Users\<username>\.aws\pems` on Windows, `~/.aws/pems` on Unix).
      - If the folder does not exist, create it. The folder name is case-sensitive.
      - Update permissions for the PEM file: `chmod 400 ~/.aws/pems` (on Unix or from Git Bash on Windows).
   8. Ensure that the `key` configuration in the [config.yml](config.yml) is set to the name of the PEM file (without the extension): `cloudx`.
   
   This Key Pair can be used later to SSH to the EC2 instances: `ssh -i ~/.aws/pems/cloudx.pem ec2-user@{public ip}`
5. Execute **CDK Bootstrap** _(this needs to be executed once)_:
   ```shell
   cdk bootstrap
   ```

### Deploying

To deploy a given stack (mentioned in the **Home tasks**), the `invoke deploy.<stack>` command can be
used, where `<stack>` is the ID of one of the stacks listed below:

```shell
invoke deploy.<stack>
```

For example:

```shell
invoke deploy.cloudxinfo
```

This command will synthesize the CloudFormation template of the stack and deploy it to your AWS Account already set up
on your computer.

**NOTES**
* The command **might** prompt you for confirmation before deploying the stack. Confirm it with `y`, otherwise, the stack won't be deployed. By default, this confirmation is explicitly set on all platforms.
* The command will display some output values of the stack, such as ARNs, URLs, etc. Normally, there is no need to do anything with them, but you might note these for manual/automated testing.
* If multiple AWS profiles are set up on your machine, the `--profile` argument can be used to set which one to use.
* For more information about the available commands, run `invoke --list`.
* In case of another version of the stack/application needs to be deployed, the `--version` argument can be used, e.g. `invoke deploy.cloudxinfo --version=2`.
* In case of redeploying any of the following stacks, the EC2 instances need a reboot to take up any changes in the application: `cloudxinfo`, `cloudximage`, and `cloudxserverless`. To reboot an EC2 instance, you can use the `aws ec2 reboot-instances --instance-ids <id>`, where the `<id>` can be found in the output of the deploy script. A reboot might take a couple of minutes.
* On Windows, the output of the command is buffered, thus it might take some time until you can see any output in the terminal. In case of any error, the output will be seen immediately.

### Destroying

**IMPORTANT** all the stacks are created to use mostly free-tier resources and services. However, some services in the
stack (e.g. NAT Gateway, EC2) may generate after some time a small amount of cost. To minimize the cost, **use the
following command to destroy the stack when you don't use it**.

To destroy a previously deployed stack (mentioned in the **Home tasks**), the `invoke destroy.<stack>` command can be
used, where `<stack>` is the ID of one of the stacks listed below:

```shell
invoke destroy.<stack>
```

For example:

```shell
invoke destroy.cloudxinfo
```

**NOTES**
* The command **might** prompt you for confirmation to destroy the stack. Confirm it with `y`, otherwise, the stack won't be destroyed. **IMPORTANT!** On Windows, this confirmation is explicitly set in advance! On other platforms, this can be bypassed with the `--force` argument.
* If multiple AWS profiles are set up on your machine, the `--profile` argument can be used to set which one to use.
* For more information about the available commands, run `invoke --list`.
* To ensure all stacks are destroyed, you can run the `invoke destroy.all` command.
* On Windows, the output of the command is buffered, thus it might take some time until you can see any output in the terminal. In case of any error, the output will be seen immediately.

#### Leftover resources

Each stack will be cleaned up when destroyed, and almost all of the active resources should be destroyed. However, some log groups are not deleted by default for all resources immediately. Those can be deleted manually on the CloudWatch / LogGroups page, or they will be deleted after some days when the log retention period is over.

## Stacks

The following stacks are available for use during the training:
- [IAM - cloudxiam](docs/cloudxiam.md)
- [INFO application - cloudxinfo](docs/cloudxinfo.md)
- [IMAGE application - cloudximage](docs/cloudximage.md)
- [Serverless IMAGE application - cloudxserverless](docs/cloudxserverless.md)

These documentations contain detailed descriptions of the stacks/applications and specific deployment/destroy guides.
