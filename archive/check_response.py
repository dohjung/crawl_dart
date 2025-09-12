#!/usr/bin/env python3
"""
A01,A02,A03 응답 상세 확인
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

def check_regular_response():
    """정기공시 응답 상세 확인"""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    })
    
    # 세션 초기화
    main_url = "https://dart.fss.or.kr/dsab007/main.do"
    session.get(main_url)
    
    search_url = "https://dart.fss.or.kr/dsab007/detailSearch.ax"
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=10*365)
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': main_url
    }
    
    params = {
        'option': 'corp',
        'textCrpNm': '삼성전자',
        'startDate': start_date.strftime('%Y%m%d'),
        'endDate': end_date.strftime('%Y%m%d'),
        'publicType': 'A01,A02,A03',
        'currentPage': '1',
        'pageCount': '100'
    }
    
    print("🔍 정기공시 응답 상세 분석")
    print("=" * 50)
    print(f"파라미터: {params}")
    print()
    
    try:
        response = session.post(search_url, data=params, headers=headers)
        print(f"응답 코드: {response.status_code}")
        print(f"응답 길이: {len(response.text)}")
        
        # 전체 응답 확인
        print(f"\n📄 응답 내용 (처음 500자):")
        print("-" * 30)
        print(response.text[:500])
        
        # BeautifulSoup로 파싱
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 모든 테이블 찾기
        tables = soup.find_all('table')
        print(f"\n📊 테이블 개수: {len(tables)}")
        
        for i, table in enumerate(tables):
            table_class = table.get('class', [])
            print(f"  테이블 {i+1}: class={table_class}")
            
            # tbody 찾기
            tbody = table.find('tbody')
            if tbody:
                rows = tbody.find_all('tr')
                print(f"    tbody 행 수: {len(rows)}")
                
                if rows:
                    for j, row in enumerate(rows[:2]):  # 처음 2개 행만
                        cells = row.find_all('td')
                        print(f"    행 {j+1}: {len(cells)}개 셀")
                        for k, cell in enumerate(cells):
                            text = cell.get_text(strip=True)[:30]
                            link = cell.find('a')
                            if link:
                                href = link.get('href', '')
                                onclick = link.get('onclick', '')[:50]
                                print(f"      셀 {k+1}: '{text}' [링크: {href}, onclick: {onclick}...]")
                            else:
                                print(f"      셀 {k+1}: '{text}'")
            else:
                # tbody 없이 tr 직접 찾기
                rows = table.find_all('tr')
                data_rows = rows[1:] if len(rows) > 1 else []
                print(f"    직접 tr 행 수: {len(data_rows)}")
                
                if data_rows:
                    first_row = data_rows[0]
                    cells = first_row.find_all('td')
                    print(f"    첫 행 셀 수: {len(cells)}")
                    for k, cell in enumerate(cells):
                        text = cell.get_text(strip=True)[:30]
                        link = cell.find('a')
                        if link:
                            href = link.get('href', '')
                            onclick = link.get('onclick', '')[:50]
                            print(f"      셀 {k+1}: '{text}' [링크: {href}, onclick: {onclick}...]")
                        else:
                            print(f"      셀 {k+1}: '{text}'")
        
        # 모든 링크 확인
        all_links = soup.find_all('a')
        report_links = []
        for link in all_links:
            onclick = link.get('onclick', '')
            if 'openReportViewer' in onclick:
                report_links.append({
                    'text': link.get_text(strip=True),
                    'onclick': onclick,
                    'href': link.get('href', '')
                })
        
        print(f"\n🔗 보고서 뷰어 링크: {len(report_links)}개")
        for link in report_links:
            print(f"  - {link['text']}: {link['href']}")
            print(f"    onclick: {link['onclick']}")
            
    except Exception as e:
        print(f"오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_regular_response()