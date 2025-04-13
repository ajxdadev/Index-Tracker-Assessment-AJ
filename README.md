Index Tracker Backend

This is a backend service to simulate a custom equal-weighted stock index, built on top of the top 100 US stocks (by daily market cap) of S&P 500 symbols.

It fetches, stores, and serves index-level and constituent-level data using FastAPI, Redis (for caching), and DuckDB (for persistent historical storage). The system is containerized using Docker.


Tech Stack
	•	Python + FastAPI – Web framework
	•	Redis – Caching layer
	•	DuckDB – Lightweight analytical DB for local storage
	•	yfinance – For fetching stock price & market cap
	•	Docker – Containerization

Guide To Run:

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