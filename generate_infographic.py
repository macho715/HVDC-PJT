#!/usr/bin/env python3
"""
generate_infographic.py
=======================
자동으로 SVG 인포그래픽을 생성하는 스크립트.

Usage:
    python generate_infographic.py --input libraries.json --output infographic.svg --theme logistics

설명:
- `libraries.json` : 라이브러리·기능 정보를 담은 입력 파일 (예시는 README 참조)
- `--theme`        : 팔레트 선택 (기본 logistics)
- 출력물           : 크로스‑플랫폼 SVG (PPT/Notion/Streamlit 삽입 가능)

필수 PyPI : svgwrite (pip install svgwrite)
"""
import json
import argparse
import sys
import os
from dataclasses import dataclass
from typing import List
import svgwrite

# ──────────────────────────────────────────────────────────────
# 🎨  PALETTE (추후 확장 가능)
# ──────────────────────────────────────────────────────────────
THEMES = {
    "logistics": {
        "bg_color": "#F5F7FA",
        "title_color": "#004B87",
        "section_bg": "#FFFFFF",
        "section_border": "#D0D7DE",
        "text_color": "#333333",
        "feature_color": "#555555",
        "category_bg": "#004B87",
        "category_text": "#FFFFFF",
        "font": "Arial"
    },
    "dark": {
        "bg_color": "#1E1E1E",
        "title_color": "#E1E1E1",
        "section_bg": "#252526",
        "section_border": "#3C3C3C",
        "text_color": "#E1E1E1",
        "feature_color": "#CCCCCC",
        "category_bg": "#007ACC",
        "category_text": "#FFFFFF",
        "font": "Arial"
    },
    "minimal": {
        "bg_color": "#FFFFFF",
        "title_color": "#2D3748",
        "section_bg": "#F7FAFC",
        "section_border": "#E2E8F0",
        "text_color": "#2D3748",
        "feature_color": "#4A5568",
        "category_bg": "#4299E1",
        "category_text": "#FFFFFF",
        "font": "Arial"
    }
}

# ──────────────────────────────────────────────────────────────
# 📏  레이아웃 상수
# ──────────────────────────────────────────────────────────────
CARD_W = 360
CARD_H = 220
PAD_X  = 40
PAD_Y  = 80
COL_GAP = 40
ROW_GAP = 40
COLS = 2  # 2열 그리드

@dataclass
class Library:
    category: str
    name: str
    features: List[str]
    icon_path: str = ""  # 향후 SVG 아이콘 경로 지원

# ──────────────────────────────────────────────────────────────
# 🔄  Helper Functions
# ──────────────────────────────────────────────────────────────

def load_data(path: str) -> List[Library]:
    """JSON 파일에서 라이브러리 데이터를 로드합니다."""
    try:
        if not os.path.exists(path):
            print(f"❌ 파일을 찾을 수 없습니다: {path}")
            print("💡 예시 JSON 파일을 생성하려면 다음 명령어를 실행하세요:")
            print(f"   python {sys.argv[0]} --create-sample")
            sys.exit(1)
        
        with open(path, encoding="utf-8") as fp:
            raw = json.load(fp)
        
        if not raw:
            print(f"⚠️  JSON 파일이 비어있습니다: {path}")
            sys.exit(1)
            
        libraries = []
        for item in raw:
            try:
                libraries.append(Library(**item))
            except TypeError as e:
                print(f"❌ JSON 데이터 형식 오류: {e}")
                print(f"💡 올바른 형식: {{'category': '...', 'name': '...', 'features': [...]}}")
                sys.exit(1)
                
        return libraries
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON 파싱 오류: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 파일 읽기 오류: {e}")
        sys.exit(1)


def create_sample_json(path: str):
    """예시 JSON 파일을 생성합니다."""
    sample_data = [
        {
            "category": "Data Analysis",
            "name": "Pandas",
            "features": [
                "DataFrame 데이터 구조",
                "CSV/Excel 파일 읽기/쓰기",
                "데이터 정제 및 변환",
                "그룹별 집계 연산"
            ]
        },
        {
            "category": "Visualization",
            "name": "Matplotlib",
            "features": [
                "2D 플롯 생성",
                "다양한 차트 타입",
                "커스터마이징 가능",
                "출판용 품질 그래프"
            ]
        },
        {
            "category": "Machine Learning",
            "name": "Scikit-learn",
            "features": [
                "분류/회귀 알고리즘",
                "데이터 전처리",
                "모델 평가 도구",
                "파이프라인 구성"
            ]
        },
        {
            "category": "Deep Learning",
            "name": "TensorFlow",
            "features": [
                "신경망 모델 구축",
                "GPU 가속 지원",
                "분산 학습",
                "모바일 배포"
            ]
        },
        {
            "category": "Numerical Computing",
            "name": "NumPy",
            "features": [
                "N차원 배열 연산",
                "선형대수 함수",
                "브로드캐스팅",
                "C/Fortran 연동"
            ]
        },
        {
            "category": "Web Scraping",
            "name": "BeautifulSoup",
            "features": [
                "HTML/XML 파싱",
                "CSS 선택자 지원",
                "태그 검색 및 수정",
                "인코딩 자동 감지"
            ]
        }
    ]
    
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(sample_data, f, ensure_ascii=False, indent=2)
        print(f"✅ 예시 JSON 파일이 생성되었습니다: {path}")
        print(f"💡 이제 다음 명령어로 인포그래픽을 생성할 수 있습니다:")
        print(f"   python {sys.argv[0]} --input {path}")
    except Exception as e:
        print(f"❌ 파일 생성 실패: {e}")
        sys.exit(1)


def draw_text(dwg: svgwrite.Drawing, text: str, pos: tuple, size: int, color: str, 
              weight: str = "normal", anchor: str = "start"):
    """SVG에 텍스트를 추가합니다."""
    dwg.add(dwg.text(text, insert=pos, fill=color,
                     font_size=f"{size}px", font_family="Arial", 
                     font_weight=weight, text_anchor=anchor))


def truncate_text(text: str, max_length: int) -> str:
    """텍스트가 너무 길면 생략합니다."""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def create_svg(libs: List[Library], output: str, theme: str, title: str = "Python Data & ML Stack"):
    """SVG 인포그래픽을 생성합니다."""
    palette = THEMES.get(theme, THEMES["logistics"])

    rows = (len(libs) + COLS - 1) // COLS
    width  = PAD_X * 2 + CARD_W * COLS + COL_GAP * (COLS - 1)
    height = PAD_Y * 2 + CARD_H * rows + ROW_GAP * (rows - 1) + 20  # 여백 추가

    try:
        dwg = svgwrite.Drawing(output, profile="full", size=(f"{width}px", f"{height}px"))
        
        # 배경
        dwg.add(dwg.rect(insert=(0, 0), size=(f"{width}px", f"{height}px"), 
                         fill=palette["bg_color"]))

        # 제목 (중앙 정렬)
        title_truncated = truncate_text(title, 50)
        draw_text(dwg, title_truncated, (width / 2, 40), 28, palette["title_color"], 
                  "bold", "middle")

        # 카드들
        for idx, lib in enumerate(libs):
            col = idx % COLS
            row = idx // COLS
            x = PAD_X + col * (CARD_W + COL_GAP)
            y = PAD_Y + row * (CARD_H + ROW_GAP)

            # 카드 배경
            dwg.add(dwg.rect((x, y), (CARD_W, CARD_H), 
                             fill=palette["section_bg"],
                             stroke=palette["section_border"], 
                             stroke_width="1px",
                             rx="8px", ry="8px"))

            # 카테고리 태그
            category_text = truncate_text(lib.category, 20)
            tag_width = max(len(category_text) * 8 + 16, 80)
            dwg.add(dwg.rect((x + 15, y + 15), (tag_width, 22),
                             fill=palette["category_bg"], 
                             rx="11px", ry="11px"))
            
            draw_text(dwg, category_text, (x + 15 + tag_width/2, y + 30), 12, 
                      palette["category_text"], "normal", "middle")

            # 라이브러리 이름
            lib_name = truncate_text(lib.name, 25)
            draw_text(dwg, lib_name, (x + 20, y + 60), 20, palette["title_color"], "bold")

            # 기능 목록
            feature_y = y + 90
            max_features = min(len(lib.features), 5)  # 최대 5개까지만
            
            for i in range(max_features):
                if feature_y + 20 > y + CARD_H - 15:  # 카드 경계 체크
                    break
                    
                feature_text = truncate_text(lib.features[i], 35)
                draw_text(dwg, f"• {feature_text}", (x + 25, feature_y), 14, 
                          palette["feature_color"])
                feature_y += 20
            
            # 더 많은 기능이 있으면 표시
            if len(lib.features) > max_features:
                remaining = len(lib.features) - max_features
                if feature_y + 20 <= y + CARD_H - 15:
                    draw_text(dwg, f"• ... 외 {remaining}개 더", (x + 25, feature_y), 12, 
                              palette["feature_color"])

        # 푸터
        footer_text = f"Generated with SVG Infographic Generator • Theme: {theme}"
        draw_text(dwg, footer_text, (width / 2, height - 15), 10, 
                  palette["feature_color"], "normal", "middle")

        dwg.save()
        
        print(f"✅ SVG 파일이 성공적으로 저장되었습니다: {output}")
        print(f"📏 크기: {width}×{height}px")
        print(f"🎨 테마: {theme}")
        print(f"📊 총 {len(libs)}개 라이브러리")
        
    except Exception as e:
        print(f"❌ SVG 생성 실패: {e}")
        sys.exit(1)


# ──────────────────────────────────────────────────────────────
# 🏁  CLI 진입점
# ──────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(
        description="Auto‑Generate SVG Infographic from JSON data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  %(prog)s                                    # 기본 설정으로 생성
  %(prog)s --theme dark                      # 다크 테마 사용
  %(prog)s --input my_data.json              # 커스텀 데이터 사용
  %(prog)s --create-sample                   # 예시 파일 생성
  %(prog)s --list-themes                     # 테마 목록 보기

지원되는 테마: """ + ", ".join(THEMES.keys())
    )
    
    ap.add_argument("--input", "-i", default="libraries.json", 
                    help="JSON 입력 파일 경로 (기본값: libraries.json)")
    ap.add_argument("--output", "-o", default="infographic.svg", 
                    help="SVG 출력 파일 경로 (기본값: infographic.svg)")
    ap.add_argument("--theme", "-t", default="logistics", 
                    choices=list(THEMES.keys()), 
                    help="색상 테마 선택 (기본값: logistics)")
    ap.add_argument("--title", default="Python Data & ML Stack",
                    help="인포그래픽 제목")
    ap.add_argument("--create-sample", action="store_true",
                    help="예시 JSON 데이터 파일을 생성합니다")
    ap.add_argument("--list-themes", action="store_true",
                    help="사용 가능한 테마 목록을 표시합니다")
    ap.add_argument("--version", action="version", version="SVG Infographic Generator v1.0")
    
    args = ap.parse_args()

    # 테마 목록 표시
    if args.list_themes:
        print("🎨 사용 가능한 테마:")
        for theme_name, theme_data in THEMES.items():
            print(f"  • {theme_name:12} - 배경: {theme_data['bg_color']}, 제목: {theme_data['title_color']}")
        return

    # 예시 파일 생성
    if args.create_sample:
        create_sample_json(args.input)
        return

    # svgwrite 모듈 체크
    try:
        import svgwrite
    except ImportError:
        print("❌ svgwrite 모듈이 설치되지 않았습니다.")
        print("💡 다음 명령어로 설치하세요:")
        print("   pip install svgwrite")
        sys.exit(1)

    # 메인 로직 실행
    try:
        print(f"🔄 JSON 파일 로딩: {args.input}")
        libs = load_data(args.input)
        
        print(f"🎨 테마 적용: {args.theme}")
        print(f"🖼️  SVG 생성 중...")
        
        create_svg(libs, args.output, args.theme, args.title)
        
    except KeyboardInterrupt:
        print("\n⚠️  사용자에 의해 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 예상치 못한 오류 발생: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()