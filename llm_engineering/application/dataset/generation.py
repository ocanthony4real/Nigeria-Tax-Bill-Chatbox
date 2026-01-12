from abc import ABC, abstractmethod

#from transformers import AutoTokenizer
from langchain_core.exceptions import OutputParserException
from langchain_core.language_models.fake import FakeListLLM
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.prompts import PromptTemplate
from langchain.output_parsers import OutputFixingParser
from langchain_ollama import ChatOllama

from loguru import logger

from llm_engineering import domain
from llm_engineering.application import utils
from llm_engineering.domain.cleaned_documents import CleanedDocument
from llm_engineering.domain.dataset import DatasetType, TrainTestSplit
from llm_engineering.domain.prompt import GenerateDatasetSamplesPrompt, Prompt
from llm_engineering.domain.types import DataCategory
from llm_engineering.settings import settings

from . import constants
from . import utils as generation_utils
from .output_parsers import ListPydanticOutputParser


class DatasetGenerator(ABC):
    dataset_type: DatasetType | None = None

    system_prompt_template = """You are a helpful assistant who generates {dataset_format} based on the given context. \
Provide your response in JSON format.
"""

    prompt_template_str: str | None = None

    @classmethod
    def get_system_prompt(cls) -> Prompt:
        assert cls.dataset_type is not None, "Dataset type must be set before calling get_system_prompt()"

        dataset_format = (
            "instruction-answer pairs"
            if cls.dataset_type == DatasetType.INSTRUCTION
            else "instruction-answer triples"
        )

        system_prompt = cls.system_prompt_template.format(dataset_format=dataset_format)

        return Prompt(
            template=cls.system_prompt_template,
            input_variables={"dataset_format": dataset_format},
            content=system_prompt,
        )

    @classmethod
    def get_prompts(
        cls, documents: list[CleanedDocument]
    ) -> dict[DataCategory, list[GenerateDatasetSamplesPrompt]]:
        documents = generation_utils.extract_substrings(documents)

        grouped_prompts: dict[DataCategory, list[GenerateDatasetSamplesPrompt]] = {}
        grouped_cleaned_documents = CleanedDocument.group_by_category(documents)

        for category, category_documents in grouped_cleaned_documents.items():
            grouped_prompts[category] = [cls.get_prompt(doc) for doc in category_documents]

        return grouped_prompts

    @classmethod
    def get_prompt(cls, document: CleanedDocument) -> GenerateDatasetSamplesPrompt:
        assert cls.prompt_template_str is not None, "Prompt template must be set before calling get_prompt()"

        prompt_template = PromptTemplate.from_template(
            template=cls.prompt_template_str,
            template_format="jinja2",
        )

        prompt = prompt_template.format(extract=document.content)

        words = prompt.split()
        max_tokens = getattr(settings, "OLLAMA_MAX_TOKEN_WINDOW", 2048)

        if len(words) > max_tokens:
            prompt = " ".join(words[:max_tokens])
            prompt_tokens = max_tokens
        else:
            prompt_tokens = len(words)

        return GenerateDatasetSamplesPrompt(
            template=prompt_template.template,
            input_variables={"extract": document.content},
            content=prompt,
            num_tokens=prompt_tokens,
            data_category=document.get_category(),
            document=document,
        )

    @classmethod
    def generate(
        cls,
        prompts: dict[DataCategory, list[GenerateDatasetSamplesPrompt]],
        test_size: float = 0.2,
        mock: bool = False,
    ) -> TrainTestSplit:
        assert cls.dataset_type is not None, "Dataset type must be set before calling generate()"

        def _to_langchain(prompt: GenerateDatasetSamplesPrompt) -> list[BaseMessage]:
            return [
                SystemMessage(content=cls.get_system_prompt().content),
                HumanMessage(content=prompt.content),
            ]

        llm_instance = (
            FakeListLLM(responses=[constants.get_mocked_response(cls.dataset_type)])
            if mock
            else ChatOllama(
                model=settings.OLLAMA_MODEL,
                temperature=0.7,
                num_predict=2000 if cls.dataset_type == DatasetType.PREFERENCE else 1200,
            )
        )

        sample_type = cls._get_dataset_sample_type()

        base_parser = ListPydanticOutputParser(pydantic_object=sample_type)
        parser = OutputFixingParser.from_llm(parser=base_parser, llm=llm_instance)

        chain = llm_instance | parser

        datasets = {}

        for category, category_prompts in prompts.items():
            langchain_prompts = [_to_langchain(p) for p in category_prompts]
            batches = utils.misc.batch(langchain_prompts, size=24)

            flattened_samples: list = []

            for batch in batches:
                try:
                    parsed_batches = chain.batch(batch, stop=None)

                    for parsed in parsed_batches:
                        if isinstance(parsed, list):
                            for item in parsed:
                                flattened_samples.append(
                                    item if isinstance(item, sample_type)
                                    else sample_type.model_validate(item)
                                )
                        else:
                            flattened_samples.append(
                                parsed if isinstance(parsed, sample_type)
                                else sample_type.model_validate(parsed)
                            )

                except OutputParserException:
                    logger.exception(f"Failed to parse JSON output for category {category}")

            assert all(
                isinstance(s, sample_type) for s in flattened_samples
            ), "Invalid dataset samples detected before dataset construction"

            dataset = domain.dataset.build_dataset(
                dataset_type=cls.dataset_type,
                category=category,
                samples=flattened_samples,
            )

            datasets[category] = dataset
            logger.info(f"Generated {len(dataset.samples)} samples for category '{category}'.")

        return cls.post_process_datasets(datasets, test_size=test_size)

    @classmethod
    def _get_dataset_sample_type(
        cls,
    ) -> type[
        domain.dataset.InstructDatasetSample
        | domain.dataset.PreferenceDatasetSample
    ]:
        return (
            domain.dataset.InstructDatasetSample
            if cls.dataset_type == DatasetType.INSTRUCTION
            else domain.dataset.PreferenceDatasetSample
        )

    @classmethod
    @abstractmethod
    def post_process_datasets(
        cls,
        datasets: dict[DataCategory, domain.dataset.InstructDataset],
        test_size: float,
    ) -> TrainTestSplit:
        pass


class InstructionDatasetGenerator(DatasetGenerator):
    dataset_type = DatasetType.INSTRUCTION

    prompt_template_str = """Based on the following extract, generate five instruction-answer pairs. Each instruction \
must ask to write about a specific topic contained in the context. Each answer \
must provide a relevant paragraph based on the information found in the \
context. Only use concepts from the context to generate the instructions. \
Instructions must never explicitly mention a context, a system, a course, or an extract. \
Instructions must be self-contained and general. \
Answers must imitate the writing style of the context. \
    
Example instruction: Explain the concept of tax. \
Example answer: Tax is a compulsory contribution to state revenue, \
levied by the government on workers' income  \
and business profits, or added to the cost of some goods, services, and transactions. \

Structure the answer in JSON format, ready to be loaded in Python by json.loads(), as a list of objects.
Do not add any extra characters and provide your response in JSON format with the following structure:
[
    {"instruction": "...", "answer": "..."},
    ...
]

Extract:
{{extract}}
"""

    @classmethod
    def post_process_datasets(
        cls,
        datasets: dict[DataCategory, domain.dataset.InstructDataset],
        test_size: float,
    ) -> TrainTestSplit:
        return generation_utils.create_instruct_train_test_split(
            datasets, test_size=test_size, random_state=42
        )


class PreferenceDatasetGenerator(DatasetGenerator):
    dataset_type = DatasetType.PREFERENCE

    prompt_template_str = """Based on the following extract, generate five instruction-answer triples. Each triple should consist of:
1. An instruction asking about a specific topic in the context.
2. A generated answer that attempts to answer the instruction based on the context, named as 'rejected'.
3. An extracted answer that is a relevant excerpt directly from the given context, named as 'chosen'.

Instructions must be self-contained and general, without explicitly mentioning a context, system, course, or extract.

Important:
- Ensure that the extracted answer, the chosen one, is a verbatim copy from the context, including all punctuation and apostrophes.
- Do not add any ellipsis (...) or [...] to indicate skipped text in the extracted answer.
- If the relevant text is not continuous, use two separate sentences from the context instead of skipping text.

Structure the answer in JSON format, ready to be loaded in Python by json.loads(), as a list of objects.
Do not add any extra characters and provide your response in JSON format with the following structure:
[
    {
        "instruction": "...",
        "rejected": "...",
        "chosen": "..."
    },
    ...
]

Extract:
{{extract}}
"""

    @classmethod
    def post_process_datasets(
        cls,
        datasets: dict[DataCategory, domain.dataset.PreferenceDataset],
        test_size: float,
    ) -> TrainTestSplit:
        datasets = generation_utils.filter_short_answers(datasets)
        datasets = generation_utils.filter_answer_format(datasets)

        remaining_samples = sum(d.num_samples for d in datasets.values())
        logger.info(
            f"Filtered out short answers and answers with incorrect format. Remaining samples: {remaining_samples}"
        )

        return generation_utils.create_preference_train_test_split(
            datasets, test_size=test_size, random_state=42
        )


def get_dataset_generator(dataset_type: DatasetType) -> type[DatasetGenerator]:
    if dataset_type == DatasetType.INSTRUCTION:
        return InstructionDatasetGenerator
    elif dataset_type == DatasetType.PREFERENCE:
        return PreferenceDatasetGenerator
    else:
        raise ValueError(f"Invalid dataset type: {dataset_type}")
