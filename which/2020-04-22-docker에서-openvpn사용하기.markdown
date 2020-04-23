---
layout: page
title: docker에서 openvpn사용하기
---

개발을 하다보면 VPN을 사용해야 하는 경우가 생긴다. 하지만 개발 시스템에 VPN을 설정하면 여러가지 불편한 경우가 생긴다. VPN 서버 설정에 따라 사용할수 없는 인테넷 서비스가 생길수도 있으며, 개발 환경마다 여러 VPN을 설정해야 하는 경우가 발생한다. 이럴때 Docker로 개발환경을 구성하고 Docker 컨테이너에 VPN 을 설정하면 간단하게 해결할 수 있다.

## Docker container 생성

docker 컨테이너에서 vpn을 사용하기 위해서는 --cap-add=NET_ADMIN 과 --device /dev/net/tun 옵션을 함께 사용하거나 --privileged 옵션을 사용해 Privileged Mode로 컨테이너를 실행하여야한다.

```bash
/# docker run --cap-add=NET_ADMIN \
              --device /dev/net/tun \
              -it alphine
or
/# docker run --privileged -it alphine
```

## Aphine linux 에서 openvpn 설치

```bash
/# apk add openvpn
```


