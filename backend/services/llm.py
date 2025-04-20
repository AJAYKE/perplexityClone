from abc import ABC, abstractmethod

from google import genai

from backend.config import OpenAIConfig


class LLMService:
    def __init__(self):
        """
        Initialize the LLMService with the OpenAI API key.
        """
        self.config = OpenAIConfig()
        self.api_key = self.config.GOOGLE_API_KEY
        self.model = self.config.MODEL
        if not self.api_key:
            raise ValueError("API_KEY must be set")

    def stream_answer(self, question: str, contexts: list[tuple[str, str]]):
        model = Gemini(model_name=self.model, api_key=self.api_key)

        prompt_lines = [f"question: {question}", "sources:"]
        for snippet, url in contexts:
            prompt_lines.append(f"  - source: {url}, content: {snippet}")
        prompt_lines.append(self.config.PROMPT)
        prompt = "\n".join(prompt_lines)

        return model.generate_response(self.config, prompt)


class LlmModel(ABC):
    def __init__(self, model_name: str, api_key: str):
        self.model_name = model_name
        self.api_key = api_key

        self.client = self._initialize_client()

    @abstractmethod
    def _initialize_client(self):
        pass

    def generate_response(self, prompt: str):
        """
        Generate a response from the LLM based on the provided prompt.
        """
        raise NotImplementedError("Subclasses should implement this method.")


class Gemini(LlmModel):
    def _initialize_client(self):
        """
        Initialize the Gemini client.
        """
        return genai.Client(api_key=self.api_key)

    def generate_response(self, config, prompt: str):
        """
        Generate a response from the Gemini LLM based on the provided prompt.
        """
        for chunk in self.client.models.generate_content_stream(
            model=config.MODEL, contents=prompt
        ):
            yield chunk.text


if __name__ == "__main__":
    model = LLMService()
    response = model.stream_answer(
        "What is the capital of France?",
        [("Paris is the capital of France.", "https://example.com")],
    )
    for chunk in response:
        print(chunk, end="")
