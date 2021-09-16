---
title: Prepare to develop
lang: en-US
---

# Prepare to develop

 * SSG : Static Site Generation
 * SSR : Server Side Rendering
 * CSR : Client Side Rendering

VuePress can be documented and tested when it develops Javascript or Typescript library 
because that developed for documented of Vue.js and that can using Vue.js component.

VuePress generates static site and GitHub can serve static site besides, that's free. 
So I'm going to start my project of Javascript Data Grid with VuePress and that deploy on GitHub. 
My Javascript Data Grid name is MoeGrid and from now on, I will say that is MoeGrid.
ModeGrid will develop on MIT license.

Now, let's lean some skills for creating VuePress project and how to distribute that on GitHub.

## Register SSH key on GitHub

Ref: [Generating a new SSH Key and adding it to the ssh agent](https://docs.github.com/en/github/authenticating-to-github/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent)
 
  1. Open terminal
  2. Paste text below to, substitute in your GitHub email address.
  ```shell:no-line-numbers
  ssh-keygen -t ed25519 -C "your_email@example.com"
  ```
  ::: tip Note
  If you are using a legacy system that doesn't support the ED25519 algorithm, use:

  $ ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
  :::

  This create a new SSH key, using the provided email as a label
  ```text:no-line-numbers
  > Generating public/private ed25519 key pair.
  ```
  3. When you're prompted to "Enter a file in which to save the key," press Enter. This accepts the default file location.
  ```text:no-line-numbers
  > Enter a file in which to save the key (/home/you/.ssh/id_ed25519): [Press enter]
  ```
  4. At the prompt, type a secure passphrase. For more information, see "[Working with SSH Key passphrases.](https://docs.github.com/en/github/authenticating-to-github/connecting-to-github-with-ssh/working-with-ssh-key-passphrases)."
  ```text:no-line-numbers
  > Enter passphrase (empty for no passphrase): [Type a passphrase]
  > Enter same passphrase again: [Type passphrase again]
  ```
  5. Completed to generate SSH key.
  ```text:no-line-numbers
  Your identification has been saved in /home/you/.ssh/id_ed25519
  Your public key has been saved in /home/you/.ssh/id_ed25519.pub
  The key fingerprint is:
  SHA256:8pTlRRkzOfdZbmNmdvhC6RK/Hb93RqxnA1hhuVE6lH4 your_email@example.com
  The key's randomart image is:
  +--[ED25519 256]--+
  |            ==+. |
  |           .=Oo .|
  |          . +=+=o|
  |         + ..+=E=|
  |      . S . o=*+o|
  |       +   ...+.+|
  |        .    ..*o|
  |              o.O|
  |               ==|
  +----[SHA256]-----+
  ```
  6. See your public key. And it copies your public key.
  ```sh:no-line-numbers
  cat ~/.ssh/id_ed25519.pub
  
  ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAILhZ9PFFejc9Jvmw1a/fa+k1CkDLZgKXDIK0XtaLcQwg your_email@example.com
  ```
  7. Sign in the [GitHub](https://github.com/login)
  8. Visit to [SSH Key and GPG keys](https://github.com/settings/keys)
  9. Click **New SSH Key** button
  10. Enter **Title** and then paste ssh public key in **Key**

## Create GitHub repository

  1. Sign in the [GitHub](https://github.com)
  2. Visit to [Creating new repository](https://github.com/new)
  3. Enter **'&lt;*GitHub Username*&gt;.github.io'** in the **Repository name**
  4. Select **Public**
  5. Check **Add .gitignore** and then select **node** of **.gitignore template**
  6. Check **Choose license** and then select **License: MIT License**
  7. Click **Create repository** button
  8. Open terminal
  9. Clone GitHub repository
  ```shell
  git clone git@github.com:<GitHub Username>/<GitHub Username>.github.io.git
  ```
  9. Set .gitignore file
  ```shell
  cd <GitHub Username>.github.io.git
  cat .temp >> .gitignore
  cat .temp/ >> .gitignore
  cat .idea >> .gitignore
  cat yarn.lock >> .gitignore
  cat package-lock.json >> gitignore
  ```

## Create VuePress
  1. Create VuePress project
  2. Create GitHub workflow
  3. Add new files to git
  4. Commit git
  5. Push git on GitHub
  6. Visit Project page of GitHub


## Debug setting for JetBrains's IDEA