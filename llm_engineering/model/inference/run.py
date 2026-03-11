from __future__ import annotations

from loguru import logger

from llm_engineering.domain.inference import Inference
from llm_engineering.settings import settings
from llm_engineering.application.utils.misc import compute_num_tokens


# Default prompt for general content creation (Llama 3.1 chat format)
DEFAULT_PROMPT = """<|begin_of_text|><|start_header_id|>system<|end_header_id|}

You are a helpful assistant. Use the provided context to answer the user's question.<|eot_id|><|start_header_id|>user<|end_header_id|>

Context: {context}

Question: {query}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""

# Specialized prompt for Nigeria Tax Bill queries (Alpaca format - matches RAG fine-tuning)
TAX_BILL_PROMPT = """Below is an instruction that describes a task. Write a response that appropriately completes the request.

### Instruction:
Based on the following excerpt from the Nigeria Tax Act 2025, answer the question.

Context:
{context}

Question: {query}

### Response:
"""


class InferenceExecutor:
    # Reserve tokens for output and safety buffer
    OUTPUT_BUFFER = 100  # Safety margin for special tokens, formatting, etc.

    def __init__(
        self,
        llm: Inference,
        query: str,
        context: str | None = None,
        prompt: str | None = None,
    ) -> None:
        self.llm = llm
        self.query = query
        self.context = context if context else ""

        if prompt is None:
            self.prompt = DEFAULT_PROMPT
        else:
            self.prompt = prompt

    def _truncate_context_smart(self, context: str, max_context_tokens: int) -> str:
        """
        Smart truncation: Keep complete chunks that fit within the token budget.
        Chunks are assumed to be separated by 'Chunk N:' markers.
        """
        if not context:
            return context

        # Split context into chunks (they start with "\nChunk N:")
        import re
        chunk_pattern = r'(\nChunk \d+:)'
        parts = re.split(chunk_pattern, context)

        # Reconstruct chunks (pattern splits into [prefix, marker1, content1, marker2, content2, ...])
        chunks = []
        i = 0
        while i < len(parts):
            if re.match(r'\nChunk \d+:', parts[i] if parts[i] else ''):
                # This is a chunk marker, combine with its content
                if i + 1 < len(parts):
                    chunks.append(parts[i] + parts[i + 1])
                    i += 2
                else:
                    chunks.append(parts[i])
                    i += 1
            else:
                # Skip non-chunk content (like leading whitespace)
                i += 1

        if not chunks:
            # No chunk markers found, do simple truncation
            context_tokens = compute_num_tokens(context)
            if context_tokens <= max_context_tokens:
                return context
            # Simple truncation by ratio
            ratio = max_context_tokens / context_tokens
            truncated_len = int(len(context) * ratio * 0.9)  # 90% to be safe
            return context[:truncated_len] + "\n[Context truncated due to length...]"

        # Add chunks one by one until we hit the budget
        truncated_context = ""
        total_tokens = 0
        chunks_added = 0

        for chunk in chunks:
            chunk_tokens = compute_num_tokens(chunk)
            if total_tokens + chunk_tokens <= max_context_tokens:
                truncated_context += chunk
                total_tokens += chunk_tokens
                chunks_added += 1
            else:
                # Can't fit this chunk, stop here
                break

        if chunks_added < len(chunks):
            logger.info(
                f"Smart truncation: Kept {chunks_added}/{len(chunks)} chunks "
                f"({total_tokens} tokens, budget: {max_context_tokens})"
            )

        return truncated_context

    def _get_truncated_context(self) -> str:
        """
        Calculate available token budget for context and truncate if necessary.
        """
        # Calculate tokens used by prompt template (without context and query placeholders)
        prompt_template_tokens = compute_num_tokens(
            self.prompt.replace("{context}", "").replace("{query}", "")
        )
        query_tokens = compute_num_tokens(self.query)

        # Calculate available tokens for context
        # MAX_INPUT_LENGTH is for input only (prompt + context + query)
        # Output tokens (max_new_tokens) are separate
        available_for_context = (
            settings.MAX_INPUT_LENGTH
            - prompt_template_tokens
            - query_tokens
            - self.OUTPUT_BUFFER
        )

        # Ensure we have at least some room for context
        available_for_context = max(available_for_context, 200)

        context_tokens = compute_num_tokens(self.context)

        if context_tokens <= available_for_context:
            logger.debug(
                f"Context fits within budget: {context_tokens}/{available_for_context} tokens"
            )
            return self.context

        logger.warning(
            f"Context exceeds budget ({context_tokens} > {available_for_context} tokens). "
            "Applying smart truncation..."
        )

        return self._truncate_context_smart(self.context, available_for_context)

    def execute(self) -> str:
        # Apply smart truncation to context
        truncated_context = self._get_truncated_context()

        self.llm.set_payload(
            inputs=self.prompt.format(query=self.query, context=truncated_context),
            parameters={
                "max_new_tokens": settings.MAX_NEW_TOKENS_INFERENCE,
                "repetition_penalty": 1.1,
                "temperature": settings.TEMPERATURE_INFERENCE,
                "top_p": settings.TOP_P_INFERENCE,
                "do_sample": True,
            },
        )
        answer = self.llm.inference()[0]["generated_text"]

        return answer
