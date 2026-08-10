from __future__ import annotations

import hashlib
import json
import shutil
from datetime import date, datetime
from pathlib import Path

import openpyxl
from openpyxl.utils.cell import range_boundaries


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
WORKBOOK = HERE / "powerbi_ready_data.xlsx"
PROJECT = "Autonomous_Driving_Benchmark"
MODEL = HERE / f"{PROJECT}.SemanticModel"
REPORT = HERE / f"{PROJECT}.Report"
HANDOFF = ROOT / "Autonomous_Driving_PowerBI_Codex_Handoff" / "Autonomous_Driving_PowerBI_Codex_Handoff"
THEME_SOURCE = HANDOFF / "04_PowerBI_Theme_Professional.json"


TABLES = {
    "dim_company": "DimCompany",
    "dim_date": "DimDate",
    "dim_geography": "DimGeography",
    "dim_source": "DimSource",
    "dim_technology": "DimTechnology",
    "fact_av_incident": "FactIncident",
    "fact_deployment_mileage": "FactDeployment",
    "fact_company_capability": "FactCapability",
    "fact_partnership": "FactPartnership",
    "fact_gpu_pricing": "FactGpuPricing",
    "fact_training_cost_scenario": "FactCostScenario",
    "fact_cost_sensitivity": "CostSensitivity",
    "fact_scalability_score": "FactScalability",
    "fact_safety_indicator": "SafetyIndicators",
    "bridge_company_technology": "BridgeCompanyTechnology",
    "qa_validation_result": "QaResults",
}


MEASURES = [
    ("Historical Cutoff", "DATE(2025, 6, 30)", "01 Executive", "mmm d, yyyy"),
    ("Historical Cutoff Label", '"Evidence cutoff: " & FORMAT([Historical Cutoff], "mmm d, yyyy")', "01 Executive", None),
    ("Source Count", "DISTINCTCOUNT(dim_source[source_id])", "01 Executive", "0"),
    ("Primary Source Count", 'CALCULATE(DISTINCTCOUNT(dim_source[source_id]), dim_source[source_class] = "Primary")', "01 Executive", "0"),
    ("Primary Source Share", "DIVIDE([Primary Source Count], [Source Count])", "01 Executive", "0.0%"),
    ("Cutoff Violations", "CALCULATE(COUNTROWS(dim_source), dim_source[cutoff_valid] = 0)", "01 Executive", "0"),
    ("Selected Company", 'SELECTEDVALUE(dim_company[company_name], "All companies")', "01 Executive", None),
    ("Selected Role", 'SELECTEDVALUE(dim_company[ecosystem_role], "Multiple roles selected")', "01 Executive", None),
    ("Comparability Banner", 'VAR Roles = DISTINCTCOUNT(dim_company[ecosystem_role]) RETURN IF(Roles > 1, "Role warning: operator, consumer ADAS, platform, and supplier metrics are not interchangeable.", "Interpret metrics within the selected ecosystem role.")', "01 Executive", None),
    ("Average Evidence Strength", "AVERAGE(fact_company_capability[evidence_strength_1_5])", "02 Evidence", "0.0"),
    ("Verified Capability Count", 'CALCULATE(COUNTROWS(fact_company_capability), fact_company_capability[evidence_status] = "Verified")', "02 Evidence", "0"),
    ("Capability Evidence Count", "COUNTROWS(fact_company_capability)", "02 Evidence", "0"),
    ("Verified Capability Share", "DIVIDE([Verified Capability Count], [Capability Evidence Count])", "02 Evidence", "0.0%"),
    ("Deployment Metric Value", "SUM(fact_deployment_mileage[metric_value])", "03 Deployment", "#,0.0"),
    ("Latest Metric Date", "MAX(fact_deployment_mileage[metric_date])", "03 Deployment", "mmm d, yyyy"),
    ("Selected Deployment Metric", "SELECTEDVALUE(fact_deployment_mileage[metric_name])", "03 Deployment", None),
    ("Selected Deployment Unit", "SELECTEDVALUE(fact_deployment_mileage[unit])", "03 Deployment", None),
    ("Deployment Context Is Valid", "IF(HASONEVALUE(fact_deployment_mileage[metric_name]) && HASONEVALUE(fact_deployment_mileage[unit]), 1, 0)", "03 Deployment", "0"),
    ("Deployment Display Value", "IF([Deployment Context Is Valid] = 1, [Deployment Metric Value], BLANK())", "03 Deployment", "#,0.0"),
    ("Deployment Context Warning", 'IF([Deployment Context Is Valid] = 1, BLANK(), "Select one deployment metric and unit. Unlike units must not be aggregated.")', "03 Deployment", None),
    ("Deployment Company Label", 'COALESCE(SELECTEDVALUE(dim_company[company_name]), IF(ISBLANK(SELECTEDVALUE(fact_deployment_mileage[company_id])), "California program total", "Multiple companies"))', "03 Deployment", None),
    ("Waymo Rider Only Miles", 'CALCULATE(SUM(fact_deployment_mileage[metric_value]), dim_company[company_name] = "Waymo", fact_deployment_mileage[metric_name] = "Rider-only autonomous miles")', "03 Deployment", "#,0"),
    ("Waymo Paid Trips Per Week", 'CALCULATE(MAX(fact_deployment_mileage[metric_value]), dim_company[company_name] = "Waymo", fact_deployment_mileage[metric_name] = "Paid trips per week")', "03 Deployment", "#,0"),
    ("Incident Reports", "DISTINCTCOUNT(fact_av_incident[report_id])", "04 Safety", "0"),
    ("No Injury Report Share", 'DIVIDE(CALCULATE([Incident Reports], fact_av_incident[severity_category] = "No injury reported"), [Incident Reports])', "04 Safety", "0.0%"),
    ("Incident Comparison Warning", '"Raw incident totals are not safety rates. The delivered incidents are a small evidence extract; compare only within reporting class, exposure, geography, system, and period."', "04 Safety", None),
    ("Safety Indicator Value", "MAX(fact_safety_indicator[value])", "04 Safety", "0.00"),
    ("Safety Indicator Lower Bound", "MAX(fact_safety_indicator[lower_confidence_bound])", "04 Safety", "0.00"),
    ("Safety Evidence Status", "SELECTEDVALUE(fact_safety_indicator[status])", "04 Safety", None),
    ("Total Scenario Cost", "SUM(fact_training_cost_scenario[total_cost_usd])", "05 Cost", "$#,0"),
    ("Training Compute Cost", "SUM(fact_training_cost_scenario[training_compute_cost_usd])", "05 Cost", "$#,0"),
    ("Simulation Compute Cost", "SUM(fact_training_cost_scenario[simulation_compute_cost_usd])", "05 Cost", "$#,0"),
    ("Storage Cost", "SUM(fact_training_cost_scenario[base_storage_cost_usd]) + SUM(fact_training_cost_scenario[checkpoint_storage_cost_usd])", "05 Cost", "$#,0"),
    ("Egress Cost", "SUM(fact_training_cost_scenario[egress_cost_usd])", "05 Cost", "$#,0"),
    ("Compute Cost Share", "DIVIDE([Training Compute Cost] + [Simulation Compute Cost], [Total Scenario Cost])", "05 Cost", "0.0%"),
    ("Cost Component Reconciliation Delta", "[Total Scenario Cost] - [Training Compute Cost] - [Simulation Compute Cost] - [Storage Cost] - [Egress Cost]", "05 Cost", "$#,0.00"),
    ("Cost Difference From On Demand", 'VAR OnDemand = CALCULATE([Total Scenario Cost], REMOVEFILTERS(fact_training_cost_scenario[discount_model]), fact_training_cost_scenario[discount_model] = "On-demand") RETURN [Total Scenario Cost] - OnDemand', "05 Cost", "$#,0"),
    ("Cost Savings Percent", 'VAR OnDemand = CALCULATE([Total Scenario Cost], REMOVEFILTERS(fact_training_cost_scenario[discount_model]), fact_training_cost_scenario[discount_model] = "On-demand") RETURN DIVIDE(OnDemand - [Total Scenario Cost], OnDemand)', "05 Cost", "0.0%"),
    ("Sensitivity Change From Baseline", "MAX(fact_cost_sensitivity[change_from_baseline_pct])", "05 Cost", "0.0%"),
    ("Sensitivity Baseline Cost", "MAX(fact_cost_sensitivity[baseline_total_cost_usd])", "05 Cost", "$#,0"),
    ("Scenario Cost Warning", '"Scenario costs are standardized analytical workload outputs, not confidential company expenditures."', "05 Cost", None),
    ("Baseline Weighted Score", "VAR WeightedPoints = SUMX(fact_scalability_score, fact_scalability_score[score_1_5] * RELATED(scalability_criteria[baseline_weight])) VAR TotalWeight = SUMX(fact_scalability_score, RELATED(scalability_criteria[baseline_weight])) RETURN DIVIDE(WeightedPoints, TotalWeight)", "06 Scalability", "0.00"),
    ("L4 Operator Weighted Score", "VAR WeightedPoints = SUMX(fact_scalability_score, fact_scalability_score[score_1_5] * RELATED(scalability_criteria[l4_operator_weight])) VAR TotalWeight = SUMX(fact_scalability_score, RELATED(scalability_criteria[l4_operator_weight])) RETURN DIVIDE(WeightedPoints, TotalWeight)", "06 Scalability", "0.00"),
    ("Platform Supplier Weighted Score", "VAR WeightedPoints = SUMX(fact_scalability_score, fact_scalability_score[score_1_5] * RELATED(scalability_criteria[platform_supplier_weight])) VAR TotalWeight = SUMX(fact_scalability_score, RELATED(scalability_criteria[platform_supplier_weight])) RETURN DIVIDE(WeightedPoints, TotalWeight)", "06 Scalability", "0.00"),
    ("Selected Weighting Scheme", 'SELECTEDVALUE(weighting_scheme[scheme], "Baseline")', "06 Scalability", None),
    ("Selected Weighted Score", 'SWITCH([Selected Weighting Scheme], "L4 operator lens", [L4 Operator Weighted Score], "Platform supplier lens", [Platform Supplier Weighted Score], [Baseline Weighted Score])', "06 Scalability", "0.00"),
    ("Selected Weighted Rank", "RANKX(ALLSELECTED(dim_company[company_name]), [Selected Weighted Score], , DESC, Dense)", "06 Scalability", "0"),
    ("Scalability Score Warning", '"Scalability scores are ordinal decision aids and change with the selected weighting lens."', "06 Scalability", None),
    ("QA Checks", "COUNTROWS(qa_validation_result)", "99 QA", "0"),
    ("QA Passed", 'CALCULATE(COUNTROWS(qa_validation_result), qa_validation_result[status] = "PASS")', "99 QA", "0"),
    ("QA Pass Rate", "DIVIDE([QA Passed], [QA Checks])", "99 QA", "0.0%"),
    ("Critical QA Failures", 'CALCULATE(COUNTROWS(qa_validation_result), qa_validation_result[severity] = "Critical", qa_validation_result[status] <> "PASS")', "99 QA", "0"),
    ("Model Health", 'IF([Critical QA Failures] = 0 && [Cutoff Violations] = 0 && ABS([Cost Component Reconciliation Delta]) < 0.01, "PASS", "REVIEW")', "99 QA", None),
]


def quote_ident(name: str) -> str:
    return name if name.replace("_", "").isalnum() and " " not in name else "'" + name.replace("'", "''") + "'"


def excel_tables():
    wb = openpyxl.load_workbook(WORKBOOK, data_only=True, read_only=False)
    result = {}
    for ws in wb.worksheets:
        for table in ws.tables.values():
            min_col, min_row, max_col, max_row = range_boundaries(table.ref)
            headers = [ws.cell(min_row, c).value for c in range(min_col, max_col + 1)]
            rows = [
                [ws.cell(r, c).value for c in range(min_col, max_col + 1)]
                for r in range(min_row + 1, max_row + 1)
            ]
            result[table.name] = (headers, rows)
    return result


def infer_kind(values, column):
    vals = [v for v in values if v is not None]
    if column.endswith("_date") or column in {"full_date", "incident_month", "submission_month", "run_date"}:
        return "dateTime", "type date"
    if vals and all(isinstance(v, (datetime, date)) for v in vals):
        return "dateTime", "type date"
    if vals and all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in vals):
        if all(float(v).is_integer() for v in vals):
            return "int64", "Int64.Type"
        return "double", "type number"
    return "string", "type text"


def m_source(excel_name: str, headers, rows, select_distinct=False):
    conversions = []
    for idx, col in enumerate(headers):
        _, m_kind = infer_kind([row[idx] for row in rows], col)
        conversions.append(f'{{"{col}", {m_kind}}}')
    workbook_path = str(WORKBOOK).replace('"', '""')
    lines = [
        "let",
        f'    Source = Excel.Workbook(File.Contents("{workbook_path}"), null, true),',
        f'    Data = Source{{[Item="{excel_name}",Kind="Table"]}}[Data],',
    ]
    if select_distinct:
        cols = ", ".join(f'"{c}"' for c in headers)
        lines += [f"    Selected = Table.SelectColumns(Data, {{{cols}}}),", "    DistinctRows = Table.Distinct(Selected),", f'    #"Changed Type" = Table.TransformColumnTypes(DistinctRows,{{{", ".join(conversions)}}})']
    else:
        lines += [f'    #"Changed Type" = Table.TransformColumnTypes(Data,{{{", ".join(conversions)}}})']
    lines += ["in", '    #"Changed Type"']
    return "\n".join(lines)


def table_tmdl(model_name: str, excel_name: str, headers, rows, measures=False, date_table=False):
    out = [f"table {model_name}"]
    if date_table:
        out.append("\tannotation __PBI_DateTable = true")
    for idx, col in enumerate(headers):
        kind, _ = infer_kind([row[idx] for row in rows], col)
        out += ["", f"\tcolumn {quote_ident(col)}", f"\t\tdataType: {kind}"]
        if kind == "dateTime":
            out.append("\t\tformatString: Short Date")
        elif kind == "int64":
            out.append("\t\tformatString: 0")
        elif kind == "double" and ("cost" in col or "price" in col or col.endswith("_usd")):
            out.append("\t\tformatString: $#,0.00")
        out.append("\t\tsummarizeBy: none" if col.endswith("_id") or col in {"date_key", "source_id"} else "\t\tsummarizeBy: sum" if kind in {"int64", "double"} else "\t\tsummarizeBy: none")
        out.append(f"\t\tsourceColumn: {col}")
        if (col.endswith("_id") and col != "source_id") or col == "date_key":
            out.append("\t\tisHidden: true")
    if measures:
        for name, expression, folder, fmt in MEASURES:
            out += ["", f"\tmeasure {quote_ident(name)} = {expression}", f"\t\tdisplayFolder: {folder}"]
            if fmt:
                out.append(f"\t\tformatString: {fmt}")
    out += ["", f"\tpartition {model_name} = m", "\t\tmode: import", "\t\tsource ="]
    out.extend("\t\t\t\t" + line for line in m_source(excel_name, headers, rows).splitlines())
    out += ["", "\tannotation PBI_ResultType = Table", ""]
    return "\n".join(out)


def criteria_tmdl(headers, rows):
    keep = ["criterion_id", "criterion_name", "definition", "baseline_weight", "l4_operator_weight", "platform_supplier_weight", "measurement_method"]
    indexes = [headers.index(c) for c in keep]
    subset_rows = [[row[i] for i in indexes] for row in rows]
    out = ["table scalability_criteria"]
    for idx, col in enumerate(keep):
        kind, _ = infer_kind([r[idx] for r in subset_rows], col)
        out += ["", f"\tcolumn {col}", f"\t\tdataType: {kind}", "\t\tformatString: 0" if kind == "int64" else "\t\tsummarizeBy: none"]
        if kind != "int64":
            pass
        else:
            out.append("\t\tsummarizeBy: none")
        out.append(f"\t\tsourceColumn: {col}")
        if col == "criterion_id":
            out.append("\t\tisHidden: true")
    out += ["", "\tpartition scalability_criteria = m", "\t\tmode: import", "\t\tsource ="]
    out.extend("\t\t\t\t" + line for line in m_source("ScoreDetail", keep, subset_rows, True).splitlines())
    out += ["", "\tannotation PBI_ResultType = Table", ""]
    return "\n".join(out)


def weighting_tmdl():
    return '''table weighting_scheme

\tcolumn scheme
\t\tdataType: string
\t\tsummarizeBy: none
\t\tsourceColumn: scheme

\tpartition weighting_scheme = m
\t\tmode: import
\t\tsource =
\t\t\t\t#table(type table [scheme = text], {{"Baseline"}, {"L4 operator lens"}, {"Platform supplier lens"}})

\tannotation PBI_ResultType = Table
'''


def build_model():
    source = excel_tables()
    tables_dir = MODEL / "definition" / "tables"
    if tables_dir.exists():
        shutil.rmtree(tables_dir)
    tables_dir.mkdir(parents=True)
    for model_name, excel_name in TABLES.items():
        headers, rows = source[excel_name]
        text = table_tmdl(model_name, excel_name, headers, rows, measures=model_name == "dim_company", date_table=model_name == "dim_date")
        (tables_dir / f"{model_name}.tmdl").write_text(text, encoding="utf-8")
    score_headers, score_rows = source["ScoreDetail"]
    (tables_dir / "scalability_criteria.tmdl").write_text(criteria_tmdl(score_headers, score_rows), encoding="utf-8")
    (tables_dir / "weighting_scheme.tmdl").write_text(weighting_tmdl(), encoding="utf-8")

    refs = list(TABLES) + ["scalability_criteria", "weighting_scheme"]
    model = [
        "model Model",
        "\tculture: en-US",
        "\tdefaultPowerBIDataSourceVersion: powerBI_V3",
        "\tsourceQueryCulture: en-US",
        "\tvalueFilterBehavior: independent",
        "\tdiscourageImplicitMeasures",
        "\tdataAccessOptions",
        "\t\tlegacyRedirects",
        "\t\treturnErrorValuesAsNull",
        "",
        "annotation __PBI_TimeIntelligenceEnabled = 0",
        "annotation PBI_QueryOrder = " + json.dumps(refs),
        "annotation PBI_ProTooling = [\"DevMode\"]",
        "",
    ]
    model += [f"ref table {t}" for t in refs]
    model += ["", "ref cultureInfo en-US", ""]
    (MODEL / "definition" / "model.tmdl").write_text("\n".join(model), encoding="utf-8")

    relationships = '''relationship rel_company_incident
\tfromColumn: fact_av_incident.company_id
\ttoColumn: dim_company.company_id

relationship rel_company_deployment
\tfromColumn: fact_deployment_mileage.company_id
\ttoColumn: dim_company.company_id

relationship rel_company_capability
\tfromColumn: fact_company_capability.company_id
\ttoColumn: dim_company.company_id

relationship rel_company_partnership
\tfromColumn: fact_partnership.company_id
\ttoColumn: dim_company.company_id

relationship rel_company_scalability
\tfromColumn: fact_scalability_score.company_id
\ttoColumn: dim_company.company_id

relationship rel_company_safety
\tfromColumn: fact_safety_indicator.company_id
\ttoColumn: dim_company.company_id

relationship rel_company_technology
\tfromColumn: bridge_company_technology.company_id
\ttoColumn: dim_company.company_id

relationship rel_technology_bridge
\tfromColumn: bridge_company_technology.technology_id
\ttoColumn: dim_technology.technology_id

relationship rel_criterion_scalability
\tfromColumn: fact_scalability_score.criterion_id
\ttoColumn: scalability_criteria.criterion_id

relationship rel_date_deployment
\tfromColumn: fact_deployment_mileage.metric_date
\ttoColumn: dim_date.full_date

relationship rel_date_safety
\tfromColumn: fact_safety_indicator.as_of_date
\ttoColumn: dim_date.full_date

relationship rel_date_incident_month
\tisActive: false
\tfromColumn: fact_av_incident.incident_month
\ttoColumn: dim_date.full_date
'''
    source_facts = [
        ("incident", "fact_av_incident"), ("deployment", "fact_deployment_mileage"),
        ("capability", "fact_company_capability"), ("partnership", "fact_partnership"),
        ("gpuprice", "fact_gpu_pricing"), ("costscenario", "fact_training_cost_scenario"),
        ("scalability", "fact_scalability_score"), ("safety", "fact_safety_indicator"),
    ]
    for suffix, table in source_facts:
        relationships += f"\nrelationship rel_source_{suffix}\n\tfromColumn: {table}.source_id\n\ttoColumn: dim_source.source_id\n"
    (MODEL / "definition" / "relationships.tmdl").write_text(relationships, encoding="utf-8")


SCHEMA_VISUAL = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.11.0/schema.json"
SCHEMA_PAGE = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json"


def stable_id(*parts):
    return hashlib.sha1("|".join(map(str, parts)).encode()).hexdigest()[:20]


def col(entity, prop, active=None):
    p = {
        "field": {"Column": {"Expression": {"SourceRef": {"Entity": entity}}, "Property": prop}},
        "queryRef": f"{entity}.{prop}",
        "nativeQueryRef": prop,
    }
    if active is not None:
        p["active"] = active
    return p


def measure(name):
    return {
        "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "dim_company"}}, "Property": name}},
        "queryRef": f"dim_company.{name}",
        "nativeQueryRef": name,
    }


def aggregate(entity, prop, function=0):
    return {
        "field": {"Aggregation": {"Expression": {"Column": {"Expression": {"SourceRef": {"Entity": entity}}, "Property": prop}}, "Function": function}},
        "queryRef": f"Sum({entity}.{prop})",
        "nativeQueryRef": f"Sum of {prop}",
    }


def title_objects(title):
    if not title:
        return None
    return {"title": [{"properties": {"text": {"expr": {"Literal": {"Value": "'" + title.replace("'", "''") + "'"}}}}}]}


def data_visual(page, key, visual_type, x, y, w, h, query_state, title=None, objects=None, z=0):
    name = stable_id(page, key)
    visual = {"visualType": visual_type, "query": {"queryState": query_state}, "drillFilterOtherVisuals": True}
    if objects:
        visual["objects"] = objects
    containers = title_objects(title)
    if containers:
        visual["visualContainerObjects"] = containers
    return name, {
        "$schema": SCHEMA_VISUAL,
        "name": name,
        "position": {"x": x, "y": y, "z": z, "height": h, "width": w, "tabOrder": z},
        "visual": visual,
        "filterConfig": {"filters": []},
    }


def textbox(page, key, text, x, y, w, h, size="11pt", color="#20262E", bold=False, z=0):
    name = stable_id(page, key)
    style = {"fontFamily": "Segoe UI", "fontSize": size, "color": color}
    if bold:
        style["fontWeight"] = "bold"
    return name, {
        "$schema": SCHEMA_VISUAL,
        "name": name,
        "position": {"x": x, "y": y, "z": z, "height": h, "width": w, "tabOrder": z},
        "visual": {
            "visualType": "textbox",
            "objects": {"general": [{"properties": {"paragraphs": [{"textRuns": [{"value": text, "textStyle": style}]}]}}]},
            "drillFilterOtherVisuals": True,
        },
    }


def slicer(page, key, entity, prop, x, y, w, h, title):
    return data_visual(page, key, "slicer", x, y, w, h, {"Values": {"projections": [col(entity, prop, True)]}}, title, {"data": [{"properties": {"mode": {"expr": {"Literal": {"Value": "'Dropdown'"}}}}}]})


def card(page, key, measure_name, x, y, w, h, title):
    literal = lambda value: {"expr": {"Literal": {"Value": value}}}
    selector = {"id": "default"}
    objects = {
        "value": [{"properties": {"fontSize": literal("24D"), "bold": literal("true")}, "selector": selector}],
        "label": [{"properties": {"show": literal("true"), "text": literal("'" + title.replace("'", "''") + "'"), "fontSize": literal("11D")}, "selector": selector}],
        "padding": [{"properties": {"paddingUniform": literal("0L")}, "selector": selector}],
        "layout": [{"properties": {"topOuterMargin": literal("0L"), "bottomOuterMargin": literal("0L"), "leftOuterMargin": literal("0L"), "rightOuterMargin": literal("0L"), "paddingUniform": literal("0L")}, "selector": selector}],
        "spacing": [{"properties": {"verticalSpacing": literal("-4L")}, "selector": selector}],
        "outline": [{"properties": {"show": literal("false")}, "selector": selector}],
    }
    return data_visual(page, key, "cardVisual", x, y, w, h, {"Data": {"projections": [measure(measure_name)]}}, objects=objects)


def table(page, key, fields, x, y, w, h, title):
    projections = [measure(f[1]) if f[0] == "measure" else col(f[0], f[1]) for f in fields]
    return data_visual(page, key, "tableEx", x, y, w, h, {"Values": {"projections": projections}}, title)


def matrix(page, key, rows, columns, values, x, y, w, h, title):
    qs = {"Rows": {"projections": [col(*f) for f in rows]}}
    if columns:
        qs["Columns"] = {"projections": [col(*f) for f in columns]}
    if values:
        qs["Values"] = {"projections": [measure(v) if isinstance(v, str) else aggregate(*v) for v in values]}
    return data_visual(page, key, "pivotTable", x, y, w, h, qs, title)


def bar(page, key, categories, values, x, y, w, h, title, visual_type="clusteredBarChart", series=None):
    qs = {"Category": {"projections": [col(e, p, i == len(categories) - 1) for i, (e, p) in enumerate(categories)]}, "Y": {"projections": [measure(v) if isinstance(v, str) else aggregate(*v) for v in values]}}
    if series:
        qs["Series"] = {"projections": [col(*series)]}
    return data_visual(page, key, visual_type, x, y, w, h, qs, title)


def line(page, key, category, value, series, x, y, w, h, title):
    qs = {"Category": {"projections": [col(*category, True)]}, "Y": {"projections": [measure(value)]}, "Series": {"projections": [col(*series)]}}
    return data_visual(page, key, "lineChart", x, y, w, h, qs, title)


def page_header(page_id, title, warning, visuals):
    visuals += [
        textbox(page_id, "page_title", title, 24, 14, 760, 34, "18pt", bold=True, z=0),
        textbox(page_id, "cutoff", "Evidence cutoff: Jun 30, 2025  |  Independent public-data reconstruction", 820, 18, 436, 24, "9pt", "#4F5B66", z=1),
        textbox(page_id, "warning", warning, 24, 56, 1232, 32, "9pt", "#866C4D", bold=True, z=2),
    ]


def build_pages():
    pages = []

    p = "executive"
    v = []
    page_header(p, "Executive Benchmark", "Comparability guardrail: ecosystem roles are not interchangeable. Scalability scores are ordinal and lens-dependent.", v)
    v += [
        slicer(p, "company", "dim_company", "company_name", 24, 96, 224, 48, "Company"),
        slicer(p, "role", "dim_company", "ecosystem_role", 264, 96, 224, 48, "Ecosystem role"),
        slicer(p, "evidence", "fact_company_capability", "evidence_status", 504, 96, 224, 48, "Evidence status"),
        slicer(p, "weight", "weighting_scheme", "scheme", 744, 96, 248, 48, "Weighting lens"),
        card(p, "sources", "Source Count", 24, 158, 180, 94, "Sources"),
        card(p, "primary", "Primary Source Count", 220, 158, 180, 94, "Primary sources"),
        card(p, "qa", "QA Pass Rate", 416, 158, 180, 94, "QA pass rate"),
        card(p, "miles", "Waymo Rider Only Miles", 612, 158, 220, 94, "Waymo rider-only miles"),
        card(p, "trips", "Waymo Paid Trips Per Week", 848, 158, 196, 94, "Paid trips / week"),
        card(p, "health", "Model Health", 1060, 158, 196, 94, "Model health"),
        table(p, "roles", [("dim_company", "company_name"), ("dim_company", "ecosystem_role"), ("dim_company", "automation_exposure"), ("dim_company", "business_model_classification")], 24, 258, 336, 210, "Company Role Matrix"),
        matrix(p, "evidence_matrix", [("dim_company", "company_name")], [("fact_company_capability", "capability_category")], ["Average Evidence Strength"], 376, 258, 488, 210, "Evidence Strength by Capability"),
        bar(p, "weighted", [("dim_company", "company_name")], ["Selected Weighted Score"], 880, 258, 376, 210, "Weighted Scalability Score | Ordinal, lens-dependent"),
        table(p, "deployment", [("measure", "Deployment Company Label"), ("fact_deployment_mileage", "metric_name"), ("fact_deployment_mileage", "metric_value"), ("fact_deployment_mileage", "unit"), ("fact_deployment_mileage", "metric_date"), ("fact_deployment_mileage", "limitation")], 24, 484, 612, 204, "Deployment Metrics | Units Kept Separate"),
        table(p, "limits", [("dim_company", "company_name"), ("fact_company_capability", "capability_category"), ("fact_company_capability", "evidence_status"), ("fact_company_capability", "limitation"), ("fact_company_capability", "source_id")], 652, 484, 604, 204, "Strengths, Limits, and Evidence Context"),
    ]
    pages.append((p, "Executive Benchmark", v, False, 1280, 720))

    p = "technology"
    v = []
    page_header(p, "Technology & Workflow", "Technology evidence is role-specific; supplier, platform, operator, and consumer-ADAS measures are not equivalent.", v)
    v += [
        slicer(p, "company", "dim_company", "company_name", 24, 96, 224, 48, "Company"),
        slicer(p, "tech_category", "dim_technology", "technology_category", 264, 96, 256, 48, "Technology category"),
        slicer(p, "relationship", "bridge_company_technology", "relationship_type", 536, 96, 256, 48, "Relationship type"),
        slicer(p, "evidence", "fact_company_capability", "evidence_status", 808, 96, 224, 48, "Evidence status"),
        textbox(p, "workflow_title", "Role-aware autonomous-driving workflow", 24, 158, 500, 30, "13pt", bold=True, z=10),
        textbox(p, "workflow", "Collect  →  Select  →  Label  →  Train  →  Simulate  →  Validate  →  Deploy  →  Monitor\nOperator, platform, supplier, and consumer-ADAS roles contribute at different stages; presence does not imply equivalence.", 24, 186, 1232, 62, "12pt", "#2E5E7E", bold=True, z=11),
        matrix(p, "company_tech", [("dim_company", "company_name")], [("dim_technology", "technology_name")], [("bridge_company_technology", "company_id", 5)], 24, 266, 600, 206, "Company × Technology"),
        table(p, "sensor", [("dim_company", "company_name"), ("dim_company", "sensor_strategy_summary"), ("dim_company", "comparability_boundary")], 640, 266, 616, 206, "Sensor Architecture Comparison"),
        table(p, "compute", [("dim_company", "company_name"), ("dim_company", "in_vehicle_compute_summary"), ("dim_company", "ecosystem_role")], 24, 488, 420, 200, "In-Vehicle Compute"),
        table(p, "evidence_limits", [("dim_company", "company_name"), ("fact_company_capability", "capability_category"), ("fact_company_capability", "evidence_status"), ("fact_company_capability", "source_id"), ("fact_company_capability", "limitation")], 460, 488, 796, 200, "Evidence and Limitations"),
    ]
    pages.append((p, "Technology & Workflow", v, False, 1280, 720))

    p = "safety"
    v = []
    page_header(p, "Safety & Deployment", "Raw incident totals are not safety rates. The delivered NHTSA incidents are a small evidence extract, not a comprehensive population trend.", v)
    v += [
        slicer(p, "company", "dim_company", "company_name", 24, 96, 208, 48, "Company"),
        slicer(p, "report_type", "fact_av_incident", "report_type", 248, 96, 208, 48, "Report type"),
        slicer(p, "state", "fact_av_incident", "state", 472, 96, 176, 48, "State"),
        slicer(p, "severity", "fact_av_incident", "severity_category", 664, 96, 240, 48, "Severity"),
        slicer(p, "metric", "fact_deployment_mileage", "metric_name", 920, 96, 336, 48, "Deployment metric"),
        bar(p, "safety_benchmark", [("fact_safety_indicator", "indicator_name")], ["Safety Indicator Value"], 24, 166, 500, 286, "Waymo Matched Safety Benchmark Indicators"),
        table(p, "deployment", [("measure", "Deployment Company Label"), ("fact_deployment_mileage", "metric_name"), ("fact_deployment_mileage", "metric_value"), ("fact_deployment_mileage", "unit"), ("fact_deployment_mileage", "geography"), ("fact_deployment_mileage", "limitation")], 540, 166, 716, 286, "Deployment / Exposure Context | Unit Preserved"),
        table(p, "incidents", [("fact_av_incident", "report_id"), ("fact_av_incident", "report_type"), ("fact_av_incident", "incident_month"), ("fact_av_incident", "state"), ("fact_av_incident", "severity_category"), ("fact_av_incident", "source_id")], 24, 470, 580, 218, "NHTSA Evidence Extract | Three Delivered Rows"),
        table(p, "limits", [("fact_safety_indicator", "indicator_name"), ("fact_safety_indicator", "exposure_basis"), ("fact_safety_indicator", "status"), ("fact_safety_indicator", "limitation"), ("fact_safety_indicator", "source_id")], 620, 470, 636, 218, "Safety Evidence Limitations"),
    ]
    pages.append((p, "Safety & Deployment", v, False, 1280, 720))

    p = "cost"
    v = []
    page_header(p, "GPU Cost & Scalability", "Scenario costs are standardized analytical workload outputs, not company expenditures. Scalability scores are ordinal and lens-dependent.", v)
    v += [
        slicer(p, "scenario", "fact_training_cost_scenario", "scenario_name", 24, 96, 184, 48, "Scenario"),
        slicer(p, "provider", "fact_training_cost_scenario", "cloud_provider", 216, 96, 184, 48, "Provider"),
        slicer(p, "gpu", "fact_training_cost_scenario", "gpu_model", 408, 96, 184, 48, "GPU"),
        slicer(p, "instance", "fact_training_cost_scenario", "instance_type", 600, 96, 184, 48, "Instance"),
        slicer(p, "pricing", "fact_training_cost_scenario", "discount_model", 792, 96, 184, 48, "Pricing model"),
        slicer(p, "weight", "weighting_scheme", "scheme", 984, 96, 272, 48, "Weighting lens"),
        card(p, "total", "Total Scenario Cost", 24, 158, 224, 94, "Total scenario cost"),
        card(p, "training", "Training Compute Cost", 264, 158, 224, 94, "Training compute"),
        card(p, "simulation", "Simulation Compute Cost", 504, 158, 224, 94, "Simulation compute"),
        card(p, "storage", "Storage Cost", 744, 158, 224, 94, "Storage"),
        card(p, "egress", "Egress Cost", 984, 158, 224, 94, "Egress"),
        bar(p, "scenario_bar", [("fact_training_cost_scenario", "cloud_provider"), ("fact_training_cost_scenario", "instance_type")], ["Total Scenario Cost"], 24, 258, 420, 194, "Scenario Cost by Provider and Instance"),
        bar(p, "composition", [("fact_training_cost_scenario", "scenario_name")], ["Training Compute Cost", "Simulation Compute Cost", "Storage Cost", "Egress Cost"], 460, 258, 420, 194, "Cost Composition", "barChart"),
        line(p, "sensitivity", ("fact_cost_sensitivity", "parameter_value"), "Sensitivity Change From Baseline", ("fact_cost_sensitivity", "variable"), 896, 258, 360, 194, "Sensitivity to Scenario Inputs"),
        matrix(p, "criterion", [("scalability_criteria", "criterion_name")], [("dim_company", "company_name")], [("fact_scalability_score", "score_1_5", 1)], 24, 470, 600, 218, "Scalability Criterion Profile | Scores 1–5"),
        bar(p, "weight_bar", [("dim_company", "company_name")], ["Selected Weighted Score"], 640, 470, 616, 218, "Weighted Score by Decision Lens | Ordinal"),
    ]
    pages.append((p, "GPU Cost & Scalability", v, False, 1280, 720))

    p = "tooltip"
    v = [
        textbox(p, "title", "Evidence & Source Detail", 12, 10, 296, 26, "14pt", bold=True, z=0),
        table(p, "source_detail", [("dim_source", "source_id"), ("dim_source", "organization"), ("dim_source", "title"), ("dim_source", "publication_date"), ("dim_source", "reliability_classification"), ("dim_source", "relevant_limitations")], 12, 42, 296, 184, "Source detail"),
    ]
    pages.append((p, "Evidence & Source Detail", v, True, 320, 240))
    return pages


def build_report():
    pages_root = REPORT / "definition" / "pages"
    if pages_root.exists():
        shutil.rmtree(pages_root)
    pages_root.mkdir(parents=True)
    pages = build_pages()
    order = []
    for logical_name, display_name, visuals, hidden, width, height in pages:
        page_name = stable_id("page", logical_name)
        order.append(page_name)
        page_dir = pages_root / page_name
        visual_root = page_dir / "visuals"
        visual_root.mkdir(parents=True)
        page_json = {"$schema": SCHEMA_PAGE, "name": page_name, "displayName": display_name, "displayOption": "FitToPage", "height": height, "width": width}
        if hidden:
            page_json["visibility"] = "HiddenInViewMode"
        (page_dir / "page.json").write_text(json.dumps(page_json, indent=2), encoding="utf-8")
        for visual_name, visual_json in visuals:
            d = visual_root / visual_name
            d.mkdir()
            (d / "visual.json").write_text(json.dumps(visual_json, indent=2, ensure_ascii=False), encoding="utf-8")
    pages_json = {"$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.1.0/schema.json", "pageOrder": order, "activePageName": order[0]}
    (pages_root / "pages.json").write_text(json.dumps(pages_json, indent=2), encoding="utf-8")

    registered = REPORT / "StaticResources" / "RegisteredResources"
    registered.mkdir(parents=True, exist_ok=True)
    theme_name = "AutonomousDrivingProfessional"
    shutil.copyfile(THEME_SOURCE, registered / f"{theme_name}.json")
    report_json = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/report/3.3.0/schema.json",
        "themeCollection": {
            "baseTheme": {"name": "CY26SU07", "reportVersionAtImport": {"visual": "2.11.0", "report": "3.4.0", "page": "2.3.1"}, "type": "SharedResources"},
            "customTheme": {"name": theme_name, "reportVersionAtImport": {"visual": "2.11.0", "report": "3.4.0", "page": "2.3.1"}, "type": "RegisteredResources"},
        },
        "objects": {"section": [{"properties": {"verticalAlignment": {"expr": {"Literal": {"Value": "'Top'"}}}}}]},
        "resourcePackages": [
            {"name": "SharedResources", "type": "SharedResources", "items": [{"name": "CY26SU07", "path": "BaseThemes/CY26SU07.json", "type": "BaseTheme"}]},
            {"name": "RegisteredResources", "type": "RegisteredResources", "items": [{"name": theme_name, "path": f"{theme_name}.json", "type": "CustomTheme"}]},
        ],
        "settings": {"useStylableVisualContainerHeader": True, "exportDataMode": "AllowSummarized", "defaultDrillFilterOtherVisuals": True, "allowChangeFilterTypes": True, "useEnhancedTooltips": True, "useDefaultAggregateDisplayName": True},
    }
    (REPORT / "definition" / "report.json").write_text(json.dumps(report_json, indent=2), encoding="utf-8")


if __name__ == "__main__":
    build_model()
    build_report()
    print("Built PBIP semantic model and five-page PBIR report definition.")
