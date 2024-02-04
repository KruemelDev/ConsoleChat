# ConsoleChat
## Content in development -> errors may occur

This program allows you to connect to your self-hosted server and communicate with other connected clients. As the host of your server, you bear responsibility for both content and security. Please note that this messenger is not advisable for transmitting sensitive information, such as passwords. <br> Exercise caution regarding the nature of the data shared.

## Functions

- Create a account and use your own username and password
- Communicate with your friends over your self-hosted server

## How to use

- Make sure python is installed
- You need to install docker and docker-compose on your system
- Run the docker demon
- Once docker and docker-compose are installed, run the file docker-compose.yml in the Server folder with this command:<br> ```` docker-compose up -d ````
  
-  ## Install packages
    - Execute this to install requirements: ````pip install -r requirements.txt````

- Open and edit the [.env](Server/.env) file to configure your server properties
- Now run the server.py file
- Create a database with the name consolechat
- Next, you can run the client.py file, but make sure you connect to the same IP and port that the socket is running on

## Planed Features
