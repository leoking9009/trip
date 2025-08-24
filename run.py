#!/usr/bin/env python3
"""
운동 관리 Flask 웹앱 실행 스크립트
"""

import os
from app import app, db
from config import config

def create_app(config_name=None):
    """애플리케이션 팩토리 함수"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app.config.from_object(config[config_name])
    
    return app

if __name__ == '__main__':
    # 환경 설정
    config_name = os.environ.get('FLASK_ENV', 'development')
    app = create_app(config_name)
    
    # 데이터베이스 초기화
    with app.app_context():
        db.create_all()
        print("데이터베이스가 초기화되었습니다.")
    
    # 개발 서버 실행
    port = int(os.environ.get('PORT', 5000))
    debug = config_name == 'development'
    
    print(f"서버가 포트 {port}에서 실행됩니다.")
    print(f"디버그 모드: {debug}")
    print(f"환경: {config_name}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
