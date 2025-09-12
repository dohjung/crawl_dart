#!/usr/bin/env python3
"""
삼성전자 전체 보고서 확인
"""

from dart_scraper import DartScraper

def check_all_reports():
    scraper = DartScraper()
    
    if not scraper.get_search_page():
        print("초기화 실패")
        return
    
    print("🔍 삼성전자 전체 보고서 확인 (3페이지)")
    
    # 필터링 없이 전체 검색
    results = scraper.search_company("삼성전자", years=10, filter_reports=False, max_pages=3)
    
    print(f"✅ 총 {len(results)}건 발견")
    
    if results:
        # 보고서 타입 분석
        report_types = {}
        for r in results:
            report_name = r['report_name']
            # 보고서 타입 추출 (괄호 앞부분)
            if '(' in report_name:
                report_type = report_name.split('(')[0].strip()
            else:
                report_type = report_name.strip()
            
            report_types[report_type] = report_types.get(report_type, 0) + 1
        
        print(f"\n📊 보고서 타입별 분포:")
        for report_type in sorted(report_types.keys(), key=lambda x: report_types[x], reverse=True):
            count = report_types[report_type]
            print(f"  {count:2d}건: {report_type}")
        
        # 필터링 대상 확인
        target_reports = ['반기보고서', '분기보고서', '사업보고서']
        filtered_count = 0
        
        print(f"\n🎯 필터링 대상 보고서:")
        for r in results:
            report_name = r['report_name']
            for target in target_reports:
                if target in report_name:
                    filtered_count += 1
                    print(f"  ✅ {report_name[:70]}... ({r['submit_date']})")
                    break
        
        print(f"\n📋 필터링 결과: {len(results)}건 → {filtered_count}건")
        
        if filtered_count == 0:
            print("\n❓ 필터링 대상이 없는 이유 분석:")
            print("   - 최근 10년간 삼성전자가 해당 보고서를 제출하지 않았거나")
            print("   - 보고서명이 예상과 다르게 명명되었을 수 있습니다")
            print("   - 예: '정기보고서(분기보고서)' 형태로 되어 있을 수 있음")

if __name__ == "__main__":
    check_all_reports()