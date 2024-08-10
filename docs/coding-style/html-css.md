출처 : https://google.github.io/styleguide/htmlcssguide.html

## 배경

이 문서는 협업 코드의 품질을 개선하고 일정 수준의 코드 품질을 유지하는 것을 목표로하며, HTML 및 CSS를 사용하는 원시 작업 파일에 적용하기 위한 
HTML 및 CSS에 대한 형식 및 스타일 규칙을 정의 한다.

## 일반적인 규칙

### 일반적인 스타일 규칙

#### Protocol

리소스 연결시 가능한 ```HTTPS```를 사용한다.

HTTPS를 통한 리소스 사용이 불가능 한 경우가 아니라면 이미지, 미디어파일, 스타일 시트 및 스크립트에 항상 HTTPS(https:)를 사용 한다.

```html
<!-- 비추천 : 프로토콜 생략 -->
<script src="//ajax.googleapis.com/ajax/libs/jquery/3.4.0/jquery.min.js"></script>

<!-- 비추천 : HTTP 사용 -->
<script src="http://ajax.googleapis.com/ajax/libs/jquery/3.4.0/jquery.min.js"></script>
```

```html
<!-- 추천 -->
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.4.0/jquery.min.js"></script>
```

```sass
/* 비추천 : omits the protocol */
@import '//fonts.googleapis.com/css?family=Open+Sans';

/* 비추천 : uses HTTP */
@import 'http://fonts.googleapis.com/css?family=Open+Sans';
```

```sass
/* 추천 */
@import 'https://fonts.googleapis.com/css?family=Open+Sans';
```

### 일반적인 구성 규칙

#### 들여쓰기

들여쓰기는 2개의 공백을 사용 한다.
 
들여쓰기에 탭과 공백을 혼용하여 사용하지 않는다.

```html
<ul>
  <li>Fantastic</li>
  <li>Great</li>
</ul>
```

```css
.example {
  color: blue;
}
```

#### 대소 문자 사용

소문자만 사용한다.

HTML의 요소 이름, 속성, 속성 값(Text/CDATA 제외), CSS Selector, 속성 및 속성 값(문자열 제외)등 모든 코드는 소문자로 작성한다.

```html 
<!-- 비추천 -->
<A HREF="/">Home</A>
```

```css
/* 비추천 */
color: #E5E5E5;
```

```css
/* 추천 */
color: #e5e5e5;
```

#### 후행 공백

```후행 공백이란 문장의 끝에 들어간 공백을 말한다.```

후행 공백을 제거한다.

불필요 한 후행 공백은 diff를 복잡하게 만들수 있으므로 사용하지 않는다.

```html
<!-- 비추천 -->
<p>What?_
```

```html
<!--추천-->
<!-- Recommended -->
<p>Yes please.
```

### 일반적인 Meta 규칙

#### Encoding

BOM을 사용하지 않는 UTF-8을 사용한다.

편집기가 BOM(byte order mark)이 없는 UTF-8 문자 인코딩을 사용하는지 확인한다.

```<meta charset="utf-8">```을 이용하여 HTML 템플릿과 문서에 인코딩을 지정한다. 스타일 시트는 UTF-8을 가정하기 때문에 인코딩을 지정하지 않는다.

(인코딩과 인코딩을 지정하는 시기와 방법에 대한 자세 한 내용은 
[HTML 및 CSS 문자 인코딩 처리](https://www.w3.org/International/tutorials/tutorial-char-enc/)에서 찾을 수 있다)

#### 작업 항목

할 일 및 작업 항목은 ```TODO```로 표시한다.

```@@```와 같은 다른 일반적인 형식이 아닌 ```TODO```를 사용하여 할 일을 강조 표시 한다.

```TODO(연락처)``` 형식으로 괄호 안에 연락처(사용자 이름 또는 Email 목록)를 추가 한다.

```TODO: 작업 내용```과 같이 콜론 뒤에 작업 항목을 추가 한다.

```html
{# TODO(john.doe): center 테그 제거 #}
<center>Test</center>
```

```html
<!-- TODO: 목록 업데이트 -->
<ul>
  <li>Apples</li>
  <li>Oranges</li>
</ul>
```

## HTML

### HTML 스타일 규칙

#### Document Type

Document Type은 HTML5를 사용 한다.

모든 HTML 문서는 HTML5 구문을 사용 한다 : ```<!DOCTYPE html```.

( HTML은 ```text/html```으로 사용 하는 것이 좋다. XHTML은 사용하지 않는다. XHTML은 ```application/xhtml+xml```으로서 HTML보다 
브라우저와 인프라 인프라 지원이 부족 하고 최적화에 제한 적이다. )

#### HTML 유효성

가능한 유효한 HTML을 사용한다.

파일 크기와 관련하여 달성할 수 없는 성능을 목표로 하는 경우가 아니라면 유효한 HTML 코드를 사용 한다.

[W3C HTML 유효성 검사기](https://validator.w3.org/nu/)와 같은 툴을 이용 하여 유효성 검사를 할 수 있다.

```html
<!-- 비추천 -->
<title>Test</title>
<article>This is only a test.
```

```html
<!-- 추천 -->
<!DOCTYPE html>
<meta charset="utf-8">
<title>Test</title>
<article>This is only a test.</article>
```

#### 시멘틱

목적에 따라 HTML을 사용 한다.

목적에 맞는 요소(Element)(때론 "tags" 라고 잘못 불리기도 한다)를 사용한다. 예를 들면 표제에는 표제 요소를 사용하고, ```p``` 요소는 
단락에, ```a``` 요소는 앵커에 사용한다.

HTML을 목적에 따라 사용하는 것은 접근성, 재사용 및 코드 효율성을 위해 중요하다.

```html
<!-- 비추천 -->
<div onclick="goToRecommendations();">All recommendations</div>
```

```html
<!-- 추천 -->
<a href="recommendations/">All recommendations</a>
```

#### 멀티미디어 대체

멀티미디어에 대한 대체 콘텐츠를 제공한다.

이미지, 비디오, ```canvas```를 이용한 에니메이션 객체는 대체 접금 방법을 제공 해야 한다. 예를 들어 이미지의 경우 (```alt```)를 이용한 의미 있는 
텍스트, 비디오 및 오디오는 스크립트 및 캡션을 사용할 수 있다. 

접근성을 위해 중요한 대체 콘텐츠 제공 : ```@alt```를 사용하지 않으면 시작장애인은 해단 이미지가 무엇인지 알수 있는 방법이 거의 없습니다. 또 다른 
사용자는 비디오 또는 오디오 콘텐츠가 무엇인지 이해할 방법이 없을 수 있습니다.

( ```alt``` 속성이 중복되는 이미지와 CSS 사용으로 인해 바로 사용 할 수 없는 순수하게 장시적인 이미지에는 ```alt=""```와 같은 대체 텍스트를 
사용하지 않는다. )

```html
<!-- 비추천 -->
<img src="spreadsheet.png">
```

```html
<!-- 추천 -->
<img src="spreadsheet.png" alt="Spreadsheet screenshot.">
```

#### 동작과 표현의 분리

동작과 표현의 구조를 분리 한다.

구조(마크업), 표현(스타일), 동작(스크립트)를 엄격하게 분리하고 이들 간의 상호 작용을 최소로 유지하려고 노력 한다.

문서와 템플릿에 HTML만 포함되어 있는지 확인하고 HTML은 구조적 목적으로만 사용한다. 
모든 표현은 스타일 시트에 선언 하고, 모든 행동은 스크립트로 이동 한다.

또한 문서와 템프릿에는 가능한 한 적은 수의 스타일 시트와 스크립트를 연결하여 접촉 영역을 최소화한다.

구조, 표현 그리고 동작을 분리하는 것은 유지보수를 위해 중요하다. HTML 문저와 템프릿을 변경하는 것은 스타일 시트와 스크립트를 업데이트 하는 것보다 항상
더 많은 비용이 든다.

```html
<!-- 비 추천 -->
<!DOCTYPE html>
<title>HTML sucks</title>
<link rel="stylesheet" href="base.css" media="screen">
<link rel="stylesheet" href="grid.css" media="screen">
<link rel="stylesheet" href="print.css" media="print">
<h1 style="font-size: 1em;">HTML sucks</h1>
<p>I’ve read about this on a few sites but now I’m sure:
  <u>HTML is stupid!!1</u>
<center>I can’t believe there’s no way to control the styling of
  my website without doing everything all over again!</center>
```

```html
<!-- 추천 -->
<!DOCTYPE html>
<title>My first CSS-only redesign</title>
<link rel="stylesheet" href="default.css">
<h1>My first CSS-only redesign</h1>
<p>I’ve read about this on a few sites but today I’m actually
  doing it: separating concerns and avoiding anything in the HTML of
  my website that is presentational.
<p>It’s awesome!
```

#### Entity 참조

Entity 참조를 사용하지 않는다.

파일과 편집기에서 동일한 인코딩(UTF-8)를 사용한다면 ```&mdash;```, ```&rdquo;```, or ```&#x263a;```와 같은 엔티티 참조를 사용할 필요가 
없다.

유일한 예외는 HTML에서 특별한 의미를 갖는 문자(예: < 및 &)와 제어 또는 "보이지 않는" 문자(예: 공백 없음)에 적용 된다.

```html
<!-- 비 추천 -->
The currency symbol for the Euro is &ldquo;&eur;&rdquo;.
```

```html
<!-- 추천 -->
The currency symbol for the Euro is “€”.
```

#### 선택적 태그

선택적 태그르 생략 할 수 있다(선택 사항).

파일 사이즈 최적화 및 스캔 가능성을 위해 선태적 태그를 생략 할 수 있다. 
[HTML5 명세서](https://html.spec.whatwg.org/multipage/syntax.html#syntax-tag-omission)에는 생략할 수 있는 태그가 정의 되어 있다.

(이 방식은 웹 개발자가 일반적으로 배우는 것과 크게 다르기 때문에 이 지침에 대한 유예기간을 더 길게 설정해야 할 수 있다.)

```html
<!-- 비추천 -->
<!DOCTYPE html>
<html>
  <head>
    <title>Spending money, spending bytes</title>
  </head>
  <body>
    <p>Sic.</p>
  </body>
</html>
```

```html
<!-- 추천 -->
<!DOCTYPE html>
<title>Saving money, saving bytes</title>
<p>Qed.
```

#### ```type``` 속성

스타일 시트와 스크립트를 위한 ```type```속성은 생략한다.

스타일 시트(CSS를 사용하지 않는 경우) 및 스크립트 (JavaScript를 사용하지 않는 경우)에 ```type```속성을 사용하지 않는다.

HTML5는 기본적으로 ```text/css``` 및 ```text/javascript```를 의미하므로 이러한 컨테스트에서 ```type```속성을 지정 할 필요는 없다.
이는 오래된 브라우저에서도 안전하게 수행할 수 있다.

```html
<!-- 비추천 -->
<link rel="stylesheet" href="https://www.google.com/css/maia.css" type="text/css">
```

```html
<!-- 추천 -->
<link rel="stylesheet" href="https://www.google.com/css/maia.css">
```

```html
<!-- 비추천 -->
<script src="https://www.google.com/js/gweb/analytics/autotrack.js"
    type="text/javascript"></script>
```

```html
<!-- 추천 -->
<script src="https://www.google.com/js/gweb/analytics/autotrack.js"></script>
```

#### ```id``` 속성

불필요한 ```id``` 속성은 사용하지 않는다.

스타일 지정에는 ```class```속성을, 스크립트에는 ```data```속성을 사용한다.

```id```속성이 필요한경우 값에 하이픈을 포함하여 JavaScript 실별자 구문과 일치하지 않도록 하여 사용한다. 예를 들면 ```profile``` 또는 
```userProfile``` 대신 ```user-profile```을 사용한다.

요소에 ```id```속성이 있으면 브라우저는 이를 
[전역 윈도우 프로토타입이 속성으로 명명](https://html.spec.whatwg.org/multipage/window-object.html#named-access-on-the-window-object)
(전역 변수로 사용 할 수 있다)하여 예기치 않은 동작을 일으킬 수 있습니다. 하이픈이 포함된 id 속성 값은 여전히 속성 이름으로 사용할 수 있지만 전역
JavaScript 변수로 참조할 수는 없다.

```html
<!-- 비추천 : `window.userProfile`은 <div> 노드를 참조한다. -->
<div id="userProfile"></div>
```

```html
<!-- 추천: `id`값이 필수라면 하이픈이 포함되도록 한다. -->
<div aria-describedby="user-profile">
  …
  <div id="user-profile"></div>
  …
</div>
```

### HTML 표현 규칙

#### 일반적인 표현 

모든 블록, 목록 또는 테이블 요소에 새 줄을 사용하고 모든 자직 요소는 들여쓰기를 한다.

요소의 스타일 지정(css는 요소가 ```display``` 속성 마다 다른 역활을 할 수 있도록 허용한다.)과 상관없이 모든 블록, 목록 또는 테이블 요소에 새 줄을 
사용한다.

또한 블록, 목록 또는 테이블 요소의 자식 요소인 경우 들여쓰기를 한다.

(목록 항목 사이이 공백 문제가 발생하면 모든 li 요소를 한 줄에 넣어도 된다. 린터는 오류 대신 경고를 표시하도록 한다.)

***린트(lint), 린터(linter) : 소스코드를 분석하여 프로그램 오류, 버그, 스타일 오류를 표시해주는 도구***

```html
<blockquote>
  <p><em>Space</em>, the final frontier.</p>
</blockquote>
```

```html
<ul>
  <li>Moe
  <li>Larry
  <li>Curly
</ul>
```

```html
<table>
  <thead>
    <tr>
      <th scope="col">Income
      <th scope="col">Taxes
  <tbody>
    <tr>
      <td>$ 5.00
      <td>$ 4.50
</table>
```

#### HTML 줄 바꿈

긴 줄은 끊어 사용한다(선택 사항).

HTML에 대한 열 제한 권장 사항은 없지만 가독성 향상을 위해 긴 줄은 줄바꿈 하는 것을 고려한다.

줄 바꿈할 때 줄 바꿈된 속성을 자식 요소와 구분하기위해 각 연속줄을 원래 줄에서 최소 4칸 더 들여써야 한다.

```html
<button mat-icon-button color="primary" class="menu-button"
    (click)="openMenu()">
  <mat-icon>menu</mat-icon>
</button>
```

```html
<button
    mat-icon-button
    color="primary"
    class="menu-button"
    (click)="openMenu()">
  <mat-icon>menu</mat-icon>
</button>
```

```html
<button mat-icon-button
        color="primary"
        class="menu-button"
        (click)="openMenu()">
  <mat-icon>menu</mat-icon>
</button>
```

#### HTML 따옴표

속성 값을 인용할 때 큰 따옴표를 사용한다.

속성 값 주위에 작음따옴표(' ') 대신 큰따옴표(" ")를 사용한다.

```html
<!-- 비추천 -->
<a class='maia-button maia-button-secondary'>Sign in</a>
```

```html
<!-- 추천 -->
<a class="maia-button maia-button-secondary">Sign in</a>
```

## CSS

### CSS 스타일 규칙

#### CSS 유효성

가능한 유효한 CSS를 사용하도록 한다.

CSS 유효성 검사기 버그를 처리하거나 독점 구문이 필요한 경우가 아니면 유효한 CSS코드를 사용하도록 한다.

[W3C CSS 유효성 검사기](https://jigsaw.w3.org/css-validator/)와 같은 툴을 이용하여 유효성 검사를 한다.

유효한 CSS를 사용하는 것은 효과가 없고 제거할 수 있는 CSS 코드를 찾아내고 적절한 CSS 사용을 보장하는 측정가능한 품질 기준이다.

#### Class 네이밍

일반적이고 의미있는 클래스 이름을 사용한다.

표현적이거나 애매모호한 이름 대신 항상 해당 요소의 목적을 반영하거나 일반적인 클래스 이름을 사용한다.

구체적이고 요소의 목적을 반영하는 이름은 이해하기 쉽고 변경될 가능성이 적기 때문에 이를 최우선 해야 한다.

일반적인 이름은 단순히 의미가 없거나 형제와 다른 의미가 없는 요소에 대한 대체이다. 그것들은 일잔적으로 "조력자"로 필요하다.

기능 또는 일반 이름을 사용하면 불필요한 문서 또는 템플릿 변경 가능성이 줄어 든다.

```css
/* 비추천: 무의미함 */
.yee-1901 {}

/* 비추천: 표현적임 */
.button-green {}
.clear {}
```

```css
/* 추천: 분명함 */
.gallery {}
.login {}
.video {}

/* 추천 : 일반적임 */
.aux {}
.alt {}
```

#### Class 이름 스타일

클래스 이름의 단어는 하이픈으로 구분한다.

이해와 가독성을 높이기 위해 선택기에서 단어와 약어를 하이픈 이외의 문자(전혀 없는 경우 포함)로 연결 하지 마라.

```css
/* 비추천 : “demo” 와 “image” 단어를 분리하지 않았다.  */
.demoimage {}

/* 비추천: 하이픈 대인 밑줄을 사용함 */
.error_status {}
```

```css
/* 추천 */
.video-id {}
.ads-sample {}
```

#### 접두사

응용 프로그램별 접두사가 있는 접두사 선택기(선택 사항).

대규모 프로젝트와 다른 프로젝트 또는 외부 사이트에 포함되는 코드의 경우 클래스 이름에 접두사(네임스페이스)를 사용한다. 짧고 고유한 식별자 뒤에 하이픈을
사용한다.

네임스페이스를 사용하면 이름 충돌을 방지하고 검색 및 바꾸기 작업 같은 유지 관리를 더 뒵게 할 수 있다.

```css
.adw-help {} /* AdWords */
.maia-note {} /* Maia */
```

#### Type 선택자

Type 선택자로 클래스 이름을 한정하지 않는다.

필요한 경우가 아니면(예: helper class), 요소이름을 클래스와 함께 사용하지 않는다.
 
불필요한 부모 선택자를 피하는 것은 [성능상의 이유](https://www.stevesouders.com/blog/2009/06/18/simplifying-css-selectors/)로 
유용하다.

```css
/* 비추천 */
ul.example {}
div.error {}
```

```css
/* 추천 */
.example {}
.error {}
```

#### ID 선택자

ID를 선택자로 사용하지 않는다.

ID 속성은 전체 페이지에서 고유해야 하므로 여러 개발자가 작업한 많은 구성 요소가 페이지에 포하되어 있는 경우 보장하기 어렵다. 모든 상황에서 클래스
선택자를 선호 해야 한다.

```css
/* 비추천 */
#example {}
```

```css
/* 추천 */
.example {}
```

#### 약식 속성

가능한 약식 속성을 사용하라.

CSS는 단 하나의 값만 명시적으로 설정 하는 경우에도 가능하다면 항상 사용해야하는 다양한 약식 속성(예: ```font```)을 제공한다.

약식 속성을 사용하면 코드 효율성과 가독성에 유용하다.

```css
/* 비추천 */
border-top-style: none;
font-family: palatino, georgia, serif;
font-size: 100%;
line-height: 1.6;
padding-bottom: 2em;
padding-left: 1em;
padding-right: 1em;
padding-top: 0;
```

```css
/* 추천 */
border-top: 0;
font: 100%/1.6 palatino, georgia, serif;
padding: 0 1em 2em;
```

#### 0과 단위

필요한 경우가 아니라면 "0"값 뒤에 단위 지정을 생략한다.

필요한 경우가 아니라면 ```0```값 뒤에 단위를 사용하지 마라.

```css
flex: 0px; /* 이 flex-basis 컴포넌트는 단위가 필요하다. */
flex: 1 1 0px; /* 단위 없이는 모호하지 않지만 IE11에서는 필요하다. */
margin: 0;
padding: 0;
```

#### 선행 0

값에 항상 선행 "0"을 포함한다.

-1과 1 사이의 값이나 길이 앞에 ```0```을 사용한다.

```css
font-size: 0.8em;
```

#### 16진수 표기법

가능하면 3자의 16진수 표기법을 상용하라.

허용하는 색상의 값의 경우 3자 16진수 표기법이 더 짧고 간결하다.

```css
/* 비추천 */
color: #eebbcc;
```

```css
/* 추천 */
color: #ebc;
```

#### Important 선언

```!important``` 선언을 사용하지 마라.

이러한 선언은 CSS의 자연스러운 캐스케이드를 깨고 스타일을 추론하고 구성하기 어렵게 만든다. 대신 선택자 특정성을 사용하여 속성을 재정의 하라.

```css
/* 비추천 */
.example {
  font-weight: bold !important;
}
```

```css
/* 추천 */
.example {
  font-weight: bold;
}
```

#### Hacks

사용자 에이전트 감지와 CSS "hacks" 사용을 자재 하고, 먼저 다른 접근 방식을 시도하라.

스타일 차이를 해결하기 위해 사용자 에이전트 감지 또는 특수 CSS 필터, 해결방법 및 핵 사용에 대한 유혹에 빠질 수 있다. 하지만 두 접근 방식 모두 
효율적으로 관리 가능한 코드를 유지하기 위해 최후의 수단으로 간주하여야 한다. 에이전트 감지 및 핵은 적은 비용을 지불하고 팀원들에게 저항을 적게 받는
경향이 있지만 장기적으로 프로젝트에 피해를 줄 수 있다. 에이전트 감지 및 핵을 허용하고 사용하기 쉽게 만들면 에이전트 감지 및 핵 사용을 더 자유롭고 자주
사용하게 할 것이다.

### CSS 서식 규칙

#### 선언 순서

선언을 알파벳순으로 지정한다(선택 사항).

프로젝트 내에서 일관되게 선언을 정렬한다. 정렬 순서를 일관되게자동화하고 적용하기 위한 도구가 없을 경우 일관되 코드를 작성하기 위해 선어을 알파벳 순서로 
배치하는 것을 려한다. 이러한 방식은 코드를 수동으로 쉽게 유지 관리하고 학습 및 기억하기 쉽게 만들어 준다.

정렬을 위해 브라우저별 접두사를 무시한다. 그러나 특정 CSS 속성에 대한 여러 브라우저별 접두사는 정렬된 상태로 유지한다.(예: -mod 접두사는 -webkit 
앞에 옴).

```css
background: fuchsia;
border: 1px solid;
-moz-border-radius: 4px;
-webkit-border-radius: 4px;
border-radius: 4px;
color: black;
text-align: center;
text-indent: 2em;
```

#### 블록 컨텐츠 들여쓰기

모든 블록 컨텐츠는 들여쓰기 한다.

모든 [블록 컨텐츠](https://www.w3.org/TR/CSS21/syndata.html#block), 즉 규칙 내의 규치과 선언을 들여쓰기하여 계층 구조를 반연하고 이해도를 
높인다.

```html
@media screen, projection {

  html {
    background: #fff;
    color: #444;
  }

}
```

#### 선언 완료

모든 선언 뒤에 세미콜론을 사용한다.

일관성과 확장성을 위해 모든 선언을 세미콜론으로 끝낸다.

```css
/* 비추천 */
.test {
  display: block;
  height: 100px
}
```

```css
/* 추천 */
.test {
  display: block;
  height: 100px;
}
```

#### 속성 이름 완료

속성 이름의 콜론 뒤에 공백을 사용한다.

일관성을 위해 항상 속성과 값 사이의 공백을 하나만 사용한다(속성과 콜론 사이에는 공백이 없음).

```css
/* 비추천 */
h3 {
  font-weight:bold;
}
```

```css
/* 추천 */
h3 {
  font-weight: bold;
}
```

#### 선언 블로 분리

마지막 선택자와 선언 블록 상이에 공백을 사용한다.

마지막 선택자와 선언 블로을 시작하는 여는 중괄호 사이에는 항상 공백 하나를 사용한다.

여는 중괄호는 주어진 규칙의 마지막 선택자와 같은 줄에 있어야한다.

```css
/* 비추천 : 공백 없음 */
.video{
  margin-top: 1em;
}

/* 비추천 : 불필요한 줄 바꿈 */
.video
{
  margin-top: 1em;
}
```

```css
/* 추천 */
.video {
  margin-top: 1em;
}
```

#### 선택자와 선언 분리

새줄로 선택자와 선언을 분리한다.

각 선택자와 선언은 항상 새 줄로 시작한다.

```css
/* 비추천 */
a:focus, a:active {
  position: relative; top: 1px;
}
```

```css
/* 추천 */
h1,
h2,
h3 {
  font-weight: normal;
  line-height: 1.2;
}
```

#### 규칙 분리

새 줄로 규칙을 분리한다.

규칙 사이는 항상 빈 줄(두 줄 바꿈)을 사용한다.

```css
html {
  background: #fff;
}

body {
  margin: auto;
  width: 50%;
}
```

#### CSS 따옴표 

속성 선택기 및 속성 값에 큰따옴표(" ")대신 작은 따옴표(' ')를 사용한다.

URI 값(url())에 따옴표를 사용하지 않는다.

예외 : @charset 규칙을 사용해야 하는 경우 큰따옴표를 사용한다. - [작은 따옴표 허용하지 않음](https://www.w3.org/TR/CSS21/syndata.html#charset)

```css
/* 비추천 */
@import url("https://www.google.com/css/maia.css");

html {
  font-family: "open sans", arial, sans-serif;
}
```

```css
/* 추천 */
@import url(https://www.google.com/css/maia.css);

html {
  font-family: 'open sans', arial, sans-serif;
}
```

### CSS 메타 규칙

#### 섹션 설명

섹션 주석으로 섹션을 그룹화 한다(선택 사항).

가능하면 주석을 사용하여 스타일 시트 섹션을 그룹화 하고 새 줄로 섹션을 구분한다.

```css
/* Header */

.adw-header {}

/* Footer */

.adw-footer {}

/* Gallery */

.adw-gallery {}
```

#### 맺음 말

코드의 일관성을 유지하세요. 코드르 편집하는 경우 몇 분 정도 시간을 내어 주변 코드를 살펴보고 스타일을 결정하세요. 주변 코드가 모든 산술 연산자 주위에 
공백을 사용하는 경우 그렇게 해야 합니다. 댓글 주변에 작은 해시 마크 상자가 있는 경우 댓글 주위 작은 해시 마크 상자가 포함되도록 해야합니다. 스타일 
가이드 라인의 요점은 사람들이 당신이 말하는 방식보다는 당신이 말하는 것에 집중할 수 있도록 코딩의 공통 어휘를 갖는 것입니다. 사람들이 어휘를 알 수 
있도록 글로벌 스타일 규칙을 제시하지만 현지 스타일도 중요합니다. 파일에 추가한 코드가 주변의 기존 코드와 크게 다르게 보이면 독자가 파일을 읽을 때
리듬에서 벗어나게 됩니다. 이것을 피하세요.
