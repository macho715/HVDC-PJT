#!/usr/bin/env python3
"""
🚀 MACHO-GPT v3.4-mini Production Automation Pipeline
완전 자동화된 프로덕션 워크플로우 시스템

기능:
- 전체 데이터 처리 파이프라인 자동화
- 실시간 품질 모니터링
- 자동 오류 복구 및 알림
- 스케줄링 및 백업 시스템
- KPI 대시보드 자동 생성

실행: python production_automation_pipeline.py --mode production
"""

import os
import sys
import pandas as pd
import numpy as np
import json
import logging
import schedule
import time
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import psutil
import shutil

class ProductionAutomationPipeline:
    """프로덕션 자동화 파이프라인"""
    
    def __init__(self, config_path="production_config.json"):
        self.start_time = datetime.now()
        self.config = self.load_config(config_path)
        self.setup_logging()
        self.setup_directories()
        self.kpi_metrics = {}
        self.error_count = 0
        self.success_count = 0
        
        print("🚀 MACHO-GPT v3.4-mini Production Pipeline 초기화")
        print("=" * 70)
        
    def load_config(self, config_path):
        """설정 파일 로드 또는 기본 설정 생성"""
        default_config = {
            "data_sources": {
                "hitachi_file": "MACHO_WH_HANDLING_HITACHI_DATA.xlsx",
                "simense_file": "MACHO_WH_HANDLING_SIMENSE_DATA.xlsx"
            },
            "quality_thresholds": {
                "min_records": 7000,
                "quality_score_threshold": 90.0,
                "flow_code_accuracy": 95.0,
                "processing_time_limit": 300  # 5분
            },
            "automation": {
                "auto_backup": True,
                "auto_validation": True,
                "auto_reporting": True,
                "retry_attempts": 3,
                "notification_email": "admin@samsung-ct.com"
            },
            "scheduling": {
                "daily_run_time": "06:00",
                "weekly_full_validation": "Sunday 02:00",
                "monthly_archive": "1st 01:00"
            },
            "containment_modes": {
                "primary": "LATTICE",
                "fallback": "ZERO",
                "monitoring": "RHYTHM"
            }
        }
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ 설정 파일 로드 실패, 기본 설정 사용: {e}")
                return default_config
        else:
            # 기본 설정 파일 생성
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            return default_config
    
    def setup_logging(self):
        """로깅 시스템 설정"""
        log_dir = Path("logs/production")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_filename = f"production_pipeline_{datetime.now().strftime('%Y%m%d')}.log"
        log_path = log_dir / log_filename
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s | %(levelname)s | %(message)s',
            handlers=[
                logging.FileHandler(log_path, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("🎯 Production Pipeline 로깅 시스템 시작")
    
    def setup_directories(self):
        """디렉토리 구조 설정"""
        directories = [
            "production_output",
            "production_backup",
            "production_logs", 
            "production_monitoring",
            "production_reports",
            "production_archive"
        ]
        
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
        
        self.logger.info(f"📁 디렉토리 구조 설정 완료: {len(directories)}개")
    
    def monitor_system_resources(self):
        """시스템 리소스 모니터링"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('.')
            
            self.kpi_metrics.update({
                'cpu_usage': cpu_percent,
                'memory_usage': memory.percent,
                'memory_available_gb': memory.available / (1024**3),
                'disk_usage': disk.percent,
                'disk_free_gb': disk.free / (1024**3)
            })
            
            # 리소스 경고 임계값 확인
            if cpu_percent > 80:
                self.logger.warning(f"🔥 CPU 사용률 높음: {cpu_percent}%")
            if memory.percent > 85:
                self.logger.warning(f"🔥 메모리 사용률 높음: {memory.percent}%")
            if disk.percent > 90:
                self.logger.warning(f"🔥 디스크 사용률 높음: {disk.percent}%")
                
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 시스템 리소스 모니터링 실패: {e}")
            return False
    
    def validate_data_sources(self):
        """데이터 소스 검증"""
        self.logger.info("🔍 데이터 소스 검증 시작")
        
        hitachi_file = self.config['data_sources']['hitachi_file']
        simense_file = self.config['data_sources']['simense_file']
        
        validation_results = {
            'hitachi_exists': os.path.exists(hitachi_file),
            'simense_exists': os.path.exists(simense_file),
            'hitachi_size': 0,
            'simense_size': 0,
            'hitachi_records': 0,
            'simense_records': 0
        }
        
        try:
            if validation_results['hitachi_exists']:
                validation_results['hitachi_size'] = os.path.getsize(hitachi_file) / (1024*1024)  # MB
                hitachi_df = pd.read_excel(hitachi_file)
                validation_results['hitachi_records'] = len(hitachi_df)
                
            if validation_results['simense_exists']:
                validation_results['simense_size'] = os.path.getsize(simense_file) / (1024*1024)  # MB
                simense_df = pd.read_excel(simense_file)
                validation_results['simense_records'] = len(simense_df)
            
            total_records = validation_results['hitachi_records'] + validation_results['simense_records']
            min_required = self.config['quality_thresholds']['min_records']
            
            validation_results['total_records'] = total_records
            validation_results['meets_minimum'] = total_records >= min_required
            
            self.logger.info(f"📊 데이터 검증 완료:")
            self.logger.info(f"   - HITACHI: {validation_results['hitachi_records']:,}건 ({validation_results['hitachi_size']:.1f}MB)")
            self.logger.info(f"   - SIMENSE: {validation_results['simense_records']:,}건 ({validation_results['simense_size']:.1f}MB)")
            self.logger.info(f"   - 총합: {total_records:,}건 (기준: {min_required:,}건)")
            
            return validation_results
            
        except Exception as e:
            self.logger.error(f"❌ 데이터 소스 검증 실패: {e}")
            validation_results['error'] = str(e)
            return validation_results
    
    def execute_integration_pipeline(self):
        """통합 파이프라인 실행"""
        self.logger.info("🔄 통합 파이프라인 실행 시작")
        
        pipeline_start = time.time()
        
        try:
            # 1. 빠른 통합 스크립트 실행
            result = subprocess.run([
                sys.executable, "06_로직함수/quick_integration.py"
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                self.logger.info("✅ 통합 데이터 생성 성공")
                
                # 생성된 파일 확인
                integration_files = [f for f in os.listdir('.') 
                                   if f.startswith('MACHO_WH_HANDLING_통합데이터_') and f.endswith('.xlsx')]
                
                if integration_files:
                    latest_file = max(integration_files, key=os.path.getmtime)
                    self.logger.info(f"📊 최신 통합 파일: {latest_file}")
                    
                    # 백업 생성
                    backup_path = f"production_backup/{latest_file}"
                    shutil.copy2(latest_file, backup_path)
                    self.logger.info(f"💾 백업 생성: {backup_path}")
                    
                    return latest_file
                else:
                    self.logger.error("❌ 통합 파일이 생성되지 않음")
                    return None
            else:
                self.logger.error(f"❌ 통합 파이프라인 실패: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            self.logger.error("❌ 통합 파이프라인 시간 초과 (5분)")
            return None
        except Exception as e:
            self.logger.error(f"❌ 통합 파이프라인 실행 오류: {e}")
            return None
        finally:
            pipeline_duration = time.time() - pipeline_start
            self.kpi_metrics['integration_time'] = pipeline_duration
            self.logger.info(f"⏱️ 통합 파이프라인 소요시간: {pipeline_duration:.2f}초")
    
    def run_quality_validation(self):
        """품질 검증 실행"""
        self.logger.info("🧪 품질 검증 실행")
        
        try:
            # TDD 검증 스크립트 실행
            result = subprocess.run([
                sys.executable, "06_로직함수/tdd_validation_simple.py"
            ], capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                self.logger.info("✅ TDD 품질 검증 통과")
                
                # 품질 리포트 파일 확인
                quality_reports = [f for f in os.listdir('.') 
                                 if f.startswith('tdd_validation_report_') and f.endswith('.json')]
                
                if quality_reports:
                    latest_report = max(quality_reports, key=os.path.getmtime)
                    
                    with open(latest_report, 'r', encoding='utf-8') as f:
                        quality_data = json.load(f)
                    
                    quality_score = quality_data.get('quality_score', 0)
                    threshold = self.config['quality_thresholds']['quality_score_threshold']
                    
                    self.kpi_metrics.update({
                        'quality_score': quality_score,
                        'total_tests': quality_data.get('total_tests', 0),
                        'passed_tests': quality_data.get('passed_tests', 0),
                        'failed_tests': quality_data.get('failed_tests', 0)
                    })
                    
                    if quality_score >= threshold:
                        self.logger.info(f"🏆 품질 점수 달성: {quality_score:.1f}% (기준: {threshold}%)")
                        return True
                    else:
                        self.logger.warning(f"⚠️ 품질 점수 미달: {quality_score:.1f}% (기준: {threshold}%)")
                        return False
                        
            else:
                self.logger.error(f"❌ 품질 검증 실패: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ 품질 검증 오류: {e}")
            return False
    
    def generate_production_report(self):
        """프로덕션 리포트 생성"""
        self.logger.info("📊 프로덕션 리포트 생성")
        
        try:
            end_time = datetime.now()
            total_duration = (end_time - self.start_time).total_seconds()
            
            report_data = {
                'timestamp': end_time.isoformat(),
                'pipeline_info': {
                    'start_time': self.start_time.isoformat(),
                    'end_time': end_time.isoformat(),
                    'total_duration_seconds': total_duration,
                    'status': 'SUCCESS' if self.error_count == 0 else 'PARTIAL_SUCCESS'
                },
                'kpi_metrics': self.kpi_metrics,
                'quality_status': {
                    'success_count': self.success_count,
                    'error_count': self.error_count,
                    'overall_health': 'EXCELLENT' if self.error_count == 0 else 'GOOD'
                },
                'containment_mode': self.config['containment_modes']['primary'],
                'recommendations': self.generate_recommendations()
            }
            
            # JSON 리포트 저장
            report_filename = f"production_reports/production_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_filename, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            
            # 마크다운 요약 리포트 생성
            md_report = self.generate_markdown_report(report_data)
            md_filename = f"production_reports/production_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            with open(md_filename, 'w', encoding='utf-8') as f:
                f.write(md_report)
            
            self.logger.info(f"📄 리포트 생성 완료:")
            self.logger.info(f"   - JSON: {report_filename}")
            self.logger.info(f"   - Markdown: {md_filename}")
            
            return report_filename
            
        except Exception as e:
            self.logger.error(f"❌ 리포트 생성 실패: {e}")
            return None
    
    def generate_recommendations(self):
        """개선 권장사항 생성"""
        recommendations = []
        
        # 성능 기반 권장사항
        if self.kpi_metrics.get('integration_time', 0) > 180:  # 3분 초과
            recommendations.append("통합 파이프라인 성능 최적화 필요")
        
        if self.kpi_metrics.get('cpu_usage', 0) > 70:
            recommendations.append("CPU 사용률 최적화 권장")
        
        if self.kpi_metrics.get('memory_usage', 0) > 80:
            recommendations.append("메모리 사용량 최적화 필요")
        
        # 품질 기반 권장사항
        quality_score = self.kpi_metrics.get('quality_score', 0)
        if quality_score < 95:
            recommendations.append("품질 점수 개선을 위한 데이터 정제 필요")
        
        if self.error_count > 0:
            recommendations.append("오류 발생 원인 분석 및 예방 조치 필요")
        
        if not recommendations:
            recommendations.append("시스템이 최적 상태로 운영 중입니다")
        
        return recommendations
    
    def generate_markdown_report(self, report_data):
        """마크다운 형식 리포트 생성"""
        md_content = f"""# 🚀 MACHO-GPT v3.4-mini Production Report

## 📊 실행 정보
- **실행 시간**: {report_data['pipeline_info']['start_time']}
- **완료 시간**: {report_data['pipeline_info']['end_time']}
- **총 소요시간**: {report_data['pipeline_info']['total_duration_seconds']:.2f}초
- **상태**: {report_data['pipeline_info']['status']}

## 📈 KPI 지표
"""
        
        # KPI 지표 추가
        if self.kpi_metrics:
            md_content += "| 지표 | 값 |\n|------|----|\n"
            for key, value in self.kpi_metrics.items():
                if isinstance(value, float):
                    md_content += f"| {key} | {value:.2f} |\n"
                else:
                    md_content += f"| {key} | {value} |\n"
        
        md_content += f"""
## 🎯 품질 상태
- **성공 건수**: {report_data['quality_status']['success_count']}
- **오류 건수**: {report_data['quality_status']['error_count']}
- **전체 상태**: {report_data['quality_status']['overall_health']}

## 💡 권장사항
"""
        
        for i, rec in enumerate(report_data['recommendations'], 1):
            md_content += f"{i}. {rec}\n"
        
        md_content += f"""
## 🔧 시스템 정보
- **Containment Mode**: {report_data['containment_mode']}
- **생성 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---
*Generated by MACHO-GPT v3.4-mini Production Automation Pipeline*
"""
        
        return md_content
    
    def send_notification(self, message, is_error=False):
        """알림 전송 (이메일/로그)"""
        if is_error:
            self.logger.error(f"🚨 {message}")
        else:
            self.logger.info(f"📢 {message}")
        
        # 실제 이메일 전송은 SMTP 설정에 따라 구현
        # 여기서는 로그만 기록
        
    def run_full_pipeline(self):
        """전체 파이프라인 실행"""
        self.logger.info("🎯 프로덕션 파이프라인 시작")
        
        try:
            # 1. 시스템 리소스 모니터링
            if not self.monitor_system_resources():
                self.error_count += 1
                self.send_notification("시스템 리소스 모니터링 실패", is_error=True)
            
            # 2. 데이터 소스 검증
            validation_results = self.validate_data_sources()
            if not validation_results.get('meets_minimum', False):
                self.error_count += 1
                self.send_notification("데이터 소스 검증 실패", is_error=True)
                return False
            else:
                self.success_count += 1
            
            # 3. 통합 파이프라인 실행
            integration_file = self.execute_integration_pipeline()
            if integration_file:
                self.success_count += 1
                self.send_notification(f"통합 데이터 생성 성공: {integration_file}")
            else:
                self.error_count += 1
                self.send_notification("통합 데이터 생성 실패", is_error=True)
                return False
            
            # 4. 품질 검증 실행
            if self.run_quality_validation():
                self.success_count += 1
                self.send_notification("품질 검증 통과")
            else:
                self.error_count += 1
                self.send_notification("품질 검증 실패", is_error=True)
            
            # 5. 프로덕션 리포트 생성
            report_file = self.generate_production_report()
            if report_file:
                self.success_count += 1
                self.send_notification(f"프로덕션 리포트 생성: {report_file}")
            
            # 6. 최종 상태 확인
            success_rate = self.success_count / (self.success_count + self.error_count) * 100
            
            if success_rate >= 80:
                self.logger.info(f"🎉 파이프라인 성공 완료 - 성공률: {success_rate:.1f}%")
                return True
            else:
                self.logger.warning(f"⚠️ 파이프라인 부분 성공 - 성공률: {success_rate:.1f}%")
                return False
                
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"❌ 파이프라인 실행 중 예외 발생: {e}")
            self.send_notification(f"파이프라인 예외 발생: {e}", is_error=True)
            return False
    
    def setup_scheduler(self):
        """스케줄러 설정"""
        self.logger.info("⏰ 스케줄러 설정")
        
        # 일일 실행
        daily_time = self.config['scheduling']['daily_run_time']
        schedule.every().day.at(daily_time).do(self.run_full_pipeline)
        
        # 주간 전체 검증
        schedule.every().sunday.at("02:00").do(self.run_comprehensive_validation)
        
        # 월간 아카이브
        schedule.every().month.do(self.archive_old_data)
        
        self.logger.info(f"📅 스케줄 설정 완료:")
        self.logger.info(f"   - 일일 실행: {daily_time}")
        self.logger.info(f"   - 주간 검증: 일요일 02:00")
        self.logger.info(f"   - 월간 아카이브: 매월 1일")
    
    def run_comprehensive_validation(self):
        """종합 검증 실행"""
        self.logger.info("🔍 종합 검증 실행")
        # 전체 파이프라인 + 추가 검증 로직
        return self.run_full_pipeline()
    
    def archive_old_data(self):
        """오래된 데이터 아카이브"""
        self.logger.info("📦 데이터 아카이브 실행")
        
        try:
            archive_date = datetime.now().strftime('%Y%m%d')
            archive_dir = f"production_archive/{archive_date}"
            Path(archive_dir).mkdir(parents=True, exist_ok=True)
            
            # 30일 이상 된 파일들 아카이브
            cutoff_date = datetime.now() - timedelta(days=30)
            
            archived_count = 0
            for file_path in Path('.').glob('*.xlsx'):
                if file_path.stat().st_mtime < cutoff_date.timestamp():
                    shutil.move(str(file_path), f"{archive_dir}/{file_path.name}")
                    archived_count += 1
            
            self.logger.info(f"📦 아카이브 완료: {archived_count}개 파일")
            
        except Exception as e:
            self.logger.error(f"❌ 아카이브 실패: {e}")

def main():
    """메인 실행 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='MACHO-GPT Production Automation Pipeline')
    parser.add_argument('--mode', choices=['production', 'test', 'scheduler'], 
                       default='production', help='실행 모드')
    parser.add_argument('--config', default='production_config.json', 
                       help='설정 파일 경로')
    
    args = parser.parse_args()
    
    # 파이프라인 인스턴스 생성
    pipeline = ProductionAutomationPipeline(args.config)
    
    if args.mode == 'production':
        # 단일 실행
        success = pipeline.run_full_pipeline()
        sys.exit(0 if success else 1)
        
    elif args.mode == 'test':
        # 테스트 모드 (검증만)
        pipeline.logger.info("🧪 테스트 모드 실행")
        validation_results = pipeline.validate_data_sources()
        quality_passed = pipeline.run_quality_validation()
        
        print(f"✅ 데이터 검증: {'통과' if validation_results.get('meets_minimum') else '실패'}")
        print(f"✅ 품질 검증: {'통과' if quality_passed else '실패'}")
        
    elif args.mode == 'scheduler':
        # 스케줄러 모드
        pipeline.setup_scheduler()
        pipeline.logger.info("🔄 스케줄러 시작 - Ctrl+C로 종료")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # 1분마다 스케줄 확인
        except KeyboardInterrupt:
            pipeline.logger.info("⏹️ 스케줄러 종료")

if __name__ == "__main__":
    main() 