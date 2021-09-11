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

  1. Register SSH key on GitHub
  Ref: [Generating a new SSH Key and adding it to the ssh agent](https://docs.github.com/en/github/authenticating-to-github/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent)
 
  - Open terminal
  - Paste text below to, substitute in your GitHub email address.
```shell
ssh-keygen -t ed25519 -C "your_email@example.com"
```

  - Sign in the [GitHub](https://github.com)
  - Visit to [SSH Key and GPG keys](https://github.com/settings/keys)
  - Click **New SSH Key** button
  - Enter **Title** and then past ssh public key in **Key**

  1. Create GitHub repository

  - Sign in the [GitHub](https://github.com)
  - Visit to [Creating new repository](https://github.com/new)
  - Enter 'moeblah.github.io' in the **repository name**
  - Select **Public**
  - Check **Add .gitignore** and then select **node** of **.gitignore template**
  - Check **Choose license** and then select **License: MIT License**
  - Click **Create repository** button

  2. Clone GitHub repository
```shell
git clone git@github.com:moeblah/moeblah.github.io.git
```

  3. Set .gitignore file
  4. Create VuePress project
  5. Create GitHub workflow
  6. Add new files to git
  7. Commit git
  8. Push git on GitHub
  9. Visit Project page of GitHub
