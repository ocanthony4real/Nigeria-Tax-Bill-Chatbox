from zenml import pipeline

# Import steps directly instead of pipelines
from steps.etl.extracts_pdf import extract_pdfs
from steps.etl.annotate_structure import annotate_document_structure
from steps import feature_engineering as fe_steps
from steps import generate_datasets as gd_steps
from steps import training as training_steps
from steps import evaluating as eval_steps
from llm_engineering.domain.dataset import DatasetType


@pipeline
def end_to_end(
    # PDF ETL parameters
    pdf_dir: str = "data/Nigeria Tax PDFs",
    pdf_names: list[str] = ["Nigeria_Tax_Act_2025"],
    # Generate datasets parameters
    test_split_size: float = 0.1,
    push_to_huggingface: bool = True,
    dataset_id: str = "Nigeria_tax_law_instruct_datasets",
    mock: bool = False,
    # Training parameters
    finetuning_type: str = "sft",
    num_train_epochs: int = 3,
    per_device_train_batch_size: int = 2,
    learning_rate: float = 3e-4,
    dataset_huggingface_workspace: str = "ocanthony4real",
    is_dummy: bool = True,
    # Evaluation parameters
    eval_is_dummy: bool = True,
) -> None:
    """
    End-to-end ZenML pipeline for the Nigeria Tax Bill Chatbot.

    This pipeline runs all steps in sequence:
    1. PDF ETL - Extract and annotate Nigerian law PDFs
    2. Feature Engineering - Clean, chunk, and embed documents
    3. Generate Datasets - Create instruct datasets for fine-tuning
    4. Training - Fine-tune LLM on SageMaker
    5. Evaluation - Evaluate fine-tuned model on SageMaker
    """
    # Step 1: PDF ETL
    extracted_docs = extract_pdfs(pdf_dir=pdf_dir)
    annotated_docs = annotate_document_structure(extracted_docs)

    # Step 2: Feature Engineering
    raw_documents = fe_steps.query_data_warehouse(pdf_names, after=[annotated_docs.invocation_id])
    cleaned_documents = fe_steps.clean_documents(raw_documents)
    fe_step_1 = fe_steps.load_to_vector_db(cleaned_documents)
    embedded_documents = fe_steps.chunk_and_embed(cleaned_documents)
    fe_step_2 = fe_steps.load_to_vector_db(embedded_documents)

    # Step 3: Generate Instruct Datasets
    cleaned_docs_for_dataset = gd_steps.query_feature_store(
        after=[fe_step_1.invocation_id, fe_step_2.invocation_id]
    )
    prompts = gd_steps.create_prompts(
        documents=cleaned_docs_for_dataset,
        dataset_type=DatasetType.INSTRUCTION
    )
    dataset = gd_steps.generate_intruction_dataset(
        prompts=prompts,
        test_split_size=test_split_size,
        mock=mock
    )
    pushed_dataset_id = gd_steps.push_to_huggingface(
        dataset=dataset,
        dataset_id=dataset_id,
    )

    # Step 4: Training (waits for dataset to be pushed)
    training_status = training_steps.train(
        finetuning_type=finetuning_type,
        num_train_epochs=num_train_epochs,
        per_device_train_batch_size=per_device_train_batch_size,
        learning_rate=learning_rate,
        dataset_huggingface_workspace=dataset_huggingface_workspace,
        is_dummy=is_dummy,
        wait_for_dataset=pushed_dataset_id,
    )

    # Step 5: Evaluation (waits for training to complete)
    eval_steps.evaluate(
        is_dummy=eval_is_dummy,
        wait_for_training=training_status,
    )
