---
title: Install node.js on Ubuntu 20.04
lang: en-US
---

# Install node.js on Ubuntu

Ref : <https://github.com/nodesource/distributions/blob/master/README.md>


You can install ```node.js``` of LTS version in Ubuntu using the commands below. If do you want installation ```node.js``` of other 
version that you can refer the [NodeSource Node.js Binary Distributions page](<https://github.com/nodesource/distributions/blob/master/README.md>).

```shell
# Using Ubuntu
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs
```