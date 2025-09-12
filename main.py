#!/usr/bin/env python3
"""
DART 공시정보 다운로드 시스템
회사명으로 검색하여 정기공시 보고서를 일괄 다운로드합니다.
"""

from dart_scraper import DartScraper
from datetime import datetime, timedelta
import os
import sys

def show_menu():
    """메인 메뉴 출력"""
    print("\n" + "="*60)
    print("🎯 DART 공시정보 다운로드 시스템")
    print("="*60)
    print("1. 회사 검색 및 정기공시 다운로드")
    print("2. 링크 파일로부터 다운로드")
    print("3. 종료")
    print("="*60)

def search_and_download():
    """회사 검색 후 정기공시 다운로드"""
    print("\n📋 회사 검색 및 정기공시 다운로드")
    print("-" * 40)
    
    # 회사명 입력
    company_name = input("회사명을 입력하세요 (예: 삼성전자): ").strip()
    if not company_name:
        print("❌ 회사명을 입력해주세요.")
        return
    
    # 검색 기간 설정
    print("\n📅 검색 기간 설정")
    years = input("검색할 년수를 입력하세요 (기본값: 10년): ").strip()
    try:
        # "10년" 같은 입력도 처리
        if years.endswith('년'):
            years = years[:-1]
        years = int(years) if years else 10
        years = min(max(years, 1), 20)  # 1~20년 제한
    except ValueError:
        years = 10
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=years * 365)
    
    print(f"🔍 검색 조건: {company_name} ({start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')})")
    
    # 스크래퍼 초기화
    scraper = DartScraper()
    
    if not scraper.get_search_page():
        print("❌ DART 사이트 접속 실패")
        return
    
    print("✅ DART 사이트 접속 성공")
    
    # 회사 검색
    print(f"\n🔍 '{company_name}' 검색 중...")
    search_results = scraper.search_company(company_name)
    
    if not search_results:
        print(f"❌ '{company_name}'을(를) 찾을 수 없습니다.")
        return
    
    # 회사 선택
    if len(search_results) > 1:
        print(f"\n📋 검색된 회사 목록:")
        for i, company in enumerate(search_results, 1):
            print(f"{i}. {company['name']} (종목코드: {company.get('stock_code', 'N/A')})")
        
        try:
            choice = int(input(f"\n선택할 회사 번호 (1-{len(search_results)}): ")) - 1
            if choice < 0 or choice >= len(search_results):
                print("❌ 잘못된 선택입니다.")
                return
            selected_company = search_results[choice]
        except ValueError:
            print("❌ 잘못된 입력입니다.")
            return
    else:
        selected_company = search_results[0]
    
    print(f"✅ 선택된 회사: {selected_company['name']}")
    
    # 정기공시 검색
    print(f"\n📊 정기공시 보고서 검색 중...")
    
    # 정기공시 유형 필터
    report_types = ['분기보고서', '반기보고서', '사업보고서']
    
    reports = scraper.search_reports(
        company_name=selected_company['name'],
        start_date=start_date.strftime('%Y%m%d'),
        end_date=end_date.strftime('%Y%m%d'),
        report_types=report_types
    )
    
    if not reports:
        print("❌ 정기공시 보고서를 찾을 수 없습니다.")
        return
    
    print(f"✅ {len(reports)}개의 정기공시 보고서를 찾았습니다.")
    
    # 다운로드 여부 확인
    print(f"\n📥 {len(reports)}개 파일을 다운로드하시겠습니까?")
    confirm = input("계속하시겠습니까? (y/N): ").strip().lower()
    
    if confirm not in ['y', 'yes']:
        print("❌ 다운로드를 취소했습니다.")
        return
    
    # 다운로드 폴더 설정
    safe_company_name = "".join(c for c in selected_company['name'] if c.isalnum() or c in "._- ")
    download_dir = f"{safe_company_name}_reports"
    
    print(f"📁 다운로드 폴더: {download_dir}")
    
    # 일괄 다운로드
    scraper.download_reports_batch(reports, download_dir)

def download_from_file():
    """링크 파일로부터 다운로드"""
    print("\n📂 링크 파일로부터 다운로드")
    print("-" * 40)
    
    # txt 파일 찾기
    txt_files = [f for f in os.listdir('.') if f.endswith('.txt') and 'report' in f.lower()]
    
    if not txt_files:
        print("❌ 보고서 링크 파일(*.txt)을 찾을 수 없습니다.")
        return
    
    if len(txt_files) == 1:
        txt_file = txt_files[0]
    else:
        print("📋 링크 파일 목록:")
        for i, file in enumerate(txt_files, 1):
            print(f"{i}. {file}")
        
        try:
            choice = int(input(f"선택할 파일 번호 (1-{len(txt_files)}): ")) - 1
            if choice < 0 or choice >= len(txt_files):
                print("❌ 잘못된 선택입니다.")
                return
            txt_file = txt_files[choice]
        except ValueError:
            print("❌ 잘못된 입력입니다.")
            return
    
    print(f"📁 선택된 파일: {txt_file}")
    
    # 다운로드 폴더명 입력
    default_dir = txt_file.replace('.txt', '_pdf')
    download_dir = input(f"다운로드 폴더명 (기본값: {default_dir}): ").strip()
    download_dir = download_dir if download_dir else default_dir
    
    # 스크래퍼 초기화
    scraper = DartScraper()
    
    if not scraper.get_search_page():
        print("❌ DART 사이트 접속 실패")
        return
    
    print("✅ DART 사이트 접속 성공")
    
    # 파일에서 다운로드
    scraper.download_all_reports_from_txt(txt_file, download_dir)

def main():
    """메인 함수"""
    while True:
        show_menu()
        
        try:
            choice = input("\n메뉴를 선택하세요 (1-3): ").strip()
            
            if choice == '1':
                search_and_download()
            elif choice == '2':
                download_from_file()
            elif choice == '3':
                print("\n👋 프로그램을 종료합니다.")
                break
            else:
                print("❌ 잘못된 선택입니다. 1-3 중에서 선택해주세요.")
                
        except KeyboardInterrupt:
            print("\n\n👋 프로그램을 종료합니다.")
            break
        except Exception as e:
            print(f"\n❌ 오류가 발생했습니다: {e}")
            print("계속 진행하려면 아무 키나 누르세요...")
            input()

if __name__ == "__main__":
    main()