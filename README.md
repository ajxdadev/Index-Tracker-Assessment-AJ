Index Tracker Backend

This is a backend service to simulate a custom equal-weighted stock index, built on top of the daily top 100 US stocks (by daily market cap) of S&P 500 symbols.

It fetches, stores, and serves index-level and constituent-level data using FastAPI, Redis (for caching), and DuckDB (for persistent historical storage). The system is containerized using Docker.

Features:
    •	Custom Index Calculation for Equal-weighted daily index using top 100 S&P stocks by market cap ( dynamic rebalncing )
    •	Use IVV ETF holdings as the golden source for S&P constituents & yfinance API to fetch daily market data.
    •	Query-level caching for all main endpoints using redis cache. 


Tech Stack
	•	Python + FastAPI – Web framework
	•	Redis – Caching layer
	•	DuckDB – Lightweight analytical DB for local storage
	•	yfinance – For fetching stock price & market cap
	•	Docker – Containerization

Running:
    1. Clone the repo  
        git clone <url to repo>
        cd index-tracker-assessment-aj
    2. Build & Run via Docker
        docker-compose -f docker/docker-compose.yml up --build
        Note:   Run the app on localhost:8000
		        Redis on port 6379
    3. To Run locally
        Install deps using pip install -r requirements.txt

API Endpoints:
    1. GET /indexservices/composition?date=YYYY-MM-DD
    2. GET /indexservices/composition-changes?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD
    3. GET /indexservices/performance?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD
    4. POST /exportservices/export-data

    To Test APIs, try endpoints in Swagger UI here: http://localhost:8000/docs

GenAI Usage:
    Aim was to use GenAI to solve time consuming/repetitive & non-core tasks, few of the examples where I leveraged GenAI in this project.
    •	Rewriting SQL for DuckDB’s syntax (e.g., date arithmetic)
    •	Drafting Excel export logic with pandas + xlsxwriter
    •	Get validations on my logics to calc index value. Possible edge cases etc
    •	Help debug docker setup issues 

To-Do (Future Improvements)
	•	Add better error handling for multiple services used in the prject eg:yfinance API calls. Fallback logic would be preferrable
	•	Clean up and isolate caching logic from DB logic. Enhance on eviction policies for redis.
	•	Authentication layer to control API access
	•	Automated jobs for background ingestion
    •	Structure project to allow for easy scaling adaptation. Eg: Scale for multiple custom index tracking, eg: top 50, top 100, top 200. In such case hardcoding can be replaced by reading from Configs.


