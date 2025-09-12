#!/usr/bin/env python3
"""
DART 응답 상세 분석
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

def analyze_search_response():
    """검색 응답 상세 분석"""
    print("🔍 DART 검색 응답 상세 분석")
    print("=" * 50)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    })
    
    # 세션 초기화
    main_url = "https://dart.fss.or.kr/dsab007/main.do"
    session.get(main_url)
    
    # 검색 요청
    search_url = "https://dart.fss.or.kr/dsab007/detailSearch.ax"
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)  # 최근 3개월
    
    params = {
        'option': 'corp',
        'textCrpNm': '삼성전자',
        'startDate': start_date.strftime('%Y%m%d'),
        'endDate': end_date.strftime('%Y%m%d'),
        'currentPage': '1',
        'pageCount': '20'
    }
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': main_url
    }
    
    try:
        response = session.post(search_url, data=params, headers=headers)
        print(f"✓ 응답 수신: {response.status_code}, 길이: {len(response.text)}")
        
        # BeautifulSoup로 파싱
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 테이블 찾기
        tables = soup.find_all('table')
        print(f"\n📊 테이블 개수: {len(tables)}")
        
        for i, table in enumerate(tables):
            print(f"\n테이블 {i+1}:")
            print(f"  클래스: {table.get('class', [])}")
            
            # 헤더 행 분석
            thead = table.find('thead')
            if thead:
                header_cells = thead.find_all(['th', 'td'])
                print(f"  헤더 개수: {len(header_cells)}")
                for j, cell in enumerate(header_cells):
                    text = cell.get_text(strip=True)
                    print(f"    {j+1}: '{text}'")
            
            # 본문 행 분석
            tbody = table.find('tbody')
            if tbody:
                rows = tbody.find_all('tr')
                print(f"  데이터 행 개수: {len(rows)}")
                
                # 첫 번째 행 상세 분석
                if rows:
                    first_row = rows[0]
                    cells = first_row.find_all(['td', 'th'])
                    print(f"  첫 번째 행 셀 개수: {len(cells)}")
                    
                    for j, cell in enumerate(cells):
                        text = cell.get_text(strip=True)[:50]
                        
                        # 링크 찾기
                        links = cell.find_all('a')
                        if links:
                            for link in links:
                                href = link.get('href', '')
                                onclick = link.get('onclick', '')
                                print(f"    셀 {j+1}: '{text}' → 링크: href='{href}', onclick='{onclick[:50]}...'")
                        else:
                            print(f"    셀 {j+1}: '{text}'")
            else:
                # tbody가 없는 경우 tr 직접 찾기
                rows = table.find_all('tr')
                data_rows = rows[1:] if len(rows) > 1 else []
                print(f"  데이터 행 개수: {len(data_rows)}")
                
                if data_rows:
                    first_row = data_rows[0]
                    cells = first_row.find_all(['td', 'th'])
                    print(f"  첫 번째 데이터 행 셀 개수: {len(cells)}")
                    
                    for j, cell in enumerate(cells):
                        text = cell.get_text(strip=True)[:30]
                        
                        # 링크 찾기
                        links = cell.find_all('a')
                        if links:
                            for link in links:
                                href = link.get('href', '')
                                onclick = link.get('onclick', '')
                                print(f"    셀 {j+1}: '{text}' → href='{href}', onclick='{onclick[:80]}...'")
                        else:
                            print(f"    셀 {j+1}: '{text}'")
        
        # 전체 링크 분석
        print(f"\n🔗 전체 링크 분석:")
        all_links = soup.find_all('a')
        print(f"  총 링크 개수: {len(all_links)}")
        
        report_links = []
        for link in all_links:
            onclick = link.get('onclick', '')
            if 'openReportViewer' in onclick:
                report_links.append({
                    'text': link.get_text(strip=True)[:40],
                    'onclick': onclick,
                    'href': link.get('href', '')
                })
        
        print(f"  보고서 뷰어 링크: {len(report_links)}개")
        for i, link in enumerate(report_links[:3]):  # 처음 3개만
            print(f"    {i+1}: '{link['text']}' → {link['onclick'][:60]}...")
    
    except Exception as e:
        print(f"✗ 분석 실패: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    analyze_search_response()