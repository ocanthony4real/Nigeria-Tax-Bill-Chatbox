from zenml import pipeline

from steps import evaluating as evaluating_steps


@pipeline
def evaluating(is_dummy: bool = True) -> None:
    """
    ZenML pipeline to evaluate fine-tuned LLM models.

    This pipeline runs evaluation on AWS SageMaker to:
    1. Generate answers from the fine-tuned models using vLLM
    2. Compare against baseline (meta-llama/Llama-3.1-8B-Instruct)
    3. Score accuracy and style using Claude
    4. Upload results to HuggingFace Hub

    Args:
        is_dummy: If True, only evaluates 10 samples for testing.
                  Set to False for full evaluation.
    """
    evaluating_steps.evaluate(is_dummy=is_dummy)
