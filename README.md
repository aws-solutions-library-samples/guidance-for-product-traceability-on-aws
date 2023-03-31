# Product Traceability on AWS - CDK Deployment
It is recommended that the following steps are followed in an AWS Cloud9 environment. This will allow for easiest deployment as AWS CDK will already be installed.
Alternatively, follow the [CDK installation instructions](https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html).
## Quickstart
### Set up the Environment
Create a virtual environment
```bash
> python3 -m venv .venv
```
Activate the environment on linux/macOS:
```bash
> source .venv/bin/activate
```
Activate the environment on windows:
```bash
> .venv\Scripts\activate.bat
```

### Deploy the Solution
Start by installing the requirements in your virtual environment
```bash
> pip install -r requirements.txt
```
Run bootstrap in order to provision resources for the CDK solution
```bash
> cdk bootstrap
```
Deploy the solution
```bash
> cdk deploy
```

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

