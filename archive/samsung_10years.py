#!/usr/bin/env python3
"""
삼성전자 10년 검색 테스트
"""

from dart_scraper import DartScraper

def test_samsung_10years():
    """삼성전자 10년치 검색"""
    print("🎯 삼성전자 10년치 DART 검색")
    print("=" * 50)
    
    scraper = DartScraper()
    
    if not scraper.get_search_page():
        print("❌ 초기화 실패")
        return
    
    print("✅ DART 사이트 접속 성공")
    
    # 10년 전체 검색
    print("\n🔍 10년 전체 검색")
    print("-" * 30)
    results_all = scraper.search_company("삼성전자", years=10, filter_reports=False, max_pages=10)
    
    if results_all:
        print(f"✅ 10년 전체 검색 결과: {len(results_all)}건")
        
        # 연도별 분포 확인
        year_counts = {}
        for result in results_all:
            submit_date = result.get('submit_date', '')
            if submit_date and len(submit_date) >= 4:
                year = submit_date[:4]
                year_counts[year] = year_counts.get(year, 0) + 1
        
        print("연도별 분포:")
        for year in sorted(year_counts.keys(), reverse=True):
            print(f"  {year}년: {year_counts[year]}건")
            
        print(f"\n최근 5건:")
        for i, result in enumerate(results_all[:5], 1):
            print(f"  {i}. {result['report_name'][:40]}... ({result['submit_date']})")
    else:
        print("❌ 검색 결과 없음")
        return
    
    # 10년 필터링 검색
    print(f"\n🔍 10년 필터링 검색 (반기보고서, 분기보고서, 사업보고서)")
    print("-" * 30)
    results_filtered = scraper.search_company("삼성전자", years=10, filter_reports=True, max_pages=10)
    
    if results_filtered:
        print(f"✅ 필터링 결과: {len(results_all)}건 → {len(results_filtered)}건")
        
        # 보고서 타입별 분포
        report_types = {}
        for result in results_filtered:
            report_name = result.get('report_name', '')
            if '반기보고서' in report_name:
                report_types['반기보고서'] = report_types.get('반기보고서', 0) + 1
            elif '분기보고서' in report_name:
                report_types['분기보고서'] = report_types.get('분기보고서', 0) + 1
            elif '사업보고서' in report_name:
                report_types['사업보고서'] = report_types.get('사업보고서', 0) + 1
        
        print("보고서 타입별 분포:")
        for report_type, count in report_types.items():
            print(f"  {report_type}: {count}건")
        
        print(f"\n모든 필터링된 보고서:")
        for i, result in enumerate(results_filtered, 1):
            print(f"  {i:2d}. {result['report_name'][:50]}... ({result['submit_date']})")
            if result.get('report_url'):
                print(f"      🔗 {result['report_url']}")
        
        # 링크 파일 저장
        print(f"\n💾 링크 파일 저장")
        print("-" * 30)
        scraper.save_links_to_txt(results_filtered, "samsung_10years_links.txt")
        
    else:
        print("❌ 필터링 조건에 맞는 보고서 없음")


if __name__ == "__main__":
    test_samsung_10years()