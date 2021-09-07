---
title: Create docker image for Vuepress
lang: en-US
---
# Create docker image for Vuepress.
It is use Vuepress v2 because that supports Typescript. However, it should be noted that Vuepress v2 has not yet been
stabilized.

1. Create ```entrypoint.sh``` for ```ENTRYPOINT``` of Vuepress docker image.

```shell

if [[ ! -v GROUP_ID ]]; then
  # GROUP_ID is not set.
elif [[ -z "$GROUP_ID" ]]; then
  # GROUP_ID is empty string.
elif [[ ! $GROUP_ID =~ ^\s+$ ]]; then
  # GROUP _D is not number.
elif [ "$GROUP_ID" != ($id -g vuepress) ]; then
    addgroup -S vuepress -u $GROUP_UID
fi


if [[ ! -v USER_ID]]; then
  # GROUP_ID is not set.
elif [[ -z "$USER_ID" ]]; then
  # GROUP_ID is empty string.
elif [[ ! $USER_ID =~ ^\s+$ ]]; then
  # GROUP _D is not number.
elif [ "$UWER_ID" != ($id -u vuepress) ]; then
    addgroup -S vuepress -u $GROUP_UID
fi

if [ "$GROUP_ID" != ($id -g vuepress) ]; then
    addgroup -S vuepress -u $GROUP_UID
    adduser -u vuepress -S $USER_NAME -G $GROUP_NAME
elif [ "$GROUP_ID" != ($id -)]
fi 
# stat -c '%u' ./yarn.lock 
```

2. Create Dockerfile.

```Dockerfile
FROM node:14-alpine
ADD entrypoint.sh /usr/bin

RUN mkdir /vuepress

ENTRYPOINT ["entrypoint.sh"]
```

3. Build Docker image

```shell
docker build --tag vuepress:2-next.20210902 .
```

4. Run Vuepress Docker image.

```shell
docker run --rm -p 8080:8080 --name vuepress -e GROUP_ID=$(id -g) -e USER_ID=$(id -u) vuepress:2-next.20210902
```

