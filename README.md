
# ChatTube

ChatTube transforms your interaction with YouTube videos. It's not just about watching videos anymore – now you can extract transcripts, get summaries, interact with a cloned voice of the speaker, and much more.

## Description

ChatTube built on Azure features to enhance your learning and interaction with YouTube content:

- **Video Transcript Extraction**: Provide any YouTube video link, and the app will extract the transcript for you.
- **Transcript Summarization**: Get the gist of the video with an automated summary of the transcript.
- **Vector Store for Retrieval Augmented Generation**: Sets up a sophisticated vector store to augment content generation.
- **Voice Cloning**: Clone the voice of the video's speaker from the audio track.
- **Interactive Chat**: Engage in a simulated conversation with the cloned voice of the speaker, receiving text responses or listening to voice clones.

## Installation Instructions

### Local Run

To run A_Information locally, follow these steps:

1. Clone the repository to your local machine:
   ```sh
   git clone https://github.com/yourusername/A_Information.git
   ```
2. Navigate to the cloned directory:
   ```sh
   cd A_Information
   ```
3. Install the required dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Run the application:
   ```sh
   python A_Information.py
   ```

### Docker Compose

If you prefer to use Docker, you can easily set up the application with docker-compose:

1. Ensure Docker and docker-compose are installed on your system.
2. In the project directory, build and start the container:
   ```sh
   docker-compose up --build
   ```

### Deployment to Azure

To deploy A_Information to Azure, you can use the Azure CLI:

1. Log in to your Azure account:
   ```sh
   az login
   ```
2. Set up your Azure configuration (replace with actual names and settings):
   ```sh
   az group create --name myResourceGroup --location eastus
   az appservice plan create --name myAppServicePlan --resource-group myResourceGroup --sku B1 --is-linux
   az webapp create --resource-group myResourceGroup --plan myAppServicePlan --name myUniqueAppName --deployment-container-image-name mydockerimage
   ```
3. Deploy the container image to Azure:
   ```sh
   az webapp create --name <app-name> --resource-group <group-name> --plan <plan-name> --deployment-container-image-name <docker-image>
   ```

## Requirements

Before running A_Information, ensure you have the following:

- Python 3+
- Docker (for Docker Compose installation)
- Azure CLI (for Azure deployment)
- Other dependencies listed in `requirements.txt`

## Usage Instructions

To use A_Information, start the application with the method you prefer (local, Docker, Azure). Once running, the application will prompt you for a YouTube video link. After providing the link, follow the on-screen instructions to interact with the application's features.
