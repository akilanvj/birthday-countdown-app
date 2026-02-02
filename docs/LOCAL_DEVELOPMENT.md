# Local Development Setup

This guide helps you run the Birthday Countdown application locally for testing before deploying to Azure.

## Quick Start

### Option 1: Using the main entry point
```bash
python3 run_local.py
```

### Option 2: Using the shell script (macOS/Linux)
```bash
./scripts/start_local.sh
```

### Option 3: Using the batch file (Windows)
```cmd
scripts/start_local.bat
```

### Option 4: Using Python directly
```bash
python3 scripts/start_local.py
```

### Option 5: Direct server execution
```bash
python3 scripts/local_server.py
```

## Access the Application

- **Frontend**: http://localhost:8000
- **API**: http://localhost:8000/api/nextbirthday?dob=1990-05-15

## Test the Application

1. Open http://localhost:8000 in your browser
2. Enter your date of birth in the web interface
3. Click "Calculate Next Birthday"
4. View your birthday countdown results

## What's Running

The local server (`local_server.py`) provides:
- **Web Server**: Serves the frontend files (HTML, CSS, JS)
- **API Server**: Mimics the Azure Functions `/api/nextbirthday` endpoint
- **CORS Support**: Enables cross-origin requests for development

## Project Structure

```
birthday-countdown/
├── 📁 src/                    # Source code
│   ├── 📁 api/               # Azure Functions backend
│   │   ├── function_app.py   # Main Azure Functions app
│   │   ├── host.json         # Azure Functions configuration
│   │   ├── local.settings.json # Local development settings
│   │   └── requirements.txt  # Python dependencies
│   └── 📁 web/               # Frontend web application
│       ├── index.html        # Main HTML page
│       ├── app.js            # JavaScript application logic
│       └── styles.css        # CSS styling
├── 📁 scripts/               # Development and utility scripts
│   ├── local_server.py       # Local development server
│   ├── start_local.py        # Python startup script
│   ├── start_local.sh        # Shell script (macOS/Linux)
│   └── start_local.bat       # Batch script (Windows)
├── 📁 tests/                 # Test suites
├── 📁 docs/                  # Documentation
├── 📁 config/                # Configuration files
├── 📁 deploy/                # Deployment configurations
├── run_local.py              # Main entry point
└── README.md                 # Project documentation
```

## API Testing

You can test the API directly:

**Valid Request:**
```bash
curl "http://localhost:8000/api/nextbirthday?dob=1990-05-15"
```

**Response:**
```json
{
  "inputDob": "1990-05-15",
  "ageYears": 35,
  "nextBirthdayDate": "2026-05-15",
  "nextBirthdayDayOfWeek": "Friday",
  "daysUntilNextBirthday": 102,
  "message": "📅 Your birthday is in 102 days. Plenty of time to prepare!"
}
```

## Error Testing

**Missing parameter:**
```bash
curl "http://localhost:8000/api/nextbirthday"
```

**Invalid date format:**
```bash
curl "http://localhost:8000/api/nextbirthday?dob=invalid"
```

**Future date:**
```bash
curl "http://localhost:8000/api/nextbirthday?dob=2030-01-01"
```

## Features Tested Locally

- ✅ Birthday calculation logic
- ✅ Age calculation in complete years
- ✅ Next birthday date calculation
- ✅ Days until next birthday
- ✅ Day of week calculation
- ✅ Leap year handling (Feb 29 birthdays)
- ✅ Input validation (format, future dates)
- ✅ Error handling and messages
- ✅ CORS support
- ✅ Frontend-backend integration

## Differences from Azure Functions

The local server mimics Azure Functions behavior but:
- Uses Python's built-in HTTP server instead of Azure Functions runtime
- Serves static files directly (Azure would use Static Web Apps or Storage)
- Uses port 8000 instead of 7071 (Azure Functions default)
- Simplified logging (no Azure Application Insights)

## Next Steps

Once you've tested locally and everything works:

1. **Deploy to Azure Functions** using the original `function_app.py`
2. **Deploy frontend** to Azure Static Web Apps or Azure Storage
3. **Update API URL** in `frontend/app.js` to point to your Azure Functions URL
4. **Configure CORS** in Azure Functions for your frontend domain

## Troubleshooting

**Port already in use:**
```bash
# Kill process using port 8000
lsof -ti:8000 | xargs kill -9
```

**Permission denied:**
```bash
# Make scripts executable
chmod +x start_local.py local_server.py
```

**Module not found:**
```bash
# Make sure you're in the project root directory
ls -la  # Should see frontend/ folder and local_server.py
```