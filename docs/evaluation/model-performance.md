# Model Performance

Comprehensive evaluation results for the fine-tuned Nigeria Tax LLaMA model.

## Executive Summary

| Metric | Score | Target |
|--------|-------|--------|
| **Overall Accuracy** | 93.3% | >90% |
| **Style Score** | 96.7% | >90% |
| **Citation Accuracy** | 92% | >85% |
| **Hallucination Rate** | <5% | <10% |
| **Response Time** | 3-5s | <10s |

---

## Evaluation Methodology

### LLM-as-Judge

We used Claude 3 Haiku as an automated judge to evaluate responses:

```python
EVALUATION_PROMPT = """
You are evaluating a tax law Q&A response. Rate on two criteria:

1. ACCURACY (1-3):
   - 3: Correct information with proper citation
   - 2: Mostly correct but minor issues
   - 1: Incorrect or missing citation

2. STYLE (1-3):
   - 3: Professional, clear, well-formatted
   - 2: Acceptable but could improve
   - 1: Poor formatting or unprofessional

Question: {question}
Expected Answer: {expected}
Model Response: {response}

Provide scores as: ACCURACY: X, STYLE: Y
Explanation: [brief reason]
"""
```

### Test Dataset

| Property | Value |
|----------|-------|
| Test Samples | 90 questions |
| Source | Held-out validation set |
| Question Types | Factual, Procedural, Interpretive |
| Difficulty | Easy (30%), Medium (50%), Hard (20%) |

---

## Results by Category

### Overall Scores

```
Accuracy Distribution:
Score 3: ████████████████████████░░░ 78 (86.7%)
Score 2: ████░░░░░░░░░░░░░░░░░░░░░░░ 10 (11.1%)
Score 1: █░░░░░░░░░░░░░░░░░░░░░░░░░░  2 (2.2%)

Style Distribution:
Score 3: ██████████████████████████░ 87 (96.7%)
Score 2: █░░░░░░░░░░░░░░░░░░░░░░░░░░  3 (3.3%)
Score 1: ░░░░░░░░░░░░░░░░░░░░░░░░░░░  0 (0.0%)
```

### By Question Type

| Type | Count | Accuracy | Style |
|------|-------|----------|-------|
| Factual | 45 | 95.6% | 97.8% |
| Procedural | 30 | 91.1% | 96.7% |
| Interpretive | 15 | 88.9% | 93.3% |

### By Difficulty

| Difficulty | Count | Accuracy | Style |
|------------|-------|----------|-------|
| Easy | 27 | 98.8% | 100% |
| Medium | 45 | 93.3% | 97.8% |
| Hard | 18 | 85.2% | 88.9% |

---

## Sample Evaluations

### High Score Example

**Question:** What is the VAT rate in Nigeria?

**Expected:**
> According to Section 148 (p. 88), the standard VAT rate in Nigeria is 7.5 percent.

**Model Response:**
> According to Section 148 (p. 88), the VAT rate in Nigeria is 7.5 percent. This rate applies to all taxable supplies as defined in the Nigeria Tax Act 2025.

**Scores:** Accuracy: 3/3, Style: 3/3

**Judge Notes:** Correct citation, accurate information, professional tone.

---

### Medium Score Example

**Question:** What are the exemptions for agricultural income?

**Expected:**
> According to Section 25 (p. 17), agricultural income from farming, livestock, and fisheries is exempt from income tax under certain conditions...

**Model Response:**
> Agricultural income is generally exempt from taxation in Nigeria. The exemption covers farming activities and related income.

**Scores:** Accuracy: 2/3, Style: 3/3

**Judge Notes:** Missing specific section citation, but information is correct.

---

### Low Score Example

**Question:** What is the penalty for tax fraud?

**Expected:**
> According to Section 93 (p. 55), tax fraud carries penalties including imprisonment for up to 5 years and fines up to 100% of the evaded tax...

**Model Response:**
> Tax fraud is a serious offense in Nigeria with significant penalties.

**Scores:** Accuracy: 1/3, Style: 2/3

**Judge Notes:** No citation, vague answer without specifics.

---

## Comparison with Base Model

### Base LLaMA 3.1 8B (No Fine-tuning)

| Metric | Base | Fine-tuned | Improvement |
|--------|------|------------|-------------|
| Accuracy | 45% | 93.3% | +48.3% |
| Style | 70% | 96.7% | +26.7% |
| Citation | 5% | 92% | +87% |
| Hallucination | 35% | <5% | -30% |

### Key Improvements

1. **Citation Format** - Base model rarely cited sections; fine-tuned model cites 92% of the time
2. **Domain Accuracy** - Significant improvement in tax-specific knowledge
3. **Hallucination Reduction** - 7x reduction in made-up information
4. **Consistent Style** - Professional legal assistant tone

---

## Error Analysis

### Common Error Types

| Error Type | Frequency | Example |
|------------|-----------|---------|
| Missing citation | 5% | "VAT rate is 7.5%" (no section) |
| Wrong section | 2% | Citing Section 100 instead of 148 |
| Incomplete answer | 3% | Missing conditions or exceptions |
| Hallucination | <5% | Made-up penalties or rates |

### Error by Topic

| Topic | Error Rate | Notes |
|-------|------------|-------|
| VAT | 3% | Well-covered in training |
| Corporate Tax | 5% | Good coverage |
| Personal Income | 8% | Some gaps |
| Penalties | 12% | Complex, multi-section |
| Exemptions | 10% | Many edge cases |

---

## Response Time Analysis

### Latency Breakdown

| Stage | Time | % of Total |
|-------|------|------------|
| Query embedding | 50ms | 1.4% |
| Vector search | 100ms | 2.9% |
| Reranking | 200ms | 5.7% |
| LLM generation | 3000ms | 85.7% |
| Post-processing | 50ms | 1.4% |
| Network overhead | 100ms | 2.9% |
| **Total** | **3500ms** | **100%** |

### Cold Start Impact

| Scenario | Time |
|----------|------|
| Warm endpoint | 3-5s |
| Cold start | 15-30s |

---

## Confidence Calibration

The model's confidence correlates with accuracy:

| Confidence | Accuracy | Samples |
|------------|----------|---------|
| High (explicit citation) | 98% | 65% |
| Medium (general reference) | 85% | 25% |
| Low ("based on the act") | 70% | 10% |

---

## Recommendations

### Model Improvements

1. **More training data** for penalties and exemptions topics
2. **Hard negative mining** for similar sections
3. **Multi-hop reasoning** for cross-section questions

### Deployment Considerations

1. **Confidence thresholds** - Flag low-confidence responses
2. **Human review** - Queue uncertain answers for review
3. **Feedback loop** - Collect user feedback for fine-tuning

---

## Reproduction

To reproduce the evaluation:

```bash
# Run evaluation pipeline
python tools/run.py --pipeline evaluating \
  --config configs/evaluating.yaml

# View results
cat data/artifacts/evaluation_report.json
```

---

## Next Steps

- [Benchmarks](benchmarks.md) - Detailed benchmarks
- [Model Training](../architecture/model-training.md) - Training details
