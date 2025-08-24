from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta, date
from sqlalchemy import func, extract
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fitness_tracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 데이터베이스 모델
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    body_part = db.Column(db.String(50), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class WorkoutSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    total_duration = db.Column(db.Integer)  # 분 단위
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class WorkoutRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('workout_session.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.id'), nullable=False)
    sets = db.Column(db.Integer, nullable=False)
    reps = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float)
    duration = db.Column(db.Integer)  # 분 단위
    distance = db.Column(db.Float)  # km 단위 (유산소 운동용)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 관계 설정
    exercise = db.relationship('Exercise', backref='records')
    session = db.relationship('WorkoutSession', backref='records')

class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    target_value = db.Column(db.Float, nullable=False)
    current_value = db.Column(db.Float, default=0)
    unit = db.Column(db.String(20), nullable=False)
    goal_type = db.Column(db.String(50), nullable=False)  # weekly, monthly, yearly
    target_date = db.Column(db.Date)
    is_achieved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class WeightRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    weight = db.Column(db.Float, nullable=False)  # kg 단위
    date = db.Column(db.Date, nullable=False)
    body_fat_percentage = db.Column(db.Float)  # 체지방률 (선택사항)
    muscle_mass = db.Column(db.Float)  # 근육량 (선택사항)
    notes = db.Column(db.Text)  # 메모
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 관계 설정
    user = db.relationship('User', backref='weight_records')

# 라우트
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/exercises')
def exercises():
    exercises = Exercise.query.all()
    return render_template('exercises.html', exercises=exercises)

@app.route('/exercises/add', methods=['GET', 'POST'])
def add_exercise():
    if request.method == 'POST':
        exercise = Exercise(
            name=request.form['name'],
            body_part=request.form['body_part'],
            difficulty=request.form['difficulty'],
            description=request.form.get('description', '')
        )
        db.session.add(exercise)
        db.session.commit()
        flash('운동 종목이 성공적으로 추가되었습니다!', 'success')
        return redirect(url_for('exercises'))
    return render_template('add_exercise.html')

@app.route('/exercises/edit/<int:id>', methods=['GET', 'POST'])
def edit_exercise(id):
    exercise = Exercise.query.get_or_404(id)
    if request.method == 'POST':
        exercise.name = request.form['name']
        exercise.body_part = request.form['body_part']
        exercise.difficulty = request.form['difficulty']
        exercise.description = request.form.get('description', '')
        db.session.commit()
        flash('운동 종목이 성공적으로 수정되었습니다!', 'success')
        return redirect(url_for('exercises'))
    return render_template('edit_exercise.html', exercise=exercise)

@app.route('/exercises/delete/<int:id>')
def delete_exercise(id):
    exercise = Exercise.query.get_or_404(id)
    db.session.delete(exercise)
    db.session.commit()
    flash('운동 종목이 삭제되었습니다!', 'success')
    return redirect(url_for('exercises'))

@app.route('/workouts')
def workouts():
    sessions = WorkoutSession.query.order_by(WorkoutSession.date.desc()).all()
    return render_template('workouts.html', sessions=sessions)

@app.route('/workouts/add', methods=['GET', 'POST'])
def add_workout():
    if request.method == 'POST':
        # 안전한 숫자 변환 함수
        def safe_int(value, default=0):
            try:
                return int(value) if value and value.strip() else default
            except (ValueError, AttributeError):
                return default
        
        def safe_float(value, default=0.0):
            try:
                return float(value) if value and value.strip() else default
            except (ValueError, AttributeError):
                return default
        
        session = WorkoutSession(
            user_id=1,  # 임시로 1번 사용자
            date=datetime.strptime(request.form['date'], '%Y-%m-%d').date(),
            total_duration=safe_int(request.form.get('duration')),
            notes=request.form.get('notes', '')
        )
        db.session.add(session)
        db.session.flush()
        
        # 운동 기록 추가
        exercises = request.form.getlist('exercise_id')
        sets_list = request.form.getlist('sets')
        reps_list = request.form.getlist('reps')
        weight_list = request.form.getlist('weight')
        exercise_duration_list = request.form.getlist('exercise_duration')
        distance_list = request.form.getlist('distance')
        
        for i, exercise_id in enumerate(exercises):
            if exercise_id and exercise_id.strip():
                record = WorkoutRecord(
                    session_id=session.id,
                    exercise_id=safe_int(exercise_id),
                    sets=safe_int(sets_list[i] if i < len(sets_list) else ''),
                    reps=safe_int(reps_list[i] if i < len(reps_list) else ''),
                    weight=safe_float(weight_list[i] if i < len(weight_list) else ''),
                    duration=safe_int(exercise_duration_list[i] if i < len(exercise_duration_list) else ''),
                    distance=safe_float(distance_list[i] if i < len(distance_list) else '')
                )
                db.session.add(record)
        
        db.session.commit()
        flash('운동 기록이 성공적으로 추가되었습니다!', 'success')
        return redirect(url_for('workouts'))
    
    exercises = Exercise.query.all()
    return render_template('add_workout.html', exercises=exercises)

@app.route('/workouts/edit/<int:id>', methods=['GET', 'POST'])
def edit_workout(id):
    session = db.session.get(WorkoutSession, id)
    if not session:
        flash('해당 운동 기록을 찾을 수 없습니다.', 'error')
        return redirect(url_for('workouts'))
    
    if request.method == 'POST':
        # 안전한 숫자 변환 함수
        def safe_int(value, default=0):
            try:
                return int(value) if value and value.strip() else default
            except (ValueError, AttributeError):
                return default
        
        def safe_float(value, default=0.0):
            try:
                return float(value) if value and value.strip() else default
            except (ValueError, AttributeError):
                return default
        
        # 세션 정보 업데이트
        session.date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        session.total_duration = safe_int(request.form.get('duration'))
        session.notes = request.form.get('notes', '')
        
        # 기존 운동 기록 삭제
        WorkoutRecord.query.filter_by(session_id=session.id).delete()
        
        # 새로운 운동 기록 추가
        exercises = request.form.getlist('exercise_id')
        sets_list = request.form.getlist('sets')
        reps_list = request.form.getlist('reps')
        weight_list = request.form.getlist('weight')
        exercise_duration_list = request.form.getlist('exercise_duration')
        distance_list = request.form.getlist('distance')
        
        for i, exercise_id in enumerate(exercises):
            if exercise_id and exercise_id.strip():
                record = WorkoutRecord(
                    session_id=session.id,
                    exercise_id=safe_int(exercise_id),
                    sets=safe_int(sets_list[i] if i < len(sets_list) else ''),
                    reps=safe_int(reps_list[i] if i < len(reps_list) else ''),
                    weight=safe_float(weight_list[i] if i < len(weight_list) else ''),
                    duration=safe_int(exercise_duration_list[i] if i < len(exercise_duration_list) else ''),
                    distance=safe_float(distance_list[i] if i < len(distance_list) else '')
                )
                db.session.add(record)
        
        db.session.commit()
        flash('운동 기록이 성공적으로 수정되었습니다!', 'success')
        return redirect(url_for('workouts'))
    
    exercises = Exercise.query.all()
    return render_template('edit_workout.html', session=session, exercises=exercises)

@app.route('/workouts/delete/<int:id>')
def delete_workout(id):
    session = db.session.get(WorkoutSession, id)
    if not session:
        flash('해당 운동 기록을 찾을 수 없습니다.', 'error')
        return redirect(url_for('workouts'))
    
    # 관련된 운동 기록들도 함께 삭제
    WorkoutRecord.query.filter_by(session_id=session.id).delete()
    db.session.delete(session)
    db.session.commit()
    
    flash('운동 기록이 삭제되었습니다!', 'success')
    return redirect(url_for('workouts'))

@app.route('/dashboard')
def dashboard():
    # 통계 데이터 계산
    today = datetime.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # 주간 운동 횟수
    weekly_sessions = WorkoutSession.query.filter(
        WorkoutSession.date >= week_ago
    ).count()
    
    # 월간 운동 횟수
    monthly_sessions = WorkoutSession.query.filter(
        WorkoutSession.date >= month_ago
    ).count()
    
    # 총 운동 시간 (분)
    total_duration = db.session.query(func.sum(WorkoutSession.total_duration)).scalar() or 0
    
    # 부위별 운동 분포
    body_part_stats = db.session.query(
        Exercise.body_part,
        func.count(WorkoutRecord.id)
    ).join(WorkoutRecord).group_by(Exercise.body_part).all()
    
    # 최근 7일간 운동 데이터
    recent_sessions = db.session.query(
        WorkoutSession.date,
        func.count(WorkoutSession.id),
        func.sum(WorkoutSession.total_duration)
    ).filter(
        WorkoutSession.date >= week_ago
    ).group_by(WorkoutSession.date).all()
    
    # 목표 진행률 계산
    goals = Goal.query.filter_by(user_id=1).all()
    goal_progress = {}
    
    for goal in goals:
        if goal.goal_type == 'weekly_workouts':
            # 주 3회 운동 목표
            current_week_sessions = WorkoutSession.query.filter(
                WorkoutSession.date >= today - timedelta(days=today.weekday())
            ).count()
            progress = min(100, (current_week_sessions / 3) * 100)
            goal_progress['weekly_workouts'] = round(progress, 1)
            
        elif goal.goal_type == 'monthly_duration':
            # 월 운동 시간 목표
            current_month_duration = db.session.query(func.sum(WorkoutSession.total_duration)).filter(
                WorkoutSession.date >= today.replace(day=1)
            ).scalar() or 0
            progress = min(100, (current_month_duration / goal.target_value) * 100)
            goal_progress['monthly_duration'] = round(progress, 1)
            
        elif goal.goal_type == 'weight_loss':
            # 체중 감량 목표
            latest_weight = db.session.query(WeightRecord.weight).filter_by(user_id=1).order_by(WeightRecord.date.desc()).first()
            if latest_weight:
                # 시작 체중을 70kg으로 가정 (실제로는 사용자 테이블에서 가져와야 함)
                start_weight = 70.0
                current_loss = start_weight - latest_weight[0]
                progress = min(100, (current_loss / goal.target_value) * 100)
                goal_progress['weight_loss'] = round(progress, 1)
            else:
                goal_progress['weight_loss'] = 0
    
    # 연속 운동일 계산
    consecutive_days = 0
    current_date = today
    while True:
        session = WorkoutSession.query.filter_by(date=current_date).first()
        if session:
            consecutive_days += 1
            current_date -= timedelta(days=1)
        else:
            break
    
    # 최근 성과 계산
    achievements = []
    
    # 연속 운동일 성과
    if consecutive_days >= 7:
        achievements.append({
            'title': f'{consecutive_days}일 연속 운동 달성!',
            'icon': 'bi-award',
            'color': 'text-warning',
            'days_ago': 0
        })
    elif consecutive_days >= 3:
        achievements.append({
            'title': f'{consecutive_days}일 연속 운동 중!',
            'icon': 'bi-fire',
            'color': 'text-danger',
            'days_ago': 0
        })
    
    # 월간 운동 횟수 성과
    if monthly_sessions >= 20:
        achievements.append({
            'title': f'이번 달 운동 {monthly_sessions}회 달성',
            'icon': 'bi-calendar-check',
            'color': 'text-primary',
            'days_ago': 0
        })
    elif monthly_sessions >= 10:
        achievements.append({
            'title': f'이번 달 운동 {monthly_sessions}회 진행 중',
            'icon': 'bi-calendar-check',
            'color': 'text-info',
            'days_ago': 0
        })
    
    # 개인 기록 갱신 (가장 최근 운동의 무게 기록)
    latest_record = db.session.query(WorkoutRecord).join(Exercise).filter(
        WorkoutRecord.weight > 0
    ).order_by(WorkoutRecord.created_at.desc()).first()
    
    if latest_record:
        achievements.append({
            'title': f'{latest_record.exercise.name} 개인기록 갱신',
            'icon': 'bi-graph-up',
            'color': 'text-success',
            'days_ago': (today - latest_record.created_at.date()).days
        })
    
    # 히트맵 데이터 계산 (최근 3개월)
    heatmap_data = []
    for i in range(90):  # 90일
        check_date = today - timedelta(days=i)
        sessions = WorkoutSession.query.filter_by(date=check_date).all()
        
        if sessions:
            # 해당 날짜의 운동 강도 계산 (운동 횟수 + 총 시간 기반)
            intensity = len(sessions) + (sum(s.total_duration for s in sessions) // 30)  # 30분당 1 강도
            intensity = min(5, intensity)  # 최대 5
        else:
            intensity = 0
        
        heatmap_data.append({
            'date': check_date,
            'intensity': intensity
        })
    
    return render_template('dashboard.html',
                         weekly_sessions=weekly_sessions,
                         monthly_sessions=monthly_sessions,
                         total_duration=total_duration,
                         body_part_stats=body_part_stats,
                         recent_sessions=recent_sessions,
                         goal_progress=goal_progress,
                         consecutive_days=consecutive_days,
                         achievements=achievements,
                         heatmap_data=heatmap_data)

@app.route('/goals')
def goals():
    goals = Goal.query.filter_by(user_id=1).all()  # 임시로 1번 사용자
    return render_template('goals.html', goals=goals)

@app.route('/goals/add', methods=['GET', 'POST'])
def add_goal():
    if request.method == 'POST':
        goal = Goal(
            user_id=1,  # 임시로 1번 사용자
            title=request.form['title'],
            description=request.form.get('description', ''),
            target_value=float(request.form['target_value']),
            unit=request.form['unit'],
            goal_type=request.form['goal_type'],
            target_date=datetime.strptime(request.form['target_date'], '%Y-%m-%d').date()
        )
        db.session.add(goal)
        db.session.commit()
        flash('목표가 성공적으로 추가되었습니다!', 'success')
        return redirect(url_for('goals'))
    return render_template('add_goal.html')

@app.route('/goals/edit/<int:id>', methods=['GET', 'POST'])
def edit_goal(id):
    goal = db.session.get(Goal, id)
    if not goal:
        flash('해당 목표를 찾을 수 없습니다.', 'error')
        return redirect(url_for('goals'))
    
    if request.method == 'POST':
        goal.title = request.form['title']
        goal.description = request.form.get('description', '')
        goal.target_value = float(request.form['target_value'])
        goal.unit = request.form['unit']
        goal.goal_type = request.form['goal_type']
        goal.target_date = datetime.strptime(request.form['target_date'], '%Y-%m-%d').date()
        
        db.session.commit()
        flash('목표가 성공적으로 수정되었습니다!', 'success')
        return redirect(url_for('goals'))
    
    return render_template('edit_goal.html', goal=goal)

@app.route('/goals/delete/<int:id>')
def delete_goal(id):
    goal = db.session.get(Goal, id)
    if not goal:
        flash('해당 목표를 찾을 수 없습니다.', 'error')
        return redirect(url_for('goals'))
    
    db.session.delete(goal)
    db.session.commit()
    flash('목표가 삭제되었습니다!', 'success')
    return redirect(url_for('goals'))

@app.route('/goals/update-progress/<int:id>', methods=['POST'])
def update_goal_progress(id):
    goal = db.session.get(Goal, id)
    if not goal:
        flash('해당 목표를 찾을 수 없습니다.', 'error')
        return redirect(url_for('goals'))
    
    new_value = float(request.form.get('current_value', 0))
    goal.current_value = new_value
    
    # 목표 달성 여부 확인
    if new_value >= goal.target_value:
        goal.is_achieved = True
    
    db.session.commit()
    flash('진행률이 업데이트되었습니다!', 'success')
    return redirect(url_for('goals'))

@app.route('/calendar')
def calendar():
    # 달력용 운동 세션 데이터
    sessions = WorkoutSession.query.all()
    calendar_data = {}
    for session in sessions:
        date_str = session.date.strftime('%Y-%m-%d')
        if date_str not in calendar_data:
            calendar_data[date_str] = []
        calendar_data[date_str].append({
            'id': session.id,
            'duration': session.total_duration,
            'notes': session.notes
        })
    
    return render_template('calendar.html', calendar_data=json.dumps(calendar_data))

@app.route('/api/chart-data')
def chart_data():
    # Chart.js용 API 엔드포인트
    today = datetime.now().date()
    week_ago = today - timedelta(days=7)
    
    # 최근 7일간 운동 데이터
    sessions = WorkoutSession.query.filter(
        WorkoutSession.date >= week_ago
    ).order_by(WorkoutSession.date).all()
    
    labels = []
    data = []
    for i in range(7):
        date = week_ago + timedelta(days=i)
        labels.append(date.strftime('%m/%d'))
        day_duration = sum(s.total_duration or 0 for s in sessions if s.date == date)
        data.append(day_duration)
    
    return jsonify({
        'labels': labels,
        'data': data
    })

@app.route('/api/body-part-data')
def body_part_data():
    # 부위별 운동 분포 데이터
    stats = db.session.query(
        Exercise.body_part,
        func.count(WorkoutRecord.id)
    ).join(WorkoutRecord).group_by(Exercise.body_part).all()
    
    labels = [stat[0] for stat in stats]
    data = [stat[1] for stat in stats]
    
    return jsonify({
        'labels': labels,
        'data': data
    })

# 몸무게 관리 라우트들
@app.route('/weight')
def weight_records():
    records = WeightRecord.query.filter_by(user_id=1).order_by(WeightRecord.date.desc()).all()
    return render_template('weight.html', records=records)

@app.route('/weight/add', methods=['GET', 'POST'])
def add_weight():
    if request.method == 'POST':
        def safe_float(value, default=None):
            try:
                return float(value) if value and value.strip() else default
            except (ValueError, AttributeError):
                return default
        
        record = WeightRecord(
            user_id=1,  # 임시로 1번 사용자
            weight=safe_float(request.form['weight']),
            date=datetime.strptime(request.form['date'], '%Y-%m-%d').date(),
            body_fat_percentage=safe_float(request.form.get('body_fat_percentage')),
            muscle_mass=safe_float(request.form.get('muscle_mass')),
            notes=request.form.get('notes', '')
        )
        
        if record.weight is None:
            flash('몸무게를 입력해주세요!', 'error')
            return redirect(url_for('add_weight'))
        
        db.session.add(record)
        db.session.commit()
        flash('몸무게 기록이 성공적으로 추가되었습니다!', 'success')
        return redirect(url_for('weight_records'))
    
    return render_template('add_weight.html')

@app.route('/weight/edit/<int:id>', methods=['GET', 'POST'])
def edit_weight(id):
    record = db.session.get(WeightRecord, id)
    if not record:
        flash('해당 기록을 찾을 수 없습니다.', 'error')
        return redirect(url_for('weight_records'))
    
    if request.method == 'POST':
        def safe_float(value, default=None):
            try:
                return float(value) if value and value.strip() else default
            except (ValueError, AttributeError):
                return default
        
        record.weight = safe_float(request.form['weight'])
        record.date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        record.body_fat_percentage = safe_float(request.form.get('body_fat_percentage'))
        record.muscle_mass = safe_float(request.form.get('muscle_mass'))
        record.notes = request.form.get('notes', '')
        
        if record.weight is None:
            flash('몸무게를 입력해주세요!', 'error')
            return render_template('edit_weight.html', record=record)
        
        db.session.commit()
        flash('몸무게 기록이 성공적으로 수정되었습니다!', 'success')
        return redirect(url_for('weight_records'))
    
    return render_template('edit_weight.html', record=record)

@app.route('/weight/delete/<int:id>')
def delete_weight(id):
    record = db.session.get(WeightRecord, id)
    if not record:
        flash('해당 기록을 찾을 수 없습니다.', 'error')
        return redirect(url_for('weight_records'))
    db.session.delete(record)
    db.session.commit()
    flash('몸무게 기록이 삭제되었습니다!', 'success')
    return redirect(url_for('weight_records'))

@app.route('/api/weight-chart-data')
def weight_chart_data():
    # 최근 30일간 몸무게 데이터
    today = datetime.now().date()
    month_ago = today - timedelta(days=30)
    
    records = WeightRecord.query.filter(
        WeightRecord.user_id == 1,
        WeightRecord.date >= month_ago
    ).order_by(WeightRecord.date).all()
    
    labels = [record.date.strftime('%m/%d') for record in records]
    weights = [float(record.weight) for record in records]
    
    return jsonify({
        'labels': labels,
        'weights': weights
    })

# 템플릿에서 사용할 함수들을 전역으로 등록
@app.template_global()
def today():
    return date.today()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # 샘플 데이터 추가 (처음 실행 시에만)
        if Exercise.query.count() == 0:
            sample_exercises = [
                Exercise(name='벤치프레스', body_part='가슴', difficulty='중급'),
                Exercise(name='스쿼트', body_part='하체', difficulty='초급'),
                Exercise(name='데드리프트', body_part='등', difficulty='고급'),
                Exercise(name='풀업', body_part='등', difficulty='중급'),
                Exercise(name='플랭크', body_part='코어', difficulty='초급'),
                Exercise(name='바이셉 컬', body_part='팔', difficulty='초급'),
            ]
            for exercise in sample_exercises:
                db.session.add(exercise)
            
            # 샘플 사용자 추가
            user = User(username='user1', email='user@example.com')
            db.session.add(user)
            
            db.session.commit()
    
    app.run(debug=True)
