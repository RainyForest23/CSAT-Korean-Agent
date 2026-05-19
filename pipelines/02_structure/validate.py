"""
구조화 결과 QA 검증

구조화 성공률, 필드 누락 여부, 이상 데이터 탐지.
"""
from typing import List, Tuple
from schema import PassageItem


def validate_item(item: PassageItem) -> Tuple[bool, List[str]]:
    """
    단일 PassageItem 검증.
    반환: (통과 여부, 실패 이유 리스트)
    """
    issues = []

    if not item.passage:
        issues.append("지문 없음")
    elif len(item.passage) < 50:
        issues.append(f"지문이 너무 짧음 ({len(item.passage)}자)")

    if not item.questions:
        issues.append("문제 없음")
    else:
        for q in item.questions:
            if not q.stem:
                issues.append(f"Q{q.number}: 문제 본문 없음")
            if len(q.options) < 4:
                issues.append(f"Q{q.number}: 선지 부족 ({len(q.options)}개)")
            if not q.commentary:
                issues.append(f"Q{q.number}: 해설 없음")

    if not item.genre:
        issues.append("장르 미분류")

    return len(issues) == 0, issues


def validate_all(items: List[PassageItem]) -> dict:
    passed, failed = [], []
    for item in items:
        ok, issues = validate_item(item)
        if ok:
            passed.append(item.id)
        else:
            failed.append({"id": item.id, "issues": issues})

    total = len(items)
    return {
        "total": total,
        "passed": len(passed),
        "failed": len(failed),
        "pass_rate": round(len(passed) / total, 3) if total else 0,
        "failures": failed,
    }


def print_report(report: dict):
    print(f"\n{'='*50}")
    print(f"QA 검증 결과")
    print(f"{'='*50}")
    print(f"전체: {report['total']}개")
    print(f"통과: {report['passed']}개 ({report['pass_rate']*100:.1f}%)")
    print(f"실패: {report['failed']}개")

    if report["failures"]:
        print("\n[실패 목록]")
        for f in report["failures"][:20]:  # 최대 20개만 출력
            print(f"  {f['id']}: {', '.join(f['issues'])}")
