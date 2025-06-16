import logging
from langchain_openai import AzureChatOpenAI

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Simple settings object (could be replaced with dotenv or argparse in prod)
class Settings:
    def __init__(self):
        self.azure_endpoint = "https://balwaXXXXXX-mav0pvsn-swedencentral.cognitiveservices.azure.com/"
        self.azure_api_key = "XXXXXX"  # 🔐 Replace this with your actual key or env variable
        self.azure_api_version = "2024-12-01-preview"
        self.azure_deployment_name = "gpt-4o"
        self.llm_temperature = 1.0
        self.llm_max_tokens = 4096

settings = Settings()

# Initialize AzureChatOpenAI
llm = AzureChatOpenAI(
    api_key=settings.azure_api_key,
    azure_endpoint=settings.azure_endpoint,
    api_version=settings.azure_api_version,
    deployment_name=settings.azure_deployment_name,
    temperature=settings.llm_temperature,
    max_tokens=settings.llm_max_tokens,
)

logger.info("✅ AzureChatOpenAI initialized.")

# Generate chat response
response = llm.invoke([
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "I am going to Paris, what should I see?"}
])

print("💬 Response:")
print(response.content)
