use crate::commands::harness::get_harness_conn;
use crate::HarnessState;
use tauri::State;

#[derive(serde::Serialize)]
pub struct ModelUsageRow {
    pub model:          String,
    pub run_count:      i64,
    pub input_tokens:   i64,
    pub output_tokens:  i64,
    pub total_cost_usd: f64,
    pub avg_cost_usd:   f64,
}

#[derive(serde::Serialize)]
pub struct UseCaseUsageRow {
    pub use_case:       String,
    pub run_count:      i64,
    pub total_cost_usd: f64,
}

#[derive(serde::Serialize)]
pub struct UsageStats {
    pub total_cost_usd:      f64,
    pub total_runs:          i64,
    pub instrumented_runs:   i64,
    pub total_input_tokens:  i64,
    pub total_output_tokens: i64,
    pub by_model:            Vec<ModelUsageRow>,
    pub by_use_case:         Vec<UseCaseUsageRow>,
}

#[tauri::command]
pub fn usage_stats_load(state: State<'_, HarnessState>) -> Result<UsageStats, String> {
    let conn = get_harness_conn(&state)?;

    // ── Summary ───────────────────────────────────────────────────────────────
    let summary_sql = "
        SELECT
            COALESCE(SUM(json_extract(payload_json, '$.cost_usd')), 0.0)    AS total_cost,
            COALESCE(SUM(json_extract(payload_json, '$.input_tokens')), 0)  AS total_in,
            COALESCE(SUM(json_extract(payload_json, '$.output_tokens')), 0) AS total_out,
            COUNT(DISTINCT run_id)                                           AS instrumented_runs
        FROM events
        WHERE type = 'llm_responded'
          AND json_extract(payload_json, '$.cost_usd') IS NOT NULL
    ";

    let (total_cost, total_in, total_out, instrumented_runs) = conn
        .query_row(summary_sql, [], |r| {
            Ok((
                r.get::<_, f64>(0)?,
                r.get::<_, i64>(1)?,
                r.get::<_, i64>(2)?,
                r.get::<_, i64>(3)?,
            ))
        })
        .map_err(|e| format!("summary query failed: {}", e))?;

    let total_runs: i64 = conn
        .query_row("SELECT COUNT(*) FROM runs", [], |r| r.get(0))
        .map_err(|e| format!("run count failed: {}", e))?;

    // ── By model ──────────────────────────────────────────────────────────────
    let model_sql = "
        SELECT
            json_extract(payload_json, '$.resolved_model')               AS model,
            COUNT(DISTINCT run_id)                                        AS run_count,
            COALESCE(SUM(json_extract(payload_json, '$.input_tokens')), 0)  AS input_tokens,
            COALESCE(SUM(json_extract(payload_json, '$.output_tokens')), 0) AS output_tokens,
            COALESCE(SUM(json_extract(payload_json, '$.cost_usd')), 0.0)    AS total_cost
        FROM events
        WHERE type = 'llm_responded'
          AND json_extract(payload_json, '$.cost_usd') IS NOT NULL
        GROUP BY model
        ORDER BY total_cost DESC
    ";

    let mut stmt = conn
        .prepare(model_sql)
        .map_err(|e| format!("model query failed: {}", e))?;

    let by_model: Vec<ModelUsageRow> = stmt
        .query_map([], |r| {
            let total_cost_usd: f64 = r.get(4)?;
            let run_count: i64 = r.get(1)?;
            let avg_cost_usd = if run_count > 0 {
                total_cost_usd / run_count as f64
            } else {
                0.0
            };
            Ok(ModelUsageRow {
                model: r.get::<_, Option<String>>(0)?.unwrap_or_default(),
                run_count,
                input_tokens: r.get(2)?,
                output_tokens: r.get(3)?,
                total_cost_usd,
                avg_cost_usd,
            })
        })
        .map_err(|e| format!("model rows failed: {}", e))?
        .filter_map(|r| r.ok())
        .collect();

    // ── By use case ───────────────────────────────────────────────────────────
    let use_case_sql = "
        SELECT
            r.label,
            COUNT(DISTINCT e.run_id)                                         AS run_count,
            COALESCE(SUM(json_extract(e.payload_json, '$.cost_usd')), 0.0)  AS total_cost
        FROM events e
        JOIN runs r ON e.run_id = r.run_id
        WHERE e.type = 'llm_responded'
          AND json_extract(e.payload_json, '$.cost_usd') IS NOT NULL
        GROUP BY r.label
        ORDER BY total_cost DESC
    ";

    let mut stmt = conn
        .prepare(use_case_sql)
        .map_err(|e| format!("use case query failed: {}", e))?;

    let raw_use_case: Vec<(String, i64, f64)> = stmt
        .query_map([], |r| {
            Ok((r.get::<_, String>(0)?, r.get::<_, i64>(1)?, r.get::<_, f64>(2)?))
        })
        .map_err(|e| format!("use case rows failed: {}", e))?
        .filter_map(|r| r.ok())
        .collect();

    let by_use_case = aggregate_by_use_case(raw_use_case);

    Ok(UsageStats {
        total_cost_usd: total_cost,
        total_runs,
        instrumented_runs,
        total_input_tokens: total_in,
        total_output_tokens: total_out,
        by_model,
        by_use_case,
    })
}

// ── Use case prefix aggregation ───────────────────────────────────────────────

// Matched against a run's label, lowercased, `starts_with` — the same shape as
// classifyRun() in rig/src/components/modules/harness/RunList.tsx, which groups the run
// list. THE TWO MUST AGREE, and until ds t1a nothing checked that they did: BL-083 fixed
// the run list's copy and left this one, so `api-tenant` / `api-gateway` sat here matching
// zero labels while every cloudcost, docbuilder, eduloka and api run fell to
// "Unclassified" in the usage view and grouped correctly one screen away.
//
// This list is derived from the DECLARED AGENT LABELS (`label:` fields in **/agents/*.exs),
// never copied from RunList.tsx — copying one hand-written list into another is what
// produced the defect it replaces. `scripts/check_run_classifier.py` now parses BOTH
// constants and compares them, and runs its dead-entry and unclassified checks against
// each; it is wrapped by tests/test_run_classifier.py and so runs in the whole-suite gate.
//
// The api agents are labelled by their agent id (at1cmd / at1qry / cot1), not by use-case
// directory name. The legacy "Capability Matrix -- ..." labels predate the `cap-matrix: `
// convention and share no prefix with it, so both are carried.
const USE_CASE_PREFIXES: &[(&str, &str)] = &[
    ("payslip",           "Payslip"),
    ("drive",             "Drive"),
    ("email",             "Email"),
    ("cloudcost",         "Cloudcost"),
    ("docbuilder",        "Docbuilder"),
    ("eduloka",           "Eduloka"),
    ("ct-bot",            "CT-Bot"),
    ("at1cmd",            "API / Tenant"),
    ("at1qry",            "API / Tenant"),
    ("cot1",              "API / Gateway"),
    ("provenance",        "Provenance"),
    ("cap-matrix",        "Capability Matrix"),
    ("capability matrix", "Capability Matrix"),
];

fn classify_label(label: &str) -> &'static str {
    let lower = label.to_lowercase();
    for &(prefix, name) in USE_CASE_PREFIXES {
        if lower.starts_with(prefix) {
            return name;
        }
    }
    "Unclassified"
}

fn aggregate_by_use_case(rows: Vec<(String, i64, f64)>) -> Vec<UseCaseUsageRow> {
    use std::collections::HashMap;

    let mut map: HashMap<&'static str, (i64, f64)> = HashMap::new();
    for (label, run_count, cost) in &rows {
        let uc: &'static str = classify_label(label);
        let entry = map.entry(uc).or_insert((0, 0.0));
        entry.0 += run_count;
        entry.1 += cost;
    }

    let mut result: Vec<UseCaseUsageRow> = USE_CASE_PREFIXES
        .iter()
        .filter_map(|&(_, name)| {
            map.get(name).map(|&(rc, cost)| UseCaseUsageRow {
                use_case: name.to_string(),
                run_count: rc,
                total_cost_usd: cost,
            })
        })
        .collect();

    if let Some(&(rc, cost)) = map.get("Unclassified") {
        result.push(UseCaseUsageRow {
            use_case: "Unclassified".to_string(),
            run_count: rc,
            total_cost_usd: cost,
        });
    }

    result
}
