#!/usr/bin/env python3
"""
삼성전자 정기공시 최종 테스트
올바른 파라미터로 정기공시만 검색
"""

from dart_scraper import DartScraper

def final_regular_test():
    """삼성전자 정기공시 최종 테스트"""
    print("🎯 삼성전자 정기공시 최종 검색")
    print("☑️ 정기공시만: 사업보고서, 반기보고서, 분기보고서")
    print("📅 기간: 10년")
    print("🔗 모든 페이지의 모든 링크 수집")
    print("=" * 60)
    
    scraper = DartScraper()
    
    if not scraper.get_search_page():
        print("❌ 초기화 실패")
        return
    
    print("✅ DART 사이트 접속 성공")
    
    # 정기공시 검색 (20페이지)
    print(f"\n🔍 정기공시 검색")
    print("-" * 40)
    results = scraper.search_company_regular_reports("삼성전자", max_pages=20)
    
    if results:
        print(f"✅ 총 검색 결과: {len(results)}건")
        
        # 연도별 분포
        year_counts = {}
        for result in results:
            submit_date = result.get('submit_date', '')
            if submit_date and len(submit_date) >= 4:
                year = submit_date[:4]
                year_counts[year] = year_counts.get(year, 0) + 1
        
        print(f"\n📊 연도별 분포:")
        for year in sorted(year_counts.keys(), reverse=True):
            print(f"  {year}년: {year_counts[year]:3d}건")
        
        # 보고서 타입별 분포
        report_types = {'사업보고서': 0, '반기보고서': 0, '분기보고서': 0}
        other_types = {}
        
        for result in results:
            report_name = result.get('report_name', '')
            if '사업보고서' in report_name:
                report_types['사업보고서'] += 1
            elif '반기보고서' in report_name:
                report_types['반기보고서'] += 1
            elif '분기보고서' in report_name:
                report_types['분기보고서'] += 1
            else:
                # 기타 타입 분석
                if '(' in report_name:
                    rtype = report_name.split('(')[0].strip()
                else:
                    rtype = report_name.strip()
                other_types[rtype] = other_types.get(rtype, 0) + 1
        
        print(f"\n📋 정기공시 보고서 타입별 분포:")
        for rtype, count in report_types.items():
            if count > 0:
                print(f"  {count:3d}건: {rtype}")
        
        if other_types:
            print(f"\n📋 기타 보고서:")
            for rtype, count in other_types.items():
                print(f"  {count:3d}건: {rtype}")
        
        print(f"\n📄 모든 정기공시 보고서:")
        for i, result in enumerate(results, 1):
            report_name = result.get('report_name', '')
            submit_date = result.get('submit_date', '')
            report_url = result.get('report_url', '')
            print(f"  {i:3d}. {report_name} ({submit_date})")
            if report_url:
                print(f"       🔗 {report_url}")
        
        # 링크 파일 저장
        print(f"\n💾 파일 저장")
        print("-" * 40)
        scraper.save_links_to_txt(results, "samsung_regular_reports_final.txt")
        scraper.save_results(results, "samsung_regular_reports_final.json")
        
        print(f"\n🎉 완료!")
        print(f"  📊 정기공시 검색: {len(results)}건")
        print(f"  📁 저장된 파일:")
        print(f"     - samsung_regular_reports_final.txt ({len(results)}개 링크)")
        print(f"     - samsung_regular_reports_final.json (상세 정보)")
        
        # 각 보고서 타입별 개수 요약
        total_reports = sum(count for count in report_types.values() if count > 0)
        print(f"\n📈 정기공시 요약:")
        print(f"  사업보고서: {report_types['사업보고서']}건")
        print(f"  반기보고서: {report_types['반기보고서']}건") 
        print(f"  분기보고서: {report_types['분기보고서']}건")
        print(f"  총 정기공시: {total_reports}건")
        
    else:
        print("❌ 검색 결과 없음")

if __name__ == "__main__":
    final_regular_test()