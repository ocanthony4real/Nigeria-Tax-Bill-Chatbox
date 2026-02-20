"""
Deploy SageMaker endpoint with autoscaling configuration.

Run this script after deleting an endpoint to redeploy with autoscaling:
    poetry run python tools/deploy_with_autoscaling.py

This script will:
1. Deploy the SageMaker endpoint
2. Configure autoscaling (min: 1, max: 3 instances)
3. Set up scaling policy based on invocations per instance
"""

import boto3
from sagemaker.enums import EndpointType

from llm_engineering.infrastructure.aws.deploy.huggingface.run import create_endpoint
from llm_engineering.settings import settings


def configure_autoscaling(endpoint_name: str, min_capacity: int = 1, max_capacity: int = 3):
    """Configure autoscaling for a SageMaker endpoint."""

    print("\n" + "=" * 60)
    print("CONFIGURING AUTOSCALING")
    print("=" * 60)

    autoscaling_client = boto3.client(
        'application-autoscaling',
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY,
        aws_secret_access_key=settings.AWS_SECRET_KEY,
    )

    resource_id = f"endpoint/{endpoint_name}/variant/AllTraffic"

    # Register scalable target
    print(f"\nRegistering scalable target for {endpoint_name}...")
    try:
        autoscaling_client.register_scalable_target(
            ServiceNamespace='sagemaker',
            ResourceId=resource_id,
            ScalableDimension='sagemaker:variant:DesiredInstanceCount',
            MinCapacity=min_capacity,
            MaxCapacity=max_capacity,
        )
        print(f"  [OK] Min: {min_capacity}, Max: {max_capacity} instances")
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False

    # Create scaling policy
    print("\nCreating scaling policy...")
    try:
        autoscaling_client.put_scaling_policy(
            PolicyName=f'{endpoint_name}-scaling-policy',
            ServiceNamespace='sagemaker',
            ResourceId=resource_id,
            ScalableDimension='sagemaker:variant:DesiredInstanceCount',
            PolicyType='TargetTrackingScaling',
            TargetTrackingScalingPolicyConfiguration={
                'TargetValue': 5.0,  # Target invocations per instance per minute
                'PredefinedMetricSpecification': {
                    'PredefinedMetricType': 'SageMakerVariantInvocationsPerInstance'
                },
                'ScaleInCooldown': 300,   # 5 minutes before scaling down
                'ScaleOutCooldown': 60,   # 1 minute before scaling up
            }
        )
        print("  [OK] Policy created: target 5 invocations/instance/min")
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False

    print("\n[OK] Autoscaling configured successfully!")
    return True


def main():
    print("=" * 60)
    print("DEPLOYING SAGEMAKER ENDPOINT WITH AUTOSCALING")
    print("=" * 60)
    print(f"\nModel: {settings.HF_MODEL_ID}")
    print(f"Endpoint: {settings.SAGEMAKER_ENDPOINT_INFERENCE}")
    print(f"Instance: {settings.GPU_INSTANCE_TYPE}")
    print(f"Max Input Length: {settings.MAX_INPUT_LENGTH}")

    # Step 1: Deploy endpoint
    print("\n" + "=" * 60)
    print("STEP 1: DEPLOYING ENDPOINT")
    print("=" * 60)
    create_endpoint(endpoint_type=EndpointType.MODEL_BASED)

    # Step 2: Configure autoscaling
    configure_autoscaling(
        endpoint_name=settings.SAGEMAKER_ENDPOINT_INFERENCE,
        min_capacity=1,
        max_capacity=3
    )

    print("\n" + "=" * 60)
    print("DEPLOYMENT COMPLETE!")
    print("=" * 60)
    print(f"""
Your endpoint is ready:
  - Endpoint: {settings.SAGEMAKER_ENDPOINT_INFERENCE}
  - Autoscaling: 1-3 instances
  - Region: {settings.AWS_REGION}

To test: poetry run python test_endpoint.py
To chat: poetry run python tools/chat_ui.py
""")


if __name__ == "__main__":
    main()
