#!/usr/bin/env python3
"""
DART 사이트 체크박스 상세 분석
"""

import requests
from bs4 import BeautifulSoup

def analyze_dart_checkboxes():
    """DART 사이트의 체크박스 구조 상세 분석"""
    print("🔍 DART 체크박스 구조 분석")
    print("=" * 50)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    })
    
    try:
        # 메인 페이지 접속
        url = "https://dart.fss.or.kr/dsab007/main.do"
        response = session.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        print("📋 모든 체크박스 찾기:")
        print("-" * 30)
        
        # 모든 input 타입 체크박스 찾기
        checkboxes = soup.find_all('input', {'type': 'checkbox'})
        
        print(f"총 체크박스 개수: {len(checkboxes)}")
        
        for i, checkbox in enumerate(checkboxes):
            name = checkbox.get('name', '없음')
            value = checkbox.get('value', '없음')
            cb_id = checkbox.get('id', '없음')
            
            # 라벨 찾기 (체크박스 설명)
            label_text = '없음'
            
            # id로 연결된 label 찾기
            if cb_id != '없음':
                label = soup.find('label', {'for': cb_id})
                if label:
                    label_text = label.get_text(strip=True)
            
            # 부모 요소에서 텍스트 찾기
            if label_text == '없음':
                parent = checkbox.parent
                if parent:
                    parent_text = parent.get_text(strip=True)
                    if parent_text and len(parent_text) < 50:
                        label_text = parent_text
            
            print(f"  {i+1:2d}. name='{name}', value='{value}', id='{cb_id}'")
            print(f"      라벨: '{label_text}'")
            
            # 정기공시 관련 체크박스 특별 표시
            if any(keyword in label_text for keyword in ['정기공시', '사업보고서', '반기보고서', '분기보고서']):
                print(f"      ⭐ 정기공시 관련!")
            
            print()
        
        print("\n📝 공시유형 관련 폼 필드 찾기:")
        print("-" * 30)
        
        # publicType 관련 요소들 찾기
        public_type_elements = soup.find_all(attrs={'name': lambda x: x and 'public' in x.lower()})
        for elem in public_type_elements:
            print(f"요소: {elem.name}, name='{elem.get('name')}', value='{elem.get('value')}'")
            print(f"내용: {elem}")
            print()
        
        print("\n🔍 JavaScript에서 정기공시 관련 코드 찾기:")
        print("-" * 30)
        
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string:
                content = script.string
                if '정기공시' in content or 'A01' in content or 'A02' in content or 'A03' in content:
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if any(keyword in line for keyword in ['정기공시', 'A01', 'A02', 'A03', 'publicType']):
                            print(f"라인 {i+1}: {line.strip()}")
                    print()
                    break
        
        print("\n📊 폼 구조 분석:")
        print("-" * 30)
        
        forms = soup.find_all('form')
        for i, form in enumerate(forms):
            form_id = form.get('id', f'form_{i}')
            action = form.get('action', '없음')
            method = form.get('method', '없음')
            
            print(f"폼 {i+1}: id='{form_id}', action='{action}', method='{method}'")
            
            # 폼 내부의 체크박스들
            form_checkboxes = form.find_all('input', {'type': 'checkbox'})
            if form_checkboxes:
                print(f"  폼 내 체크박스: {len(form_checkboxes)}개")
                for cb in form_checkboxes[:5]:  # 처음 5개만
                    name = cb.get('name', '없음')
                    value = cb.get('value', '없음')
                    print(f"    - name='{name}', value='{value}'")
            print()
            
    except Exception as e:
        print(f"오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_dart_checkboxes()