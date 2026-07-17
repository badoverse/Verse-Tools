# VerseTools

## Requirements

### Frontend
- Node.js (includes npm)
- npm package manager

Check installation:
```bash
node --version
npm --version
```

### Backend
- Python 3.10+
- pip package manager

Check installation:
```bash
python --version
pip --version
```

## Technologies Used
- Python
- FastAPI
- Uvicorn
- Node.js
- npm
- Vue.js
- Vite
- Axios

## Backend Setup (./backend)

Backend Python packages required:
- fastapi
- uvicorn[standard]

### Steps

4. Install dependencies:
   ```bash
   pip install fastapi "uvicorn[standard]" 
   ```

5. Start FastAPI:
   ```bash
   python -m uvicorn main:app --reload
   ```

The backend will run on: **http://127.0.0.1:8000**

## Frontend Setup (./frontend)

Frontend packages are installed automatically from `package.json`.

### Steps

1. Open another terminal in `VerseTools/frontend`

2. Install dependencies:
   ```bash
   npm install
   npm install vue-router@4   
   ```

3. Start the Vue development server:
   ```bash
   npm run dev
   ```

The frontend will run on: **http://localhost:5173**

## Running the Project

Both servers must be running at the same time, in separate terminals:

**Backend:**
```bash
python -m uvicorn main:app --reload
```

**Frontend:**
```bash
npm run dev
```
