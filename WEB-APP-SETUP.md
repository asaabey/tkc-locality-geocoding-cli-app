# CHC Geocoding Web App - Complete Setup Guide

## 🚀 Quick Start

### Option 1: Full Stack (Recommended)
```bash
./start-dev.sh
```
This starts both backend and frontend servers automatically.

### Option 2: Individual Services

**Backend Only:**
```bash
./start-backend.sh
```

**Frontend Only:**
```bash
./start-frontend.sh
```

### Option 3: Manual Setup (Two Terminals)

**Terminal 1 - Backend:**
```bash
uv run uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install  # First time only
npm run dev
```

## 🌐 Access Points

Once both servers are running:
- **Web Interface**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (Interactive Swagger UI)
- **Health Check**: http://localhost:8000/api/health

## ⚙️ System Requirements

### Backend Dependencies
- **Python**: 3.10+
- **Package Manager**: [uv](https://docs.astral.sh/uv/)
- **Python Packages**: FastAPI, uvicorn, pandas, geopandas, etc. (auto-installed)

### Frontend Dependencies  
- **Node.js**: 18+
- **Package Manager**: npm/yarn
- **Frameworks**: React 19 + TypeScript + Vite + TailwindCSS

## 🔧 Installation

### Initial Setup
```bash
# Install Python dependencies
uv pip install -e ".[dev]"

# Install frontend dependencies (if not done automatically)
cd frontend && npm install && cd ..
```

## 📡 API Endpoints

### Available Routes:
- `POST /api/geocode/single` - Geocode a single location
- `POST /api/geocode/batch` - Geocode multiple locations
- `GET /api/health` - System health check

### Request/Response Examples:

**Single Location:**
```json
POST /api/geocode/single
{
  "location": "Alice Springs Hospital, NT"
}
```

**Batch Locations:**
```json  
POST /api/geocode/batch
{
  "locations": ["Darwin Hospital, NT", "Katherine Hospital, NT"]
}
```

## 🗺️ Features Supported

### Geocoding
- **Service**: Nominatim (OpenStreetMap)
- **Rate Limiting**: 1 request/second (respects ToS)
- **Retry Logic**: Automatic retries with exponential backoff
- **Error Handling**: Graceful failure handling

### ABS Statistical Classifications
- **SA1-SA4**: Statistical Areas (all levels)
- **GCCSA**: Greater Capital City Statistical Areas
- **STE**: State and Territory boundaries
- **IARE**: Indigenous Areas (NEW - with Indigenous Regions)

### Output Columns
Each geocoded location returns:
```
- location: Original input
- latitude/longitude: Coordinates
- sa1_code, sa2_code/name, sa3_name, sa4_name: Statistical areas
- gccsa_name: Capital city areas  
- state_name: State/Territory
- iare_code/name: Indigenous Area
- ireg_code/name: Indigenous Region (parent of IARE)
- geocode_success: Success flag
- error_message: Error details if failed
```

## 🛠️ Development Features

### Backend (FastAPI)
- **Hot Reload**: Automatic restart on code changes
- **CORS**: Configured for frontend communication  
- **Documentation**: Auto-generated OpenAPI/Swagger docs
- **Logging**: Comprehensive request/error logging
- **Type Safety**: Full Pydantic model validation

### Frontend (React)
- **Hot Reload**: Instant updates during development
- **TypeScript**: Full type safety
- **Modern UI**: TailwindCSS with custom components
- **API Integration**: Axios with TanStack Query
- **Error Handling**: User-friendly error messages

## 🔍 Health Monitoring

### Backend Health Check
Visit: http://localhost:8000/api/health

Returns:
```json
{
  "status": "healthy",
  "version": "1.0.0", 
  "asgs_files_available": true,
  "nominatim_accessible": true
}
```

### Frontend Status
- Build status: ✅ TypeScript compilation successful
- Dependencies: ✅ All packages installed  
- API connectivity: ✅ Configured for http://localhost:8000

## 📁 File Structure

```
├── backend/              # FastAPI backend
│   ├── main.py          # Server entry point
│   ├── routers/         # API endpoints
│   ├── services/        # Business logic
│   └── models/          # Pydantic models
├── frontend/            # React frontend  
│   ├── src/
│   │   ├── components/  # UI components
│   │   ├── lib/         # API client & utils
│   │   └── types/       # TypeScript types
│   └── package.json
├── src/                 # Core CHC logic
│   ├── geocode.py      # Geocoding functions  
│   ├── classify.py     # IARE classification
│   └── settings.py     # Configuration
├── start-dev.sh        # Full stack startup
├── start-backend.sh    # Backend only  
└── start-frontend.sh   # Frontend only
```

## 🐛 Troubleshooting

### Backend Issues
- **ModuleNotFoundError**: Run from project root directory
- **Port 8000 in use**: Kill process with `pkill -f uvicorn`
- **Missing ASGS files**: Download to `data/asgs/` directory

### Frontend Issues  
- **Port 5173 in use**: Vite auto-selects next available port
- **Module errors**: Run `npm install` in frontend directory
- **API connection**: Check backend is running on port 8000

### Dependencies
- **uv not found**: Install from https://docs.astral.sh/uv/
- **Node.js issues**: Ensure Node 18+ is installed

## 🎯 Next Steps

1. **Start the servers** using one of the methods above
2. **Open web interface** at http://localhost:5173  
3. **Test with sample data** - try "Darwin Hospital, NT"
4. **Explore API docs** at http://localhost:8000/docs
5. **Check health status** at http://localhost:8000/api/health

The web application provides the same powerful geocoding and IARE classification capabilities as the CLI tool, but with a modern, user-friendly interface! 🎉