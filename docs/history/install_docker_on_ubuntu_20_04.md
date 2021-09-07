---
title: Install Docker on Ubuntu 20.04
lang: en-US
---

# Install Docker on Ubuntu 20.04

Ref : <https://docs.docker.com/engine/install/ubuntu/>

Install Docker on Ubuntu 20.04

1. Update the ```apt``` package index and install packages to allow ```apt``` to use a repository over HTTPS:

```sh
sudo apt update
sudo apt install apt-transport-https ca-certificates curl gnupg lsb-release
```

2. Add Docker's official GPG key:

```sh
curl -fsSl https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
```

3. Use the following command to set up the **stable** repository.

```sh
echo \
  "dev [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
```

4. install Docker Engine

```sh
sudo apt install docker-ce docker-ce-cli containerd.io
```

5. Verify that Docker Engine is installed correctly by running the ```hello-world``` image.

```sh
sudo docker run --rm hello-world
```

6. Add your user to the docker group.

```sh
sudo usermod -aG docker $USER
```

7. Log out and log back in so that your group membership is re-evaluated.
