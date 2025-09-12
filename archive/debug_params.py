#!/usr/bin/env python3
"""
DART 파라미터 디버깅
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

def debug_dart_params():
    """실제 DART 파라미터 디버깅"""
    print("🔍 DART 파라미터 디버깅")
    print("=" * 50)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    })
    
    # 세션 초기화
    main_url = "https://dart.fss.or.kr/dsab007/main.do"
    session.get(main_url)
    
    # 여러 파라미터 조합 테스트
    search_url = "https://dart.fss.or.kr/dsab007/detailSearch.ax"
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=10*365)
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': main_url
    }
    
    # 테스트할 파라미터 조합들
    test_cases = [
        {
            'name': '기본 검색',
            'params': {
                'option': 'corp',
                'textCrpNm': '삼성전자',
                'startDate': start_date.strftime('%Y%m%d'),
                'endDate': end_date.strftime('%Y%m%d'),
                'currentPage': '1',
                'pageCount': '10'
            }
        },
        {
            'name': '정기공시 A01,A02,A03',
            'params': {
                'option': 'corp',
                'textCrpNm': '삼성전자',
                'startDate': start_date.strftime('%Y%m%d'),
                'endDate': end_date.strftime('%Y%m%d'),
                'publicType': 'A01,A02,A03',
                'currentPage': '1',
                'pageCount': '10'
            }
        },
        {
            'name': '정기공시 개별 체크',
            'params': {
                'option': 'corp',
                'textCrpNm': '삼성전자',
                'startDate': start_date.strftime('%Y%m%d'),
                'endDate': end_date.strftime('%Y%m%d'),
                'A01': 'on',  # 사업보고서
                'A02': 'on',  # 반기보고서
                'A03': 'on',  # 분기보고서
                'currentPage': '1',
                'pageCount': '10'
            }
        },
        {
            'name': '전체 공시유형',
            'params': {
                'option': 'corp',
                'textCrpNm': '삼성전자',
                'startDate': start_date.strftime('%Y%m%d'),
                'endDate': end_date.strftime('%Y%m%d'),
                'publicType': '',
                'currentPage': '1',
                'pageCount': '10'
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 테스트 {i}: {test_case['name']}")
        print("-" * 30)
        
        try:
            response = session.post(search_url, data=test_case['params'], headers=headers)
            print(f"응답 코드: {response.status_code}")
            print(f"응답 길이: {len(response.text)}")
            
            # BeautifulSoup로 파싱
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 테이블 찾기
            table = soup.find('table', {'class': 'tbList'})
            if table:
                tbody = table.find('tbody')
                if tbody:
                    rows = tbody.find_all('tr')
                    print(f"검색 결과: {len(rows)}건")
                    
                    if rows:
                        first_row = rows[0]
                        cells = first_row.find_all('td')
                        if len(cells) >= 3:
                            company = cells[1].get_text(strip=True)
                            report = cells[2].get_text(strip=True)[:40]
                            print(f"첫 번째 결과: {company} - {report}...")
                else:
                    print("tbody 없음")
            else:
                print("테이블 없음")
                
                # 에러 메시지 확인
                if '조회 결과가 없습니다' in response.text:
                    print("조회 결과 없음 메시지 확인")
                elif '<table' in response.text:
                    print("테이블은 있으나 클래스명이 다름")
                else:
                    print("HTML 구조 분석 필요")
                    
        except Exception as e:
            print(f"오류: {e}")
            
        print()

if __name__ == "__main__":
    debug_dart_params()