---
title: Create VuePress project
lang: en-US
---

# Create VuePress project

Ref: <https://v2.vuepress.vuejs.org/guide/getting-started.html>

I will install ```VuePress``` version 2 using ```yarn```.

 - **Step 1:** Create and change into a new directory
```shell
mkdir vuepress
cd vuepress
```
 - **Step 2:** Initialize your project
```shell
git init
yarn init
```
 - **Step 3:** Install VuePress locally
```shell
yarn add -D vuepress@next
```
 - **Step 4:** Add som scripts to package.json
```json
{
  "scripts": {
    "docs:dev": "vuepress dev docs",
    "docs:build": "vuepress build docs"
  }
}
```
 - **Step 5:** Add the default temp and cache directory to ```.gitignore``` file
```shell
echo 'node_modules' >> .gitignore
echo '.temp' >> .gitignore
echo '.cache' >> .gitignore
```
 - **Step 6:** Create your first document
```shell
mkdir docs
echo '# Hello VuePress' > docs/README.md
```
 - **Step 7:** Serve the documentation site in the local server
```shell
yarn docs:dev
```