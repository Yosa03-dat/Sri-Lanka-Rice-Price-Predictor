<?php
namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;
use Illuminate\Routing\Controller;

class ForecastController extends Controller
{
    private $apiUrl = 'http://127.0.0.1:8005';

    /**
     * Main dashboard: fetch prediction + date status and render view.
     */
    public function getForecast()
    {
        $predictedPrice = null;
        $targetDate     = null;
        $dateStatus     = null;
        $error          = null;

        try {
            // 1. Fetch prediction
            $predResponse = Http::timeout(8)
                ->withBody('{}', 'application/json')
                ->post("{$this->apiUrl}/predict");

            if ($predResponse->successful()) {
                $data           = $predResponse->json();
                $predictedPrice = $data['predicted_price_lkr'] ?? null;
                $targetDate     = $data['target_date'] ?? null;
            } else {
                $error = 'Prediction engine returned an error: ' . $predResponse->body();
            }

            // 2. Fetch date status (controls sync button visibility)
            $statusResponse = Http::timeout(5)->get("{$this->apiUrl}/date-status");
            if ($statusResponse->successful()) {
                $dateStatus = $statusResponse->json();
            }
        } catch (\Exception $e) {
            $error = 'Unable to reach the predictive engine. Please ensure the backend is running.';
        }

        return view('forecast.index', compact('predictedPrice', 'targetDate', 'dateStatus'))
            ->with('apiError', $error);
    }

    /**
     * Sync next week's data and trigger retrain.
     */
    public function syncData(Request $request)
    {
        $inputs = $request->except('_token');

        // FastAPI needs {} not [] — use raw JSON body
        $rawJson = empty($inputs) ? '{}' : json_encode(['manual_inputs' => $inputs]);

        $syncResponse = Http::timeout(30)
            ->withBody($rawJson, 'application/json')
            ->post("{$this->apiUrl}/sync-weekly-data");

        if (!$syncResponse->successful()) {
            $detail = $syncResponse->json('detail') ?? $syncResponse->body();
            $msg    = is_string($detail) ? $detail : json_encode($detail);
            return back()->with('error', 'Data sync failed: ' . $msg);
        }

        // Trigger background retrain
        Http::timeout(5)->withBody('{}', 'application/json')->post("{$this->apiUrl}/retrain");

        $addedDate = $syncResponse->json('added_date') ?? 'new date';
        return redirect()->route('forecast.index')
            ->with('success', "Weekly data synced for {$addedDate} — model retraining started in the background.");
    }

    /**
     * Lookup historical rice price for a specific date.
     */
    public function lookupDate(Request $request)
    {
        $request->validate(['lookup_date' => 'required|date']);

        $date = $request->input('lookup_date');

        try {
            $response = Http::timeout(10)->get("{$this->apiUrl}/history/{$date}");

            if ($response->successful()) {
                $result = $response->json();
                return back()->with('lookupResult', $result);
            }

            $detail = $response->json('detail') ?? 'Unknown error';
            return back()->with('lookupError', is_string($detail) ? $detail : json_encode($detail));
        } catch (\Exception $e) {
            return back()->with('lookupError', 'Backend unreachable: ' . $e->getMessage());
        }
    }

    /**
     * Proxy the history chart data from FastAPI (avoids CORS issues).
     */
    public function getHistory(Request $request)
    {
        $days = (int) $request->query('days', 730);

        try {
            $response = Http::timeout(15)->get("{$this->apiUrl}/history?days={$days}");

            if ($response->successful()) {
                return response()->json($response->json());
            }

            return response()->json(['error' => 'History fetch failed'], 500);
        } catch (\Exception $e) {
            return response()->json(['error' => $e->getMessage()], 500);
        }
    }
}