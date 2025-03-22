import os
import asyncio
from azure.ai.inference.aio import ChatCompletionsClient  # Use async version
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential

class AIModelManager:
    _instance = None  # Singleton instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AIModelManager, cls).__new__(cls)
            cls._instance._load_models()
        return cls._instance

    def _load_models(self):
        """Initialize the Azure AI Inference client with GitHub API Key."""
        print("Loading AI models...")

        github_api_key = os.getenv("GITHUB_API_KEY")
        if not github_api_key:
            raise ValueError("GITHUB_API_KEY is not set. Please configure it in your environment variables.")

        # Initialize Azure AI Inference Client (async version)
        self.azure_client = ChatCompletionsClient(
            endpoint="https://models.github.ai/inference",
            credential=AzureKeyCredential(github_api_key),
        )

        print("AI Models loaded successfully!")

    async def chat(self, prompt, model="gpt-4-turbo", temperature=0.8):
        """Generate text using different AI models asynchronously."""
        response = await self.azure_client.complete(
            messages=[
                SystemMessage("You are a helpful AI assistant."),
                UserMessage(prompt),
            ],
            model=model,
            temperature=temperature,
            max_tokens=2048,
        )
        return response.choices[0].message.content

async def main():
    ai_manager = AIModelManager()

    prompts = [
        ("Explain the basics of machine learning.", "gpt-4o"),
        ("Tell me about reinforcement learning.", "DeepSeek-R1"),
        ("Describe neural networks.", "Llama-3.3-70B-Instruct"),
        ("How does a transformer model work?", "Mistral-Large-2411"),
    ]

    # Run multiple AI requests asynchronously
    tasks = [ai_manager.chat(prompt, model) for prompt, model in prompts]
    responses = await asyncio.gather(*tasks)

    for model, response in zip([p[1] for p in prompts], responses):
        print(f"\n🧠 Model: {model}\n📜 Response: {response}\n")

# Run the async event loop
if __name__ == "__main__":
    asyncio.run(main())
