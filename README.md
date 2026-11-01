# NetCalc – IPv4 Subnetting and VLSM Calculator

Beginner-friendly full-stack Computer Networks project using React, Flask, SQLite, and Python's `ipaddress` module.

## Run locally

### Backend
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

### Frontend
```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The Flask API runs at `http://localhost:5000`.

## API
- `POST /api/calculate/subnet` with `{ "address": "192.168.1.42", "prefix": 24 }`
- `POST /api/calculate/vlsm` with `{ "network": "192.168.1.0/24", "departments": [{"name":"HR","hosts":50}] }`
- `GET /api/history`, `DELETE /api/history`, `DELETE /api/history/:id`

## Demo examples
For `192.168.1.42/24`: network `192.168.1.0`, broadcast `192.168.1.255`, usable range `192.168.1.1–192.168.1.254`, and 254 usable hosts.

For `192.168.1.0/24` with HR 50, IT 25, Marketing 10, Finance 5, VLSM allocates `/26`, `/27`, `/28`, and `/29` blocks in descending host order.

## Viva explanation
The frontend collects inputs and calls REST endpoints. Flask validates input and delegates networking rules to `calculations.py`. SQLite stores both JSON input and output so the history page can reproduce previous results. VLSM sorts requirements, rounds each block to the smallest power-of-two address range, and advances a cursor through the parent network to guarantee no overlap.
