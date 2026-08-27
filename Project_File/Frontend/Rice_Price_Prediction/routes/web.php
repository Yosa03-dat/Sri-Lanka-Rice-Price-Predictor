<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\ForecastController;

// Main dashboard — prediction + chart + status
Route::get('/', [ForecastController::class, 'getForecast'])->name('forecast.index');
Route::get('/forecast', [ForecastController::class, 'getForecast']);

// Sync data & retrain model
Route::post('/forecast/sync', [ForecastController::class, 'syncData'])->name('forecast.sync');

// Date lookup — retrieve historical rice price for a given date
Route::post('/forecast/lookup', [ForecastController::class, 'lookupDate'])->name('forecast.lookup');

// History chart data (JSON, called by JS on page load)
Route::get('/api/history', [ForecastController::class, 'getHistory'])->name('forecast.history');
