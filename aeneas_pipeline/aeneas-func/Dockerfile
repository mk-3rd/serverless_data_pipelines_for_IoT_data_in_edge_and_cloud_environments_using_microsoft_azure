# To enable ssh & remote debugging on app service change the base image to the one below
# FROM mcr.microsoft.com/azure-functions/python:4-python3.9-appservice
FROM mcr.microsoft.com/azure-functions/python:4-python3.9

ENV AzureWebJobsScriptRoot=/home/site/wwwroot \
    AzureFunctionsJobHost__Logging__Console__IsEnabled=true

COPY . /home/site/wwwroot

WORKDIR /root

COPY requirements.txt /

RUN \
    pip install -r /requirements.txt && \
    apt-get update && apt-get install -y \
    git && \
    git init && \
    git remote add -f origin https://github.com/qub-blesson/DeFog.git && \
    git config core.sparsecheckout true && \
    echo Aeneas/aeneas/ >> .git/info/sparse-checkout && \
    git pull https://github.com/qub-blesson/DeFog.git master && \
    cd Aeneas/aeneas && \
    bash install_dependencies.sh && \
    python setup.py build_ext --inplace