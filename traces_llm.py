# === Test minimal MLflow autolog + LangChain + Bedrock (1 cellule) ===
# Prérequis: tu as déjà accès à Bedrock et à ton tracking server SageMaker MLflow.

import os, time
import mlflow

# --- Mets ton ARN de tracking server ici ---
TRACKING_ARN = "arn:aws:sagemaker:REGION:ACCOUNT:mlflow-tracking-server/NAME"
EXPERIMENT = "autolog-smoke-test"

# (optionnel) fix région si besoin
# os.environ["AWS_DEFAULT_REGION"] = "eu-west-1"

# --- Versions (utile en debug) ---
import langchain, langchain_core
from importlib.metadata import version
print("mlflow:", mlflow.__version__)
print("langchain:", langchain.__version__)
print("langchain-core:", langchain_core.__version__)
print("langgraph:", version("langgraph"))       # même si on ne l'utilise pas ici
print("langchain-aws:", version("langchain-aws"))

# --- MLflow setup ---
mlflow.set_tracking_uri(TRACKING_ARN)
mlflow.set_experiment(EXPERIMENT)

# 🔥 Active autolog/traces
mlflow.langchain.autolog(log_traces=True)

# --- LangChain + Bedrock ---
from langchain_aws import ChatBedrockConverse
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

llm = ChatBedrockConverse(
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    temperature=0
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "Tu es un assistant concis. Réponds en français."),
    ("user", "{question}")  # important pour Bedrock Converse
])
parser = StrOutputParser()

question = "Explique LangChain en une phrase."

try:
    # Un run MLflow explicite (recommandé pour retrouver facilement)
    with mlflow.start_run(run_name="autolog_langchain_bedrock"):
        mlflow.log_param("model_id", llm.model_id)
        mlflow.log_param("temperature", 0)

        t0 = time.time()
        chain = prompt | llm | parser
        answer = chain.invoke({"question": question})
        latency = time.time() - t0

        mlflow.log_metric("latency_s", latency)
        mlflow.log_metric("answer_words", len(answer.split()))

        print("Q:", question)
        print("A:", answer)
        print("latency_s:", latency)

except Exception as e:
    # Si tu veux debug rapide dans MLflow
    with mlflow.start_run(run_name="autolog_langchain_bedrock_error"):
        mlflow.set_tag("status", "error")
        mlflow.set_tag("error_type", type(e).__name__)
        mlflow.set_tag("error_msg", str(e)[:250])
    raise
