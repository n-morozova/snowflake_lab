# Just Enough Docker

##

Creating a simple Python program that hosts a web server on `http://localhost:80` and managing it with a virtual environment involves several steps. Here's a guide to help you set it up:

1. **Create a Virtual Environment:**
   - First, create a new directory for your project.
   - Open a terminal and navigate to this directory.
   - Run `python3 -m venv venv` to create a new virtual environment named `venv`.
   - Activate the virtual environment:
     - On Windows, use `venv\Scripts\activate`.

2. **Install Dependencies:**
   - You'll need a web framework. A common choice is Flask.
   - Install Flask by running `pip install flask`.
   - After installing Flask, freeze the installed packages into `requirements.txt` by running `pip freeze > requirements.txt`.

3. **Create the `app.py` File:**
   - In your project directory, create a file named `app.py`.
   - Add the following code to `app.py`:
     ```python
     from flask import Flask
     app = Flask(__name__)

     @app.route('/')
     def hello_world():
         return 'Hello, World!'

     if __name__ == '__main__':
         app.run(host='0.0.0.0', port=80)
     ```
   - This code creates a basic Flask app that responds with "Hello, World!" when accessed.

4. **Run the Application:**
   - In your terminal, ensure you are in the project directory and your virtual environment is activated.
   - Run the app by executing `python app.py`.
   - Your application should now be running on `http://localhost:80`.
   - Open a web browser and navigate to `http://localhost:80` to see the message.

5. **Deactivating the Virtual Environment:**
   - When you’re done, you can deactivate the virtual environment by running `deactivate` in your terminal.

Docker in the web-app folder:

docker run -p 80:80 --name web-app-container web-app

docker ps

docker rm web-app-container

docker run -p 80:80 --rm --name web-app-container web-app

docker run -p 80:80 --rm -d --name web-app-container web-app

docker ps

docker exec -it ##### bash

Docker Compose in the root folder

docker-compose build

docker-compose build --no-cache

docker-compose up

## Deploy on Azure

On mac os

Install:

brew update && brew install azure-cli

Login:

az login

Create Resource Group

az group create --name rg-projectname-docker --location westus

Create registry

az acr create --resource-group rg-projectname-docker --name projectnameregistry --sku Basic


I'm sorry for the confusion. The error message indicates that the admin user for your Azure Container Registry (ACR) is disabled. The admin user is a pre-created user that has push/pull permissions to the ACR.

You can enable the admin user and retrieve the username and password with the following commands:

1. **Enable the admin user**:
```bash
az acr update --name projectnameregistry --admin-enabled true
```

2. **Get the credentials**:
```bash
az acr credential show --name projectnameregistry
```

The second command will output the `username` and `passwords` for your ACR. You can use these credentials to login to your ACR.

Please note that using the admin account for ACR is convenient for a quick start but it's not recommended for production scenarios. For production scenarios, it's recommended to use an Azure Active Directory service principal or managed identity that has the appropriate role assigned.

az acr login --name projectnameregistry

Great! Now that you're logged in to your Azure Container Registry (ACR), you can push your Docker images to it. However, please note that Docker Compose files themselves are not pushed to the registry. Instead, the Docker images defined in the Docker Compose file are built and pushed to the registry. Here's how you can do it:

1. **Build your Docker image**: Build your Docker image locally using the Dockerfile in your `web-app` directory. Make sure to tag the image with the login server name of your ACR instance:
```bash
docker build -t projectnameregistry.azurecr.io/web-app:latest ./web-app
```

2. **Push your Docker image to ACR**: After building the image, push it to your Azure Container Registry:
```bash
docker push projectnameregistry.azurecr.io/web-app:latest
```

3. **Update your Docker Compose file**: Replace the `build` directive with the `image` directive in your Docker Compose file. The `image` should be the name of the image you just pushed to ACR:
```yaml
version: '3'
services:
  web:
    image: projectnameregistry.azurecr.io/web-app:latest
    ports:
      - "80:80"
    depends_on:
      - redis
  redis:
    image: "redis:6.0"
```

After these steps, your Docker image should be available in your Azure Container Registry, and you can use it to deploy containers to Azure Container Instances or other Azure services.

Now that you have your Docker images in Azure Container Registry (ACR), you can deploy your Docker Compose application to Azure Container Instances (ACI). Here are the steps:

1. **Create a Service Principal**: Azure Container Instances needs to pull your images from ACR. For that, you need to create a service principal with `AcrPull` role. Run the following command:
```bash
az ad sp create-for-rbac --name http://projectname-service-principal --role AcrPull --scopes /subscriptions/<subscription-id>/resourceGroups/rg-projectname-docker/providers/Microsoft.ContainerRegistry/registries/projectnameregistry
```
Replace `<service-principal-name>` with a name for your service principal, and `<subscription-id>` with your Azure subscription ID.

This command will output the `appId` and `password` of your service principal. Take note of these values as you'll need them in the next step.

2. **Deploy to Azure Container Instances**: Now, you can deploy your Docker Compose application to Azure Container Instances using the `az container create` command:
```bash
az container create --resource-group rg-projectname-docker --file docker-compose.yml --registry-login-server projectnameregistry.azurecr.io --registry-username '#########' --registry-password '#########' --dns-name-label projectname-app --name projectname-container
```
Replace `<app-id>` and `<password>` with the `appId` and `password` of your service principal.

3. **Access your Application**: Once the deployment is successful, you can access your application at `http://projectname-app.<location>.azurecontainer.io`.

Please replace `<service-principal-name>`, `<subscription-id>`, `<app-id>`, and `<password>` with your actual values. Let me know if you need further assistance! 😊

az ad sp create-for-rbac --name http://projectname-service-principal --role AcrPull --scopes /subscriptions/`<subscription-id>`/resourceGroups/rg-projectname-docker/providers/Microsoft.ContainerRegistry/registries/projectnameregistry

Creating 'AcrPull' role assignment under scope '/subscriptions/`<subscription-id>`/resourceGroups/rg-projectname-docker/providers/Microsoft.ContainerRegistry/registries/projectnameregistry'
The output includes credentials that you must protect. Be sure that you do not include these credentials in your code or check the credentials into your source control. For more information, see https://aka.ms/azadsp-cli

az acr credential show --name projectnameregistry
