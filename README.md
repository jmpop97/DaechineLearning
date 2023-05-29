# DaechineLearning

# 프로젝트 개요
    본 프로젝트에서는 사용자가 음악을 추천할 수 있고 소개된 음악을 감상하며 게시글에 머문 시간을 통해 장르 선호도를 예상하고 그에 맞는 음악을 추천해줄 수 있습니다.

# 설치 및 설정
    본 프로젝트에 사용된 라이브러리는 requirements.txt를 따릅니다.

# 프로젝트 설명
## 모델 설명
### 공통모델
    - 사용자의 삭제요청에 따라 DB에 저장된 데이터를 즉각 삭제하는 방법이 아닌 삭제 상태 값을 변경하여 관리할 수 있도록 작성됐습니다.
    이는 사용자에 의한 복구요청에 대응할 수 있으며 본 프로젝트에서 구현되지 않았지만 추후 기간설정을 통한 DB관리까지도 고려하여 적용했습니다.
    - 모든 모델에 적용될 수 있도록 공통필드를 가진 모델을 작성한 후 이를 상속받아 모델작성이 진행됐습니다.

### 유저모델
    - 흠......................................................... 유저는 잘몰라서 어떻게 쓰죠...?

### 게시글 모델
    - 게시글 모델은 open api를 통해 받아온 데이터로 music모델을 생성하고 music모델을 참조하는 모델로 생성됩니다.

### 음악 모델
    - spotify open api를 통해 받아온 데이터로 생성합니다.
    - 단독적으로 생성하는게 아닌 사용자가 추천하고자 하는 음악을 검색하여 가져왔을때 게시글과 같이 생성되도록 작성하였습니다.

### 장르 모델
    - 서버 최초 실행시 spotify open api를 통해 받아온 장르 목록을 베이스로 장르 모델을 생성, 게시글 모델과 관계테이블 모델로 연결되어있습니다.

### 이모티콘 모델
    - 두개 이상의 이미지를 연결하기 위해 이미지모델을 분리하여 작성했고  사용할 이모티콘을 선택할 수 있도록 사용자 모델과 이모티콘 모델의 관계테이블 모델로 연결되어 있습니다. 

#### 관계테이블 모델
    - 이는 데이터 변동시 조금 더 유연하게 대응할 수 있도록 채택했습니다.

## 기능 설명
    spotify open api를 통해 받아온 음악별 게시글을 작성할 수 있습니다. 

    최초 메인페이지에서는 작성된 게시글들을 확인할 수 있고 게시글 조회 및 댓글 조회는 로그인 없이도 이용할 수 있도록 진행됐습니다.
    이외의 기능을 사용하기 위해서는 회원 권한이 요구되며 회원가입은 이메일 인증을 통해 완료할 수 있습니다.

### 유저관련?
    - 

### 게시글 작성
    음악을 추천할 수 있는 게시글을 작성하는 기능입니다.
        - 게시글 작성에서는 본 프로젝트의 목적에 따라 Music모델을 기반으로 작성할 수 있도록 구현돼 있으며, Music모델은 open api에서 가져온 데이터를 기반으로 생성하게 됩니다.
        - 게시글 작성 페이지의 음악검색을 통해 생성하고자 하는 Music모델의 데이터를 받아 작성되는 게시글의 참조모델로 들어가게 됩니다.
        - 제목과 내용에는 사용자가 입력하고자 하는 값을 받습니다.
        - 장르 필드 에서는 저장된 데이터 중에서 선택할 수 있도록 구현되어있습니다. 두가지 이상의 장르를 선택할 수 있습니다.

### 게시글 상세보기
    작성된 게시글의 상세페이지를 조회하는 기능입니다.
        - 상세보기 페이지에서는 본 프로젝트의 기획 목적에 사용될 사용자의 머문시간을 서버로 받을 수 있게 구현됐습니다.
        - 사용자가 페이지에 머문시간이 90초가 지나면 설정한 값을 서버로 받아올 수 있고 이를 활용하여 사용자의 선호도를 예상하고자 합니다.
        - 게시글 작성자만 수정 또는 삭제가 가능합니다.

### 댓글
    게시글에 작성할 수 있는 댓글 기능입니다.
        - 이모티콘과 댓글내용 둘중 하나이상의 값이 있어야 작성가능합니다.
        - 이모티콘을 사용하지 않는경우 불필요한 서버요청을 줄이기 위해 이모티콘버튼 클릭시에 서버요청을 실행하도록 구현했습니다.
        - 수정 / 삭제 는 작성한 사용자만 가능합니다.

### 이모티콘
    댓글 작성시 사용 가능한 이모티콘 기능입니다. 
        - 사용자가 원하는 이미지를 업로드하여 직접 제작할 수 있도록 이모티콘 만들기 기능이 있습니다.
        - 만들어진 모든 이모티콘은 공유되며 사용자별로 이모티콘을 선택하여 사용할 수 있도록 구현했습니다.
        - 이모티콘 수정 / 삭제는 작성한 사용자만 가능합니다.


## API 설계
|url|Method|기능|Request|Response|
|---|------|---|-------|--------|
|articles/music/api |METHOD|api 트랙 1000 목록 조회|request|response|
|articles/music/api |GET|api 트랙 1000 목록 조회|{id:"str", popularity:int, genre:"str", "images":"url", "name":"str", "preview_url":"url", "artist":"str"}||
|articles/music/api/token |POST|API 토큰 조회|{"access_token":"access_token"}||
|articles/music/api/search |POST|api 이용 해당 하는 title 음악 검색|{"query":"title", "limit":int}||
|articles/music/api/music-id-search |POST|api 이용 단일 음악 검색 preview_url 끌어오기 용|{"preview_url":"preview_music"}||
|articles/music/api/save_music |POST|api 이용 검색한 음악데이터 db에 저장|{"user":"User.objects.get(id=user)","name":"name","artist":"artist","album":"album","music_id":"music_id","images":"images"}||
|articles|GET, PUT|게시글 조회 및 작성||{"user", "title", "content","images","music_id","music_search","created_at","updated_at"}|
|articles/<int:pk>|GET, PUT, DELETE|게시글 상세 조회,수정,삭제||{"user", "title", "content","images","music_id","music_search","created_at","updated_at"}|
|articles/genre|GET, POST|장르 조회, 수정||{"genre"}|
|articles/genre/<int:genre_id>|GET, POST|장르 수정, 삭제||{"genre"}|
|articles/<int:article_id>/genre|GET, POST, DELETE|게시글 장르 조회 생성 삭제||{"genre","article","user", "title", "content","images","music_id","music_search}|
|articles/genre/restore|GET, POST, DELETE|genre db status변경 시 관련 테이블 복구|||
|comments/<int:article_id>/comment|GET, POST, PUT, DELETE|게시글 댓글 가져오기, 생성||{"article","user", "title", "content","images","music_id","music_search"}|
|comments/<int:article_id>/comment/<int:comment_id>|GET, POST, PUT, DELETE|게시글 댓글 수정, 삭제||{"article","user", "title", "content","images","music_id","music_search"}|
|comments/emoticon|GET, POST, PUT, DELETE|이모티콘 전체조회 및 제작|{"title":"제목","used_emoticon":"이미지 경로"}|{"title", "used_emoticon"}|
|comments/emoticon/images|GET|이모티콘 이미지 전체조회||{"creator", "title", "emoticon", "image"}|
|comments/emoticon/detail/<int:emoticon_id>|GET|이모티콘 자세히 보기 / 수정|||
|comments/emoticon/<int:user_id>|GET, POST, DELETE|유저가 가진 이모티콘 조회 / 선택|||
|comments/emoticon/<int:user_id>/base|GET|기본 이모티콘 가져오기|||
|users/dj-rest-auth|POST|일반 회원 회원가입/로그인|request|response|
|users/dj-rest-auth/registration|POST|일반 회원 회원가입/로그인|request|response|
|users/active|POST|유저가 클릭한 이메일(=링크) 확인|request|response|
