// 피트니스 트래커 메인 JavaScript 파일

// 전역 설정
const FitnessTracker = {
    // API 기본 URL
    apiUrl: '',
    
    // 초기화 함수
    init: function() {
        this.setupEventListeners();
        this.initializeTooltips();
        this.setupFormValidation();
    },
    
    // 이벤트 리스너 설정
    setupEventListeners: function() {
        // 네비게이션 활성화
        this.setActiveNavItem();
        
        // 폼 제출 확인
        document.querySelectorAll('form[data-confirm]').forEach(form => {
            form.addEventListener('submit', function(e) {
                const message = this.dataset.confirm;
                if (!confirm(message)) {
                    e.preventDefault();
                }
            });
        });
        
        // 삭제 확인
        document.querySelectorAll('a[data-confirm]').forEach(link => {
            link.addEventListener('click', function(e) {
                const message = this.dataset.confirm || '정말 삭제하시겠습니까?';
                if (!confirm(message)) {
                    e.preventDefault();
                }
            });
        });
    },
    
    // 툴팁 초기화
    initializeTooltips: function() {
        if (typeof bootstrap !== 'undefined') {
            const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
            tooltips.forEach(tooltip => {
                new bootstrap.Tooltip(tooltip);
            });
        }
    },
    
    // 폼 유효성 검사 설정
    setupFormValidation: function() {
        const forms = document.querySelectorAll('.needs-validation');
        forms.forEach(form => {
            form.addEventListener('submit', function(e) {
                if (!form.checkValidity()) {
                    e.preventDefault();
                    e.stopPropagation();
                }
                form.classList.add('was-validated');
            });
        });
    },
    
    // 활성 네비게이션 아이템 설정
    setActiveNavItem: function() {
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
        
        navLinks.forEach(link => {
            if (link.getAttribute('href') === currentPath) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });
    },
    
    // 로딩 스피너 표시
    showLoading: function(element) {
        const originalText = element.innerHTML;
        element.innerHTML = '<span class="loading-spinner"></span> 로딩 중...';
        element.disabled = true;
        return originalText;
    },
    
    // 로딩 스피너 숨기기
    hideLoading: function(element, originalText) {
        element.innerHTML = originalText;
        element.disabled = false;
    },
    
    // 성공 알림
    showSuccess: function(message) {
        this.showAlert(message, 'success');
    },
    
    // 오류 알림
    showError: function(message) {
        this.showAlert(message, 'danger');
    },
    
    // 알림 표시
    showAlert: function(message, type = 'info') {
        const alertContainer = document.querySelector('.alert-container') || document.querySelector('main');
        const alertId = 'alert-' + Date.now();
        
        const alertHtml = `
            <div id="${alertId}" class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        alertContainer.insertAdjacentHTML('afterbegin', alertHtml);
        
        // 5초 후 자동 제거
        setTimeout(() => {
            const alert = document.getElementById(alertId);
            if (alert) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    },
    
    // AJAX 요청 헬퍼
    ajax: function(url, options = {}) {
        const defaultOptions = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        };
        
        const config = Object.assign(defaultOptions, options);
        
        return fetch(url, config)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .catch(error => {
                console.error('AJAX Error:', error);
                this.showError('서버 요청 중 오류가 발생했습니다.');
                throw error;
            });
    },
    
    // 날짜 포맷팅
    formatDate: function(date, format = 'YYYY-MM-DD') {
        const d = new Date(date);
        const year = d.getFullYear();
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        
        switch (format) {
            case 'YYYY-MM-DD':
                return `${year}-${month}-${day}`;
            case 'MM/DD':
                return `${month}/${day}`;
            case 'YYYY년 MM월 DD일':
                return `${year}년 ${month}월 ${day}일`;
            default:
                return `${year}-${month}-${day}`;
        }
    },
    
    // 숫자 포맷팅 (천 단위 콤마)
    formatNumber: function(num) {
        return new Intl.NumberFormat('ko-KR').format(num);
    },
    
    // 디바운스 함수
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    // 로컬 스토리지 헬퍼
    storage: {
        set: function(key, value) {
            try {
                localStorage.setItem(key, JSON.stringify(value));
            } catch (e) {
                console.error('로컬 스토리지 저장 실패:', e);
            }
        },
        
        get: function(key, defaultValue = null) {
            try {
                const item = localStorage.getItem(key);
                return item ? JSON.parse(item) : defaultValue;
            } catch (e) {
                console.error('로컬 스토리지 읽기 실패:', e);
                return defaultValue;
            }
        },
        
        remove: function(key) {
            try {
                localStorage.removeItem(key);
            } catch (e) {
                console.error('로컬 스토리지 삭제 실패:', e);
            }
        }
    }
};

// DOM 로드 완료 시 초기화
document.addEventListener('DOMContentLoaded', function() {
    FitnessTracker.init();
});

// 전역으로 노출
window.FitnessTracker = FitnessTracker;
