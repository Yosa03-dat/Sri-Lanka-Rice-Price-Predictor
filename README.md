# Sri Lankan Rice Price Forecasting Engine

This repository contains the Final Capstone Project for Data Science II. It is an automated ingestion, retraining, and inference system for agricultural commodity forecasting, specifically targeting rice prices in Sri Lanka.

## Project Structure

- **Literature Review**: Academic research and literature review documents.
- **Raw_data** & **Preprocessed_data**: Datasets used for modeling and analysis.
- **Project_File**: Core project code.
  - **app.py**: FastAPI backend server.
  - **ingestion.py**: Script for automated data collection.
  - **Data_Preprocessing**: Scripts and notebooks for data cleaning and prep.
  - **Web_Scraping_and_Data_Collection**: Scraping scripts.
  - **Frontend/Rice_Price_Prediction**: Laravel + Vite frontend application.
  - **Jupyter Notebooks**: Exploratory Data Analysis and time series modeling (`feature_target_exploration.ipynb`, `Real_Price_Forecasting.ipynb`, `Time_Series_Modelling.ipynb`).

## Setup and Running

### Backend (FastAPI)
1. Navigate to the `Project_File` directory.
2. Install Python dependencies (ensure you are using a virtual environment).
3. Run the server:
   ```bash
   python app.py
   ```
   The API will be available at `http://127.0.0.1:8005`. You can view the API documentation at `http://127.0.0.1:8005/docs`.

### Frontend (Laravel + Vite)
1. Navigate to `Project_File/Frontend/Rice_Price_Prediction`.
2. Install PHP dependencies using Composer and JS dependencies using NPM:
   ```bash
   composer install
   npm install
   ```
3. Copy the `.env.example` file to `.env` and configure your environment variables.
4. Run the frontend server:
   ```bash
   php artisan serve
   ```
   This will start the PHP server at `http://127.0.0.1:8000`.
5. In a separate terminal, run Vite for asset compilation:
   ```bash
   npm run dev
   ```

## Architecture
The system utilizes an XGBoost regressor model, continuously trained on newly ingested data to predict rice prices based on historical trends and macroeconomic factors.
