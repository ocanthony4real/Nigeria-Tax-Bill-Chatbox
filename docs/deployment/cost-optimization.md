# Cost Optimization

This guide provides strategies to minimize AWS costs for the Nigeria Tax Bill Chatbot.

## Current Cost Breakdown

| Service | Configuration | Monthly Cost |
|---------|---------------|--------------|
| SageMaker (always on) | ml.g5.xlarge | ~$300 |
| SageMaker (scale-to-zero) | ml.g5.xlarge | $0-150 |
| App Runner | 2 vCPU, 4GB | $50-80 |
| ECR | ~5GB storage | $1-5 |
| Qdrant Cloud | Starter tier | Free |
| MongoDB Atlas | M0 tier | Free |
| **Total (optimized)** | | **$51-235** |

---

## SageMaker Optimization

### Scale to Zero

The biggest cost saver - scale the endpoint to zero when idle.

```python
import boto3

client = boto3.client('application-autoscaling')

# Register scalable target with MinCapacity=0
client.register_scalable_target(
    ServiceNamespace='sagemaker',
    ResourceId='endpoint/nigeria-tax-llama-v3/variant/AllTraffic',
    ScalableDimension='sagemaker:variant:DesiredInstanceCount',
    MinCapacity=0,  # KEY: Scale to zero
    MaxCapacity=1
)

# Create scaling policy
client.put_scaling_policy(
    PolicyName='scale-to-zero-policy',
    ServiceNamespace='sagemaker',
    ResourceId='endpoint/nigeria-tax-llama-v3/variant/AllTraffic',
    ScalableDimension='sagemaker:variant:DesiredInstanceCount',
    PolicyType='TargetTrackingScaling',
    TargetTrackingScalingPolicyConfiguration={
        'TargetValue': 1.0,
        'PredefinedMetricSpecification': {
            'PredefinedMetricType': 'SageMakerVariantInvocationsPerInstance'
        },
        'ScaleInCooldown': 900,   # 15 min before scale down
        'ScaleOutCooldown': 60     # 1 min before scale up
    }
)
```

**Savings**: ~$150/month for low-traffic periods

### Spot Instances

Use spot instances for training (not inference):

```python
from sagemaker.estimator import Estimator

estimator = Estimator(
    ...,
    use_spot_instances=True,
    max_wait=7200,  # 2 hours max wait
    max_run=3600,   # 1 hour training
)
```

**Savings**: Up to 70% on training costs

### Right-Size Instance

Choose the smallest instance that meets requirements:

| Instance | GPU | VRAM | Cost/hr | Use Case |
|----------|-----|------|---------|----------|
| ml.g5.xlarge | A10G | 24GB | $1.41 | Production |
| ml.g4dn.xlarge | T4 | 16GB | $0.74 | Testing |
| ml.m5.xlarge | - | - | $0.23 | CPU inference |

---

## App Runner Optimization

### Min/Max Instances

```yaml
InstanceConfiguration:
  MinSize: 1      # Minimum instances
  MaxSize: 3      # Maximum instances (auto-scale)
```

For very low traffic, set MinSize to 0 (with cold start tradeoff).

### Resource Sizing

Right-size CPU and memory:

| Traffic | CPU | Memory | Est. Cost |
|---------|-----|--------|-----------|
| Low | 1 vCPU | 2 GB | $25-40 |
| Medium | 2 vCPU | 4 GB | $50-80 |
| High | 4 vCPU | 8 GB | $100-150 |

### Pause During Off-Hours

```python
import boto3
from datetime import datetime

def manage_service():
    client = boto3.client('apprunner')
    hour = datetime.now().hour

    if 0 <= hour < 6:  # Midnight to 6 AM
        client.pause_service(ServiceArn=SERVICE_ARN)
    else:
        client.resume_service(ServiceArn=SERVICE_ARN)
```

---

## ECR Optimization

### Lifecycle Policies

Remove old images automatically:

```json
{
  "rules": [
    {
      "rulePriority": 1,
      "description": "Keep last 5 images",
      "selection": {
        "tagStatus": "any",
        "countType": "imageCountMoreThan",
        "countNumber": 5
      },
      "action": {
        "type": "expire"
      }
    }
  ]
}
```

```bash
aws ecr put-lifecycle-policy \
  --repository-name nigeria-tax-chatbot \
  --lifecycle-policy-text file://lifecycle-policy.json
```

### Image Size Reduction

Optimize Docker image:

```dockerfile
# Use slim base
FROM python:3.11-slim

# Multi-stage build
FROM node:20-alpine AS frontend
...
FROM python:3.11-slim AS production
COPY --from=frontend /app/out ./static

# Minimize layers
RUN pip install --no-cache-dir -r requirements.txt
```

---

## Free Tier Services

### Qdrant Cloud

Use the free Starter tier:
- 1GB storage
- Sufficient for 291 vectors
- No cost

### MongoDB Atlas

Use the free M0 tier:
- 512MB storage
- Shared cluster
- No cost

### HuggingFace Hub

Free model hosting:
- Unlimited public models
- No storage limits
- No cost

---

## Cost Monitoring

### AWS Cost Explorer

```bash
# Get current month costs
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-01-31 \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=DIMENSION,Key=SERVICE
```

### Budget Alerts

```bash
aws budgets create-budget \
  --account-id YOUR_ACCOUNT \
  --budget '{
    "BudgetName": "NigeriaTaxChatbot",
    "BudgetLimit": {
      "Amount": "100",
      "Unit": "USD"
    },
    "TimeUnit": "MONTHLY",
    "BudgetType": "COST"
  }' \
  --notifications-with-subscribers '[{
    "Notification": {
      "NotificationType": "ACTUAL",
      "ComparisonOperator": "GREATER_THAN",
      "Threshold": 80
    },
    "Subscribers": [{
      "SubscriptionType": "EMAIL",
      "Address": "your@email.com"
    }]
  }]'
```

---

## Cost Comparison

### Before Optimization

| Service | Config | Monthly |
|---------|--------|---------|
| SageMaker | Always on | $300 |
| App Runner | 4 vCPU, 8GB | $150 |
| ECR | No cleanup | $20 |
| **Total** | | **$470** |

### After Optimization

| Service | Config | Monthly |
|---------|--------|---------|
| SageMaker | Scale-to-zero | $50-100 |
| App Runner | 2 vCPU, 4GB | $50 |
| ECR | Lifecycle policy | $2 |
| **Total** | | **$102-152** |

**Savings**: ~$320/month (68% reduction)

---

## Traffic-Based Cost Estimates

### Low Traffic (<100 queries/day)

| Service | Est. Cost |
|---------|-----------|
| SageMaker | $20-30 |
| App Runner | $30 |
| Other | $5 |
| **Total** | **$55-65** |

### Medium Traffic (100-1000 queries/day)

| Service | Est. Cost |
|---------|-----------|
| SageMaker | $80-120 |
| App Runner | $60 |
| Other | $5 |
| **Total** | **$145-185** |

### High Traffic (1000+ queries/day)

| Service | Est. Cost |
|---------|-----------|
| SageMaker | $200-300 |
| App Runner | $100 |
| Other | $10 |
| **Total** | **$310-410** |

---

## Recommendations

### For Development

1. Use smallest instance sizes
2. Enable scale-to-zero
3. Use free tier services
4. Delete unused resources

### For Production

1. Right-size based on actual traffic
2. Set up autoscaling
3. Configure lifecycle policies
4. Enable budget alerts
5. Review costs monthly

---

## Next Steps

- [AWS Setup](aws-setup.md) - Infrastructure configuration
- [Infrastructure](../architecture/infrastructure.md) - Architecture details
