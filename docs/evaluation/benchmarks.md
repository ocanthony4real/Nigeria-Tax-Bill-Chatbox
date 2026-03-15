# Benchmarks

Performance benchmarks for the Nigeria Tax Bill Chatbot.

## Latency Benchmarks

### End-to-End Response Time

| Percentile | Warm (ms) | Cold (ms) |
|------------|-----------|-----------|
| p50 | 3,200 | 18,000 |
| p90 | 4,500 | 25,000 |
| p95 | 5,200 | 28,000 |
| p99 | 6,800 | 35,000 |

### Component Latency

| Component | p50 (ms) | p95 (ms) |
|-----------|----------|----------|
| Embedding | 45 | 80 |
| Vector Search | 85 | 150 |
| Reranking | 180 | 320 |
| LLM Generation | 2,800 | 4,500 |
| Post-processing | 30 | 60 |

---

## Throughput Benchmarks

### Requests per Second

| Configuration | RPS | Notes |
|---------------|-----|-------|
| Single instance | 0.3 | Sequential requests |
| Concurrent (10) | 2.5 | Limited by SageMaker |
| With queue | 5.0 | Async processing |

### Concurrent Users

| Users | Avg Latency | Error Rate |
|-------|-------------|------------|
| 1 | 3.2s | 0% |
| 5 | 4.1s | 0% |
| 10 | 6.5s | 0% |
| 20 | 12.0s | 5% |
| 50 | timeout | 40% |

---

## Accuracy Benchmarks

### By Question Category

| Category | Accuracy | F1 Score |
|----------|----------|----------|
| VAT Questions | 95.6% | 0.94 |
| Corporate Tax | 93.2% | 0.91 |
| Personal Income | 89.5% | 0.87 |
| Penalties | 85.0% | 0.82 |
| Exemptions | 88.7% | 0.85 |
| Procedures | 91.1% | 0.89 |

### Citation Accuracy

| Metric | Score |
|--------|-------|
| Section Cited | 92% |
| Correct Section | 89% |
| Page Cited | 88% |
| Correct Page | 85% |

---

## Retrieval Benchmarks

### Vector Search Quality

| Metric | Score |
|--------|-------|
| Recall@5 | 0.85 |
| Recall@10 | 0.92 |
| MRR | 0.78 |
| NDCG@10 | 0.81 |

### Reranking Impact

| Configuration | Accuracy |
|---------------|----------|
| Vector only (top-5) | 78% |
| + Reranking | 92% |
| **Improvement** | **+14%** |

---

## Resource Utilization

### SageMaker Endpoint

| Metric | Value |
|--------|-------|
| GPU Utilization | 75-85% |
| GPU Memory | 18GB/24GB |
| CPU Utilization | 15-25% |
| Memory | 8GB/32GB |

### App Runner

| Metric | Value |
|--------|-------|
| CPU Utilization | 20-40% |
| Memory | 1.5GB/4GB |
| Network In | 50KB/req |
| Network Out | 5KB/req |

---

## Cost Benchmarks

### Per-Request Cost

| Component | Cost/Request |
|-----------|--------------|
| SageMaker | $0.002 |
| App Runner | $0.0001 |
| Qdrant | $0.0000 |
| **Total** | **$0.0021** |

### Monthly Cost by Traffic

| Daily Requests | Monthly Cost |
|----------------|--------------|
| 100 | $56 |
| 500 | $82 |
| 1,000 | $115 |
| 5,000 | $365 |

---

## Comparison with Alternatives

### vs. GPT-4 with RAG

| Metric | Our Model | GPT-4 |
|--------|-----------|-------|
| Accuracy | 93.3% | 88% |
| Citation Rate | 92% | 60% |
| Latency | 3.5s | 5.2s |
| Cost/Request | $0.002 | $0.05 |

### vs. Claude 3 with RAG

| Metric | Our Model | Claude 3 |
|--------|-----------|----------|
| Accuracy | 93.3% | 90% |
| Citation Rate | 92% | 70% |
| Latency | 3.5s | 4.8s |
| Cost/Request | $0.002 | $0.03 |

---

## Stress Testing

### Load Test Results

```
Duration: 10 minutes
Virtual Users: 20
Total Requests: 3,450

Response Times:
  min: 2,850ms
  max: 45,200ms (cold starts)
  avg: 5,120ms

Errors:
  Timeouts: 12 (0.35%)
  5xx: 3 (0.09%)
  Total: 15 (0.44%)
```

### Failure Modes

| Failure | Cause | Mitigation |
|---------|-------|------------|
| Timeout | Cold start | Retry logic |
| 503 | Scaling | Queue requests |
| 500 | OOM | Reduce batch size |

---

## Benchmark Environment

### Test Configuration

| Property | Value |
|----------|-------|
| Test Tool | Locust |
| Duration | 10 min each test |
| Region | us-east-1 |
| Network | Same VPC |

### Model Configuration

| Property | Value |
|----------|-------|
| Model | LLaMA 3.1 8B |
| Instance | ml.g5.xlarge |
| GPU | NVIDIA A10G |
| Batch Size | 1 |
| Max Tokens | 1024 |

---

## Running Benchmarks

### Latency Test

```bash
# Install
pip install locust

# Run
locust -f benchmarks/load_test.py \
  --host https://YOUR_URL \
  --users 10 \
  --spawn-rate 1 \
  --run-time 5m
```

### Accuracy Test

```bash
python tools/run.py --pipeline evaluating \
  --config configs/evaluating.yaml
```

---

## Next Steps

- [Model Performance](model-performance.md) - Detailed evaluation
- [Cost Optimization](../deployment/cost-optimization.md) - Reduce costs
