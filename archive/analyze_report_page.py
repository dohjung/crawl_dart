#!/usr/bin/env python3
"""
DART 보고서 페이지 분석 - 다운로드 버튼 찾기
"""

import requests
from bs4 import BeautifulSoup
import re

def analyze_report_page():
    """DART 보고서 페이지에서 다운로드 정보 분석"""
    print("🔍 DART 보고서 페이지 다운로드 분석")
    print("=" * 50)
    
    # 첫 번째 링크 테스트
    test_url = "https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20250814003156"
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    })
    
    try:
        print(f"📄 테스트 URL: {test_url}")
        response = session.get(test_url)
        response.raise_for_status()
        
        print(f"✅ 페이지 접속 성공 (길이: {len(response.text)})")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. rcpNo 추출 (URL에서)
        rcp_no_match = re.search(r'rcpNo=(\d+)', test_url)
        rcp_no = rcp_no_match.group(1) if rcp_no_match else None
        print(f"📋 rcpNo: {rcp_no}")
        
        # 2. dcmNo 찾기 - 여러 방법으로 시도
        print(f"\n🔍 dcmNo 찾기:")
        
        # 방법 1: JavaScript 변수에서 찾기
        scripts = soup.find_all('script')
        dcm_no = None
        
        for script in scripts:
            if script.string:
                content = script.string
                # dcmNo 변수 찾기
                dcm_match = re.search(r'dcmNo\s*[=:]\s*["\']?(\d+)["\']?', content, re.IGNORECASE)
                if dcm_match:
                    dcm_no = dcm_match.group(1)
                    print(f"  JavaScript 변수에서 발견: {dcm_no}")
                    break
                
                # openPdfDownload 함수 호출 찾기
                pdf_match = re.search(r'openPdfDownload\s*\(\s*["\']?(\d+)["\']?\s*,\s*["\']?(\d+)["\']?\s*\)', content)
                if pdf_match:
                    rcp_param = pdf_match.group(1)
                    dcm_param = pdf_match.group(2)
                    print(f"  openPdfDownload 호출에서 발견: rcpNo={rcp_param}, dcmNo={dcm_param}")
                    if not dcm_no:
                        dcm_no = dcm_param
                    break
        
        # 방법 2: HTML 속성에서 찾기
        if not dcm_no:
            # data-* 속성이나 value 속성에서 찾기
            elements_with_dcm = soup.find_all(attrs={'data-dcm-no': True})
            if elements_with_dcm:
                dcm_no = elements_with_dcm[0]['data-dcm-no']
                print(f"  HTML data-dcm-no 속성에서 발견: {dcm_no}")
        
        # 방법 3: 숨겨진 input 필드에서 찾기
        if not dcm_no:
            hidden_inputs = soup.find_all('input', {'type': 'hidden'})
            for inp in hidden_inputs:
                name = inp.get('name', '').lower()
                if 'dcm' in name or 'doc' in name:
                    value = inp.get('value', '')
                    if value and value.isdigit():
                        dcm_no = value
                        print(f"  숨겨진 input[{inp.get('name')}]에서 발견: {dcm_no}")
                        break
        
        # 방법 4: 다운로드 버튼/링크에서 찾기
        if not dcm_no:
            # 다운로드 관련 버튼이나 링크 찾기
            download_elements = soup.find_all(['a', 'button'], 
                string=re.compile(r'다운로드|download|PDF', re.IGNORECASE))
            
            for elem in download_elements:
                onclick = elem.get('onclick', '')
                href = elem.get('href', '')
                
                # onclick에서 dcmNo 추출
                if onclick:
                    dcm_match = re.search(r'(\d{8,})', onclick)
                    if dcm_match:
                        dcm_no = dcm_match.group(1)
                        print(f"  다운로드 버튼 onclick에서 발견: {dcm_no}")
                        print(f"  전체 onclick: {onclick}")
                        break
                
                # href에서 dcmNo 추출
                if href and 'dcm' in href.lower():
                    dcm_match = re.search(r'dcm[_-]?no=(\d+)', href, re.IGNORECASE)
                    if dcm_match:
                        dcm_no = dcm_match.group(1)
                        print(f"  다운로드 링크 href에서 발견: {dcm_no}")
                        break
        
        print(f"\n📋 최종 파라미터:")
        print(f"  rcpNo: {rcp_no}")
        print(f"  dcmNo: {dcm_no}")
        
        # 다운로드 URL 생성 시도
        if rcp_no and dcm_no:
            download_url = f"https://dart.fss.or.kr/pdf/download/main.do?rcp_no={rcp_no}&dcm_no={dcm_no}"
            print(f"\n🔗 예상 다운로드 URL:")
            print(f"  {download_url}")
            
            # 다운로드 URL 테스트
            print(f"\n🧪 다운로드 URL 테스트:")
            try:
                dl_response = session.get(download_url, allow_redirects=True, stream=True)
                print(f"  상태 코드: {dl_response.status_code}")
                print(f"  Content-Type: {dl_response.headers.get('Content-Type', '없음')}")
                print(f"  Content-Length: {dl_response.headers.get('Content-Length', '없음')}")
                
                if dl_response.status_code == 200 and 'application/pdf' in dl_response.headers.get('Content-Type', ''):
                    print(f"  ✅ PDF 다운로드 가능!")
                    
                    # 파일명 추출
                    content_disposition = dl_response.headers.get('Content-Disposition', '')
                    if content_disposition:
                        filename_match = re.search(r'filename[*]?=["\']?([^"\';\s]+)', content_disposition)
                        if filename_match:
                            filename = filename_match.group(1)
                            print(f"  파일명: {filename}")
                
            except Exception as e:
                print(f"  ❌ 다운로드 테스트 실패: {e}")
        else:
            print(f"\n❌ rcpNo 또는 dcmNo를 찾을 수 없음")
            
        # 페이지 구조 간단 분석
        print(f"\n📊 페이지 구조 분석:")
        title = soup.find('title')
        if title:
            print(f"  페이지 제목: {title.get_text(strip=True)}")
        
        # 다운로드 관련 요소들 찾기
        download_related = soup.find_all(string=re.compile(r'다운로드|download|PDF|파일', re.IGNORECASE))
        print(f"  다운로드 관련 텍스트: {len(download_related)}개 발견")
        for text in download_related[:3]:  # 처음 3개만
            print(f"    - '{text.strip()}'")
            
    except Exception as e:
        print(f"❌ 오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_report_page()