from fastapi import APIRouter, Query
from typing import Optional
from datetime import datetime
from app.DB.duckdb_connection import get_connection
from app.cache.redis_cache import get_cache, set_cache

router = APIRouter()

#index/performance API
@router.get("/performance")
def get_index_performance(
    start_date: str = Query(..., description="Start date YYYY-MM-DD"),
    end_date: str = Query(..., description="End date YYYY-MM-DD")
):
    try:
        # Basic error handling around dates. 
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        return {"error": "Invalid date format. Use YYYY-MM-DD."}

    if start > end:
        return {"error": "start_date must be earlier than end_date."}

    cache_key = f"index_performance:{start_date}:{end_date}"
    cached = get_cache(cache_key)
    if cached:
        print("Returning result from redis cache!!")
        return cached

    conn = get_connection()
    query = f"""
        SELECT date, index_value
        FROM custom_index_history
        WHERE date BETWEEN '{start}' AND '{end}'
        ORDER BY date
    """
    rows = conn.execute(query).fetchall()
    conn.close()

    values = [{"date": str(row[0]), "index_value": row[1]} for row in rows]

    if len(values) < 2:
        return {
            "start_date": str(start),
            "end_date": str(end),
            "message": "Not enough data to calculate performance change.",
            "values": values
        }

    index_start = values[0]["index_value"]
    index_end = values[-1]["index_value"]
    percent_change = ((index_end - index_start) / index_start) * 100
    direction = "grew" if percent_change >= 0 else "declined"

    response = {
        "start_date": str(start),
        "end_date": str(end),
        "performance_change": f"{percent_change:.2f}%",
        "message": f"Index {direction} by {abs(percent_change):.2f}% between {start} and {end}.",
        "values": values
    }
    set_cache(cache_key, response)
    return response

@router.get("/composition")
def get_index_composition(
    date: str = Query(..., description="Date in YYYY-MM-DD format")
):
    try:
        day = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        return {"error": "Invalid date format. Use YYYY-MM-DD."}

    #check if exist in redis cache, if yes return from cache
    cache_key = f"index_composition:{date}"
    cached = get_cache(cache_key)
    if cached:
        print("Returning result from redis cache!!")
        return cached
    
    conn = get_connection()

    # Data exist check
    result = conn.execute(
        f"SELECT COUNT(*) FROM daily_price_data WHERE date = '{day}'"
    ).fetchone()
    if result[0] == 0:
        conn.close()
        return {"error": f"No data found for {day}"}

    top_100 = conn.execute(f"""
        SELECT symbol
        FROM daily_price_data
        WHERE date = '{day}' AND market_cap IS NOT NULL
        ORDER BY market_cap DESC
        LIMIT 100
    """).fetchall()

    constituents = [{"symbol": row[0], "weight": "1.00%"} for row in top_100]

    conn.close()
    response = {
        "date": str(day),
        "constituents": constituents
    }
    set_cache(cache_key, response)
    return response

@router.get("/composition-changes")
def get_composition_changes(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)")
):
    from datetime import datetime, timedelta

    try:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        return {"error": "Invalid date format. Use YYYY-MM-DD"}

    if start >= end:
        return {"error": "start_date must be before end_date"}

    #check if exist in redis cache, if yes return from cache
    cache_key = f"composition_changes:{start}:{end}"
    cached = get_cache(cache_key)
    if cached:
        print("Returning result from redis cache!!")
        return cached
    
    conn = get_connection()
    dates = conn.execute("""
        SELECT DISTINCT date
        FROM daily_price_data
        WHERE date BETWEEN ? AND ?
        ORDER BY date
    """, (start, end)).fetchall()

    dates = [d[0] for d in dates]
    changes = []

    prev_day_set = set()

    for i in range(1, len(dates)):
        day_prev = dates[i - 1]
        day_curr = dates[i]

        top_prev = conn.execute(f"""
            SELECT symbol FROM daily_price_data
            WHERE date = '{day_prev}' AND market_cap IS NOT NULL
            ORDER BY market_cap DESC LIMIT 100
        """).fetchall()

        top_curr = conn.execute(f"""
            SELECT symbol FROM daily_price_data
            WHERE date = '{day_curr}' AND market_cap IS NOT NULL
            ORDER BY market_cap DESC LIMIT 100
        """).fetchall()

        set_prev = set(row[0] for row in top_prev)
        set_curr = set(row[0] for row in top_curr)

        added = sorted(set_curr - set_prev)
        removed = sorted(set_prev - set_curr)

        if added or removed:
            changes.append({
                "date": str(day_curr),
                "added": added,
                "removed": removed
            })

    conn.close()
    response = {"changes": changes}
    set_cache(cache_key,response)
    return response