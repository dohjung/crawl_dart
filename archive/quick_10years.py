#!/usr/bin/env python3
"""
삼성전자 10년 간단 테스트
"""

from dart_scraper import DartScraper

def quick_test():
    scraper = DartScraper()
    
    if not scraper.get_search_page():
        print("초기화 실패")
        return
    
    print("🔍 삼성전자 10년 검색 (3페이지만)")
    
    # 3페이지만 검색
    results = scraper.search_company("삼성전자", years=10, filter_reports=True, max_pages=3)
    
    print(f"✅ 총 {len(results)}건 발견")
    
    if results:
        # 연도별 분포
        years = {}
        for r in results:
            year = r['submit_date'][:4] if r['submit_date'] else 'Unknown'
            years[year] = years.get(year, 0) + 1
        
        print("연도별 분포:")
        for year in sorted(years.keys(), reverse=True):
            print(f"  {year}: {years[year]}건")
        
        print(f"\n모든 보고서:")
        for i, r in enumerate(results, 1):
            print(f"  {i:2d}. {r['report_name'][:60]}... ({r['submit_date']})")
        
        # 링크 파일 저장
        scraper.save_links_to_txt(results, "samsung_quick_links.txt")

if __name__ == "__main__":
    quick_test()