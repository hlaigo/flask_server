# AIGO API 사용 가이드


### 토큰 등록하기
기본 정보
|메서드|URL|인증방식
|---|---|---|
|POST|https://hlaigo.co.kr/regist/token|-|

디바이스의 토큰 정보를 등록합니다.  
디바이스명(Key)과 토큰(Value)을 Dict 형식으로 저장됩니다.  
응답 본문은 msg로 구성된 Json 객체입니다.

요청

헤더
|이름|설명|필수|
|---|---|---|
|Content-Type|Content-Type: application/json<br>요청 데이터 타입|O|

퀴리 파라미터
|이름|타입|설명|필수|
|---|---|---|---|
|device_name|String|디바이스명|O|
|device_token|String|디바이스 토큰|O|

응답

본문
|이름|타입|설명|
|---|---|---|
|msg|String|작업 완료 메시지    |

예제

요청
```bash
curl -v -X POST "https://hlaigo.co.kr/regist/token" \
    -H "Content-Type: application/json" \
    -d '{
        "device_name": "TestDevice",
        "device_token": "TestDeviceToken"
        }'
```

응답: 성공
```http
HTTP/1.1 200 OK
Content-Type: application/json
{
  "msg": "Regist Success"
}
```
응답: 실패
```http
HTTP/1.1 400 BAD REQUEST
Content-Type: application/json
{
  "msg": "Incorrect Data Type"
}
```
***
### 테스트 알림 요청하기
기본 정보
|메서드|URL|인증방식
|---|---|---|
|POST|https://hlaigo.co.kr/test/notify|-|

디바이스에 알림을 전송합니다.  
해당 기능 사용 전 토큰 등록을 진행 해야합니다.
디바이스명(Key)과 토큰(Value)을 Dict 형식으로 저장됩니다.  
응답 본문은 msg로 구성된 Json 객체입니다.

요청

헤더
|이름|설명|필수|
|---|---|---|
|Content-Type|Content-Type: application/json<br>요청 데이터 타입|O|

퀴리 파라미터
|이름|타입|설명|필수|
|---|---|---|---|
|device_name|String|디바이스명|O|
|device_token|String|디바이스 토큰|O|

응답

본문
|이름|타입|설명|
|---|---|---|
|msg|String|작업 완료 메시지    |

예제

요청
```bash
curl -v -X POST "https://hlaigo.co.kr/regist/token" \
    -H "Content-Type: application/json" \
    -d '{
        "device_name": "TestDevice",
        "device_token": "TestDeviceToken"
        }'
```

응답: 성공
```http
HTTP/1.1 200 OK
Content-Type: application/json
{
  "msg": "Regist Success"
}
```
응답: 실패
```http
HTTP/1.1 400 BAD REQUEST
Content-Type: application/json
{
  "msg": "Incorrect Data Type"
}
```