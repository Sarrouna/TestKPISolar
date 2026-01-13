import time, mlflow
from langchain_aws import ChatBedrockConverse
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

TRACKING_ARN = "arn:aws:sagemaker:REGION:ACCOUNT:mlflow-tracking-server/NAME"
mlflow.set_tracking_uri(TRACKING_ARN)
mlflow.set_experiment("autolog-smoke-test")

mlflow.langchain.autolog(log_traces=True)

llm = ChatBedrockConverse(
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    temperature=0
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "Réponds en français, très concis."),
    ("user", "{question}")
])
parser = StrOutputParser()

question = "Explique LangChain en une phrase."

with mlflow.start_run(run_name="autolog-span-parent"):
    with mlflow.start_span(name="app_request", span_type="request") as sp:
        sp.set_attribute("question", question)

        t0 = time.time()
        answer = (prompt | llm | parser).invoke({"question": question})
        latency = time.time() - t0

        mlflow.log_metric("latency_s", latency)
        mlflow.log_metric("answer_words", len(answer.split()))

print(answer)
