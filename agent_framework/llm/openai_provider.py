from typing import Any, Dict, List, Optional, AsyncGenerator, Type, TypeVar
from openai import AsyncOpenAI
from pydantic import BaseModel
import os
import time
from dotenv import load_dotenv

from .base import LLMProvider
from .models import LLMMessage, LLMResponse, LLMConfig

T = TypeVar("T", bound=BaseModel)


class OpenAIProvider(LLMProvider):
    """OpenAI implementation of LLM provider"""

    def __init__(self, config: LLMConfig, organization: Optional[str] = None):
        super().__init__(config)

        # Load environment variables
        load_dotenv()

        # Use provided API key or load from environment
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key must be provided or set in OPENAI_API_KEY environment variable"
            )

        self.client = AsyncOpenAI(api_key=self.api_key)

    def _prepare_messages(self, messages: List[LLMMessage]) -> List[Dict[str, Any]]:
        """Convert internal message format to OpenAI format"""
        return [
            {
                "role": msg.role,
                "content": msg.content,
                **({"name": msg.name} if msg.name else {}),
            }
            for msg in messages
        ]

    def _prepare_config(self, config: Optional[LLMConfig] = None) -> Dict[str, Any]:
        """Prepare configuration for OpenAI API"""
        cfg = config or self.config
        return {
            "model": cfg.model,
            "temperature": cfg.temperature,
            "max_tokens": cfg.max_tokens,
            "top_p": cfg.top_p,
            "frequency_penalty": cfg.frequency_penalty,
            "presence_penalty": cfg.presence_penalty,
            "stop": cfg.stop,
            **cfg.custom_settings,
        }

    async def generate(
        self,
        messages: List[LLMMessage],
        config: Optional[LLMConfig] = None,
        logger=None,
    ) -> LLMResponse:
        """Generate a response using OpenAI with optional Galileo logging"""
        openai_messages = self._prepare_messages(messages)
        api_config = self._prepare_config(config)

        # Get the input text for logging
        input_text = "\n".join([f"{msg.role}: {msg.content}" for msg in messages])

        # Time the LLM call
        start_ns = time.perf_counter_ns()

        try:
            response = await self.client.chat.completions.create(
                messages=openai_messages, **api_config
            )

            # Calculate duration
            duration_ns = time.perf_counter_ns() - start_ns

            choice = response.choices[0]
            output_text = choice.message.content or ""

            # Log to Galileo if logger is provided
            if logger and hasattr(logger, "add_llm_span"):
                logger.add_llm_span(
                    input_text=input_text,
                    output_text=output_text,
                    model=api_config.get("model", "unknown"),
                    name=f"OpenAI {api_config.get('model', 'unknown')} completion",
                    num_input_tokens=(
                        response.usage.prompt_tokens if response.usage else None
                    ),
                    num_output_tokens=(
                        response.usage.completion_tokens if response.usage else None
                    ),
                    total_tokens=(
                        response.usage.total_tokens if response.usage else None
                    ),
                    duration_ns=duration_ns,
                )

            return LLMResponse(
                content=output_text,
                raw_response=response.model_dump(),
                finish_reason=choice.finish_reason,
                usage=response.usage.model_dump() if response.usage else None,
            )

        except Exception as e:
            # Calculate duration even on error
            duration_ns = time.perf_counter_ns() - start_ns

            # Log error to Galileo if logger is provided
            if logger and hasattr(logger, "add_llm_span"):
                logger.add_llm_span(
                    input_text=input_text,
                    output_text=f"Error: {str(e)}",
                    model=api_config.get("model", "unknown"),
                    name=f"OpenAI {api_config.get('model', 'unknown')} error",
                    duration_ns=duration_ns,
                )

            raise

    async def generate_stream(
        self, messages: List[LLMMessage], config: Optional[LLMConfig] = None
    ) -> AsyncGenerator[LLMResponse, None]:
        """Generate a streaming response using OpenAI"""
        openai_messages = self._prepare_messages(messages)
        api_config = self._prepare_config(config)

        stream = await self.client.chat.completions.create(
            messages=openai_messages, stream=True, **api_config
        )

        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield LLMResponse(
                    content=chunk.choices[0].delta.content,
                    raw_response=chunk.model_dump(),
                    finish_reason=chunk.choices[0].finish_reason,
                )

    async def generate_structured(
        self,
        messages: List[LLMMessage],
        output_model: Type[T],
        config: Optional[LLMConfig] = None,
        logger=None,
    ) -> T:
        """Generate a response with structured output using function calling"""
        openai_messages = self._prepare_messages(messages)
        api_config = self._prepare_config(config)

        # Get the input text for logging
        input_text = "\n".join([f"{msg.role}: {msg.content}" for msg in messages])

        # Time the LLM call
        start_ns = time.perf_counter_ns()

        # Create function definition from Pydantic model
        schema = output_model.model_json_schema()
        function_def = {
            "name": "output_structured_data",
            "description": f"Output data in {output_model.__name__} format",
            "parameters": schema,
        }

        try:
            response = await self.client.chat.completions.create(
                messages=openai_messages,
                functions=[function_def],
                function_call={"name": "output_structured_data"},
                **api_config,
            )

            # Calculate duration
            duration_ns = time.perf_counter_ns() - start_ns

            try:
                function_args = response.choices[0].message.function_call.arguments
                result = output_model.model_validate_json(function_args)

                # Log to Galileo if logger is provided
                if logger and hasattr(logger, "add_llm_span"):
                    logger.add_llm_span(
                        input_text=input_text,
                        output_text=function_args,
                        model=api_config.get("model", "unknown"),
                        name=f"OpenAI {api_config.get('model', 'unknown')} structured completion",
                        num_input_tokens=(
                            response.usage.prompt_tokens if response.usage else None
                        ),
                        num_output_tokens=(
                            response.usage.completion_tokens if response.usage else None
                        ),
                        total_tokens=(
                            response.usage.total_tokens if response.usage else None
                        ),
                        duration_ns=duration_ns,
                    )

                return result

            except Exception as e:
                # Log parsing error to Galileo if logger is provided
                if logger and hasattr(logger, "add_llm_span"):
                    logger.add_llm_span(
                        input_text=input_text,
                        output_text=f"Parsing Error: {str(e)}",
                        model=api_config.get("model", "unknown"),
                        name=f"OpenAI {api_config.get('model', 'unknown')} parsing error",
                        duration_ns=duration_ns,
                    )

                raise ValueError(f"Failed to parse structured output: {e}")

        except Exception as e:
            # Calculate duration even on error
            duration_ns = time.perf_counter_ns() - start_ns

            # Log error to Galileo if logger is provided
            if logger and hasattr(logger, "add_llm_span"):
                logger.add_llm_span(
                    input_text=input_text,
                    output_text=f"Error: {str(e)}",
                    model=api_config.get("model", "unknown"),
                    name=f"OpenAI {api_config.get('model', 'unknown')} error",
                    duration_ns=duration_ns,
                )

            raise
