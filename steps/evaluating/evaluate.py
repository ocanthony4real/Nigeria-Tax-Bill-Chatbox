from zenml import step

from llm_engineering.model.evaluation.sagemaker import run_evaluation_on_sagemaker


@step
def evaluate(is_dummy: bool = True) -> None:
    """
    ZenML step to run model evaluation on AWS SageMaker.

    This step:
    1. Generates answers from fine-tuned models using vLLM
    2. Evaluates answers using GPT-4o-mini for accuracy and style
    3. Uploads results to HuggingFace Hub

    Args:
        is_dummy: If True, only evaluates 10 samples for testing.
                  Set to False for full evaluation.
    """
    run_evaluation_on_sagemaker(is_dummy=is_dummy)
