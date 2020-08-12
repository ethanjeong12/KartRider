# wekart

[Kartrider TMI](https://tmi.nexon.com/kart) is the platform that provides insights and statistics to gamers for Nexon(The biggest video game publisher in Korea)'s Kart Rider. Original website does not provide social login function, so social login function was added. Additionally, we mapped each social user to the actual game user.

This project was done by 3 backends and 2 frontends

- [Backend github](https://github.com/wecode-bootcamp-korea/9-5dragon-backend)
- [Frontend github](https://github.com/wecode-bootcamp-korea/9-5dragon-frontend)

## Demo
[![](https://images.velog.io/images/yongineer1990/post/87664e61-d90c-469b-8678-24f42405b1e6/image.png)*동영상 보기*](https://youtu.be/Av_p4sCT4Wg)

## Applied Skills (Backend)

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

## API's
### Social Login
- Provides Social Login with KaKao (A free mobile instant messaging application for smartphones with free text and free call features, operated by Kakao Corporation.)
- If the user info is not in DB, very user is registered.
- Password was hashed via Bcrpyt.
- If login was successfull, JWT Access Token is published.

### Mapping Social User to the Game User
- When Social Login is done, that user is mapped with the actual game user with necessary information such as email and name.

### Rank List
- Provides rank List of Top 100 users in individual matches and team matches.
  - User Nickname
  - Rank
  - Win Percentage
  - Retire Percentage

### Rank Detail Info
- Provides detailed information about the individual matches and team matches.
  - Character used by the user
  - User Nickname
  - Total Played Times
  - Total Wins
  - Total Losses
  - Win Percentage
  - Complete Percentage
  - Retire Percentage
  - Average Total Rank
  - Average Rank of Last 50 Matches
  - List of Ranks in Last 50 Matches

### Comment
- In each user's rank detail page, any logged in user can leave a comment.
- Checks JWT Access Token in order to verify the user.

### Track Detail Info
- Provides information about certain tracks.
  - Track Name
  - Track Win Percentage
  - Track Records Normal Distribution Graph
  - Track's Best Records
  
### Match Detail Info
- Provides information about certain matches.
  - List of All Matches
  - User's Rank in Match
  - Track Info
  - Kart Info
  - User's Record in that track
  - All Users' Info in that match.
