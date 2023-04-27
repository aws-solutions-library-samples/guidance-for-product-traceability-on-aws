# Product Traceability on AWS - CDK Deployment
## Table of Contents
- [About](#about)
- [Quickstart](#quickstart)
  * [Clone the Repository](#clone-the-repository)
  * [Set up the Environment](#set-up-the-environment)
  * [Deploy the Solution](#deploy-the-solution)
  * [Test the Solution](#test-the-solution)
  * [Destroy the Solution](#destroy-the-solution)
- [Security](#security)
- [License](#license)
## About
This code is a AWS CDK deployment of the Prescriptive Guidance for Product Traceability on AWS. It will allow you to easily deploy all the necessary resources to get started on ingesting and extracting supply chain certificates.

### Note
The resources deployed are by no means a complete solution. The resulting resources act as a framework, and starting point, within which you can build your own extraction pipeline.

## Quickstart
It is recommended that the following steps are followed in an AWS Cloud9 environment. This will allow for easiest deployment as AWS CDK will already be installed.
Alternatively, follow the [CDK installation instructions](https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html).
### Clone the Repository
After cloning the repository, navigate into the CDK folder.
```bash
cd guidance-for-product-traceability-on-aws/product-traceability
```
### Set up the Environment
Create a virtual environment
```bash
python3 -m venv .venv
```
Activate the environment on linux/macOS:
```bash
source .venv/bin/activate
```
Activate the environment on windows:
```bash
.venv\Scripts\activate.bat
```

### Deploy the Solution
Start by installing the requirements in your virtual environment
```bash
pip install -r requirements.txt
```
Run bootstrap in order to provision resources for the CDK solution
```bash
cdk bootstrap
```
Deploy the solution
```bash
cdk deploy
```
### Test the Solution
Extraction is triggered by uploading a file to the newly created S3 bucket, with a prefix 'landing/'. This is to say, uploading anything to the landing "folder" will trigger the step function. Included in this repo is a file called "Mock Dock.pdf", which can be used to test the solution. Expected behaviour is:
- File uploaded to 'landing/'
- Step function is triggered
- Step function completes
- Data is exported to S3 bucket as 'data/demo_output.json'
- Certificate is archived with prefix 'archive/'

Note: Creating the 'landing/' folder will trigger the step-function. This is expected behaviour. The function will fail immediately, and cause no changes.
### Destroy the Solution
If you want to free up resources, run the following command:
```bash
cdk destroy
```
NOTE: This will **NOT** destroy the deployed S3 bucket. You will need to empty and delete the bucket through the console.

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

