#!/usr/bin/env python3
"""Create an editable XLSX review workbook from the generated CSV workpack."""
import csv
import json
import pathlib
import sys

import xlsxwriter

HERE = pathlib.Path(__file__).resolve().parent
OUT = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else HERE / "deliverable"


def load(name):
    with (OUT / name).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def main():
    rows = load("487_definition_review.csv")
    projects = load("project_dedup_candidates.csv")
    queue = load("review_queue.csv")
    inventory = load("reconstructed_1006_evidence_ledger.csv")
    name_clusters = load("exact_state_name_cluster_candidates.csv")
    legacy_crosswalk = load("legacy_86_exact_name_crosswalk_review.csv")
    company_queue = load("company_entity_resolution_queue_487.csv")
    state_coverage = load("state_source_coverage_and_gaps.csv")
    reproducibility = load("upstream_reproducibility_gaps.csv")
    decision_rules = load("five_condition_decision_rules.csv")
    legacy_selection = load("legacy_203_selection_audit.csv")
    candidate_selection = load("source_candidate_selection_audit_1006.csv")
    reproduced_cohort = load("reconstructed_cohort_487.csv")
    cohort_summary = json.loads((OUT / "cohort_reproduction_summary.json").read_text(encoding="utf-8"))
    candidate_evidence = load("project_candidate_evidence_review.csv")
    inclusion_gate = load("487_inclusion_gate.csv")
    gate_rules = load("project_inclusion_gate_rules.csv")
    tenure_status = load("487_official_tenure_trace_status.csv")
    tenure_evidence = load("487_official_tenure_intersection_evidence.csv")
    summary = json.loads((OUT / "487_full_census_adjudication_summary.json").read_text(encoding="utf-8"))
    candidate_rows = summary["status_counts"].get("PROJECT_CANDIDATE_REVIEW", 0)
    ree_hold_rows = summary["status_counts"].get("HOLD_REE_ROLE", 0)
    identity_hold_rows = summary["status_counts"].get("HOLD_INSUFFICIENT_PROJECT_IDENTITY_OR_REE_ROLE", 0)
    path = OUT / "AU_REE_487_pre_MCDA_five_definition_review.xlsx"
    wb = xlsxwriter.Workbook(path)
    wb.set_properties({"title": "Australian REE project census five-definition review", "subject": "Pre-MCDA census/entity linkage only", "author": "AU_REE research workpack"})
    navy, blue, amber, green, white = "#17365D", "#D9EAF7", "#FFF2CC", "#E2F0D9", "#FFFFFF"
    hdr = wb.add_format({"bold": True, "font_color": white, "bg_color": navy, "text_wrap": True, "valign": "vcenter"})
    title = wb.add_format({"bold": True, "font_size": 15, "font_color": navy})
    wrap = wb.add_format({"text_wrap": True, "valign": "top"})
    edit = wb.add_format({"bg_color": amber, "text_wrap": True, "valign": "top"})
    passfmt = wb.add_format({"bg_color": green})
    holdfmt = wb.add_format({"bg_color": amber})

    s = wb.add_worksheet("讀我與統計")
    s.hide_gridlines(2)
    s.set_column("A:A", 40)
    s.set_column("B:B", 18)
    s.set_column("D:D", 48)
    s.set_column("E:E", 100)
    s.write("A1", "全澳 REE 專案母體｜MCDA 前五項操作型定義核對", title)
    s.merge_range("A2:E2", "僅進行 census、來源證據及 entity linkage；本表不是 MCDA 入選名單或排名。原始 487 筆 ID 與上游來源欄位均保留。", wrap)
    s.write("A4", "487列初步狀態", hdr)
    s.write("B4", "筆數", hdr)
    for i, (k, v) in enumerate(summary["status_counts"].items(), 4):
        s.write(i, 0, k, wrap)
        s.write_number(i, 1, v)
    notes = [
        ("母體抽取重現性", "已重建並逐列重現：歷史203筆扣除與126暫定組連結的117個ID，得86筆；1,006筆中選E1_DIRECT_REE且E1_MISSING_PROJECT_LINK，得401筆。兩組ID均與凍結487清單完全相符。"),
        ("原始來源", "2026-10-29 快照包含 10 個政府來源組；screening 1,006 列分為 E1 803、E2 163、E3 40。"),
        ("礦權追溯", "官方點落多邊形回傳 764 筆交集，涉及 258 個目標；128 筆 SA 尚未驗證礦權層；50 筆無可用座標。titleholder/applicant 不代表 developer/operator。"),
        ("位置判讀", "401 筆 E1 有官方來源點位，暫判可定位但未確認專案邊界；36 筆 legacy 可由單一同州同名來源候選補位置，仍須人工核對；其餘 50 筆無匹配座標。"),
        ("州別範圍", "WA 127、SA 131、QLD 47、NSW 56、VIC 43、NT 55、TAS 28。ACT 只有全國 GA 資料覆蓋，沒有獨立州級礦業調查來源。"),
        ("五項定義", "澳洲管轄、地點可識別、獨立 Project 身分、REE 作為商品/計畫副產品/明確目標、屬於勘探/資源評估/採礦開發單位。每項分欄判讀，證據不足一律 HOLD。"),
        ("去重", "project_dedup_candidates 為候選分組，不等於已核准合併。多來源 deposit/site/occurrence 仍保留各自 ID；所有 project link 需人工核准。"),
        ("選取邏輯限制", "四個抽取檔依留存上游與記錄規則重建，原始sandbox ZIP位元組不可得，故非位元級還原。126組仍為暫定群；487筆納入查核佇列不代表已確認為專案。"),
        ("來源查核進度", f"目前有{summary.get('new_case_groups_reviewed', '未統計')}個命名查核群；逐列狀態不是獨立Project數：{candidate_rows}列為候選審閱、{ree_hold_rows}列稀土角色待查、{identity_hold_rows}列專案身分或稀土角色證據不足。HOLD不是排除；全部目標列的現任權利人、歷史轉讓與目標幾何到title連結仍未完成。"),
        ("納入門檻", "五項操作定義均需Project層級證據；要求至少一項政府／礦權來源及一項正式技術／專案揭露，明確證明REE商品、共同產品、計畫回收副產品或勘探開發目標。礦物含REE、名稱相似或點位相交均不足以自動納入或合併。"),
    ]
    s.write("D4", "說明", hdr)
    s.write("E4", "內容", hdr)
    for i, (a, b) in enumerate(notes, 4):
        s.write(i, 3, a, wrap)
        s.write(i, 4, b, wrap)
        s.set_row(i, 48)

    def add_table(name, data, editable_columns=()):
        sh = wb.add_worksheet(name)
        sh.freeze_panes(1, 4)
        sh.hide_gridlines(2)
        headers = list(data[0]) if data else []
        sh.autofilter(0, 0, len(data), len(headers) - 1)
        for c, h in enumerate(headers):
            sh.write(0, c, h, hdr)
            width = 22
            if any(t in h for t in ("url", "note", "evidence", "commodity", "context", "holder", "operator", "candidate", "decision")):
                width = 45
            if h in editable_columns:
                width = 36
            sh.set_column(c, c, width)
        for r, row in enumerate(data, 1):
            for c, h in enumerate(headers):
                val = row.get(h, "")
                fmt = edit if h in editable_columns else (
                    passfmt if h == "definition_screen_status" and val == "PROJECT_CANDIDATE_REVIEW" else
                    holdfmt if h.startswith("HOLD") or (h == "definition_screen_status" and val.startswith("HOLD")) else wrap
                )
                sh.write(r, c, val, fmt)
        return sh

    add_table("487逐列五條件", rows, ("reviewer_decision", "reviewer_notes", "asx_code_or_security_id", "historical_company_names", "transfer_or_rename_effective_date", "company_relationship_evidence_url"))
    add_table("Project去重候選", projects, ("review_decision", "open_review"))
    add_table("待查佇列", queue, ("reviewer_decision", "reviewer_notes"))
    add_table("全澳候選1006", inventory, ("reviewer_decision", "project_identity_result", "ree_role_result"))
    add_table("同州同名候選群", name_clusters)
    add_table("Legacy86精確連結", legacy_crosswalk, ("decision",))
    add_table("公司沿革待查487", company_queue, ("asx_code_or_security_id", "asic_acn_abn", "legal_entity_id", "current_company_name", "historical_company_names", "transfer_or_rename_effective_date", "asx_announcement_reference", "company_announcement_reference", "relationship_source_url", "review_status", "reviewer_decision", "reviewer_notes"))
    add_table("州別來源與缺口", state_coverage)
    add_table("上游重現性缺口", reproducibility)
    add_table("五條件判定規則", decision_rules)
    add_table("歷史203選取稽核", legacy_selection)
    add_table("全澳1006選取稽核", candidate_selection)
    add_table("重現487候選清單", reproduced_cohort)
    summary_rows = []
    for section, values in (("counts", cohort_summary["counts"]), ("comparison", cohort_summary["comparison_to_frozen_target_list"])):
        for key, value in values.items():
            summary_rows.append({"section": section, "metric": key, "value": json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else str(value)})
    for cohort, counts in cohort_summary["state_counts"].items():
        for state, count in counts.items():
            summary_rows.append({"section": "state_counts:" + cohort, "metric": state, "value": str(count)})
    add_table("86加401規則摘要", summary_rows)
    add_table("Project候選來源核對", candidate_evidence, ("reviewer_decision", "reviewer_notes"))
    add_table("487筆納入門檻", inclusion_gate, ("reviewer_decision", "reviewer_notes"))
    add_table("487列官方礦權查詢狀態", tenure_status)
    add_table("764筆礦權空間相交證據", tenure_evidence)
    add_table("納入與去重規則", gate_rules)
    add_table("487實體連結核對", load("project_entity_membership_487.csv"))
    add_table("連結品質檢查", load("quality_gate_487.csv"))
    add_table("Project實體名冊", load("project_entity_register.csv"), ("reviewer_decision",))
    add_table("來源證據定位", load("project_evidence_register.csv"), ("publication_date", "locator_page_or_section", "supports_condition", "review_status"))
    add_table("連結跨表差異", load("target_link_reconciliation_487.csv"))
    wb.close()
    print(json.dumps({"workbook": str(path), "rows": len(rows), "project_groups": len(projects), "queue": len(queue)}, ensure_ascii=False))


if __name__ == "__main__":
    main()

