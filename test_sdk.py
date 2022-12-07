# Import required libraries
from azure.identity import DefaultAzureCredential, InteractiveBrowserCredential

from azure.ai.ml import MLClient, Input, Output
from azure.ai.ml.dsl import pipeline
from azure.ai.ml import load_component
from azure.ai.ml.entities import (
    Environment,
    BuildContext,
    Model,
    ManagedOnlineEndpoint,
    ManagedOnlineDeployment,
    CodeConfiguration,
)
from azure.ai.ml.constants import AssetTypes
import time, datetime, os

try:
    credential = DefaultAzureCredential()
    # Check if given credential can get token successfully.
    credential.get_token("https://management.azure.com/.default")
except Exception as ex:
    # Fall back to InteractiveBrowserCredential in case DefaultAzureCredential not work
    credential = InteractiveBrowserCredential()

sid="a90550ee-2b3c-4802-acef-79472a9b6510"
rid="rg-ml0826-1920dev"
wid="mlw-ml0826-1920dev"

ml_client_workspace = MLClient(
    credential=credential,
    subscription_id=sid,
    resource_group_name=rid,
    workspace_name=wid,
)
print(ml_client_workspace)

ml_client_registry = MLClient(credential=credential, registry_name="mma", resource_group_name=rid, subscription_id=sid)
print(ml_client_registry)


# version = str(123456)
version = str(int(time.time()))
print("version: ", version)

# Create environment in registry

env_docker_context = Environment(
    build=BuildContext(path=os.path.join("custom-docker", "docker")),
    name="embeddings-env",
    version=version,
    description="embeddings-env environment",
)
ml_client_registry.environments.create_or_update(env_docker_context)

path=os.path.join("custom-docker", "docker")
