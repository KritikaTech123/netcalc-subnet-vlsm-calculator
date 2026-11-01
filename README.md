# NetCalc

## IPv4 Subnetting and VLSM Calculator

NetCalc is a modern, beginner-friendly web application for learning and practicing IPv4 subnetting. It calculates detailed subnet information, designs efficient VLSM address plans, visualizes allocations, and stores previous calculations for later review.

Built as a Computer Networks academic project with a React frontend, Flask REST API, and SQLite database.

---

## Live Demo

Deploy the project on Render with the included [`render.yaml`](./render.yaml) blueprint. After deployment, add the generated frontend URL here:

```text
Live application: https://your-netcalc-frontend.onrender.com
```

The frontend uses the deployed Flask API automatically through the `VITE_API_URL` environment variable.

### Deploy on Render

1. Sign in at [render.com](https://render.com).
2. Select **New → Blueprint**.
3. Connect this GitHub repository.
4. Choose the `main` branch.
5. Apply the blueprint from `render.yaml`.
6. Open the `netcalc-frontend` service URL.
7. Replace the placeholder URL above with the generated live link.

The free Render plan may sleep after inactivity, so the first request can take a few seconds.

---

## Features

### IPv4 Subnet Calculator

- Accepts an IPv4 address, CIDR prefix, and optional subnet mask
- Calculates:
  - Network address
  - Broadcast address
  - Subnet mask
  - CIDR notation
  - First and last usable addresses
  - Total IP addresses
  - Usable host addresses
  - Wildcard mask
  - IP address class
  - Network and host bit counts
- Validates invalid addresses, prefixes, and mismatched masks
- Handles `/31` and `/32` networks correctly

### VLSM Calculator

- Accepts a parent network and multiple departments
- Sorts host requirements from largest to smallest
- Automatically selects the smallest suitable subnet for each department
- Displays:
  - Allocated network
  - CIDR prefix
  - Subnet mask
  - Broadcast address
  - Usable IP range
  - Usable host capacity
- Prevents allocations from overlapping or exceeding the parent network
- Shows allocated and unused address space visually

### Dashboard

- Summary statistics
- Quick access to all major tools
- Recent calculation activity
- Networking concepts at a glance

### Calculation History

- Stores successful calculations in SQLite
- Shows calculation type, input, result, and timestamp
- Deletes individual records
- Clears the complete history

### Learning Section

Simple explanations of:

- IPv4
- IP addresses
- Subnetting
- Subnet masks
- CIDR notation
- Network and broadcast addresses
- VLSM
- FLSM vs VLSM
- Usable host addresses

---

## Technology Stack

### Frontend

- React.js
- Vite
- JavaScript
- CSS3
- Lucide React icons
- Responsive dashboard layout

### Backend

- Python
- Flask
- Flask-CORS
- REST API
- Python `ipaddress` module

### Database

- SQLite
- JSON input and output storage

---

## Project Architecture

```text
netcalc-subnet-vlsm-calculator/
├── backend/
│   ├── app.py              # Flask application and REST endpoints
│   ├── calculations.py     # IPv4 and VLSM calculation logic
│   └── requirements.txt    # Python dependencies
├── database/
│   └── .gitkeep            # SQLite database is created here at runtime
├── frontend/
│   ├── src/
│   │   ├── main.jsx        # React pages and reusable components
│   │   └── styles.css      # Dashboard styling and responsive layout
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
├── .gitignore
└── README.md
```

---

## How It Works

1. The user enters an IPv4 address or network requirement in the React interface.
2. The frontend sends the data to the Flask REST API.
3. Flask validates the request and calls the reusable functions in `calculations.py`.
4. Python's `ipaddress` module calculates reliable network boundaries.
5. The result is returned to the frontend and displayed in cards, tables, and diagrams.
6. Successful calculations are saved to SQLite as JSON input and output records.

For VLSM, NetCalc:

1. Sorts departments by required host count.
2. Adds network and broadcast address space to each host requirement.
3. Rounds the requirement to the next valid power-of-two block size.
4. Allocates aligned blocks sequentially inside the parent network.
5. Rejects any allocation that would overlap or exceed the parent network.

---

## Installation and Setup

### Prerequisites

- Python 3.10 or later
- Node.js 18 or later
- npm

### 1. Clone the repository

```powershell
git clone https://github.com/KritikaTech123/netcalc-subnet-vlsm-calculator.git
cd netcalc-subnet-vlsm-calculator
```

### 2. Start the Flask backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

The backend runs at:

```text
http://localhost:5000
```

### 3. Start the React frontend

Open a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the application at:

```text
http://localhost:5173
```

The SQLite database is created automatically at `database/netcalc.db` when the backend starts saving calculations.

---

## REST API

### Health Check

```http
GET /api/health
```

### Subnet Calculation

```http
POST /api/calculate/subnet
Content-Type: application/json
```

Request:

```json
{
  "address": "192.168.1.42",
  "prefix": 24,
  "mask": ""
}
```

### VLSM Calculation

```http
POST /api/calculate/vlsm
Content-Type: application/json
```

Request:

```json
{
  "network": "192.168.1.0/24",
  "departments": [
    { "name": "HR", "hosts": 50 },
    { "name": "IT", "hosts": 25 },
    { "name": "Marketing", "hosts": 10 },
    { "name": "Finance", "hosts": 5 }
  ]
}
```

### History

```http
GET    /api/history
DELETE /api/history
DELETE /api/history/<id>
```

---

## Sample Results

### Subnet Example

Input:

```text
Address: 192.168.1.42
CIDR: /24
```

Output:

```text
Network address:     192.168.1.0
Broadcast address:   192.168.1.255
Subnet mask:         255.255.255.0
First usable IP:     192.168.1.1
Last usable IP:      192.168.1.254
Total addresses:     256
Usable hosts:        254
```

### VLSM Example

Parent network:

```text
192.168.1.0/24
```

| Department | Required Hosts | Allocated Block |
|---|---:|---|
| HR | 50 | `192.168.1.0/26` |
| IT | 25 | `192.168.1.64/27` |
| Marketing | 10 | `192.168.1.96/28` |
| Finance | 5 | `192.168.1.112/29` |

The remaining addresses are reported as unused space.

---

## Testing

Run the backend calculation checks:

```powershell
python -c "from backend.calculations import subnet_calculation, vlsm_calculation; print(subnet_calculation('192.168.1.42', 24)); print(vlsm_calculation('192.168.1.0/24', [{'name':'HR','hosts':50}]))"
```

Build the frontend for production:

```powershell
cd frontend
npm run build
```

---

## Academic Project Objective

The objective of NetCalc is to provide an interactive way to understand IPv4 addressing, subnetting, and Variable Length Subnet Masking. Instead of relying only on manual calculations, students can enter real network requirements and immediately see how addresses, masks, host ranges, and broadcast boundaries are determined.

### Project Scope

- IPv4 subnet analysis
- VLSM network planning
- Address validation
- Allocation visualization
- Persistent calculation history
- Educational networking content

### Future Improvements

- User authentication
- Export allocation plans as PDF or CSV
- IPv6 calculator
- Network utilization charts
- Automated deployment and hosted demo

---

## Viva Explanation

The frontend is responsible for collecting input and presenting results. It communicates with Flask through REST API requests. The backend validates the data and keeps the networking logic separate in `calculations.py`, which makes the code easier to test and explain. SQLite stores each calculation's type, input, output, and timestamp. The VLSM algorithm sorts departments by size and allocates properly aligned blocks from the parent network, ensuring that no subnets overlap.

---

## License

This project was created for educational and academic use.
