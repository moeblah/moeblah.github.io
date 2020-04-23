---
layout: page
title: 부팅가능한 ubuntu usb 스틱 만들기
---

https://idratherbewriting.com/documentation-theme-jekyll/index.html

# macOS에서 부팅가능한 Ubuntu usb 스틱 만들기
원문 : <https://ubuntu.com/tutorials/tutorial-create-a-usb-stick-on-macos#1-overview>

## 개요

부팅가능한 Ubuntu usb 스틱으로 아래와 같은 일을 할수 있습니다.

  * PC 또는 Mac 에서  Ubuntu 설치또는 업그레이드를 할수 있습니다.
  * PC에 Ubuntu를 설치하지 않고 Ubuntu desktop 환경을 사용할 수 있습니다.
  * 대여한 노트북 또는 인터넷 까페에서 Ubuntu로 부팅하여 사용할수 있습니다.
  * USB 스틱에 기본적으로 설치된 도구를 사용하여 손상된 구성을 복구하거나 수정 할 수 있습니다..

Window 또는 Linux PC에서 USB 스틱을 사용하려는 경우 부팅가능한 USB 스틱을 만드는것은 매우 간단하지만 Mac에서 사용하려는 경우 몇가지 추가적인 고려사항이 있습니다. 맥에서 USB 스틱으로 부팅하려는 경우 부팅시 Option/alt(⌥) 키를 눌러 'Startup Manager'로 진입하여야하는데 'Startup Manager'가 특정 파티션 테이블과 레이아웃이 없으면 USB 스틱을 인식하지 못하기 때문입니다. 이에 대해서 이후 단계에서 다루겠습니다.
 

## 요구사항

우리에게 필요한건:

  * 2GB이상의 USB 스틱/플래시 드라이브
  * macOS가 탑제된 Apple 컴퓨터 또는 랩탑
  * Ubuntu ISO 파일. [Ubuntu Download](https://ubuntu.com/download)에서 다운 받을 수 있다.

## USB 스틱 준비

Apple 하드웨어와 최대한 호환성을 보장하기위해 먼저 Apple의 'Disk Utility'를 사용하여 USB 스틱을 다시 포멧 하여야 합니다. 그러나 일반적인 PC 하드웨어에서 USB 스틱을 사용한다면 이단계는 건너 뛰어도 괜찮습니다.

  * 파인더의 Application > Utilites 또는 Spotlight 검색을 이용해  ```Disk Utility```를 실행합니다.
  * USB 스틱을 삽입하면 Disk Utility가 삽입된 USB 스틱을 인식합니다.
  * 삽입된 USB 스틱 디바이스를 선택하고(View.Show All Devices 옵션을 활성화 해야 할수도 있습니다) 툴바 메뉴(또는 오른쪽 클릭 메뉴)에서 ```Erase``` 를 선택합니다.
  * Format은 ```MS-DOS (FAT)```으로 Scheme은 ```GUID Partition Map``` 으로 설정합니다.
  * 올바른 장치를 선택했는지 확인한후 ```Erase``` 버튼을 클릭합니다.


주의 : 디스트 유틸리티 사용시 잘못된 장치 또는 파티션을 선택하면 데이터가 손실 될수 있으므로 주의해야 합니다.
