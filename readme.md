# AzureML Repositories with custom docker image

Aim: I have custom Environment based on custom docker image and I would like to use when experimenting and/or in produciotn pipeline. Thus, I want to save that Environment in AzureML Registry so that it can be reused.


## Approach 1: CREATE CUSTOM IMAGE - BUILD in Registry's ACR

Step 1: Create Environment in AzureML registry by specifying YML ans Docker


Dockerfile:
```shell
FROM mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04:20220729.v1
ENV AZUREML_CONDA_ENVIRONMENT_PATH /azureml-envs/sklearn-1.0
# Create conda environment
RUN conda create -p $AZUREML_CONDA_ENVIRONMENT_PATH \
    python=3.8 pip=21.3.1 -c anaconda -c conda-forge
# Prepend path to AzureML conda environment
ENV PATH $AZUREML_CONDA_ENVIRONMENT_PATH/bin:$PATH
# Install pip dependencies
RUN pip install 'matplotlib~=3.5.0' \
                'psutil~=5.8.0' \
                'tqdm~=4.62.0' \
                'pandas~=1.3.0' \
                'scipy~=1.7.0' \
                'numpy~=1.21.0' \
                'ipykernel~=6.0' \
                'scikit-learn~=1.0.0' \
                'stellargraph~=1.2.1' \
                'gensim~=4.2.0' \
                'azure-ai-ml~=0.1.0b6' \
                'azureml-mlflow' \
                'mltable~=0.1.0b3' \
                'chardet' \
                'mlflow'\
                'papermill'\
                'xgboost'
# This is needed for mpi to locate libpython
ENV LD_LIBRARY_PATH $AZUREML_CONDA_ENVIRONMENT_PATH/lib:$LD_LIBRARY_PATH
```

```shell
cd custom-docker
az ml environment create --file environment.yml --registry-name mma  --verbose
```

Environemnt is present in AzureML Registry

```shell
az ml environment list --registry-name mma
```

Output:
```
[
  {
    "latest version": "1",
    "name": "embeddings-env"
  }
]
```

Step 2: Run job based on the Environment in AzureML Registry

```shell
az ml job create --file ./job/job-custom-env.yml
```

### Throws error:
```shell
(UserError) More than one of BaseImage, BaseDockerfile, and BuildContext were set; these are mutually exclusive properties.
Code: UserError
Message: More than one of BaseImage, BaseDockerfile, and BuildContext were set; these are mutually exclusive properties.
Additional Information:Type: ComponentName
Info: {
    "value": "managementfrontend"
}Type: Correlation
Info: {
    "value": {
        "operation": "6e4c9385ea4ab2cbe675b3ea87817616",
        "request": "5437c8df3ad9226c"
    }
}Type: Environment
Info: {
    "value": "westeurope"
}Type: Location
Info: {
    "value": "westeurope"
}Type: Time
Info: {
    "value": "2022-11-23T14:58:44.8639911+00:00"
}
```

### Questions:
- what the error means?


## Approach 2: Create Environment in AzureML Registry based on existing environment in AzureML Workspace ACR docker image
This approach expects the image/env to be already in ACR created with AzureML - crml08261920dev.azurecr.io 

```
az ml environment create --name myenv-sample-python --version 1 --image crml08261920dev.azurecr.io/sample/python:v2  --registry-name mma
```

### Throws error:
```
(UserError) Authentication failed for container registry acraicentredevshared.azurecr.io
Code: UserError
Message: Authentication failed for container registry acraicentredevshared.azurecr.io
```
### Questions:
- is that supported?
- Auth error - am I misssing some RBAC/permissions?



## Approach 3: Create custom Env based on public Pytorch image in Registry's ACR
Basically Approach 1, just using public Pytorch image.

```
az ml environment create --name my-pytorch --version 1  --image pytorch/pytorch --registry-name mma
```

Environemnt is present in AzureML Registry

```shell
az ml environment list --registry-name mma
```

Output:
```
[
  {
    "latest version": "1",
    "name": "my-pytorch"
  }
]
```

Step 2: Run job based on the Environment in AzureML Registry

```shell
az ml job create --file ./job/job-pytorch-env.yml
```
### Throws error:
```
AzureMLCompute job failed.
AggregatedUnauthorizedAccessError: Failed to pull Docker image mma57500dd5c1bf4fb9a4f.azurecr.io/my-pytorch_1_9177bed4-0cce-538a-90d0-c42b92f709da. This error may occur because the compute could not authenticate with the Docker registry to pull the image. If using ACR please ensure the ACR has Admin user enabled or a Managed Identity with `AcrPull` access to the ACR is assigned to the compute. If the ACR Admin user's password was changed recently it may be necessary to synchronize the workspace keys.
	Authentication methods attempted: Anonymous
	Note: Request to obtain credential was rejected, if the intention is to authenticate with credentials verify if the AML environment is configured correctly and, if using ACR, that both the compute and the user (or service principal) submitting the run have access to the AML environment and ACR (visit https://docs.microsoft.com/en-us/azure/machine-learning/how-to-assign-roles#common-scenarios for more information about expected permissions)
	Note: Identity (MSI) not found on the compute, if the intention is to authenticate with identity ensure that a Managed Identity with `AcrPull` access to the ACR is assigned to the compute
	Error: {"Code":"DockerUnauthorizedAccessError","Category":"UserError","Message":"Failed to pull Docker image mma57500dd5c1bf4fb9a4f.azurecr.io/my-pytorch_1_9177bed4-0cce-538a-90d0-c42b92f709da with authentication mode Anonymous due to: Docker responded with status code 500: {\"message\":\"Head \\\"https://mma57500dd5c1bf4fb9a4f.azurecr.io/v2/my-pytorch_1_9177bed4-0cce-538a-90d0-c42b92f709da/manifests/latest\\\": unauthorized: authentication required, visit https://aka.ms/acr/authorization for more information.\"}\n. Compute could not authenticate with the Docker registry to pull the image.","Details":[],"Error":null}
```

### Questions:
- Basically Approach 1, just using public Pytorch image - so why is the error different?
- Auth error - am I misssing some RBAC/permissions? (cannot pull from AzureML Registry ACR)

