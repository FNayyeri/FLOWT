import mlflow
from mlflow.deployments import get_deploy_client

def deploy_model(model_uri, deployment_name, triton_host, triton_port):
    client = get_deploy_client("triton")
    client.create_deployment(
        name=deployment_name,
        model_uri=model_uri,
        config={"triton_host": triton_host, "triton_port": triton_port}
    )

if __name__ == "__main__":
    deploy_model(
        model_uri="models:/yolo-marine-litter/latest",
        deployment_name="yolo-marine-litter",
        triton_host="localhost",
        triton_port=8000
    )