from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from app.DB.duckdb_connection import get_connection
from datetime import datetime
import pandas as pd
import io

router = APIRouter()

@router.post("/export-data")
def export_data(
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format")
):
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        return {"error": "Invalid date format. Use YYYY-MM-DD."}

    conn = get_connection()

    # Index Performance
    index_df = conn.execute("""
        SELECT date, index_value
        FROM custom_index_history
        WHERE date BETWEEN ? AND ?
        ORDER BY date
    """, (start, end)).df()

    # Daily Composition
    composition_df = conn.execute("""
        WITH ranked AS (
            SELECT date, symbol, close AS close_price, market_cap,
                   RANK() OVER (PARTITION BY date ORDER BY market_cap DESC) AS rnk
            FROM daily_price_data
            WHERE date BETWEEN ? AND ?
        )
        SELECT date, symbol, close_price, market_cap
        FROM ranked
        WHERE rnk <= 100
        ORDER BY date, symbol
    """, (start, end)).df()

    # Composition Changes - Took help from AI, I couldn't get it right 
    changes_df = conn.execute("""
        WITH ranked_symbols AS (
            SELECT date, symbol,
                   RANK() OVER (PARTITION BY date ORDER BY market_cap DESC) AS rnk
            FROM daily_price_data
            WHERE date BETWEEN (? - INTERVAL 1 DAY) AND ?
        ),
        top100 AS (
            SELECT date, symbol
            FROM ranked_symbols
            WHERE rnk <= 100
        ),
        entered AS (
            SELECT curr.date, 'entered' AS change_type, curr.symbol
            FROM top100 curr
            LEFT JOIN top100 prev
              ON curr.symbol = prev.symbol
             AND curr.date = prev.date + INTERVAL 1 DAY
            WHERE prev.symbol IS NULL
        ),
        exited AS (
            SELECT prev.date, 'exited' AS change_type, prev.symbol
            FROM top100 prev
            LEFT JOIN top100 curr
              ON prev.symbol = curr.symbol
             AND curr.date = prev.date - INTERVAL 1 DAY
            WHERE curr.symbol IS NULL
        )
        SELECT * FROM entered
        UNION ALL
        SELECT * FROM exited
        ORDER BY date, change_type, symbol
    """, (start, end)).df()

    # Used AI to do this part, reading docs & figuring out would have been time consuming
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        index_df.to_excel(writer, index=False, sheet_name="Index Performance")
        composition_df.to_excel(writer, index=False, sheet_name="Daily Composition")
        changes_df.to_excel(writer, index=False, sheet_name="Composition Changes")

    output.seek(0)
    filename = f"index_export_{start}_{end}.xlsx"

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )