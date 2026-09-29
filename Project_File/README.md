# Sri Lanka Rice Price Predictor

This project is a comprehensive Data Science and Web Application solution for forecasting rice prices in Sri Lanka. It features automated web scraping for live data, time series forecasting using XGBoost, a backend powered by FastAPI, and a frontend user interface built with Laravel.

## Project Structure

- `app.py`: FastAPI backend application serving predictions, data synchronization, and historical data.
- `ingestion.py`: Script for fetching live data (e.g., exchange rates) and preprocessing it for the model.
- `Data_Preprocessing/`: Contains data preprocessing scripts and paths.
- `Web_Scraping_and_Data_Collection/`: Scripts for web scraping historical and live data.
- `Frontend/Rice_Price_Prediction/`: The Laravel-based frontend application.
- `*.ipynb`: Jupyter notebooks for exploratory data analysis (EDA) and model training (`Real_Price_Forecasting.ipynb`, `Time_Series_Modelling.ipynb`, `feature_target_exploration.ipynb`).

## Requirements

### Backend (Python)
- Python 3.8+
- FastAPI
- Uvicorn
- XGBoost
- Pandas
- NumPy
- BeautifulSoup4
- Requests
- Pydantic

Install the Python dependencies via:
```bash
pip install -r requirements.txt
```

### Frontend (PHP/Laravel)
- PHP 8.1+
- Composer
- Node.js & NPM

## Setup and Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd Project_File
   ```

2. **Backend Setup:**
   Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   Start the FastAPI server:
   ```bash
   uvicorn app:app --host 127.0.0.1 --port 8005
   ```

3. **Frontend Setup:**
   Navigate to the frontend directory:
   ```bash
   cd Frontend/Rice_Price_Prediction
   ```
   Install PHP dependencies:
   ```bash
   composer install
   ```
   Install NPM dependencies:
   ```bash
   npm install
   npm run dev
   ```
   Copy the example environment file and generate an application key:
   ```bash
   cp .env.example .env
   php artisan key:generate
   ```
   Start the Laravel development server:
   ```bash
   php artisan serve
   ```

## API Endpoints

- `GET /` - Check API status.
- `GET /health` - Health check and model loaded status.
- `GET /latest-date` - Fetch the latest date available in the dataset.
- `POST /sync-weekly-data` - Fetch and sync the latest weekly data.
- `POST /retrain` - Trigger background model retraining.
- `POST /predict` - Predict the rice price for the next week.
- `GET /date-status` - Retrieve the synchronization status.
- `GET /history` - Fetch historical price charts.
- `GET /history/{query_date}` - Fetch historical data for a specific date.

## License
MIT License
