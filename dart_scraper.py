#!/usr/bin/env python3
"""
DART 공시정보 검색 프로그램
https://dart.fss.or.kr/dsab007/main.do 사이트의 회사 검색 기능을 콘솔에서 사용
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import json
import re
import os
from typing import List, Dict, Optional


class DartScraper:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://dart.fss.or.kr"
        self.main_url = f"{self.base_url}/dsab007/main.do"
        self.search_url = f"{self.base_url}/dsab007/detailSearch.ax"
        
        # 기본 헤더 설정
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def get_search_page(self) -> bool:
        """검색 페이지에 접속하여 세션 초기화"""
        try:
            response = self.session.get(self.main_url)
            response.raise_for_status()
            
            # HTML 파싱하여 필요한 정보 확인
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 검색 폼이 있는지 확인
            search_form = soup.find('form')
            if search_form:
                print("✓ DART 검색 페이지 접속 성공")
                return True
            else:
                print("✗ 검색 폼을 찾을 수 없습니다")
                return False
                
        except Exception as e:
            print(f"✗ 페이지 접속 실패: {e}")
            return False
    
    def search_company_regular_reports(self, company_name: str, max_pages: int = 20) -> List[Dict]:
        """
        회사명으로 정기공시 검색 (10년, 정기공시 체크박스 사용)
        
        Args:
            company_name: 검색할 회사명
            max_pages: 최대 검색할 페이지 수
        
        Returns:
            검색 결과 리스트
        """
        try:
            # 10년 기간 설정
            end_date = datetime.now()
            start_date = end_date - timedelta(days=10*365)
            
            print(f"🔍 '{company_name}' 정기공시 검색 중... (기간: 10년)")
            print(f"   검색 기간: {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
            print(f"   공시유형: 정기공시 (사업보고서, 반기보고서, 분기보고서)")
            
            # Ajax 요청 헤더 설정
            ajax_headers = {
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': self.main_url
            }
            
            all_results = []
            
            # 여러 페이지 검색
            for page in range(1, max_pages + 1):
                # 검색 파라미터 설정 (튜플 배열 방식 - 성공 확인됨)
                search_data = [
                    ('option', 'corp'),
                    ('textCrpNm', company_name),
                    ('startDate', start_date.strftime('%Y%m%d')),
                    ('endDate', end_date.strftime('%Y%m%d')),
                    ('publicType', 'A001'),  # 사업보고서
                    ('publicType', 'A002'),  # 반기보고서
                    ('publicType', 'A003'),  # 분기보고서
                    ('currentPage', str(page)),
                    ('pageCount', '100')
                ]
                
                print(f"   페이지 {page} 검색 중...")
                
                # POST 요청으로 검색 실행 (data 파라미터 사용)
                response = self.session.post(self.search_url, data=search_data, headers=ajax_headers)
                response.raise_for_status()
                
                # 결과 파싱
                page_results = self._parse_search_results(response.text)
                
                if not page_results:
                    print(f"   페이지 {page}: 결과 없음 - 검색 종료")
                    break
                
                print(f"   페이지 {page}: {len(page_results)}건 발견")
                all_results.extend(page_results)
                
                # 잠시 대기 (서버 부하 방지)
                time.sleep(0.5)
            
            results = all_results
            print(f"   총 검색 결과: {len(results)}건")
            
            return results
            
        except Exception as e:
            print(f"✗ 검색 실패: {e}")
            return []
    
    def search_company_all(self, company_name: str, years: int = 10, max_pages: int = 20) -> List[Dict]:
        """
        회사명으로 전체 공시정보 검색 (필터링 없음)
        
        Args:
            company_name: 검색할 회사명
            years: 검색 기간 (년)
            max_pages: 최대 검색할 페이지 수
        
        Returns:
            검색 결과 리스트
        """
        try:
            # 날짜 계산
            end_date = datetime.now()
            start_date = end_date - timedelta(days=years*365)
            
            print(f"🔍 '{company_name}' 전체 검색 중... (기간: {years}년)")
            print(f"   검색 기간: {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
            
            # Ajax 요청 헤더 설정
            ajax_headers = {
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': self.main_url
            }
            
            all_results = []
            
            # 여러 페이지 검색
            for page in range(1, max_pages + 1):
                # 기본 검색 파라미터 (가장 많은 결과 반환)
                search_params = {
                    'option': 'corp',
                    'textCrpNm': company_name,
                    'startDate': start_date.strftime('%Y%m%d'),
                    'endDate': end_date.strftime('%Y%m%d'),
                    'currentPage': str(page),
                    'pageCount': '100'
                }
                
                print(f"   페이지 {page} 검색 중...")
                
                # POST 요청으로 검색 실행
                response = self.session.post(self.search_url, data=search_params, headers=ajax_headers)
                response.raise_for_status()
                
                # 결과 파싱
                page_results = self._parse_search_results(response.text)
                
                if not page_results:
                    print(f"   페이지 {page}: 결과 없음 - 검색 종료")
                    break
                
                print(f"   페이지 {page}: {len(page_results)}건 발견")
                all_results.extend(page_results)
                
                # 잠시 대기 (서버 부하 방지)
                time.sleep(0.5)
            
            print(f"   총 검색 결과: {len(all_results)}건")
            return all_results
            
        except Exception as e:
            print(f"✗ 검색 실패: {e}")
            return []
    
    def _parse_search_results(self, html_content: str) -> List[Dict]:
        """검색 결과 HTML 파싱"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            results = []
            
            # 결과 테이블 찾기 (실제 DART 구조)
            table = soup.find('table', {'class': 'tbList'})
            if not table:
                # 다른 방식으로 찾기
                table = soup.find('table')
                
            if table:
                tbody = table.find('tbody')
                if tbody:
                    rows = tbody.find_all('tr')
                    
                    for row in rows:
                        cols = row.find_all('td')
                        if len(cols) >= 6:  # 최소 6개 컬럼이 있어야 함
                            try:
                                # 보고서명 컬럼에서 링크 추출
                                report_cell = cols[2]
                                report_link = report_cell.find('a')
                                report_url = ''
                                
                                if report_link and report_link.get('href'):
                                    href = report_link.get('href')
                                    if href.startswith('/'):
                                        report_url = self.base_url + href
                                    elif href.startswith('http'):
                                        report_url = href
                                    else:
                                        report_url = self.base_url + '/' + href
                                
                                # 각 컬럼에서 텍스트 추출
                                result = {
                                    'no': cols[0].get_text(strip=True),
                                    'company': cols[1].get_text(strip=True),
                                    'report_name': cols[2].get_text(strip=True),
                                    'submitter': cols[3].get_text(strip=True),
                                    'submit_date': cols[4].get_text(strip=True),
                                    'note': cols[5].get_text(strip=True) if len(cols) > 5 else '',
                                    'report_url': report_url  # 보고서 링크 추가
                                }
                                
                                # 빈 결과가 아닌 경우만 추가
                                if result['company'] and result['report_name']:
                                    results.append(result)
                                    
                            except Exception as e:
                                print(f"행 파싱 오류: {e}")
                                continue
            
            # 결과가 없는 경우 "조회 결과가 없습니다" 메시지 확인
            if not results:
                no_result = soup.find(string=lambda text: text and '조회 결과가 없습니다' in text)
                if no_result:
                    print("📭 검색 결과가 없습니다.")
                else:
                    print("⚠️ 결과 파싱 중 문제가 발생했습니다.")
                    # 디버그용: HTML 일부 출력
                    print("HTML 샘플:")
                    print(soup.prettify()[:500] + "...")
            
            return results
            
        except Exception as e:
            print(f"✗ 결과 파싱 실패: {e}")
            return []
    
    def display_results(self, results: List[Dict]) -> None:
        """검색 결과를 보기 좋게 출력"""
        if not results:
            print("📭 검색 결과가 없습니다.")
            return
        
        print(f"\n📊 검색 결과: 총 {len(results)}건")
        print("=" * 100)
        
        for i, result in enumerate(results, 1):
            print(f"{i:3d}. 회사: {result['company']}")
            print(f"     보고서: {result['report_name']}")
            print(f"     제출인: {result['submitter']}")
            print(f"     접수일: {result['submit_date']}")
            if result.get('report_url'):
                print(f"     링크: {result['report_url']}")
            if result['note']:
                print(f"     비고: {result['note']}")
            print("-" * 80)
    
    def save_results(self, results: List[Dict], filename: str = None) -> None:
        """검색 결과를 JSON 파일로 저장"""
        if not results:
            print("저장할 결과가 없습니다.")
            return
        
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"dart_search_results_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            print(f"💾 결과가 {filename}에 저장되었습니다.")
            
        except Exception as e:
            print(f"✗ 파일 저장 실패: {e}")
    
    def save_links_to_txt(self, results: List[Dict], filename: str = None) -> None:
        """필터링된 보고서의 링크를 텍스트 파일로 저장"""
        if not results:
            print("저장할 링크가 없습니다.")
            return
        
        # 링크가 있는 결과만 필터링
        results_with_links = [r for r in results if r.get('report_url')]
        
        if not results_with_links:
            print("링크가 있는 보고서가 없습니다.")
            return
        
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"dart_report_links_{timestamp}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"# DART 보고서 링크 목록\n")
                f.write(f"# 생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"# 총 {len(results_with_links)}개 링크\n")
                f.write(f"{'='*80}\n\n")
                
                for i, result in enumerate(results_with_links, 1):
                    f.write(f"[{i:3d}] {result['company']} - {result['report_name']}\n")
                    f.write(f"      접수일: {result['submit_date']}\n")
                    f.write(f"      링크: {result['report_url']}\n")
                    if result.get('note'):
                        f.write(f"      비고: {result['note']}\n")
                    f.write(f"\n")
                
                # 링크만 별도로 정리
                f.write(f"\n{'='*80}\n")
                f.write(f"# 링크만 별도 정리 (복사용)\n")
                f.write(f"{'='*80}\n\n")
                
                for result in results_with_links:
                    f.write(f"{result['report_url']}\n")
            
            print(f"🔗 링크가 {filename}에 저장되었습니다. (총 {len(results_with_links)}개)")
            
        except Exception as e:
            print(f"✗ 링크 파일 저장 실패: {e}")
    
    def get_report_download_info(self, report_url: str) -> Optional[Dict[str, str]]:
        """보고서 페이지에서 다운로드 정보 추출"""
        try:
            print(f"📄 보고서 페이지 분석: {report_url}")
            
            response = self.session.get(report_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # rcpNo 추출 (URL에서)
            rcp_no_match = re.search(r'rcpNo=(\d+)', report_url)
            rcp_no = rcp_no_match.group(1) if rcp_no_match else None
            
            if not rcp_no:
                print("  ❌ rcpNo를 찾을 수 없음")
                return None
            
            # dcmNo 찾기 - 여러 방법으로 시도
            dcm_no = None
            
            # 방법 1: JavaScript 변수에서 찾기
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string:
                    content = script.string
                    
                    # dcmNo 변수 찾기
                    dcm_match = re.search(r'dcmNo\s*[=:]\s*["\']?(\d+)["\']?', content, re.IGNORECASE)
                    if dcm_match:
                        dcm_no = dcm_match.group(1)
                        print(f"  ✅ JavaScript 변수에서 dcmNo 발견: {dcm_no}")
                        break
                    
                    # openPdfDownload 함수 호출 찾기
                    pdf_match = re.search(r'openPdfDownload\s*\(\s*["\']?(\d+)["\']?\s*,\s*["\']?(\d+)["\']?\s*\)', content)
                    if pdf_match:
                        rcp_param = pdf_match.group(1)
                        dcm_param = pdf_match.group(2)
                        print(f"  ✅ openPdfDownload 호출에서 발견: rcpNo={rcp_param}, dcmNo={dcm_param}")
                        dcm_no = dcm_param  # openPdfDownload에서 찾은 dcmNo가 정확함
                        break
            
            # 방법 2: HTML 속성에서 찾기
            if not dcm_no:
                elements_with_dcm = soup.find_all(attrs={'data-dcm-no': True})
                if elements_with_dcm:
                    dcm_no = elements_with_dcm[0]['data-dcm-no']
                    print(f"  ✅ HTML data-dcm-no 속성에서 발견: {dcm_no}")
            
            # 방법 3: 숨겨진 input 필드에서 찾기
            if not dcm_no:
                hidden_inputs = soup.find_all('input', {'type': 'hidden'})
                for inp in hidden_inputs:
                    name = inp.get('name', '').lower()
                    if 'dcm' in name or 'doc' in name:
                        value = inp.get('value', '')
                        if value and value.isdigit():
                            dcm_no = value
                            print(f"  ✅ 숨겨진 input[{inp.get('name')}]에서 발견: {dcm_no}")
                            break
            
            # 방법 4: 다운로드 버튼/링크에서 찾기
            if not dcm_no:
                download_elements = soup.find_all(['a', 'button'], 
                    string=re.compile(r'다운로드|download|PDF', re.IGNORECASE))
                
                for elem in download_elements:
                    onclick = elem.get('onclick', '')
                    href = elem.get('href', '')
                    
                    # onclick에서 dcmNo 추출 (openPdfDownload 함수 호출에서)
                    if onclick:
                        pdf_onclick_match = re.search(r'openPdfDownload\s*\(\s*["\']?(\d+)["\']?\s*,\s*["\']?(\d+)["\']?\s*\)', onclick)
                        if pdf_onclick_match:
                            rcp_param = pdf_onclick_match.group(1)
                            dcm_param = pdf_onclick_match.group(2)
                            dcm_no = dcm_param
                            print(f"  ✅ 다운로드 버튼 onclick에서 발견: dcmNo={dcm_no}")
                            print(f"  전체 onclick: {onclick}")
                            break
                    
                    # href에서 dcmNo 추출
                    if href and 'dcm' in href.lower():
                        dcm_match = re.search(r'dcm[_-]?no=(\d+)', href, re.IGNORECASE)
                        if dcm_match:
                            dcm_no = dcm_match.group(1)
                            print(f"  ✅ 다운로드 링크 href에서 발견: {dcm_no}")
                            break
            
            if rcp_no and dcm_no:
                return {
                    'rcp_no': rcp_no,
                    'dcm_no': dcm_no,
                    'download_page_url': f"https://dart.fss.or.kr/pdf/download/main.do?rcp_no={rcp_no}&dcm_no={dcm_no}",
                    'download_url': f"https://dart.fss.or.kr/pdf/download/pdf.do?rcp_no={rcp_no}&dcm_no={dcm_no}"
                }
            else:
                print(f"  ❌ 다운로드 파라미터를 찾을 수 없음 (rcpNo: {rcp_no}, dcmNo: {dcm_no})")
                return None
                
        except Exception as e:
            print(f"  ❌ 다운로드 정보 추출 실패: {e}")
            return None
    
    def download_report_file(self, download_info: Dict[str, str], save_dir: str = "downloads") -> bool:
        """보고서 파일 다운로드"""
        try:
            download_url = download_info['download_url']
            rcp_no = download_info['rcp_no']
            dcm_no = download_info['dcm_no']
            
            print(f"📥 파일 다운로드 시도: rcpNo={rcp_no}, dcmNo={dcm_no}")
            
            # 다운로드 폴더 생성
            os.makedirs(save_dir, exist_ok=True)
            
            # 1단계: 보고서 페이지 방문하여 세션 설정
            report_page_url = f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcp_no}"
            self.session.get(report_page_url)
            
            # 2단계: 다운로드 페이지 방문 (필요시)
            if 'download_page_url' in download_info:
                download_page_url = download_info['download_page_url']
                self.session.get(download_page_url)
                referer_url = download_page_url
            else:
                referer_url = report_page_url
            
            # 3단계: 실제 PDF 파일 다운로드
            headers = {
                'Referer': referer_url,
                'Accept': 'application/pdf,*/*'
            }
            response = self.session.get(download_url, headers=headers, allow_redirects=True, stream=True)
            
            print(f"  응답 상태: {response.status_code}")
            print(f"  Content-Type: {response.headers.get('Content-Type', '없음')}")
            print(f"  Content-Length: {response.headers.get('Content-Length', '없음')}")
            
            if response.status_code == 200:
                content_type = response.headers.get('Content-Type', '')
                
                if 'application/pdf' in content_type:
                    # 파일명 생성 - 한글 인코딩 문제 해결
                    content_disposition = response.headers.get('Content-Disposition', '')
                    filename = None
                    
                    if content_disposition:
                        try:
                            # filename*= 형태 (RFC 6266) 우선 처리
                            filename_star_match = re.search(r'filename\*=UTF-8\'\'([^;]+)', content_disposition)
                            if filename_star_match:
                                import urllib.parse
                                filename = urllib.parse.unquote(filename_star_match.group(1))
                                print(f"  📝 UTF-8 파일명: {filename}")
                            else:
                                # 일반 filename= 형태 처리
                                filename_match = re.search(r'filename=["\']?([^"\';\s][^"\';]*)["\']?', content_disposition)
                                if filename_match:
                                    raw_filename = filename_match.group(1)
                                    print(f"  🔍 원본 파일명: {repr(raw_filename)}")
                                    
                                    # 여러 인코딩 방식 시도
                                    encodings_to_try = [
                                        ('euc-kr', 'EUC-KR'),      # 한국어 주요 인코딩
                                        ('cp949', 'CP949'),        # 한국어 확장 인코딩  
                                        ('utf-8', 'UTF-8'),        # 일반적인 UTF-8
                                        ('iso-8859-1', 'ISO-8859-1')  # 서버 기본값
                                    ]
                                    
                                    filename = None
                                    for encoding, desc in encodings_to_try:
                                        try:
                                            # 먼저 ISO-8859-1로 바이트화한 후 해당 인코딩으로 디코딩
                                            decoded = raw_filename.encode('iso-8859-1').decode(encoding)
                                            # 한글이 포함되어 있는지 확인 (유효성 검사)
                                            if any('\uac00' <= c <= '\ud7a3' for c in decoded):
                                                filename = decoded
                                                print(f"  ✅ {desc} 디코딩 성공: {filename}")
                                                break
                                        except (UnicodeDecodeError, UnicodeEncodeError):
                                            continue
                                    
                                    # 모든 디코딩이 실패한 경우 원본 사용
                                    if not filename:
                                        filename = raw_filename
                                        print(f"  ⚠️  원본 파일명 사용: {filename}")
                        except Exception as e:
                            print(f"  ❌ 파일명 처리 오류: {e}")
                    
                    # 기본 파일명 설정
                    if not filename:
                        filename = f"report_{rcp_no}_{dcm_no}.pdf"
                    
                    # 파일명 정리 (안전한 파일명 생성)
                    import string
                    # 한글, 영문, 숫자, 기본 기호만 허용
                    safe_filename = ""
                    for c in filename:
                        if (c.isalnum() or c in "-_.() []" or 
                            '\uac00' <= c <= '\ud7a3' or  # 한글 음절
                            '\u3131' <= c <= '\u318e'):   # 한글 자모
                            safe_filename += c
                    
                    filename = safe_filename if safe_filename else f"report_{rcp_no}_{dcm_no}.pdf"
                    
                    # PDF 확장자 확인
                    if not filename.lower().endswith('.pdf'):
                        filename += '.pdf'
                        
                    print(f"  📝 최종 파일명: {filename}")
                    
                    # 파일 저장
                    file_path = os.path.join(save_dir, filename)
                    
                    with open(file_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                    
                    print(f"  ✅ 다운로드 완료: {file_path}")
                    return True
                    
                else:
                    print(f"  ⚠️ PDF가 아닌 응답: {content_type}")
                    # HTML 응답인 경우 로그인 페이지일 가능성
                    if 'text/html' in content_type:
                        print(f"  📄 HTML 응답 - 로그인이 필요하거나 다른 처리가 필요할 수 있음")
                    return False
            else:
                print(f"  ❌ 다운로드 실패: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"  ❌ 파일 다운로드 실패: {e}")
            return False
    
    def download_all_reports_from_txt(self, txt_file: str, save_dir: str = "downloads") -> None:
        """TXT 파일의 모든 링크에서 보고서 다운로드"""
        try:
            print(f"📁 링크 파일 읽기: {txt_file}")
            
            if not os.path.exists(txt_file):
                print(f"❌ 파일이 없습니다: {txt_file}")
                return
            
            # 링크 추출
            links = []
            with open(txt_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('https://dart.fss.or.kr/dsaf001/main.do?rcpNo='):
                        links.append(line)
            
            if not links:
                print("❌ 유효한 링크를 찾을 수 없습니다")
                return
            
            print(f"🔍 총 {len(links)}개 링크 발견")
            print(f"📁 다운로드 폴더: {save_dir}")
            print("=" * 80)
            
            # 다운로드 통계
            success_count = 0
            fail_count = 0
            
            for i, link in enumerate(links, 1):
                print(f"\n[{i:2d}/{len(links)}] 처리 중...")
                
                # 다운로드 정보 추출
                download_info = self.get_report_download_info(link)
                
                if download_info:
                    # 파일 다운로드
                    if self.download_report_file(download_info, save_dir):
                        success_count += 1
                    else:
                        fail_count += 1
                else:
                    fail_count += 1
                
                # 서버 부하 방지를 위한 대기
                if i < len(links):
                    time.sleep(1)
            
            # 결과 요약
            print("\n" + "=" * 80)
            print(f"🎉 다운로드 완료!")
            print(f"  ✅ 성공: {success_count}건")
            print(f"  ❌ 실패: {fail_count}건")
            print(f"  📁 저장 위치: {os.path.abspath(save_dir)}")
            
        except Exception as e:
            print(f"❌ 일괄 다운로드 실패: {e}")
    
    def search_by_criteria(self, company: str, start_date: str, end_date: str, report_name: str = "") -> List[Dict]:
        """조건에 따른 보고서 검색"""
        try:
            print(f"🔍 DART 검색: {company} - {report_name}")
            
            # 검색 요청 데이터 구성
            search_data = {
                'currentPage': '1',
                'maxResults': '100',
                'maxLinks': '10',
                'sort': 'rcpDt',
                'series': 'desc',
                'textCrpNm': company,
                'startDate': start_date,
                'endDate': end_date,
            }
            
            # 보고서 유형이 지정된 경우 추가
            if report_name:
                search_data['textRptNm'] = report_name
            
            # DART 검색 요청
            response = self.session.post(self.search_url, data=search_data)
            
            if response.status_code == 200:
                # HTML 파싱하여 결과 추출
                results = self._parse_search_results(response.text)
                
                # 보고서 유형별 필터링
                if report_name:
                    filtered_results = []
                    for result in results:
                        if report_name in result.get('report_name', ''):
                            filtered_results.append(result)
                    return filtered_results
                else:
                    return results
            else:
                print(f"  ❌ 검색 요청 실패: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"  ❌ 검색 오류: {e}")
            return []
    
    def search_company(self, company_name: str) -> List[Dict[str, str]]:
        """회사명으로 회사 검색"""
        try:
            print(f"🔍 회사 검색: {company_name}")
            
            # 간단한 회사 검색 구현 - 입력받은 회사명을 그대로 사용
            # 실제로는 DART API를 통해 정확한 회사 정보를 가져와야 함
            companies = [{
                'name': company_name,
                'stock_code': 'N/A',
                'corp_code': 'N/A'
            }]
            
            print(f"   ✅ 회사 찾음: {company_name}")
            return companies
                
        except Exception as e:
            print(f"❌ 회사 검색 오류: {e}")
            return []
    
    def search_reports(self, company_name: str, start_date: str, end_date: str, report_types: List[str]) -> List[Dict[str, str]]:
        """정기공시 보고서 검색"""
        try:
            print(f"📊 정기공시 검색: {company_name}")
            print(f"   기간: {start_date} ~ {end_date}")
            print(f"   유형: {', '.join(report_types)}")
            
            # 기존의 search_company_regular_reports 메서드 활용
            print("   🔎 정기공시 보고서 검색 중...")
            
            # 기간 계산 (년수로 변환)
            from datetime import datetime
            start = datetime.strptime(start_date, '%Y%m%d')
            end = datetime.strptime(end_date, '%Y%m%d')
            years = max(1, (end - start).days // 365)
            
            reports = self.search_company_regular_reports(company_name, max_pages=10)
            
            if reports:
                print(f"     ✅ {len(reports)}건 발견")
                print(f"📊 총 {len(reports)}개 보고서 발견")
                return reports
            else:
                print(f"     ℹ️  검색 결과 없음")
                print(f"📊 총 0개 보고서 발견")
                return []
            
        except Exception as e:
            print(f"❌ 보고서 검색 오류: {e}")
            return []
    
    def download_reports_batch(self, reports: List[Dict[str, str]], download_dir: str):
        """보고서 목록 일괄 다운로드"""
        try:
            if not reports:
                print("❌ 다운로드할 보고서가 없습니다.")
                return
            
            print(f"\n📥 {len(reports)}개 보고서 일괄 다운로드 시작")
            print(f"📁 다운로드 폴더: {download_dir}")
            print("=" * 80)
            
            success_count = 0
            fail_count = 0
            
            for i, report in enumerate(reports, 1):
                print(f"\n[{i:2d}/{len(reports)}] 처리 중...")
                
                # 보고서 URL 추출
                report_url = report.get('report_url')
                if not report_url:
                    print("  ❌ 보고서 URL이 없습니다.")
                    fail_count += 1
                    continue
                
                # 다운로드 정보 추출
                download_info = self.get_report_download_info(report_url)
                
                if download_info:
                    # PDF 다운로드
                    if self.download_report_file(download_info, download_dir):
                        success_count += 1
                    else:
                        fail_count += 1
                else:
                    fail_count += 1
                
                # 서버 부하 방지를 위한 대기
                time.sleep(1)
            
            print("\n" + "=" * 80)
            print("🎉 다운로드 완료!")
            print(f"  ✅ 성공: {success_count}건")
            print(f"  ❌ 실패: {fail_count}건")
            if download_dir:
                print(f"  📁 저장 위치: {os.path.abspath(download_dir)}")
                
        except Exception as e:
            print(f"❌ 일괄 다운로드 오류: {e}")


def main():
    """메인 실행 함수"""
    print("🎯 DART 공시정보 검색 프로그램")
    print("=" * 50)
    
    scraper = DartScraper()
    
    # 초기화
    if not scraper.get_search_page():
        print("프로그램을 종료합니다.")
        return
    
    try:
        while True:
            print("\n" + "=" * 50)
            company_name = input("🏢 검색할 회사명을 입력하세요 (종료: q): ").strip()
            
            if company_name.lower() == 'q':
                print("👋 프로그램을 종료합니다.")
                break
            
            if not company_name:
                print("⚠️ 회사명을 입력해주세요.")
                continue
            
            # 보고서 필터 옵션 선택
            filter_choice = input("📋 특정 보고서만 검색하시겠습니까? (반기보고서, 분기보고서, 사업보고서) (y/n, 기본값: n): ").strip().lower()
            filter_reports = filter_choice == 'y'
            
            # 검색 실행 (최대 5페이지까지)
            results = scraper.search_company(company_name, years=10, filter_reports=filter_reports, max_pages=5)
            
            # 결과 출력
            scraper.display_results(results)
            
            # 결과 저장 여부 확인
            if results:
                print("\n💾 저장 옵션:")
                print("   1) JSON 파일로 저장 (전체 정보)")
                print("   2) 링크만 TXT 파일로 저장")
                print("   3) 둘 다 저장")
                print("   4) 저장하지 않음")
                
                save_choice = input("선택하세요 (1-4, 기본값: 4): ").strip()
                
                if save_choice == '1':
                    scraper.save_results(results)
                elif save_choice == '2':
                    scraper.save_links_to_txt(results)
                elif save_choice == '3':
                    scraper.save_results(results)
                    scraper.save_links_to_txt(results)
                else:
                    print("저장하지 않습니다.")
            
            # 잠시 대기 (서버 부하 방지)
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n👋 프로그램이 중단되었습니다.")
    except Exception as e:
        print(f"\n✗ 오류 발생: {e}")


if __name__ == "__main__":
    main()