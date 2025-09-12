#!/usr/bin/env python3
"""
삼성전자 정기공시 보고서 일괄 다운로드
samsung_regular_reports_final.txt 파일의 모든 링크에서 PDF 파일 다운로드
"""

from dart_scraper import DartScraper
import os

def download_samsung_reports():
    """삼성전자 정기공시 보고서 일괄 다운로드"""
    print("🎯 삼성전자 정기공시 보고서 일괄 다운로드")
    print("=" * 60)
    
    # 링크 파일 확인
    txt_file = "samsung_regular_reports_final.txt"
    if not os.path.exists(txt_file):
        print(f"❌ 링크 파일이 없습니다: {txt_file}")
        print("   먼저 samsung_regular_final.py를 실행하여 링크를 생성하세요.")
        return
    
    print(f"📁 링크 파일: {txt_file}")
    
    # 다운로드 폴더 설정
    downloads_dir = "samsung_reports_pdf"
    print(f"📥 다운로드 폴더: {downloads_dir}")
    print()
    
    # 스크래퍼 초기화
    scraper = DartScraper()
    
    if not scraper.get_search_page():
        print("❌ DART 사이트 초기화 실패")
        return
    
    print("✅ DART 사이트 접속 성공")
    print()
    
    # 일괄 다운로드 실행
    scraper.download_all_reports_from_txt(txt_file, downloads_dir)

if __name__ == "__main__":
    download_samsung_reports()