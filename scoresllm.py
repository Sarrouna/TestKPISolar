import mlflow
from mlflow.genai import scorer
from mlflow.genai.scorers import Correctness, Guidelines
from langchain_aws import ChatBedrockConverse
@scorer
def is_concise(outputs: str) -> bool:
    """Evaluate if the answer is concise (less than 5 words)"""
    return len(outputs.split()) <= 5


scorers = [
    Correctness(),
    Guidelines(
        name="is_english",
        guidelines="The answer must be in English"
    ),
    is_concise,
]
llm = ChatBedrockConverse(
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    temperature=0
)
def predict(prompt: str) -> str:
    response = llm.invoke(prompt)
    return response.content
eval_data = [
    {
        "inputs": "What is the capital of France?",
        "ground_truth": "Paris"
    },
    {
        "inputs": "Translate to English: bonjour",
        "ground_truth": "hello"
    },
    {
        "inputs": "Explain quantum physics briefly",
        "ground_truth": "It is complex"
    },
]
with mlflow.start_run(run_name="claude-genai-eval"):
    results = mlflow.evaluate(
        model=predict,
        data=eval_data,
        model_type="text",
        scorers=scorers,
    )

print(results.metrics)
print(results.tables["eval_results"])
