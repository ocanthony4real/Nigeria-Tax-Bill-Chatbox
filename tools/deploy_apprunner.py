"""
Deploy Nigeria Tax Bill Chatbot to AWS App Runner.

Prerequisites:
1. AWS CLI configured with credentials
2. Docker installed and running
3. ECR repository created (or will be created automatically)

Usage:
    poetry run python tools/deploy_apprunner.py
"""

import subprocess
import sys
import boto3
from llm_engineering.settings import settings


# Configuration
APP_NAME = "nigeria-tax-chatbot"
ECR_REPO_NAME = "nigeria-tax-chatbot"
AWS_REGION = settings.AWS_REGION


def run_command(cmd: str, description: str) -> bool:
    """Run a shell command and return success status."""
    print(f"\n[STEP] {description}")
    print(f"  Command: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  [ERROR] {result.stderr}")
        return False
    print(f"  [OK] {description}")
    if result.stdout:
        print(f"  Output: {result.stdout[:500]}")
    return True


def get_account_id() -> str:
    """Get AWS account ID."""
    sts = boto3.client('sts',
        region_name=AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY,
        aws_secret_access_key=settings.AWS_SECRET_KEY,
    )
    return sts.get_caller_identity()["Account"]


def create_ecr_repo_if_not_exists(ecr_client, repo_name: str) -> str:
    """Create ECR repository if it doesn't exist."""
    try:
        response = ecr_client.describe_repositories(repositoryNames=[repo_name])
        repo_uri = response['repositories'][0]['repositoryUri']
        print(f"  [OK] ECR repository exists: {repo_uri}")
        return repo_uri
    except ecr_client.exceptions.RepositoryNotFoundException:
        print(f"  Creating ECR repository: {repo_name}")
        response = ecr_client.create_repository(
            repositoryName=repo_name,
            imageScanningConfiguration={'scanOnPush': True},
            imageTagMutability='MUTABLE'
        )
        repo_uri = response['repository']['repositoryUri']
        print(f"  [OK] Created ECR repository: {repo_uri}")
        return repo_uri


def main():
    print("=" * 60)
    print("DEPLOYING TO AWS APP RUNNER")
    print("=" * 60)

    # Get AWS account ID
    print("\n[STEP] Getting AWS account information...")
    account_id = get_account_id()
    print(f"  Account ID: {account_id}")
    print(f"  Region: {AWS_REGION}")

    # Create ECR client
    ecr_client = boto3.client('ecr',
        region_name=AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY,
        aws_secret_access_key=settings.AWS_SECRET_KEY,
    )

    # Create ECR repository
    print("\n[STEP] Setting up ECR repository...")
    ecr_uri = create_ecr_repo_if_not_exists(ecr_client, ECR_REPO_NAME)
    image_uri = f"{ecr_uri}:latest"

    # Get ECR login password
    print("\n[STEP] Logging into ECR...")
    token = ecr_client.get_authorization_token()
    password = token['authorizationData'][0]['authorizationToken']

    # Docker login to ECR
    ecr_endpoint = f"{account_id}.dkr.ecr.{AWS_REGION}.amazonaws.com"
    if not run_command(
        f'echo {password} | docker login --username AWS --password-stdin {ecr_endpoint}',
        "Docker login to ECR"
    ):
        print("\n[ERROR] Failed to login to ECR")
        print("Make sure Docker is running!")
        sys.exit(1)

    # Build Docker image
    if not run_command(
        f'docker build -t {ECR_REPO_NAME}:latest .',
        "Building Docker image"
    ):
        print("\n[ERROR] Failed to build Docker image")
        sys.exit(1)

    # Tag image for ECR
    if not run_command(
        f'docker tag {ECR_REPO_NAME}:latest {image_uri}',
        "Tagging image for ECR"
    ):
        sys.exit(1)

    # Push to ECR
    if not run_command(
        f'docker push {image_uri}',
        "Pushing image to ECR"
    ):
        print("\n[ERROR] Failed to push image to ECR")
        sys.exit(1)

    # Create App Runner service
    print("\n[STEP] Creating App Runner service...")
    apprunner_client = boto3.client('apprunner',
        region_name=AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY,
        aws_secret_access_key=settings.AWS_SECRET_KEY,
    )

    # Check if service exists
    try:
        services = apprunner_client.list_services()
        existing = [s for s in services['ServiceSummaryList'] if s['ServiceName'] == APP_NAME]
        if existing:
            print(f"  [INFO] Service '{APP_NAME}' already exists. Updating...")
            # Trigger new deployment
            apprunner_client.start_deployment(ServiceArn=existing[0]['ServiceArn'])
            service_url = existing[0]['ServiceUrl']
            print(f"\n[OK] Deployment triggered!")
            print(f"  URL: https://{service_url}")
            return
    except Exception as e:
        print(f"  [WARNING] Could not check existing services: {e}")

    # Create new service
    try:
        response = apprunner_client.create_service(
            ServiceName=APP_NAME,
            SourceConfiguration={
                'ImageRepository': {
                    'ImageIdentifier': image_uri,
                    'ImageRepositoryType': 'ECR',
                    'ImageConfiguration': {
                        'Port': '8080',
                        'RuntimeEnvironmentVariables': {
                            'PYTHONPATH': '/app',
                            'PORT': '8080',
                            'AWS_REGION': AWS_REGION,
                            'AWS_ACCESS_KEY': settings.AWS_ACCESS_KEY,
                            'AWS_SECRET_KEY': settings.AWS_SECRET_KEY,
                            'QDRANT_CLOUD_URL': settings.QDRANT_CLOUD_URL,
                            'QDRANT_APIKEY': settings.QDRANT_APIKEY or '',
                            'DATABASE_HOST': settings.DATABASE_HOST or '',
                            'COMET_API_KEY': settings.COMET_API_KEY or '',
                        }
                    }
                },
                'AutoDeploymentsEnabled': False,
                'AuthenticationConfiguration': {
                    'AccessRoleArn': settings.AWS_ARN_ROLE
                }
            },
            InstanceConfiguration={
                'Cpu': '1 vCPU',
                'Memory': '2 GB'
            },
            HealthCheckConfiguration={
                'Protocol': 'HTTP',
                'Path': '/',
                'Interval': 20,
                'Timeout': 5,
                'HealthyThreshold': 1,
                'UnhealthyThreshold': 5
            }
        )
        service_url = response['Service']['ServiceUrl']
        print(f"\n{'=' * 60}")
        print("DEPLOYMENT INITIATED!")
        print("=" * 60)
        print(f"""
Your chatbot is being deployed to App Runner.

Service Name: {APP_NAME}
Status: Creating (takes 2-5 minutes)
URL: https://{service_url}

To check status:
    aws apprunner list-services --region {AWS_REGION}

To view logs:
    aws apprunner list-operations --service-arn {response['Service']['ServiceArn']}
""")
    except Exception as e:
        print(f"\n[ERROR] Failed to create App Runner service: {e}")
        print("\nYou may need to create an App Runner access role first.")
        print("See: https://docs.aws.amazon.com/apprunner/latest/dg/security_iam_service-with-iam.html")
        sys.exit(1)


if __name__ == "__main__":
    main()
