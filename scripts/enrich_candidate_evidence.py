#!/usr/bin/env python3
"""Add a sourced, conservative admission-gate review to the pre-MCDA workpack.

Research dispositions apply only to the enumerated candidate groups. Unreviewed
targets remain HOLD; no fuzzy entity links or automatic project merges are made.
"""
import csv
import json
import pathlib
import sqlite3

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path, rows):
    fields = list(rows[0]) if rows else []
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def load_gate_sqlite():
    db = OUT / "census_review.sqlite"
    migration = ROOT / "db" / "migrations" / "0009_project_evidence_and_admission_gate.sql"
    if not db.exists():
        return
    with sqlite3.connect(db) as conn:
        conn.executescript(migration.read_text(encoding="utf-8-sig"))
        conn.execute("DELETE FROM census_project_candidate_evidence")
        conn.execute("DELETE FROM census_project_inclusion_gate")
        conn.execute("DELETE FROM census_project_inclusion_gate_rules")
        for row in read_csv(OUT / "project_candidate_evidence_review.csv"):
            conn.execute(
                "INSERT INTO census_project_candidate_evidence(candidate_group_key,canonical_project_unit,project_identity_status,ree_role_status,stage_status,inclusion_gate,evidence_urls,payload_json) VALUES (?,?,?,?,?,?,?,?)",
                (row["candidate_group_key"], row["canonical_project_unit"], row["project_identity_status"], row["ree_role_status"], row["stage_status"], row["inclusion_gate"], row["primary_source_urls"], json.dumps(row, ensure_ascii=False)),
            )
        for row in read_csv(OUT / "487_inclusion_gate.csv"):
            conn.execute(
                "INSERT INTO census_project_inclusion_gate(target_id,cohort,state,candidate_group_key,inclusion_gate,dedup_relation,evidence_urls,payload_json) VALUES (?,?,?,?,?,?,?,?)",
                (row["target_id"], row["cohort"], row["state"], row["candidate_group_key"], row["inclusion_gate"], row["dedup_relation"], row["primary_source_urls"], json.dumps(row, ensure_ascii=False)),
            )
        conn.executemany(
            "INSERT INTO census_project_inclusion_gate_rules(rule_id,minimum_threshold,effect) VALUES (?,?,?)",
            [(r["rule_id"], r["minimum_threshold"], r["effect"]) for r in read_csv(OUT / "project_inclusion_gate_rules.csv")],
        )
        for table, filename in (("row_review", "487_definition_review.csv"), ("company_entity_resolution_queue_487", "company_entity_resolution_queue_487.csv")):
            rows = read_csv(OUT / filename)
            if not rows:
                continue
            columns = list(rows[0])
            assignments = ",".join(f"{c}=?" for c in columns if c != "target_id")
            values = [tuple(row[c] for c in columns if c != "target_id") + (row["target_id"],) for row in rows]
            conn.executemany(f"UPDATE {table} SET {assignments} WHERE target_id=?", values)
        for row in read_csv(OUT / "upstream_reproducibility_gaps.csv"):
            conn.execute(
                "UPDATE upstream_reproducibility_gaps SET status=?, effect=? WHERE missing_input=?",
                (row["status"], row["effect"], row["missing_input"]),
            )


# A source must support the project-level claim in the row. Government and
# company/technical sources are kept side-by-side where both are available.
CASES = {
    "Avonbank Project": dict(identity="PASS", ree="PASS_CO_PRODUCT_PLANNED", stage="PASS_DEVELOPMENT", company="WIM Resource Pty Ltd", company_history="Official Victorian page records RL2014 held by WIM Resource Pty Ltd; no change in project proponent evidenced in sources reviewed.", dedup="SINGLE_PROJECT; do not merge with Bungalally, WIM150 or other mineral-sands projects by basin/name alone.", gate="INCLUDE_CANDIDATE", reason="Victoria identifies a defined Avonbank mining project, location near Horsham, commercial rare-earth-bearing products and current mining-licence approval. Work plan/rehabilitation approval remains an operating-condition step.", urls="https://resources.vic.gov.au/landholders-and-community/key-site-updates/avonbank-mineral-sands-project;https://resources.vic.gov.au/about-us/news/mining-licence-granted-for-avonbank-project;https://www.avonbankproject.com.au/"),
    "Balranald Mineral Sands Project": dict(identity="PASS", ree="PASS_PLANNED_REE_MINERAL_PRODUCT", stage="PASS_APPROVED_DEVELOPMENT", company="Iluka Resources Limited / Iluka Resources Pty Ltd", company_history="NSW approval and Iluka project materials identify Iluka as proponent; no transfer affecting the project identified in reviewed sources.", dedup="SINGLE_PROJECT; retain Balranald and West Balranald deposit/source IDs as child records unless formal project documents establish a separate decision unit.", gate="INCLUDE_CANDIDATE", reason="Iluka and NSW project records identify a defined mine near Balranald; planned mineral products include rare-earth-bearing monazite/xenotime concentrate.", urls="https://www.iluka.com/supplier-contractor-eoi/;https://www.iluka.com/community-engagement/balranald/;https://www.iluka.com/documents/2023/asx-releases/balranald-fid-annoucement/"),
    "Barkly Rare Earths Project": dict(identity="PASS", ree="PASS_PRIMARY_AND_RESOURCE", stage="PASS_EXPLORATION_RESOURCE", company="Barkly Rare Earths Limited (ASX: BAK)", company_history="NT government records current company and project; NT reports state company listed on ASX on 10 January 2026. Older Barkly tenement/operator records name Transition Minerals; do not assume same legal entity or same licence without tenement-level crosswalk.", dedup="Barkly REE and Barkly REE-V appear to refer to the same company project family; confirm legacy tenement IDs against current BAK title schedule before merging. Do not merge other Barkly-named base-metal projects.", gate="INCLUDE_CANDIDATE", reason="NT government and company technical material identify a defined Barkly REE project, location, 40 Mt @ 0.21% TREO inferred resource, and active exploration/metallurgy stage.", urls="https://resourcingtheterritory.nt.gov.au/minerals/mineral-commodities/ree;https://resourcingtheterritory.nt.gov.au/minerals/mines-and-projects/developing-projects;https://barklyrareearths.com/barkly-project;https://environment.nt.gov.au/mining/exploration"),
    "Charley Creek Project": dict(identity="PASS", ree="PASS_RESOURCE_AND_EXPLORATION_TARGET", stage="PASS_FEASIBILITY", company="Enova Mining Limited (ASX: ENV); NT environmental MMP archive also names URO Corporation Pty Ltd as operator for a 2023 Charley Creek ZIP", company_history="NT government resource table continues to attribute the project to Enova. A 2023 NT environmental register names URO Corporation Pty Ltd for a Charley Creek ZIP; this is an operating-authorisation relationship, not evidence of resource/title transfer. Verify current MMP and title holder before recording current operator.", dedup="SINGLE_PROJECT; Charley Creek deposit and associated licence-area records are project children. Keep Cockroach Dam separate unless technical disclosure ties it to the same development unit.", gate="INCLUDE_CANDIDATE", reason="NT government identifies the project at Aileron Province, 805 Mt @ 0.029% REO resource, and feasibility status; project stage and REE role are explicit.", urls="https://resourcingtheterritory.nt.gov.au/minerals/mineral-commodities/ree;https://environment.nt.gov.au/mining/exploration;https://enovamining.com/projects/"),
    "Copi Mineral Sands Project": dict(identity="PASS", ree="PASS_PLANNED_MONAZITE_PRODUCT", stage="PASS_APPROVED_DEVELOPMENT", company="RZ Resources Limited (private); project documents name RZ Resources Limited as applicant", company_history="ABN 23 160 863 892 changed from Relentless Resources Limited to RZ Resources Ltd effective 23 April 2021; ACN 160 863 892. NSW planning documents identify RZ as applicant. JX Advanced Metals announced a project participation agreement; exact current interest/shareholding should be checked against completion filings.", dedup="SINGLE_PROJECT; do not merge with nearby mineral-sands prospects or RZ's other tenements without title/project evidence.", gate="INCLUDE_CANDIDATE", reason="NSW project and approval records identify location, applicant, mine development and planned monazite product; government records list REE as other commodity.", urls="https://www.resources.nsw.gov.au/invest-nsw/investment-pathways/nsw-minerals-and-metals-projects;https://majorprojects.planningportal.nsw.gov.au/prweb/PRRestService/mp/01/getContent?AttachRef=SSD-41294067%2120250821T063321.798+GMT;https://majorprojects.planningportal.nsw.gov.au/prweb/PRRestService/mp/01/getContent?AttachRef=SSD-41294067%2120240428T100906.433+GMT;https://abr.business.gov.au/AbnHistory/View?id=23160863892;https://wwwcdn.furuchi.co.jp/english/newsrelease/fy2025/20250609_02.html"),
    "Donald Mineral Sands Project": dict(identity="PASS", ree="PASS_PLANNED_REE_CONCENTRATE", stage="PASS_ADVANCED_DEVELOPMENT", company="Donald Project Pty Ltd (project/JV entity); Astron Limited (ASX: ATR) manager; Energy Fuels Inc. earns into JV", company_history="MIN5532/RL2002 transferred from Donald Mineral Sands Pty Ltd to The Donald Project Pty Ltd in 2024. Astron retained 51% and Energy Fuels has an earn-in right up to 49%; 2026 company reporting gave 12.68% Energy Fuels / 87.32% Astron at 30 June 2026. Record title holder, manager and beneficial ownership separately.", dedup="SINGLE_DONALD_PROJECT; MIN5532 and RL2002 are phases/tenements of one project; Jackson Project is a separate project despite Astron relationship.", gate="INCLUDE_CANDIDATE", reason="Victorian government confirms defined location, mineral-sands project and associated rare earth elements; project/technical records specify monazite-xenotime rare-earth concentrate and advanced approvals.", urls="https://resources.vic.gov.au/landholders-and-community/key-site-updates/donald-mineral-sands-project;https://astronlimited.com.au/operations/donald-project/;https://announcements.asx.com.au/asxpdf/20250917/pdf/06p9cfgtqm12wy.pdf;https://www.sec.gov/Archives/edgar/data/1385849/000106299326001182/exhibit99-2.htm;https://www.nrf.gov.au/our-investments/donald-mineral-sands-project"),
    "Euston Critical Minerals Project": dict(identity="PASS", ree="HOLD_RECOVERY_PLAN", stage="PASS_EARLY_PLANNING", company="Iluka Resources Limited", company_history="Iluka identifies itself as proponent. No transfer found in reviewed project materials.", dedup="SINGLE_PROJECT; Iluka states five adjacent deposits form this one 62 km project. Keep individual deposits as children.", gate="HOLD", reason="Defined project, location, proponent and early planning stage are established. NSW says deposits include monazite/xenotime, but evidence reviewed does not establish that the Euston project plans to recover/sell an REE-bearing product; mineral presence alone does not meet the role threshold.", urls="https://www.iluka.com/community-engagement/euston/;https://www.resources.nsw.gov.au/invest-nsw/investment-pathways/nsw-priority-metals/rare-earth-elements"),
    "Fingerboards Project": dict(identity="PASS", ree="PASS_PLANNED_REE_PRODUCTS", stage="PASS_EES_PREPARATION", company="Gippsland Critical Minerals Pty Ltd (GCM)", company_history="Current GCM materials state joint ownership by REZir Ltd and Appian Capital Advisory; new management/governance and retention-licence extensions RL2026/RL2023 were recorded in October 2024. 2026 referral is a modified/rescoped project version; preserve old EES/project name as predecessor, not separate current project.", dedup="MERGE Fingerboards / The Fingerboards / Fingerboards Mineral Sands as project aliases/version records; link Glenaladale deposit as child. Do not treat each E1 observation or revised proposal as a separate project.", gate="INCLUDE_CANDIDATE", reason="Victoria's 2026 referral identifies proponent, jurisdiction, location, formal EES project, 22-year development and planned monazite/xenotime plus REO products.", urls="https://www.planning.vic.gov.au/environmental-assessments/browse-projects/referrals/fingerboards-critical-minerals-project;https://www.gippslandcriticalminerals.com/project-overview/;https://www.gippslandcriticalminerals.com/company/;https://www.business.gov.au/Grants-and-Programs/Major-Project-Status/Current-Major-Projects"),
    "Goschen Central Project": dict(identity="PASS", ree="PASS_PLANNED_MONAZITE_XENOTIME", stage="PASS_SCOPING_STUDY", company="ACDC Metals Ltd (ASX: ADC) 80%; Providence Gold & Minerals Pty Ltd 20%", company_history="ACDC project page gives current 80/20 ownership and retention licence RL008706; verify registered title holder separately from project interest.", dedup="KEEP_DISTINCT_FROM_VHM_GOSCHEN; separate proponent, RL008706, deposit/project footprint and location (about 50 km SSW of Swan Hill) from VHM's Goschen project.", gate="INCLUDE_CANDIDATE", reason="Company technical page defines Goschen Central as a distinct rare-earth/mineral-sands project and plans monazite-xenotime concentrate; Victoria project listing separately identifies ACDC Metals.", urls="https://acdcmetals.com.au/projects/goschen-central/;https://resources.vic.gov.au/geology-and-data/industry-investment/mineral-resources-development/Current-Mineral-Projects-and-Selected-Occurrences-2025-10-20-Web.pdf"),
    "Goschen Rare Earths and Mineral Sands Project": dict(identity="PASS", ree="PASS_RARE_EARTH_MINERAL_PRODUCTS", stage="PASS_APPROVED_DEVELOPMENT", company="VHM Limited (ASX: VHM)", company_history="Victorian EPA identifies VHM as proponent and issued development licence DL000300088 in July 2026. Use this name for the VHM Goschen project; not ACDC's Goschen Central.", dedup="MERGE Goschen Project / Goschen Mineral Sands and Rare Earths Project aliases under VHM. KEEP DISTINCT FROM ACDC GOSCHEN CENTRAL.", gate="INCLUDE_CANDIDATE", reason="Victorian EPA describes a separate defined project, location, mining/processing scope and rare-earth mineral products; licence granted to VHM.", urls="https://www.epa.vic.gov.au/goschen-mineral-sands-and-rare-earths-project;https://resources.vic.gov.au/__data/assets/pdf_file/0010/1191844/fe17b69e802fb6308e5100ce9c62e30dfbc8624d.pdf"),
    "Koppamurra Project": dict(identity="PASS", ree="PASS_PRIMARY_REE", stage="PASS_EXPLORATION_AND_PFS", company="Australian Rare Earths Limited (ASX: AR3), with subsidiary RDBD Developments Pty Ltd named in SA project record", company_history="South Australian government identifies AR3 as sole project owner; subsidiary is the company named for the project record. No title transfer found in reviewed sources.", dedup="MERGE all four Koppamurra E1 source observations as one project; link Red Tail/Yellow Tail and source-coded parcels as deposits/tenements. Project spans SA and Victoria but remains one project.", gate="INCLUDE_CANDIDATE", reason="SA government identifies owner, six SA ELs, exploration stage and magnet REE target; company/ASX disclosure reports JORC resource and PFS.", urls="https://energymining.sa.gov.au/industry/minerals-and-mining/mining/major-projects-and-mining-activities/developing-projects/the-koppamurra-project;https://energymining.sa.gov.au/industry/minerals-and-mining/mineral-commodities/rare_earths;https://data-api.marketindex.com.au/api/v1/announcements/XASX%3AAR3%3A2A1307140/pdf/inline/australian-rare-earths-commences-trading-on-asx;https://www.asx.com.au/listings"),
    "Narraburra REE Project": dict(identity="PASS", ree="PASS_PRIMARY_REE_AND_MREC_TESTWORK", stage="PASS_ADVANCED_EXPLORATION_RESOURCE", company="Orbit Resources Limited (ASX: OBT; formerly Godolphin Resources Limited, ASX: GRL); title held through Critical Rare Earths Pty Ltd; Matrix Critical Minerals transfer/IPO pending", company_history="Orbit/Godolphin's 2026 announcements state 100%-owned Narraburra and proposed transfer/spin-out to Matrix. As of 29 Oct 2026 Matrix IPO had not closed and ASX listing was scheduled for 23 Nov 2026; do not record Matrix as current owner until transfer/listing completion evidence.", dedup="SINGLE_NARRABURRA_PROJECT; EL8420 and the resource outline are project/tenement evidence. Treat Matrix as proposed future entity, not a second project.", gate="INCLUDE_CANDIDATE", reason="NSW government lists an advanced REE project/resource; company technical disclosures report a 94.9 Mt TREO resource and mixed rare-earth carbonate metallurgical products.", urls="https://www.resources.nsw.gov.au/invest-nsw/investment-pathways/nsw-priority-metals/rare-earth-elements;https://godolphinresources.com.au/downloads/announcements/grl_2026052201.pdf;https://www.asx.com.au/listings/upcoming-floats-and-listings.html;https://orbitresources.au/announcements"),
    "Nolans Project (Nolans Bore deposit)": dict(identity="PASS", ree="PASS_PRIMARY_REE_AND_PHOSPHATE", stage="PASS_CONSTRUCTION", company="Arafura Rare Earths Limited (ASX: ARU)", company_history="NT government names Arafura Rare Earths Ltd as project company. Historical Arafura Resources naming should be preserved as issuer-name history, not a separate project/company absent entity-ID evidence.", dedup="MERGE Nolans Bore as the deposit/alias child of the Nolans project; not an independent project. Preserve source candidate ID.", gate="INCLUDE_CANDIDATE", reason="NT government describes the Nolans project as in construction, identifies location north of Alice Springs, resource and REE/phosphate commodity.", urls="https://resourcingtheterritory.nt.gov.au/minerals/mineral-commodities/ree;https://resourcingtheterritory.nt.gov.au/minerals/mines-and-projects/developing-projects"),
    "Sonoran Project candidate": dict(identity="HOLD_PROJECT_UNIT", ree="HOLD_RECOVERY_PLAN", stage="HOLD_CURRENT_PROJECT_STAGE", company="Iluka Resources Limited", company_history="Iluka's 2025 annual report lists exploration at Sonoran; no current standalone project decision unit or transfer found.", dedup="HOLD_RELATION_TO_EUCLA_BASIN_PROJECTS; retain Sonoran deposit record and do not merge into Jacinth-Ambrosia without title/project-boundary evidence.", gate="HOLD", reason="SARIG identifies Sonoran as a heavy-mineral-sands deposit with resource, but the reviewed government/company evidence does not establish a current independent REE mining project or planned recovery/sale of monazite/xenotime. Mere mineral presence is insufficient.", urls="https://minerals.sarig.sa.gov.au/MineralDepositDetails.aspx?DEPOSIT_NO=9350;https://www.iluka.com/media/yhwn2hzi/iluka-ar25-final-single-pages-18226.pdf;https://map.sarig.sa.gov.au/CrystalRunner/Report/Export/2?exportName=DevelopingProjects"),
    "Tripitaka Project candidate": dict(identity="HOLD_PROJECT_UNIT", ree="HOLD_RECOVERY_PLAN", stage="HOLD_CURRENT_PROJECT_STAGE", company="Iluka (Eucla Basin) Pty Ltd / Iluka Resources Limited (historical report attribution)", company_history="SARIG mineral-deposit record and historical resource report identify Tripitaka; current registered title holder and project proponent were not verified in this review.", dedup="HOLD_RELATION_TO_EUCLA_BASIN_ASSETS; preserve deposit ID, do not promote to independent project or merge to Jacinth-Ambrosia without title and project documentation.", gate="HOLD", reason="The available record establishes a mineral-sands deposit/resource and historical company attribution, but not a current independent REE project unit or planned recovery/sale of REE product.", urls="https://minerals.sarig.sa.gov.au/MineralDepositDetails.aspx?DEPOSIT_NO=8345;https://map.sarig.sa.gov.au/CrystalRunner/Report/Export/2?exportName=DevelopingProjects;https://www.iluka.com/products-markets/rare-earth-products"),
    "Typhoon Project candidate": dict(identity="PASS_SATELLITE_PROJECT", ree="HOLD_RECOVERY_PLAN", stage="PASS_PROPOSED_DEVELOPMENT", company="Iluka Resources Limited", company_history="EPBC referral names Iluka as proponent. Current exploration/resource reporting is company-held; no title transfer identified.", dedup="KEEP_AS_SATELLITE_PROJECT_CANDIDATE_LINKED_TO_JACINTH_AMBROSIA; EPBC describes it as a satellite mine using existing facilities. Do not merge project decision record until scope/tenure confirms the appropriate census unit.", gate="HOLD", reason="EPBC identifies a defined Typhoon Mineral Sands Project and proposed mine. SA records report monazite/xenotime in resource, but the reviewed project referral does not establish a planned REE-bearing product/recovery stream.", urls="https://epbcpublicportal.environment.gov.au/all-referrals/project-referral-summary/?id=d0871673-1f74-f111-ab0f-7ced8d33db9b;https://map.sarig.sa.gov.au/CrystalRunner/Report/Export/2?exportName=DevelopingProjects;https://www.iluka.com/media/yhwn2hzi/iluka-ar25-final-single-pages-18226.pdf"),
    "Wudinna Project": dict(identity="PASS_REE_PROJECT_WITH_SPLIT_COMMODITY_RIGHTS", ree="PASS_EXPLICIT_REE_RESOURCE_AND_TARGET", stage="PASS_RESOURCE_EXPLORATION", company="Cobra Resources plc (LSE: COBR) for retained REE rights; Barton Gold Holdings Limited (ASX: BGD) acquired Wudinna gold assets", company_history="Cobra acquired the remaining 25% Wudinna interest from Andromeda Metals in April 2024. In July/August 2025 Barton acquired Wudinna Gold Assets; Cobra retained certain REE and other mineral rights. Treat gold and REE rights as separate commodity-rights interests within the Wudinna area, not as a blanket transfer of all mineral rights.", dedup="MERGE Baggy Green REE deposit group into Wudinna REE project; retain Baggy Green as a deposit/observation. Do not use gold-title sale to infer REE ownership transfer.", gate="INCLUDE_CANDIDATE", reason="SA government project register lists Wudinna commodities including REE and a JORC REE resource; current rights are split from the gold project and require mineral-specific title crosswalk.", urls="https://map.sarig.sa.gov.au/CrystalRunner/Report/Export/2?exportName=DevelopingProjects;https://announcements.asx.com.au/asxpdf/20250630/pdf/06l8nyj65y0czg.pdf;https://www.lse.co.uk/rns/COBR/completion-wudinna-gold-sale-payments-received-3diaxnb62pyy3no.html;https://cobraplc.com/project/wudinna-project/;https://www.elementalroyalty.com/projects/wudinna/"),
    "Wudinna Project (Baggy Green deposit)": dict(identity="PASS_CHILD_DEPOSIT", ree="PASS_REE_RESOURCE", stage="PASS_RESOURCE", company="Cobra Resources plc (REE rights); historic Wudinna gold interests now include Barton Gold", company_history="Baggy Green is a named deposit within the Wudinna project/resource area. 2025 sale transferred Wudinna Gold Assets to Barton while Cobra retained certain REE rights; verify licence/mineral schedule for each target observation.", dedup="CHILD_DEPOSIT_OF_WUDINNA_REE_PROJECT; merge at Project level only, preserve all Baggy Green target/source IDs and deposit relation.", gate="INCLUDE_CANDIDATE", reason="Project-level JORC/SA evidence includes Baggy Green among the Wudinna REE resource localities; it is not a separate mining Project.", urls="https://map.sarig.sa.gov.au/CrystalRunner/Report/Export/2?exportName=DevelopingProjects;https://www.cobraplc.com/project/wudinna-project/;https://announcements.asx.com.au/asxpdf/20250630/pdf/06l8nyj65y0czg.pdf"),
}


GATE_RULES = [
    {"rule_id": "INCLUDE_CANDIDATE", "minimum_threshold": "All five operational conditions PASS on project-level evidence: Australian jurisdiction; georeferenced location; formal independent project/development unit; explicit REE primary/co-product/planned recovery by-product/development target; exploration/resource assessment/development stage. Require at least one government/tenure source and one formal technical/project disclosure, with source date and project relation recorded. Resolve material duplicate conflicts before promotion.", "effect": "Eligible for MCDA candidate-list review after reviewer sign-off; not automatically admitted."},
    {"rule_id": "HOLD", "minimum_threshold": "Any required condition is unknown, evidence is only an occurrence/mineral indication, planned REE recovery is not evidenced, project-vs-deposit unit is unresolved, tenure/source coverage is missing, or contradictory identity/ownership evidence remains.", "effect": "Retain in audit queue; do not score or silently discard."},
    {"rule_id": "EXCLUDE", "minimum_threshold": "Positive evidence establishes failure of a mandatory condition (outside Australian jurisdiction; no project-level REE role; no qualifying exploration/resource/development unit; or only a deposit/occurrence child with no independent project identity). Record the failed condition and evidence, then require human review.", "effect": "Exclude from project candidate table but retain raw/source IDs and lineage."},
    {"rule_id": "DEDUP_MERGE", "minimum_threshold": "Require authoritative project alias/parent-child disclosure, exact government project code/tenement relationship, or at least two independent matching identifiers including geography/tenure plus project/company evidence. Exact name/string match alone is only a candidate link.", "effect": "Preserve all original IDs; record parent Project, child Deposit/Prospect/Tenement and merge evidence."},
]


def main():
    groups = read_csv(OUT / "project_dedup_candidates.csv")
    targets = read_csv(OUT / "cohort_reproduction" / "reconstructed_cohort_487.csv")
    by_key = {g["canonical_project_candidate_not_approved"]: g for g in groups}
    evidence = []
    target_to_case = {}
    for key, case in CASES.items():
        g = by_key.get(key)
        if not g:
            raise SystemExit(f"Missing candidate group: {key}")
        target_refs = [x.strip() for x in g["target_ids_preserved"].split("|") if x.strip()]
        for ref in target_refs:
            if ref.startswith("LEGACY:"):
                project_id = ref.split(":", 1)[1]
                for t in targets:
                    if t.get("legacy_project_id") == project_id:
                        canonical_unit = "Wudinna REE Project" if key in ("Wudinna Project", "Wudinna Project (Baggy Green deposit)") else key
                        target_to_case[t["target_id"]] = (key, case, canonical_unit)
            elif ref.startswith("E1:"):
                candidate_id = ref.split(":", 1)[1]
                for t in targets:
                    if t.get("candidate_id") == candidate_id:
                        canonical_unit = "Wudinna REE Project" if key in ("Wudinna Project", "Wudinna Project (Baggy Green deposit)") else key
                        target_to_case[t["target_id"]] = (key, case, canonical_unit)
        evidence.append({
            "candidate_group_key": key,
            "canonical_project_unit": "Wudinna REE Project" if key in ("Wudinna Project", "Wudinna Project (Baggy Green deposit)") else key,
            "target_ids_preserved": g["target_ids_preserved"],
            "source_names": g.get("source_names", ""),
            "state_or_states": g.get("states", ""),
            "project_identity_status": case["identity"],
            "jurisdiction_status": "PASS_AUSTRALIA",
            "location_status": "PASS_SOURCE_LOCATION; boundary/tenure still target-specific",
            "ree_role_status": case["ree"],
            "stage_status": case["stage"],
            "current_project_or_rights_entity": case["company"],
            "company_name_transfer_and_interest_history": case["company_history"],
            "dedup_decision": case["dedup"],
            "inclusion_gate": case["gate"],
            "evidence_assessment": case["reason"],
            "primary_source_urls": case["urls"],
            "as_of_date": "2026-10-29",
            "review_status": "SOURCE_REVIEWED; TENURE_AND_FINAL_ENTITY_SIGNOFF_PENDING",
            "reviewer_decision": "",
            "reviewer_notes": "",
        })

    gate_rows = []
    definition_rows = read_csv(OUT / "487_definition_review.csv")
    for row in definition_rows:
        hit = target_to_case.get(row["target_id"])
        if not hit:
            continue
        key, case, canonical_unit = hit
        verified_project = case["identity"].startswith("PASS")
        role_pass = case["ree"].startswith("PASS")
        stage_pass = case["stage"].startswith("PASS")
        row.update({
            "jurisdiction_check": "PASS_AUSTRALIA_OFFICIAL_PROJECT_SOURCE",
            "location_check": "PASS_IDENTIFIABLE_PROJECT_LOCATION_BOUNDARY_PENDING",
            "location_evidence": "Official project source identifies the named project and locality; target-specific coordinate/title polygon linkage remains open. Sources: " + case["urls"],
            "location_boundary_check": "PROJECT_LOCATION_IDENTIFIED_BOUNDARY_AND_TITLE_TRACE_PENDING",
            "project_identity_check": case["identity"],
            "project_linkage_check": "LINKED_TO_REVIEWED_PROJECT_CANDIDATE" if verified_project else "PROJECT_UNIT_UNRESOLVED_HOLD",
            "canonical_project_candidate_not_approved": canonical_unit,
            "entity_level_assessed": "Project with child Deposit observation" if "Baggy Green" in key or "Nolans Bore" in key else "Project candidate",
            "project_lifecycle_check": case["stage"],
            "ree_role_check": case["ree"],
            "condition_1_jurisdiction": "PASS_AUSTRALIA_OFFICIAL_PROJECT_SOURCE",
            "condition_2_location": "PASS_IDENTIFIABLE_LOCATION_BOUNDARY_PENDING",
            "condition_3_distinct_project": case["identity"],
            "condition_4_ree_role": case["ree"],
            "condition_5_project_lifecycle": case["stage"],
            "definition_screen_status": "PROJECT_CANDIDATE_REVIEW" if role_pass and stage_pass and verified_project else "HOLD_REE_ROLE" if not role_pass else "HOLD_INSUFFICIENT_PROJECT_IDENTITY_OR_REE_ROLE",
            "source_evidence_note": case["reason"] + " Project boundary/titleholder relationship remains a separate target-level check.",
            "project_evidence_url": case["urls"],
            "evidence_status": "PRIMARY_SOURCES_REVIEWED; PROJECT_BOUNDARY_AND_TITLE_TRACE_PENDING",
            "company_asx_name_transfer_review": "PROJECT_ENTITY_SOURCE_REVIEWED; REGISTERED_HOLDER_AND_OPERATOR_RELATION_PENDING",
            "historical_company_names": case["company_history"],
            "company_relationship_evidence_url": case["urls"],
            "project_dedup_group_candidate": canonical_unit,
            "project_dedup_decision": "SOURCE_REVIEWED_CANDIDATE; HUMAN_SIGNOFF_PENDING: " + case["dedup"],
        })
    write_csv(OUT / "487_definition_review.csv", definition_rows)

    # Enrich company queue with sourced proponent/rights history without
    # converting project interest into registered title or field operator.
    company_rows = read_csv(OUT / "company_entity_resolution_queue_487.csv")
    asx_codes = {"Barkly Rare Earths Project": "ASX:BAK", "Charley Creek Project": "ASX:ENV", "Donald Mineral Sands Project": "ASX:ATR", "Goschen Central Project": "ASX:ADC", "Goschen Rare Earths and Mineral Sands Project": "ASX:VHM", "Koppamurra Project": "ASX:AR3", "Narraburra REE Project": "ASX:OBT (formerly ASX:GRL)", "Nolans Project (Nolans Bore deposit)": "ASX:ARU", "Wudinna Project": "LSE:COBR", "Wudinna Project (Baggy Green deposit)": "LSE:COBR"}
    for row in company_rows:
        hit = target_to_case.get(row["target_id"])
        if not hit:
            continue
        key, case, _ = hit
        row.update({
            "developer_status": "PROJECT PROPONENT / RIGHTS ENTITY SUPPORTED BY PRIMARY SOURCE",
            "operator_status": "CURRENT FIELD OPERATOR NOT INFERRED FROM PROJECT PROPONENT",
            "owner_status": "PROJECT INTEREST EVIDENCE RECORDED; REGISTERED TITLE LINK PENDING",
            "asx_code_or_security_id": asx_codes.get(key, ""),
            "current_company_name": case["company"],
            "historical_company_names": case["company_history"],
            "relationship_source_url": case["urls"],
            "review_status": "PARTIAL_PRIMARY_SOURCE_REVIEW; TITLE_AND_OPERATOR_CONFIRMATION_PENDING",
            "reviewer_notes": (row.get("reviewer_notes", "") + " " + case["company_history"]).strip(),
        })
        if key == "Copi Mineral Sands Project":
            row["asic_acn_abn"] = "ACN 160 863 892; ABN 23 160 863 892"
            row["transfer_or_rename_effective_date"] = "RZ Resources Ltd name effective 2021-04-23 (ABN Lookup); project equity participation requires current completion crosscheck."
        elif key == "Donald Mineral Sands Project":
            row["transfer_or_rename_effective_date"] = "Mining title transfer from Donald Mineral Sands Pty Ltd to The Donald Project Pty Ltd in 2024; Energy Fuels JV effective September 2024."
        elif key == "Narraburra REE Project":
            row["transfer_or_rename_effective_date"] = "Godolphin Resources renamed Orbit Resources effective 2026-08-19; proposed Matrix asset transfer/listing not completed as of 2026-10-29."
        elif key.startswith("Wudinna"):
            row["transfer_or_rename_effective_date"] = "Cobra acquired 100% Wudinna in April 2024; Wudinna Gold Assets sale to Barton completed 2025; Cobra retained certain REE mineral rights."
    write_csv(OUT / "company_entity_resolution_queue_487.csv", company_rows)

    for t in targets:
        hit = target_to_case.get(t["target_id"])
        if hit:
            key, case, _ = hit
            status = case["gate"]
            why = case["reason"]
            urls = case["urls"]
            dedup = case["dedup"]
            company = case["company"]
        else:
            key, status, why, urls, dedup, company = "", "HOLD", "No project-level evidence review completed for this target yet; keep its fixed ID and current five-condition disposition. No exclusion inferred from missing evidence.", "", "UNRESOLVED", "NOT_VERIFIED"
        gate_rows.append({
            "target_id": t["target_id"], "cohort": t["cohort"], "state": t["state"],
            "source_name": t.get("source_name", ""), "candidate_group_key": key,
            "project_unit_status": "REVIEWED" if hit else "NOT_YET_REVIEWED",
            "inclusion_gate": status, "dedup_relation": dedup,
            "current_project_or_rights_entity": company,
            "decision_reason": why, "primary_source_urls": urls,
            "reviewer_decision": "", "reviewer_notes": "",
        })
    write_csv(OUT / "project_candidate_evidence_review.csv", evidence)
    write_csv(OUT / "487_inclusion_gate.csv", gate_rows)
    write_csv(OUT / "project_inclusion_gate_rules.csv", GATE_RULES)
    gap_rows = read_csv(OUT / "upstream_reproducibility_gaps.csv")
    for row in gap_rows:
        row["status"] = "RECONSTRUCTED_NOT_BYTE_IDENTICAL"
        row["effect"] = "Selection rules and row-level results are independently regenerated from retained ledgers and exactly match the frozen 487 IDs; original ChatGPT sandbox ZIP bytes are unavailable."
    write_csv(OUT / "upstream_reproducibility_gaps.csv", gap_rows)
    # Keep the manifest aligned with the source-enriched row statuses and recovered ledgers.
    manifest_path = OUT / "census_review_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    from collections import Counter
    manifest["definition_status_counts"] = dict(Counter(r["definition_screen_status"] for r in definition_rows))
    manifest["missing_upstream_files"] = []
    manifest["reconstructed_upstream_files"] = ["provisional_project_groups_126.csv", "legacy_203_crosswalk_audit.csv", "all_1006_evidence_decisions.csv", "E1_project_unlinked_review_queue.csv"]
    manifest["project_evidence_review"] = {
        "candidate_groups_source_reviewed": len(evidence),
        "candidate_groups_meeting_project_and_ree_evidence_gate": sum(r["inclusion_gate"] == "INCLUDE_CANDIDATE" for r in evidence),
        "distinct_project_units_after_documented_child_merge": len({r["canonical_project_unit"] for r in evidence if r["inclusion_gate"] == "INCLUDE_CANDIDATE"}),
        "candidate_groups_on_hold": sum(r["inclusion_gate"] == "HOLD" for r in evidence),
        "target_rows_meeting_candidate_gate": sum(r["inclusion_gate"] == "INCLUDE_CANDIDATE" for r in gate_rows),
        "target_rows_still_on_hold": sum(r["inclusion_gate"] == "HOLD" for r in gate_rows),
        "as_of_date": "2026-10-29",
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    load_gate_sqlite()
    verified_units = {r["canonical_project_unit"] for r in evidence if r["inclusion_gate"] == "INCLUDE_CANDIDATE"}
    print(json.dumps({"candidate_groups_source_reviewed": len(evidence), "distinct_verified_project_candidates": len(verified_units), "hold_candidate_groups": sum(r['inclusion_gate']=='HOLD' for r in evidence), "target_gate_counts": {k: sum(r['inclusion_gate']==k for r in gate_rows) for k in sorted({r['inclusion_gate'] for r in gate_rows})}}, ensure_ascii=False))


if __name__ == "__main__":
    main()


