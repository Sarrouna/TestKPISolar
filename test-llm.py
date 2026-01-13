import mlflow, time

mlflow.set_tracking_uri("arn:aws:sagemaker:REGION:ACCOUNT:mlflow-tracking-server/NAME")
mlflow.set_experiment("autolog-smoke-test")

with mlflow.start_run(run_name="manual-trace-test"):
    with mlflow.start_span(name="manual_span", span_type="test") as sp:
        sp.set_attribute("hello", "world")
        time.sleep(0.2)

print("Done")
