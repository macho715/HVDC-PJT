#!/usr/bin/env python3
"""
HVDC 온톨로지 추론 엔진 (업그레이드 v1.1)
/cmd_ontology_reasoning 명령어 구현
AI 기반 패턴 발견 및 자동 추론 (머신러닝 기반 고도화)
"""

import pandas as pd
import json
from datetime import datetime, timedelta
from pathlib import Path
import logging
import time
import numpy as np
from collections import defaultdict, Counter
import re

# [UPDATE v1.1] 머신러닝 라이브러리 추가
try:
    from sklearn.experimental import enable_iterative_imputer
    from sklearn.impute import IterativeImputer
    from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
    from sklearn.tree import DecisionTreeClassifier, export_text
    from sklearn.preprocessing import LabelEncoder
    ML_AVAILABLE = True
    print("✅ 머신러닝 라이브러리 로드 성공")
except ImportError as e:
    print(f"⚠️ 머신러닝 라이브러리 없음: {e}")
    print("💡 pip install scikit-learn으로 설치하면 ML 기능을 사용할 수 있습니다.")
    ML_AVAILABLE = False

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HVDCOntologyReasoner:
    """HVDC 온톨로지 추론 엔진 (업그레이드 v1.1)"""
    
    def __init__(self, config_path='config.json'):
        self.data = {}
        self.rules = {}
        self.inferences = []
        self.patterns = {}
        self.anomalies = []
        self.config = self._load_config(config_path)
        self.ml_available = ML_AVAILABLE

    # [UPDATE v1.1] 설정 파일 로드 기능 추가
    def _load_config(self, config_path):
        """설정 파일(데이터 경로 등)을 로드하여 유연성 증대"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                print(f"✅ 설정 파일 로드 성공: {config_path}")
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️ 설정 파일({config_path})을 찾을 수 없습니다. 기본값으로 실행합니다.")
            return {
                "data_files": {
                    'HITACHI': 'data/HVDC WAREHOUSE_HITACHI(HE).xlsx',
                    'SIMENSE': 'data/HVDC WAREHOUSE_SIMENSE(SIM).xlsx',
                    'INVOICE': 'data/HVDC WAREHOUSE_INVOICE.xlsx'
                },
                "mapping_rules_file": "mapping_rules_v2.6.json"
            }

    def load_data_and_rules(self):
        """데이터 및 규칙 로드 (설정 파일 기반으로 변경)"""
        print("🧠 온톨로지 추론 엔진 초기화 중...")
        
        # 설정 파일에서 데이터 파일 경로 로드
        data_files = self.config.get("data_files", {})
        
        for name, file_path in data_files.items():
            try:
                df = pd.read_excel(file_path)
                # [UPDATE v1.1] 데이터 타입 자동 변환 및 정리
                df = self._preprocess_dataframe(df)
                self.data[name] = df
                print(f"✅ {name}: {len(df):,}행 로드")
            except Exception as e:
                print(f"❌ {name} 로드 실패: {e}")
        
        # 매핑 규칙 로드
        try:
            mapping_rules_file = self.config.get("mapping_rules_file", "mapping_rules_v2.6.json")
            if Path(mapping_rules_file).exists():
                with open(mapping_rules_file, 'r', encoding='utf-8') as f:
                    self.rules = json.load(f)
                print("✅ 매핑 규칙 로드 완료")
            else:
                print(f"⚠️ 매핑 규칙 파일({mapping_rules_file})이 없습니다. 기본 규칙 사용.")
                self.rules = self._create_default_rules()
        except Exception as e:
            print(f"❌ 매핑 규칙 로드 실패: {e}")
            self.rules = self._create_default_rules()

    def _create_default_rules(self):
        """기본 매핑 규칙 생성"""
        return {
            "common_patterns": {
                "cbm_keywords": ["CBM", "Volume", "부피"],
                "weight_keywords": ["Weight", "G.W", "무게", "KG"],
                "location_keywords": ["Location", "위치", "DSV", "AGI", "MIR"]
            }
        }

    # [UPDATE v1.1] 데이터 전처리 함수 추가
    def _preprocess_dataframe(self, df):
        """데이터프레임의 기본 전처리를 수행합니다."""
        # 날짜 형식으로 변환 시도
        for col in df.columns:
            if 'date' in col.lower() or 'month' in col.lower():
                try:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                except:
                    pass
        
        # 숫자 형식에서 쉼표 제거 및 변환
        for col in df.select_dtypes(include=['object']).columns:
            try:
                if df[col].dtype == 'object' and df[col].str.contains(',', na=False).any():
                    df[col] = pd.to_numeric(df[col].str.replace(',', '', regex=False), errors='ignore')
            except:
                pass
        
        return df

    def analyze_data_relationships(self):
        """데이터 관계 분석 및 추론"""
        print("\n🔍 데이터 관계 분석 및 추론 수행 중...")
        
        relationships = {}
        
        for source_name, df in self.data.items():
            print(f"\n📊 {source_name} 데이터 관계 분석:")
            
            # 1. 컬럼 간 상관관계 분석
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 1:
                try:
                    correlation_matrix = df[numeric_cols].corr()
                    high_correlations = []
                    
                    for i in range(len(correlation_matrix.columns)):
                        for j in range(i+1, len(correlation_matrix.columns)):
                            corr_value = correlation_matrix.iloc[i, j]
                            if abs(corr_value) > 0.7 and not np.isnan(corr_value):
                                high_correlations.append({
                                    'col1': correlation_matrix.columns[i],
                                    'col2': correlation_matrix.columns[j],
                                    'correlation': round(corr_value, 3)
                                })
                    
                    relationships[f'{source_name}_correlations'] = high_correlations
                    print(f"  📈 강한 상관관계 발견: {len(high_correlations)}개")
                except Exception as e:
                    print(f"  ⚠️ 상관관계 분석 오류: {e}")
            
            # 2. 범주형 데이터 패턴 분석
            categorical_patterns = {}
            text_cols = df.select_dtypes(include=['object']).columns
            
            for col in text_cols[:5]:  # 상위 5개 텍스트 컬럼만 분석
                if col in df.columns:
                    try:
                        value_counts = df[col].value_counts()
                        if 1 < len(value_counts) < 50:  # 고유값이 1개 초과, 50개 미만인 경우만
                            categorical_patterns[col] = {
                                'unique_count': len(value_counts),
                                'top_values': value_counts.head(5).to_dict(),
                                'distribution': 'uniform' if value_counts.std() < value_counts.mean() * 0.5 else 'skewed'
                            }
                    except Exception as e:
                        print(f"    ⚠️ {col} 패턴 분석 오류: {e}")
            
            relationships[f'{source_name}_patterns'] = categorical_patterns
            print(f"  📊 범주형 패턴 분석: {len(categorical_patterns)}개 컬럼")
        
        self.patterns['relationships'] = relationships
        return relationships

    # [MAJOR UPDATE v1.1] 머신러닝 기반 비즈니스 규칙 추론
    def infer_business_rules(self):
        """비즈니스 규칙 자동 추론 (Decision Tree 기반)"""
        print("\n🎯 비즈니스 규칙 자동 추론 중 (ML)...")
        
        business_rules = []

        if not self.ml_available:
            print("  ⚠️ ML 라이브러리가 없어 기본 규칙 추론을 사용합니다.")
            return self._infer_basic_business_rules()

        # HITACHI 데이터에서 Location 예측 모델
        if 'HITACHI' in self.data:
            df = self.data['HITACHI'].copy()
            
            # 가능한 feature와 target 조합 시도
            possible_features = ['CBM', 'Pkg', 'G.W(KG)', 'N.W(kgs)', 'L(CM)', 'W(CM)', 'H(CM)']
            possible_targets = ['Location', 'HVDC CODE 1', 'HVDC CODE 2']
            
            for target_col in possible_targets:
                if target_col not in df.columns:
                    continue
                    
                available_features = [f for f in possible_features if f in df.columns]
                if len(available_features) < 2:
                    continue
                
                try:
                    # 분석에 필요한 데이터만 필터링 및 결측치 제거
                    df_clean = df[[target_col] + available_features].dropna()

                    if len(df_clean) > 50 and df_clean[target_col].nunique() > 1:
                        le = LabelEncoder()
                        X = df_clean[available_features]
                        y = le.fit_transform(df_clean[target_col].astype(str))

                        # 의사결정나무 모델 학습
                        tree_model = DecisionTreeClassifier(
                            max_depth=4, 
                            min_samples_leaf=10, 
                            random_state=42
                        )
                        tree_model.fit(X, y)

                        # 학습된 규칙 텍스트로 추출
                        tree_rules = export_text(
                            tree_model, 
                            feature_names=available_features, 
                            class_names=le.classes_.astype(str)
                        )
                        
                        accuracy = tree_model.score(X, y)
                        
                        business_rules.append({
                            'type': 'ml_inferred_rule',
                            'rule': f"'{target_col}' 예측 모델 (Decision Tree)",
                            'inference': f"{', '.join(available_features)} 값에 따라 {target_col}이 결정되는 패턴 발견.",
                            'details': tree_rules.split('\n')[:10],  # 상위 10개 규칙만 표시
                            'confidence': round(accuracy, 3),
                            'features_used': available_features,
                            'target': target_col
                        })
                        print(f"  ✅ {target_col} 예측 모델 학습 완료. 정확도: {accuracy:.2%}")
                        
                except Exception as e:
                    print(f"  ❌ {target_col} 모델 학습 실패: {e}")

        # INVOICE 데이터에서 금액 예측 모델
        if 'INVOICE' in self.data:
            df = self.data['INVOICE'].copy()
            
            if 'Amount' in df.columns and 'Weight (kg)' in df.columns:
                try:
                    df_clean = df[['Amount', 'Weight (kg)', 'CBM']].dropna()
                    
                    if len(df_clean) > 30:
                        X = df_clean[['Weight (kg)', 'CBM']]
                        y = df_clean['Amount']
                        
                        # 회귀 모델 학습
                        rf_model = RandomForestRegressor(n_estimators=10, random_state=42)
                        rf_model.fit(X, y)
                        
                        score = rf_model.score(X, y)
                        feature_importance = dict(zip(X.columns, rf_model.feature_importances_))
                        
                        business_rules.append({
                            'type': 'ml_regression_rule',
                            'rule': 'Amount 예측 모델 (Random Forest)',
                            'inference': f"Weight와 CBM으로 Amount를 {score:.2%} 정확도로 예측 가능",
                            'feature_importance': {k: round(v, 3) for k, v in feature_importance.items()},
                            'confidence': round(score, 3)
                        })
                        print(f"  ✅ Amount 예측 모델 학습 완료. R² 점수: {score:.2%}")
                        
                except Exception as e:
                    print(f"  ❌ Amount 예측 모델 학습 실패: {e}")

        self.inferences.extend(business_rules)
        print(f"✅ {len(business_rules)}개 ML 기반 비즈니스 규칙 추론 완료")
        return business_rules

    def _infer_basic_business_rules(self):
        """기본 통계 기반 비즈니스 규칙 추론 (ML 없이)"""
        business_rules = []
        
        for source, df in self.data.items():
            # 기본 통계 기반 규칙
            if 'CBM' in df.columns and df['CBM'].notna().sum() > 10:
                avg_cbm = df['CBM'].mean()
                business_rules.append({
                    'type': 'statistical_rule',
                    'rule': f'{source} 평균 CBM 패턴',
                    'inference': f'{source}의 평균 CBM: {avg_cbm:.2f}',
                    'confidence': 0.8
                })
        
        return business_rules

    def detect_anomalies(self):
        """이상치 및 불일치 탐지"""
        print("\n🚨 이상치 및 데이터 불일치 탐지 중...")
        
        anomalies = []
        
        for source, df in self.data.items():
            print(f"📊 {source} 이상치 분석:")
            
            # 1. 숫자형 데이터 이상치 (IQR 방법)
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                if col in df.columns and df[col].notna().sum() > 10:
                    try:
                        Q1 = df[col].quantile(0.25)
                        Q3 = df[col].quantile(0.75)
                        IQR = Q3 - Q1
                        
                        if IQR > 0:
                            lower_bound = Q1 - 1.5 * IQR
                            upper_bound = Q3 + 1.5 * IQR
                            
                            outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
                            if len(outliers) > 0:
                                anomalies.append({
                                    'type': 'numeric_outlier',
                                    'source': source,
                                    'column': col,
                                    'outlier_count': len(outliers),
                                    'percentage': round(len(outliers) / len(df) * 100, 2),
                                    'bounds': f'[{lower_bound:.2f}, {upper_bound:.2f}]',
                                    'severity': 'high' if len(outliers) / len(df) > 0.05 else 'medium'
                                })
                    except Exception as e:
                        print(f"    ⚠️ {col} 이상치 분석 오류: {e}")
            
            # 2. 결측값 패턴 분석
            missing_analysis = df.isnull().sum()
            high_missing = missing_analysis[missing_analysis > len(df) * 0.5]
            
            for col in high_missing.index:
                anomalies.append({
                    'type': 'high_missing_rate',
                    'source': source,
                    'column': col,
                    'missing_count': int(high_missing[col]),
                    'percentage': round(high_missing[col] / len(df) * 100, 2),
                    'severity': 'high' if high_missing[col] / len(df) > 0.8 else 'medium'
                })
        
        self.anomalies = anomalies
        print(f"✅ {len(anomalies)}개 이상치/불일치 탐지 완료")
        return anomalies

    def generate_ontology_rules(self):
        """온톨로지 규칙 자동 생성"""
        print("\n📜 온톨로지 규칙 자동 생성 중...")
        
        ontology_rules = []
        
        # 클래스 계층 규칙
        class_hierarchy_rules = [
            {
                'rule': 'IndoorWarehouse ⊆ Warehouse',
                'description': '실내 창고는 창고의 하위 클래스'
            },
            {
                'rule': 'OutdoorWarehouse ⊆ Warehouse', 
                'description': '실외 창고는 창고의 하위 클래스'
            },
            {
                'rule': 'Site ⊆ Warehouse',
                'description': '현장은 창고의 하위 클래스'
            }
        ]
        
        # 속성 제약 규칙
        property_constraint_rules = [
            {
                'rule': 'hasAmount: TransportEvent → xsd:decimal',
                'description': 'hasAmount 속성은 TransportEvent에서 decimal 값으로'
            },
            {
                'rule': 'hasCBM: TransportEvent → xsd:decimal',
                'description': 'hasCBM 속성은 TransportEvent에서 decimal 값으로'
            },
            {
                'rule': 'hasPackageCount: TransportEvent → xsd:integer',
                'description': 'hasPackageCount 속성은 TransportEvent에서 integer 값으로'
            }
        ]
        
        # 비즈니스 로직 규칙
        business_logic_rules = [
            {
                'rule': 'TransportEvent(x) ∧ hasAmount(x, amt) ∧ amt > 100000 → HighValueCargo(x)',
                'description': '금액이 100,000 초과인 이벤트는 고가 화물로 분류'
            },
            {
                'rule': 'TransportEvent(x) ∧ hasCBM(x, cbm) ∧ cbm > 50 → LargeCargo(x)',
                'description': 'CBM이 50 초과인 이벤트는 대형 화물로 분류'
            },
            {
                'rule': 'TransportEvent(x) ∧ hasLocation(x, loc) ∧ IndoorWarehouse(loc) → hasStorageType(x, "indoor")',
                'description': '실내 창고 위치의 이벤트는 실내 저장 타입'
            }
        ]
        
        # 모든 규칙 통합
        all_rules = class_hierarchy_rules + property_constraint_rules + business_logic_rules
        
        for rule_set in [class_hierarchy_rules, property_constraint_rules, business_logic_rules]:
            for rule in rule_set:
                rule_type = 'class_hierarchy' if rule in class_hierarchy_rules else \
                           'property_constraint' if rule in property_constraint_rules else \
                           'business_logic'
                
                ontology_rules.append({
                    'type': rule_type,
                    'rule': rule['rule'],
                    'description': rule['description']
                })
        
        print(f"✅ {len(ontology_rules)}개 온톨로지 규칙 생성 완료")
        return ontology_rules

    # [MAJOR UPDATE v1.1] 머신러닝 기반 결측값 예측
    def predict_missing_values(self):
        """결측값 예측 및 추론 (IterativeImputer 기반)"""
        print("\n🔮 결측값 예측 및 추론 중 (ML)...")
        
        predictions = []
        
        if not self.ml_available:
            print("  ⚠️ ML 라이브러리가 없어 기본 통계 기반 예측을 사용합니다.")
            return self._predict_missing_basic()
        
        for source, df in self.data.items():
            print(f"📊 {source} 결측값 분석:")
            
            # 숫자형 데이터에 대해서만 예측 수행
            numeric_df = df.select_dtypes(include=[np.number])
            missing_cols = numeric_df.columns[numeric_df.isnull().any()].tolist()

            if not missing_cols:
                print(f"  ✅ {source}: 결측값 없음")
                continue

            if len(numeric_df.dropna()) < 10:
                print(f"  ⚠️ {source}: 학습 데이터 부족으로 ML 예측 스킵.")
                continue

            try:
                # IterativeImputer: 다른 모든 컬럼을 사용하여 결측값을 예측하는 정교한 방식
                imputer = IterativeImputer(
                    estimator=RandomForestRegressor(n_estimators=5, random_state=42),
                    max_iter=5, 
                    random_state=42,
                    tol=0.01
                )
                
                imputed_data = imputer.fit_transform(numeric_df)
                imputed_df = pd.DataFrame(imputed_data, columns=numeric_df.columns, index=numeric_df.index)
                
                print(f"  ✅ ML 기반 결측치 예측 모델 학습 및 적용 완료.")

                for col in missing_cols:
                    missing_indices = df[col][df[col].isnull()].index
                    if not missing_indices.empty:
                        # 결측이 발생했던 위치의 예측값 추출
                        predicted_values = imputed_df.loc[missing_indices, col]
                        
                        predictions.append({
                            'source': source,
                            'column': col,
                            'missing_count': len(missing_indices),
                            'missing_percentage': round(len(missing_indices) / len(df) * 100, 2),
                            'predicted_value_example': round(predicted_values.iloc[0], 3) if not predicted_values.empty else 'N/A',
                            'predicted_mean': round(predicted_values.mean(), 3) if not predicted_values.empty else 'N/A',
                            'method': 'IterativeImputer (RandomForest)',
                            'confidence': 0.85
                        })

            except Exception as e:
                print(f"  ❌ {source}: ML 예측 중 오류 발생 - {e}")

        print(f"✅ {len(predictions)}개 컬럼에 대한 ML 결측값 예측 완료")
        return predictions

    def _predict_missing_basic(self):
        """기본 통계 기반 결측값 예측 (ML 없이)"""
        predictions = []
        
        for source, df in self.data.items():
            missing_analysis = df.isnull().sum()
            missing_cols = missing_analysis[missing_analysis > 0].index
            
            for col in missing_cols:
                if df[col].dtype in ['int64', 'float64']:
                    mean_val = df[col].mean()
                    predictions.append({
                        'source': source,
                        'column': col,
                        'missing_count': int(missing_analysis[col]),
                        'missing_percentage': round(missing_analysis[col] / len(df) * 100, 2),
                        'predicted_value_example': round(mean_val, 3) if not pd.isna(mean_val) else 'N/A',
                        'method': 'Mean Imputation',
                        'confidence': 0.6
                    })
        
        return predictions

    def save_reasoning_results(self, relationships, business_rules, anomalies, ontology_rules, predictions):
        """온톨로지 추론 결과 저장"""
        print("\n💾 온톨로지 추론 결과 저장 중...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path('reasoning_output')
        output_dir.mkdir(exist_ok=True)
        
        # 종합 리포트 생성
        reasoning_report = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'engine_version': '1.1-ML' if self.ml_available else '1.1-Basic',
                'ml_enabled': self.ml_available,
                'total_records': sum(len(df) for df in self.data.values()),
                'data_sources': list(self.data.keys())
            },
            'data_relationships': relationships,
            'inferred_business_rules': business_rules,
            'anomalies_detected': anomalies,
            'ontology_rules': ontology_rules,
            'missing_value_predictions': predictions,
            'summary': {
                'relationships_found': len(relationships),
                'business_rules_inferred': len(business_rules),
                'anomalies_detected': len(anomalies),
                'ontology_rules_generated': len(ontology_rules),
                'missing_predictions': len(predictions)
            }
        }
        
        # JSON 리포트 저장
        json_file = output_dir / f'hvdc_reasoning_report_{timestamp}.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(reasoning_report, f, ensure_ascii=False, indent=2, default=str)
        
        # 마크다운 요약 리포트 생성
        md_file = output_dir / f'hvdc_reasoning_summary_{timestamp}.md'
        self._generate_markdown_summary(reasoning_report, md_file)
        
        # SPARQL 쿼리 생성
        sparql_file = output_dir / f'hvdc_reasoning_queries_{timestamp}.sparql'
        self._generate_sparql_queries(ontology_rules, sparql_file)
        
        print(f"  📊 JSON 리포트: {json_file.name} ({json_file.stat().st_size:,} bytes)")
        print(f"  📝 요약 리포트: {md_file.name} ({md_file.stat().st_size:,} bytes)")
        print(f"  🔍 SPARQL 쿼리: {sparql_file.name} ({sparql_file.stat().st_size:,} bytes)")
        
        return [json_file, md_file, sparql_file]

    def _generate_markdown_summary(self, report, output_file):
        """마크다운 요약 리포트 생성"""
        content = f"""# HVDC 온톨로지 추론 리포트

## 📊 실행 정보
- **생성 일시**: {report['metadata']['generated_at']}
- **엔진 버전**: {report['metadata']['engine_version']}
- **ML 활성화**: {'✅ 예' if report['metadata']['ml_enabled'] else '❌ 아니오'}
- **총 레코드**: {report['metadata']['total_records']:,}개
- **데이터 소스**: {', '.join(report['metadata']['data_sources'])}

## 🎯 추론 결과 요약
- **데이터 관계**: {report['summary']['relationships_found']}개 발견
- **비즈니스 규칙**: {report['summary']['business_rules_inferred']}개 추론
- **이상치 탐지**: {report['summary']['anomalies_detected']}개 발견
- **온톨로지 규칙**: {report['summary']['ontology_rules_generated']}개 생성
- **결측값 예측**: {report['summary']['missing_predictions']}개 컬럼

## 🤖 ML 기반 비즈니스 규칙

"""
        
        for rule in report['inferred_business_rules']:
            if rule['type'] == 'ml_inferred_rule':
                content += f"### {rule['rule']}\n"
                content += f"- **추론**: {rule['inference']}\n"
                content += f"- **신뢰도**: {rule['confidence']:.2%}\n"
                if 'features_used' in rule:
                    content += f"- **사용 특성**: {', '.join(rule['features_used'])}\n"
                content += "\n"
        
        content += "\n## 🚨 이상치 탐지 결과\n\n"
        
        high_severity = [a for a in report['anomalies_detected'] if a.get('severity') == 'high']
        for anomaly in high_severity[:5]:  # 상위 5개만
            if 'outlier_count' in anomaly:
                content += f"- **{anomaly['source']}.{anomaly['column']}**: {anomaly['outlier_count']}개 이상치 ({anomaly['percentage']:.1f}%)\n"
            elif 'missing_count' in anomaly:
                content += f"- **{anomaly['source']}.{anomaly['column']}**: {anomaly['missing_count']}개 결측값 ({anomaly['percentage']:.1f}%)\n"
            else:
                content += f"- **{anomaly['source']}.{anomaly.get('column', 'N/A')}**: {anomaly['type']} 탐지\n"
        
        content += "\n## 🔮 결측값 예측\n\n"
        
        for pred in report['missing_value_predictions'][:10]:  # 상위 10개만
            content += f"- **{pred['source']}.{pred['column']}**: {pred['missing_percentage']:.1f}% 결측 → 예측값 예시: {pred['predicted_value_example']}\n"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

    def _generate_sparql_queries(self, ontology_rules, output_file):
        """SPARQL 쿼리 생성"""
        queries = []
        
        # 고가 화물 자동 분류 쿼리
        queries.append("""
# 고가 화물 자동 분류
PREFIX ex: <http://samsung.com/project-logistics#>
CONSTRUCT {
    ?event a ex:HighValueCargo .
} WHERE {
    ?event a ex:TransportEvent ;
           ex:hasAmount ?amount .
    FILTER(?amount > 100000)
}
""")
        
        # 대형 화물 자동 분류 쿼리
        queries.append("""
# 대형 화물 자동 분류
PREFIX ex: <http://samsung.com/project-logistics#>
CONSTRUCT {
    ?event a ex:LargeCargo .
} WHERE {
    ?event a ex:TransportEvent ;
           ex:hasCBM ?cbm .
    FILTER(?cbm > 50)
}
""")
        
        # 창고 타입별 이벤트 조회
        queries.append("""
# 창고 타입별 이벤트 조회
PREFIX ex: <http://samsung.com/project-logistics#>
SELECT ?warehouse ?warehouseType ?eventCount WHERE {
    {
        SELECT ?warehouse ?warehouseType (COUNT(?event) AS ?eventCount) WHERE {
            ?event a ex:TransportEvent ;
                   ex:hasLocation ?warehouse .
            ?warehouse a ?warehouseType .
            FILTER(?warehouseType IN (ex:IndoorWarehouse, ex:OutdoorWarehouse, ex:Site))
        }
        GROUP BY ?warehouse ?warehouseType
    }
}
ORDER BY DESC(?eventCount)
""")
        
        content = "# HVDC 온톨로지 추론 SPARQL 쿼리\n"
        content += f"# 생성 일시: {datetime.now().isoformat()}\n\n"
        content += "\n".join(queries)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)


def main():
    """메인 실행 함수"""
    print("🧠 /cmd_ontology_reasoning 실행 (v1.1-ML)")
    print("=" * 70)
    print("🤖 HVDC 온톨로지 AI 추론 엔진 (머신러닝 업그레이드)")
    print("=" * 70)
    
    start_time = time.time()
    
    # 추론 엔진 초기화
    reasoner = HVDCOntologyReasoner(config_path='config.json')
    
    # 1단계: 데이터 및 규칙 로드
    reasoner.load_data_and_rules()
    
    if not reasoner.data:
        print("❌ 데이터를 로드할 수 없습니다.")
        return
    
    # 2단계: 데이터 관계 분석
    relationships = reasoner.analyze_data_relationships()
    
    # 3단계: 비즈니스 규칙 추론 (ML)
    business_rules = reasoner.infer_business_rules()
    
    # 4단계: 이상치 탐지
    anomalies = reasoner.detect_anomalies()
    
    # 5단계: 온톨로지 규칙 생성
    ontology_rules = reasoner.generate_ontology_rules()
    
    # 6단계: 결측값 예측 (ML)
    predictions = reasoner.predict_missing_values()
    
    # 7단계: 결과 저장
    result_files = reasoner.save_reasoning_results(
        relationships, business_rules, anomalies, ontology_rules, predictions
    )
    
    total_time = time.time() - start_time
    total_records = sum(len(df) for df in reasoner.data.values())
    
    print("\n🎉 온톨로지 추론 완료!")
    print("=" * 70)
    print(f"📊 처리 결과:")
    print(f"  • 총 처리 시간: {total_time:.2f}초")
    print(f"  • 분석 레코드: {total_records:,}개")
    print(f"  • 데이터 관계: {len(relationships)}개 발견")
    print(f"  • 비즈니스 규칙: {len(business_rules)}개 추론")
    print(f"  • 이상치 탐지: {len(anomalies)}개")
    print(f"  • 온톨로지 규칙: {len(ontology_rules)}개 생성")
    print(f"  • 결측값 예측: {len(predictions)}개")
    
    if reasoner.ml_available:
        print(f"  • ML 기반 규칙: {len([r for r in business_rules if 'ml_' in r['type']])}개 추론")
        print(f"  • ML 기반 예측: {len([p for p in predictions if 'RandomForest' in p.get('method', '')])}개 컬럼")
    
    print("\n📁 생성된 파일:")
    for file_path in result_files:
        print(f"  • {file_path.name}")

    print("\n🔧 추천 명령어:")
    print("  /validate_ontology [온톨로지 검증 실행]")
    print("  /predictive_analytics [예측 분석 실행]")
    print("  /visualize_data [데이터 시각화 실행]")

if __name__ == "__main__":
    main() 