import logging
import os
from pathlib import Path
from typing import Any, List, Callable, Coroutine, Union

import openai
from dtb.settings import OPENAI_TOKEN


class LLMHelper:
    logger = logging.getLogger(__name__)

    def __init__(self, model="gpt-4-1106-preview"):
        self.client = openai.AsyncOpenAI(api_key=OPENAI_TOKEN)
        self.model = model

    async def chat_complete(
        self,
        messages: List[Any],
        message_callback: Callable[[str], Coroutine[Any, Any, None]] = None,
    ) -> str:
        self.logger.info(f"Chat complete with messages: {messages}")
        # Create a stream from OpenAI API
        stream = await self.client.chat.completions.create(
            messages=messages, model=self.model, stream=True
        )
        # Iterate over the stream and append the deltas to the result
        res = ""
        async for item in stream:
            self.logger.debug(item)
            delta = item.choices[0].delta.content

            # if delta is None, this is the last message
            if delta is None:
                break

            res += delta

            # update the message callback
            if message_callback is not None:
                await message_callback(res)

        self.logger.debug(f"Chat complete response: {res}")
        return res

    comparison_system_prompt = (
        "Your task is to assess the semantic similarity between the player's verdict and "
        "author's verdict. If the player's verdict is correct, answer '1'. If not, "
        "answer '0'. The texts are separated by '###'."
    ).strip()

    async def is_solved(self, player_answer: str, ground_truth: str) -> bool:
        text = f"{player_answer}###{ground_truth}"
        chat_completion = await self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": self.comparison_system_prompt},
                {"role": "user", "content": text},
            ],
            model=self.model,
        )
        res = chat_completion.choices[0].message.content.strip()
        return res == "1"

    async def transcribe_audio_file(self, path: Union[Path, str]) -> str:
        """Transcribe an audio file using OpenAI API and return the text"""
        with open(path, "rb") as f:
            transcript = await self.client.audio.transcriptions.create(
                model="whisper-1", file=f, response_format="text"
            )
        self.logger.debug(f"Transcription from {path}: {transcript}")
        return transcript.strip()
