"""
Delete SageMaker endpoint to save costs.

Run this script to delete the endpoint when not in use:
    poetry run python tools/delete_endpoint.py

To redeploy later:
    poetry run python tools/deploy_with_autoscaling.py
"""

import boto3
from llm_engineering.settings import settings


def delete_endpoint():
    print("=" * 60)
    print("DELETING SAGEMAKER ENDPOINT")
    print("=" * 60)

    sagemaker_client = boto3.client(
        'sagemaker',
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY,
        aws_secret_access_key=settings.AWS_SECRET_KEY,
    )

    endpoint_name = settings.SAGEMAKER_ENDPOINT_INFERENCE
    print(f"\nEndpoint to delete: {endpoint_name}")

    # Delete endpoint
    print("\n[Step 1] Deleting endpoint...")
    try:
        sagemaker_client.delete_endpoint(EndpointName=endpoint_name)
        print(f"  [OK] Endpoint '{endpoint_name}' deletion initiated")
    except Exception as e:
        print(f"  [ERROR] {e}")

    # Delete endpoint configuration
    print("\n[Step 2] Deleting endpoint configuration...")
    try:
        sagemaker_client.delete_endpoint_config(EndpointConfigName=endpoint_name)
        print(f"  [OK] Endpoint config deleted")
    except Exception as e:
        print(f"  [ERROR] {e}")

    print("\n" + "=" * 60)
    print("ENDPOINT DELETED")
    print("=" * 60)
    print("""
The endpoint has been deleted. You are no longer being charged.

To redeploy later, run:
    poetry run python tools/deploy_with_autoscaling.py
""")


if __name__ == "__main__":
    confirm = input("Are you sure you want to delete the endpoint? (yes/no): ")
    if confirm.lower() == 'yes':
        delete_endpoint()
    else:
        print("Cancelled.")
