# 피트니스 트래커 (Fitness Tracker)

체계적인 운동 관리를 위한 Flask 웹 애플리케이션입니다.

## 🌟 주요 기능

### 📋 운동 종목 관리
- 운동 종목 등록/수정/삭제
- 운동 부위별 분류 (가슴, 등, 하체, 어깨, 팔, 코어, 전신, 유산소)
- 난이도별 관리 (초급, 중급, 고급)

### 📊 운동 기록 관리
- 상세한 운동 기록 (날짜, 종목, 세트수, 횟수, 무게, 소요시간)
- 운동 세션별 관리
- 메모 기능으로 개인적인 소감 기록

### 📈 통계 대시보드
- 주/월별 운동 빈도 차트
- 총 운동 시간 및 평균 시간
- 부위별 운동 분포 (도넛 차트)
- 운동 히트맵으로 패턴 분석

### 🎯 목표 설정 및 추적
- SMART 목표 설정 (구체적, 측정가능, 달성가능, 현실적, 시간제한)
- 진행률 실시간 추적
- 목표 유형별 관리 (주간, 월간, 연간)
- 목표 달성 알림

### 📅 달력 기반 일정 관리
- 월별 운동 기록 시각화
- 운동 계획 추가 및 관리
- 운동 일관성 분석
- 월간 통계 및 성과 요약

## 🛠 기술 스택

### Backend
- **Flask 3.0.0** - 웹 프레임워크
- **SQLAlchemy** - ORM
- **SQLite** - 데이터베이스

### Frontend
- **Bootstrap 5** - UI 프레임워크
- **Chart.js** - 데이터 시각화
- **Bootstrap Icons** - 아이콘

### 배포
- **Gunicorn** - WSGI 서버
- **Heroku** 지원 (Procfile 포함)

## 📦 설치 및 실행

### 1. 저장소 클론
```bash
git clone <repository-url>
cd fitness-tracker
```

### 2. 가상환경 생성 및 활성화
```bash
python -m venv venv

# Windows
venv\\Scripts\\activate

# macOS/Linux
source venv/bin/activate
```

### 3. 패키지 설치
```bash
pip install -r requirements.txt
```

### 4. 애플리케이션 실행
```bash
python app.py
```

또는 프로덕션 모드로:
```bash
python run.py
```

### 5. 브라우저에서 접속
```
http://localhost:5000
```

## 📁 프로젝트 구조

```
fitness-tracker/
├── app.py                 # 메인 애플리케이션
├── run.py                 # 실행 스크립트
├── config.py              # 설정 파일
├── requirements.txt       # 패키지 의존성
├── Procfile              # Heroku 배포용
├── README.md             # 프로젝트 문서
├── templates/            # HTML 템플릿
│   ├── base.html
│   ├── index.html
│   ├── exercises.html
│   ├── add_exercise.html
│   ├── edit_exercise.html
│   ├── workouts.html
│   ├── add_workout.html
│   ├── dashboard.html
│   ├── goals.html
│   ├── add_goal.html
│   └── calendar.html
└── fitness_tracker.db    # SQLite 데이터베이스 (자동 생성)
```

## 🗃 데이터베이스 구조

### Users (사용자)
- id, username, email, created_at

### Exercises (운동 종목)
- id, name, body_part, difficulty, description, created_at

### WorkoutSessions (운동 세션)
- id, user_id, date, start_time, end_time, total_duration, notes, created_at

### WorkoutRecords (운동 기록)
- id, session_id, exercise_id, sets, reps, weight, duration, created_at

### Goals (목표)
- id, user_id, title, description, target_value, current_value, unit, goal_type, target_date, is_achieved, created_at

## 🔧 환경 변수

개발 환경에서는 기본값이 사용되지만, 프로덕션에서는 다음 환경 변수를 설정하세요:

```bash
SECRET_KEY=your-secret-key-here
DATABASE_URL=your-database-url
FLASK_ENV=production
```

## 🚀 배포

### Heroku 배포
```bash
# Heroku CLI 설치 후
heroku create your-app-name
heroku config:set SECRET_KEY=your-secret-key-here
heroku config:set FLASK_ENV=production
git push heroku main
```

### 로컬 프로덕션 테스트
```bash
FLASK_ENV=production python run.py
```

## 📱 사용법

### 1. 운동 종목 등록
1. "운동 종목" 메뉴 선택
2. "새 운동 추가" 버튼 클릭
3. 운동 정보 입력 (이름, 부위, 난이도)

### 2. 운동 기록 추가
1. "운동 기록" 메뉴 선택
2. "새 운동 기록" 버튼 클릭
3. 운동 정보 입력 (날짜, 시간, 세부 기록)

### 3. 목표 설정
1. "목표" 메뉴 선택
2. "새 목표 추가" 버튼 클릭
3. SMART 목표 설정

### 4. 통계 확인
1. "대시보드" 메뉴에서 전체 통계 확인
2. 차트를 통한 시각적 분석
3. 주간/월간/연간 필터 적용

### 5. 일정 관리
1. "달력" 메뉴 선택
2. 월별 운동 기록 확인
3. 운동 계획 추가

## 🎨 주요 특징

- **반응형 디자인**: 모바일, 태블릿, 데스크톱 모든 기기 지원
- **직관적 UI**: Bootstrap 5 기반의 현대적 인터페이스
- **실시간 차트**: Chart.js를 활용한 인터랙티브 시각화
- **데이터 보안**: SQLAlchemy ORM을 통한 안전한 데이터 관리
- **확장 가능**: 모듈화된 구조로 기능 추가 용이

## 🔄 향후 개발 계획

- [ ] 사용자 인증 시스템
- [ ] 운동 타이머 기능
- [ ] 운동 루틴 템플릿
- [ ] 소셜 기능 (친구, 랭킹)
- [ ] 모바일 앱 (React Native/Flutter)
- [ ] API 문서화 (Swagger)
- [ ] 데이터 내보내기/가져오기
- [ ] 운동 동영상 연결
- [ ] AI 기반 운동 추천

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 문의

프로젝트에 대한 질문이나 제안사항이 있으시면 이슈를 생성해주세요.

---

⭐ 이 프로젝트가 도움이 되셨다면 스타를 눌러주세요!



