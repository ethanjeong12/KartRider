# wekart 소개

국내 최대 게임회사인 넥슨의 오랜기간 사랑받는 캐쥬얼 레이싱 장르인 카트라이더의 전적 정보를 제공하는 [Kartrider TMI](https://tmi.nexon.com/kart)를 클론하는 프로젝트입니다. 공식 홈페이지와는 다르게 소셜 로그인 기능이 없어 클론하지 않고 직접 개발하였으며 추가적으로 소셜계정과 실제 카트라이더 유저의 계정을 연동하는 기능도 추가하였습니다. 개발 인원은 총 5명이며 백엔드 3명 프론트엔드 2명으로 구성되었으며 여담으로 게임회사 출신이 저 포함 3명이나 되는 팀이었습니다.

- [Backend github](https://github.com/wecode-bootcamp-korea/9-5dragon-backend)
- [Frontend github](https://github.com/wecode-bootcamp-korea/9-5dragon-frontend)

## Demo
[![](https://images.velog.io/images/yongineer1990/post/87664e61-d90c-469b-8678-24f42405b1e6/image.png)*동영상 보기*](https://youtu.be/Av_p4sCT4Wg)

## 적용 기술 (Backend)

- Python
- Django
- Beautifulsoup
- Selenium
- Requests
- Pandas
- Crontab
- Design Pattern : Abstract factory
- Bcrypt
- JWT
- Social Login : KAKAO
- Mysql
- CORS headers
- AWS : EC2, RDS, S3
- Git Rebase

## Modeling
![](https://yongnas.iptime.org/images/KartRider_modeling.png)

## 구현 기능
### 소셜로그인 및 회원가입
- Kakao 소셜 로그인을 지원합니다.
- 만약 User 테이블에 해당 회원이 없다면 가입시킵니다.
- Password는 암호화(Bycrpt)과정을 거칩니다.
- Frontend에서 전달받은 사용자 정보가 User 테이블에 저장된 사용자인지 검증합니다.
- 로그인 성공시 JWT Access Token을 발급합니다.
### 게임유저 연동
- 소셜로그인에 성공하면 게임유저의 닉네임을 받아 연동시킵니다.
### 랭크 리스트
- 개인전과 팀전 TOP 100위의 유저 랭크 리스트가 제공됩니다.
  - 유저 닉네임
  - 순위
  - 승률
  - 리타이어율
### 랭크 상세 정보
- 개인전과 팀전의 랭크 상세정보를 제공합니다.
   - 유저 캐릭터
   - 유저 닉네임
   - 누적 플레이 횟수
   - 누적 승
   - 누적 패
   - 승률
   - 완주율
   - 리타이어율
   - 누적 순위 평균
   - 최근 50경기 순위 평균
   - 최근 50경기 순위 리스트
### 댓글작성
- 해당 유저의 랭크 상세정보에서 댓글 작성 기능을 제공합니다.
- 회원만 작성가능 하도록 JWT Access Token 검증합니다.
- 랭크 상세정보 페이지 입장시 해당 유저에 대한 댓글을 전달합니다.
### 트랙 상세 정보
- 개인전과 팀전의 랭크 상세정보에서 해당 유저의 트랙별 기록을 제공합니다.
  - 트랙 이름
  - 트랙별 승률
  - 트랙별 기록 분포
  - 트랙별 최고 기록
### 매치 상세 정보
- 개인전과 팀전의 랭크 상세정보에서 해당 유저의 매치별 기록을 제공합니다.
  - 유저의 모든 매치 리스트
  - 매치별 유저 순위
  - 매치가 열린 트랙
  - 매치에서 사용한 카트
  - 해당 매치에서 유저 기록
  - 참가 유저 정보
    - 참가 유저 닉네임
    - 참가 유저가 사용한 카트
    - 참가 유저의 기록
