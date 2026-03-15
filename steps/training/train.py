"""
Model training step for the training pipeline.

Launches fine-tuning jobs on AWS SageMaker with configurable
hyperparameters and training methods (SFT/DPO).
"""

from zenml import step

from llm_engineering.model.finetuning.sagemaker import run_finetuning_on_sagemaker


@step
def train(
    finetuning_type: str,
    num_train_epochs: int,
    per_device_train_batch_size: int,
    learning_rate: float,
    dataset_huggingface_workspace: str = "ocanthony4real",
    is_dummy: bool = False,
) -> None:
    run_finetuning_on_sagemaker(
        finetuning_type=finetuning_type,
        num_train_epochs=num_train_epochs,
        per_device_train_batch_size=per_device_train_batch_size,
        learning_rate=learning_rate,
        dataset_huggingface_workspace=dataset_huggingface_workspace,
        is_dummy=is_dummy,
    )
