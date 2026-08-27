<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Sri Lankan Rice Price Forecasting Engine — AI-powered weekly retail price predictions using macroeconomic, weather, and supply chain data.">
    <title>🌾 Rice Price Forecast — Sri Lanka</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.2/dist/chart.umd.min.js"></script>
    <style>
        :root {
            --gold:        hsl(42,95%,55%);
            --gold-dim:    hsl(42,60%,38%);
            --emerald:     hsl(158,64%,42%);
            --emerald-glow:hsl(158,64%,55%);
            --sapphire:    hsl(213,89%,58%);
            --rose:        hsl(350,80%,60%);
            --bg-deep:     hsl(222,28%,8%);
            --bg-mid:      hsl(222,24%,11%);
            --bg-card:     hsl(222,20%,15%);
            --bg-card2:    hsl(222,18%,18%);
            --border:      hsl(222,18%,22%);
            --border-lite: hsl(222,15%,28%);
            --text-1:      hsl(210,25%,96%);
            --text-2:      hsl(210,15%,70%);
            --text-3:      hsl(210,10%,46%);
        }
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            font-family: 'Inter', system-ui, sans-serif;
            background: var(--bg-deep);
            color: var(--text-1);
            min-height: 100vh;
            overflow-x: hidden;
        }
        body::before {
            content: '';
            position: fixed; inset: 0;
            background:
                radial-gradient(ellipse 80% 60% at 15% 5%,  hsl(42 60% 20%/.18) 0%, transparent 60%),
                radial-gradient(ellipse 60% 50% at 85% 95%, hsl(158 60% 15%/.16) 0%, transparent 60%),
                radial-gradient(ellipse 50% 40% at 50% 50%, hsl(213 60% 15%/.10) 0%, transparent 70%);
            pointer-events: none; z-index: 0;
        }
        .wrap { position: relative; z-index: 1; min-height: 100vh; display: flex; flex-direction: column; }

        /* ─── Header ─── */
        header {
            padding: 1.25rem 2rem;
            display: flex; align-items: center; justify-content: space-between;
            border-bottom: 1px solid var(--border);
            backdrop-filter: blur(14px);
            background: hsl(222 28% 8%/.8);
            position: sticky; top: 0; z-index: 20;
        }
        .logo { display: flex; align-items: center; gap: .7rem; }
        .logo-icon { font-size: 1.6rem; filter: drop-shadow(0 0 8px hsl(42 95% 55%/.6)); }
        .logo-title { font-size: .95rem; font-weight: 700; }
        .logo-sub { font-size: .68rem; color: var(--text-3); text-transform: uppercase; letter-spacing: .05em; }
        .badge-live {
            display: flex; align-items: center; gap: .4rem;
            background: hsl(158 64% 42%/.15); border: 1px solid hsl(158 64% 42%/.35);
            color: var(--emerald-glow); font-size: .7rem; font-weight: 600;
            padding: .28rem .7rem; border-radius: 999px; letter-spacing: .05em; text-transform: uppercase;
        }
        .badge-live::before {
            content: ''; width: 7px; height: 7px; border-radius: 50%;
            background: var(--emerald-glow); animation: pulse 2s infinite;
        }
        @keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.4;transform:scale(.75)} }

        /* ─── Main ─── */
        main { flex: 1; padding: 2rem 2rem 4rem; max-width: 1160px; margin: 0 auto; width: 100%; }

        /* ─── Alerts ─── */
        .alert {
            display: flex; align-items: flex-start; gap: .75rem;
            padding: .9rem 1.2rem; border-radius: 12px; margin-bottom: 1.25rem;
            font-size: .85rem; font-weight: 500; animation: slideIn .3s ease;
        }
        @keyframes slideIn { from{opacity:0;transform:translateY(-10px)} to{opacity:1;transform:translateY(0)} }
        .alert-success { background: hsl(142 71% 45%/.12); border: 1px solid hsl(142 71% 45%/.3); color: hsl(142,60%,65%); }
        .alert-danger  { background: hsl(4 86% 58%/.12);  border: 1px solid hsl(4 86% 58%/.3);  color: hsl(4,86%,72%); }
        .alert-warning { background: hsl(42 95% 55%/.12); border: 1px solid hsl(42 95% 55%/.3); color: hsl(42,90%,65%); }
        .alert-info    { background: hsl(213 89% 58%/.12);border: 1px solid hsl(213 89% 58%/.3);color: hsl(213,80%,72%); }

        /* ─── Top row: hero + status ─── */
        .top-row { display: grid; grid-template-columns: 1fr 340px; gap: 1.25rem; margin-bottom: 1.25rem; }

        /* ─── Hero card ─── */
        .hero-card {
            background: linear-gradient(135deg, hsl(222 22% 13%) 0%, hsl(222 20% 16%) 50%, hsl(42 22% 11%) 100%);
            border: 1px solid var(--border); border-radius: 22px; padding: 2.5rem 3rem;
            position: relative; overflow: hidden;
        }
        .hero-card::after {
            content: '🌾'; position: absolute; right: 2rem; top: 50%; transform: translateY(-50%);
            font-size: 8rem; opacity: .05; pointer-events: none; line-height: 1;
        }
        .hero-eyebrow {
            font-size: .7rem; font-weight: 600; color: var(--gold); text-transform: uppercase;
            letter-spacing: .12em; margin-bottom: .6rem; display: flex; align-items: center; gap: .5rem;
        }
        .hero-eyebrow::before { content: ''; display: inline-block; width: 16px; height: 2px; background: var(--gold); border-radius: 2px; }
        .hero-label { font-size: .9rem; color: var(--text-2); margin-bottom: .3rem; }
        .hero-date  { font-size: 1.25rem; font-weight: 700; color: var(--text-1); margin-bottom: 1.75rem; }
        .price-display { display: flex; align-items: baseline; gap: .35rem; animation: fadeUp .6s ease .1s both; }
        @keyframes fadeUp { from{opacity:0;transform:translateY(16px)} to{opacity:1;transform:translateY(0)} }
        .price-rs    { font-size: 1.8rem; font-weight: 700; color: var(--gold); line-height: 1; }
        .price-val   { font-size: 4rem; font-weight: 900; line-height: 1; letter-spacing: -.04em; text-shadow: 0 0 40px hsl(42 95% 55%/.3); }
        .price-unit  { font-size: .9rem; color: var(--text-3); font-weight: 500; margin-left: .2rem; }
        .price-na    { font-size: 2.5rem; font-weight: 700; color: var(--text-3); }
        .price-hint  { font-size: .8rem; color: var(--text-3); margin-top: .6rem; line-height: 1.5; }

        /* ─── Status / Sync card ─── */
        .status-card {
            background: var(--bg-card); border: 1px solid var(--border); border-radius: 22px;
            padding: 1.75rem; display: flex; flex-direction: column; gap: 1.1rem;
        }
        .status-title { font-size: .78rem; font-weight: 600; text-transform: uppercase; letter-spacing: .08em; color: var(--text-3); }
        .status-rows  { display: flex; flex-direction: column; gap: .6rem; }
        .status-row   { display: flex; justify-content: space-between; align-items: center; font-size: .82rem; }
        .status-key   { color: var(--text-3); }
        .status-val   { font-weight: 600; color: var(--text-1); }
        .status-val.ok   { color: var(--emerald-glow); }
        .status-val.warn { color: hsl(42,90%,65%); }
        .status-val.bad  { color: hsl(4,86%,65%); }
        .divider { border: none; border-top: 1px solid var(--border); margin: 0; }

        .btn { display: inline-flex; align-items: center; justify-content: center; gap: .55rem; padding: .8rem 1.5rem; border: none; border-radius: 11px; cursor: pointer; font-size: .85rem; font-weight: 700; transition: transform .15s, box-shadow .15s, filter .15s, opacity .15s; width: 100%; text-decoration: none; letter-spacing: -.01em; }
        .btn-gold  { background: linear-gradient(135deg, hsl(42 95% 48%), hsl(38 90% 40%)); color: hsl(222 28% 8%); box-shadow: 0 4px 18px hsl(42 95% 48%/.35); }
        .btn-gold:hover  { transform: translateY(-2px); box-shadow: 0 8px 26px hsl(42 95% 48%/.5); filter: brightness(1.05); }
        .btn-ghost { background: var(--bg-card2); color: var(--text-2); border: 1px solid var(--border-lite); }
        .btn-ghost:hover { border-color: hsl(222,18%,38%); color: var(--text-1); transform: translateY(-1px); }
        .btn:disabled { opacity: .45; cursor: not-allowed; transform: none !important; box-shadow: none !important; }
        .btn.loading  { pointer-events: none; opacity: .75; }

        .lock-msg { font-size: .75rem; color: hsl(42,90%,65%); line-height: 1.5; text-align: center; background: hsl(42 60% 25%/.15); border: 1px solid hsl(42 60% 35%/.25); border-radius: 8px; padding: .6rem .75rem; }

        /* ─── Stats row ─── */
        .stats-row { display: grid; grid-template-columns: repeat(4,1fr); gap: 1rem; margin-bottom: 1.25rem; }
        .stat-card {
            background: var(--bg-card); border: 1px solid var(--border); border-radius: 16px;
            padding: 1.25rem 1.5rem; transition: border-color .2s, transform .2s;
        }
        .stat-card:hover { border-color: var(--border-lite); transform: translateY(-2px); }
        .stat-icon  { font-size: 1.3rem; margin-bottom: .4rem; }
        .stat-label { font-size: .68rem; font-weight: 600; color: var(--text-3); text-transform: uppercase; letter-spacing: .08em; margin-bottom: .2rem; }
        .stat-val   { font-size: 1.2rem; font-weight: 700; }
        .stat-sub   { font-size: .72rem; color: var(--text-3); margin-top: .15rem; }
        .c-gold    { color: var(--gold); }
        .c-emerald { color: var(--emerald-glow); }
        .c-sapphire{ color: var(--sapphire); }
        .c-rose    { color: var(--rose); }

        /* ─── Chart card ─── */
        .chart-card {
            background: var(--bg-card); border: 1px solid var(--border); border-radius: 20px;
            padding: 1.75rem 2rem; margin-bottom: 1.25rem;
        }
        .chart-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.25rem; flex-wrap: wrap; gap: .75rem; }
        .chart-title  { font-size: 1rem; font-weight: 700; }
        .chart-title span { color: var(--text-3); font-weight: 400; font-size: .82rem; margin-left: .4rem; }
        .chart-tabs   { display: flex; gap: .4rem; }
        .tab-btn {
            padding: .3rem .75rem; font-size: .75rem; font-weight: 600; border-radius: 8px; border: 1px solid var(--border);
            background: transparent; color: var(--text-3); cursor: pointer; transition: all .15s;
        }
        .tab-btn.active { background: var(--bg-card2); border-color: var(--border-lite); color: var(--text-1); }
        .chart-wrap { position: relative; height: 300px; }
        #priceChart { width: 100% !important; height: 100% !important; }
        .chart-legend { display: flex; flex-wrap: wrap; gap: .5rem 1rem; margin-top: 1rem; }
        .legend-item  { display: flex; align-items: center; gap: .4rem; font-size: .72rem; color: var(--text-2); cursor: pointer; }
        .legend-dot   { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }

        /* ─── Bottom row ─── */
        .bottom-row { display: grid; grid-template-columns: 1fr 1fr; gap: 1.25rem; }

        /* ─── Lookup card ─── */
        .lookup-card {
            background: var(--bg-card); border: 1px solid var(--border); border-radius: 20px;
            padding: 1.75rem 2rem;
        }
        .section-title { font-size: .78rem; font-weight: 600; text-transform: uppercase; letter-spacing: .08em; color: var(--text-3); margin-bottom: 1.1rem; display: flex; align-items: center; gap: .5rem; }
        .form-row  { display: flex; gap: .6rem; align-items: flex-end; }
        .field { flex: 1; }
        label.field-label { font-size: .78rem; color: var(--text-3); font-weight: 500; display: block; margin-bottom: .35rem; }
        input[type="date"] {
            width: 100%; background: var(--bg-card2); border: 1px solid var(--border-lite); border-radius: 10px;
            color: var(--text-1); padding: .65rem .9rem; font-size: .85rem; font-family: inherit;
            outline: none; transition: border-color .15s;
        }
        input[type="date"]:focus { border-color: hsl(213 89% 58%/.6); }
        input[type="date"]::-webkit-calendar-picker-indicator { filter: invert(.6); cursor: pointer; }

        .lookup-result {
            margin-top: 1.1rem; padding: 1.1rem; background: var(--bg-card2); border: 1px solid var(--border-lite);
            border-radius: 12px; animation: slideIn .3s ease;
        }
        .lookup-result-date { font-size: .72rem; color: var(--text-3); margin-bottom: .6rem; }
        .lookup-grid  { display: grid; grid-template-columns: 1fr 1fr; gap: .4rem .8rem; }
        .lookup-item  { font-size: .8rem; }
        .lookup-key   { color: var(--text-3); }
        .lookup-price { font-weight: 700; color: var(--text-1); }
        .lookup-price.composite { color: var(--gold); font-size: .9rem; }
        .no-exact-badge {
            display: inline-block; font-size: .65rem; padding: .15rem .5rem;
            background: hsl(42 60% 35%/.2); border: 1px solid hsl(42 60% 35%/.35);
            color: hsl(42,85%,65%); border-radius: 6px; margin-left: .4rem;
        }

        /* ─── Info card ─── */
        .info-card {
            background: var(--bg-card); border: 1px solid var(--border); border-radius: 20px;
            padding: 1.75rem 2rem;
        }
        .info-list { list-style: none; display: flex; flex-direction: column; gap: .55rem; }
        .info-list li { display: flex; align-items: flex-start; gap: .6rem; font-size: .82rem; color: var(--text-2); line-height: 1.45; }
        .info-list li::before { content: ''; width: 6px; height: 6px; border-radius: 50%; background: var(--gold); flex-shrink: 0; margin-top: .45rem; }

        /* ─── Footer ─── */
        footer {
            border-top: 1px solid var(--border); padding: 1.1rem 2rem; text-align: center;
            font-size: .72rem; color: var(--text-3); background: hsl(222 28% 8%/.6); backdrop-filter: blur(8px);
        }

        /* ─── Spinner ─── */
        .spinner {
            display: inline-block; width: 15px; height: 15px;
            border: 2.5px solid hsl(222 28% 10%/.4); border-top-color: hsl(222 28% 10%);
            border-radius: 50%; animation: spin .7s linear infinite; flex-shrink: 0;
        }
        @keyframes spin { to{transform:rotate(360deg)} }

        /* ─── Responsive ─── */
        @media(max-width:900px) {
            .top-row    { grid-template-columns: 1fr; }
            .stats-row  { grid-template-columns: 1fr 1fr; }
            .bottom-row { grid-template-columns: 1fr; }
        }
        @media(max-width:600px) {
            main { padding: 1.25rem 1rem 3rem; }
            .stats-row { grid-template-columns: 1fr 1fr; }
            .hero-card { padding: 1.75rem 1.5rem; }
            .price-val { font-size: 2.8rem; }
        }
    </style>
</head>
<body>
<div class="wrap">

<!-- ══════════ HEADER ══════════ -->
<header>
    <div class="logo">
        <span class="logo-icon">🌾</span>
        <div>
            <div class="logo-title">Rice Price Engine</div>
            <div class="logo-sub">Sri Lanka · AI Forecasting</div>
        </div>
    </div>
    <span class="badge-live">Model Active</span>
</header>

<main>

    {{-- ── Alerts ── --}}
    @if(session('success'))
        <div class="alert alert-success" id="al-ok">✅ &nbsp;{{ session('success') }}</div>
    @endif
    @if(session('error'))
        <div class="alert alert-danger" id="al-err">⚠️ &nbsp;{{ session('error') }}</div>
    @endif
    @if($apiError ?? null)
        <div class="alert alert-danger">⚠️ &nbsp;{{ $apiError }}</div>
    @endif

    {{-- ── TOP ROW: Hero + Status/Sync ── --}}
    <div class="top-row">

        {{-- Hero Prediction Card --}}
        <div class="hero-card">
            <div class="hero-eyebrow">Weekly Forecast</div>
            <div class="hero-label">Predicted retail price (composite)</div>
            <div class="hero-date">📅 &nbsp;{{ $targetDate ?? 'Awaiting model…' }}</div>

            @if($predictedPrice !== null && $predictedPrice > 0)
                <div class="price-display">
                    <span class="price-rs">Rs.</span>
                    <span class="price-val">{{ number_format($predictedPrice, 2) }}</span>
                    <span class="price-unit">/ kg</span>
                </div>
                <p class="price-hint">XGBoost prediction based on latest macroeconomic, weather &amp; supply signals.</p>
            @else
                <div class="price-na">Prediction Unavailable</div>
                <p class="price-hint">The model is not loaded or an error occurred. Click <strong style="color:var(--gold)">Sync &amp; Retrain</strong> to initialise it.</p>
            @endif
        </div>

        {{-- Status + Sync Card --}}
        <div class="status-card">
            <div class="status-title">📡 System Status</div>

            @php
                $ds = $dateStatus;
                $syncAllowed = $ds['sync_allowed'] ?? true;
                $daysAhead   = $ds['days_ahead'] ?? 0;
            @endphp

            <div class="status-rows">
                <div class="status-row">
                    <span class="status-key">Today</span>
                    <span class="status-val">{{ $ds['today'] ?? '—' }}</span>
                </div>
                <div class="status-row">
                    <span class="status-key">Latest data</span>
                    <span class="status-val">{{ $ds['latest_data_date'] ?? '—' }}</span>
                </div>
                <div class="status-row">
                    <span class="status-key">Next prediction</span>
                    <span class="status-val {{ $syncAllowed ? 'ok' : 'warn' }}">{{ $ds['next_prediction'] ?? $targetDate ?? '—' }}</span>
                </div>
                <div class="status-row">
                    <span class="status-key">Sync window</span>
                    <span class="status-val {{ $syncAllowed ? 'ok' : 'bad' }}">
                        {{ $syncAllowed ? '✓ Open' : '✗ Closed' }}
                    </span>
                </div>
            </div>

            <hr class="divider">

            @if($syncAllowed)
                <form action="{{ route('forecast.sync') }}" method="POST" id="sync-form">
                    @csrf
                    <button type="submit" class="btn btn-gold" id="sync-btn">
                        <span id="btn-icon">⚡</span>
                        <span id="btn-label">Sync &amp; Retrain</span>
                    </button>
                </form>
                <p style="font-size:.72rem;color:var(--text-3);text-align:center;margin-top:.5rem;">
                    Ingests next week's features and retrains the XGBoost model.
                </p>
            @else
                <div class="lock-msg">
                    🔒 Sync is locked. The model is already predicting
                    <strong>{{ $daysAhead }} day{{ $daysAhead == 1 ? '' : 's' }}</strong> ahead of today
                    ({{ $ds['next_prediction'] ?? '' }}). Come back when that date is within the current week.
                </div>
            @endif
        </div>
    </div>

    {{-- ── STATS ROW ── --}}
    <div class="stats-row">
        <div class="stat-card">
            <div class="stat-icon">🤖</div>
            <div class="stat-label">Model</div>
            <div class="stat-val c-gold">XGBoost</div>
            <div class="stat-sub">Gradient Boosted Regressor</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">📊</div>
            <div class="stat-label">Data Sources</div>
            <div class="stat-val c-emerald">6 Feeds</div>
            <div class="stat-sub">HARTI · WFP · CBSL · DCS · FAOSTAT · Weather</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">📅</div>
            <div class="stat-label">Training Range</div>
            <div class="stat-val c-sapphire">2015 – 2026</div>
            <div class="stat-sub">Weekly granularity · 570+ records</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">🌡️</div>
            <div class="stat-label">Features</div>
            <div class="stat-val c-rose">62 Signals</div>
            <div class="stat-sub">Macro · Weather · Supply · Seasonal</div>
        </div>
    </div>

    {{-- ── PRICE TREND CHART ── --}}
    <div class="chart-card">
        <div class="chart-header">
            <div>
                <div class="chart-title">📈 Price Distribution <span>— Sri Lankan Rice Varieties (LKR / kg)</span></div>
            </div>
            <div class="chart-tabs">
                <button class="tab-btn active" onclick="loadChart(365, this)">1Y</button>
                <button class="tab-btn" onclick="loadChart(730, this)">2Y</button>
                <button class="tab-btn" onclick="loadChart(1825, this)">5Y</button>
                <button class="tab-btn" onclick="loadChart(4015, this)">All</button>
            </div>
        </div>
        <div class="chart-wrap">
            <canvas id="priceChart"></canvas>
        </div>
        <div class="chart-legend" id="chart-legend"></div>
    </div>

    {{-- ── BOTTOM ROW: Lookup + Info ── --}}
    <div class="bottom-row">

        {{-- Date Lookup --}}
        <div class="lookup-card">
            <div class="section-title">🔍 Historical Price Lookup</div>

            <form action="{{ route('forecast.lookup') }}" method="POST" id="lookup-form">
                @csrf
                <div class="form-row">
                    <div class="field">
                        <label class="field-label" for="lookup_date">Select a date (Aug 2015 – present)</label>
                        <input type="date" id="lookup_date" name="lookup_date"
                               min="2015-08-09" max="{{ date('Y-m-d') }}"
                               value="{{ session('lookupResult')['queried_date'] ?? old('lookup_date') }}"
                               required>
                    </div>
                    <button type="submit" class="btn btn-ghost" style="width:auto;padding:.65rem 1.2rem;flex-shrink:0;">
                        Search
                    </button>
                </div>
            </form>

            @if(session('lookupError'))
                <div class="alert alert-danger" style="margin-top:.9rem;font-size:.8rem;">
                    ⚠️ {{ session('lookupError') }}
                </div>
            @endif

            @if(session('lookupResult'))
                @php $lr = session('lookupResult'); @endphp
                <div class="lookup-result">
                    <div class="lookup-result-date">
                        Results for <strong>{{ $lr['queried_date'] }}</strong>
                        @if(!$lr['exact_match'])
                            &nbsp;→ nearest record: <strong>{{ $lr['actual_date'] }}</strong>
                            <span class="no-exact-badge">Nearest match</span>
                        @else
                            <span style="font-size:.65rem;color:var(--emerald-glow);margin-left:.4rem;">✓ Exact match</span>
                        @endif
                    </div>

                    @if($lr['composite_price_lkr'])
                        <div style="margin-bottom:.75rem;font-size:.9rem;">
                            <span class="lookup-key">Composite (exp log price):</span>
                            <span class="lookup-price composite"> Rs. {{ number_format($lr['composite_price_lkr'], 2) }} / kg</span>
                        </div>
                    @endif

                    <div class="lookup-grid">
                        @foreach($lr['varieties'] as $variety => $price)
                            <div class="lookup-item">
                                <div class="lookup-key">{{ $variety }}</div>
                                <div class="lookup-price">Rs. {{ number_format($price, 2) }}</div>
                            </div>
                        @endforeach
                    </div>
                </div>
            @endif
        </div>

        {{-- Info Signals --}}
        <div class="info-card">
            <div class="section-title">📡 Input Signals</div>
            <ul class="info-list">
                <li>USD/LKR exchange rate (live-scraped + 30-day % change)</li>
                <li>Fuel (diesel &amp; petrol) national average prices</li>
                <li>CBSL agricultural wage indices (8 categories)</li>
                <li>HARTI Pettah &amp; Marandagahamula weekly spot prices</li>
                <li>National paddy production &amp; yield efficiency (DCS)</li>
                <li>WFP market prices across Colombo, Anuradhapura &amp; Kurunegala</li>
                <li>FAOSTAT pesticide application per cropland area</li>
                <li>Daily max/min temperature &amp; 14-day cumulative rainfall</li>
                <li>Extreme heat event binary flag</li>
                <li>Maha / Yala season one-hot encoding (12 seasons)</li>
                <li>Lagged log-prices &amp; log-returns (1, 2, 4 weeks back)</li>
                <li>Volatility rolling windows (4, 8, 12 periods)</li>
            </ul>
        </div>
    </div>

</main>

<footer>
    Sri Lankan Rice Price Forecasting Engine &nbsp;·&nbsp;
    Capstone Project in Data Science II &nbsp;·&nbsp;
    XGBoost · FastAPI · Laravel · 2026
</footer>

</div><!-- .wrap -->

<script>
/* ─────────────────────────────────────────
   Chart.js — Price Trend
───────────────────────────────────────── */
const PALETTE = [
    '#f5a623', '#4ecdc4', '#a8e6cf', '#ff6b6b',
    '#c7b8f5', '#74b9ff', '#fdcb6e', '#aaa'
];

let chartInstance = null;
let activeTab     = null;

async function loadChart(days, tabEl) {
    // Tab highlight
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    if (tabEl) tabEl.classList.add('active');
    activeTab = days;

    const res  = await fetch(`/api/history?days=${days}`);
    if (!res.ok) { console.error('History fetch failed'); return; }
    const data = await res.json();

    const { labels, series } = data;
    const seriesKeys = Object.keys(series);

    // Destroy old chart
    if (chartInstance) chartInstance.destroy();

    const ctx = document.getElementById('priceChart').getContext('2d');

    const datasets = seriesKeys.map((key, i) => ({
        label:           key,
        data:            series[key],
        borderColor:     PALETTE[i % PALETTE.length],
        backgroundColor: PALETTE[i % PALETTE.length] + '18',
        borderWidth:     key === 'Composite (exp log_price)' ? 2.5 : 1.5,
        pointRadius:     0,
        pointHoverRadius:4,
        tension:         0.35,
        fill:            false,
        hidden:          key === 'Composite (exp log_price)' ? false : (i > 4),
    }));

    chartInstance = new Chart(ctx, {
        type: 'line',
        data: { labels, datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: 'index', intersect: false },
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'hsl(222,24%,13%)',
                    borderColor: 'hsl(222,18%,26%)',
                    borderWidth: 1,
                    titleColor: 'hsl(210,25%,90%)',
                    bodyColor: 'hsl(210,15%,70%)',
                    padding: 10,
                    callbacks: {
                        label: ctx => ` ${ctx.dataset.label}: Rs. ${ctx.parsed.y?.toFixed(2) ?? 'N/A'}`
                    }
                }
            },
            scales: {
                x: {
                    grid: { color: 'hsl(222,18%,20%)' },
                    ticks: {
                        color: 'hsl(210,10%,46%)', font: { size: 10 },
                        maxTicksLimit: 10,
                        callback: (val, i, ticks) => {
                            if (i === 0 || i === ticks.length-1 || i % Math.ceil(ticks.length/8) === 0)
                                return labels[i]?.slice(0,7);
                            return '';
                        }
                    }
                },
                y: {
                    grid: { color: 'hsl(222,18%,20%)' },
                    ticks: { color: 'hsl(210,10%,46%)', font: { size: 10 }, callback: v => 'Rs. ' + v }
                }
            }
        }
    });

    // Custom legend
    const legendEl = document.getElementById('chart-legend');
    legendEl.innerHTML = datasets.map((ds, i) => `
        <div class="legend-item" onclick="toggleSeries(${i})" id="legend-${i}"
             style="${ds.hidden ? 'opacity:.4' : ''}">
            <div class="legend-dot" style="background:${ds.borderColor}"></div>
            <span>${ds.label}</span>
        </div>`).join('');
}

function toggleSeries(idx) {
    if (!chartInstance) return;
    const meta = chartInstance.getDatasetMeta(idx);
    meta.hidden = !meta.hidden;
    chartInstance.update();
    const legendItem = document.getElementById('legend-' + idx);
    legendItem.style.opacity = meta.hidden ? '.4' : '1';
}

// Initial load
loadChart(365, document.querySelector('.tab-btn.active'));

/* ─── Sync button loading state ─── */
const syncForm = document.getElementById('sync-form');
const syncBtn  = document.getElementById('sync-btn');
if (syncForm && syncBtn) {
    syncForm.addEventListener('submit', () => {
        syncBtn.classList.add('loading');
        document.getElementById('btn-icon').innerHTML = '<span class="spinner"></span>';
        document.getElementById('btn-label').textContent = 'Syncing…';
    });
}

/* ─── Auto-dismiss alerts ─── */
['al-ok','al-err'].forEach(id => {
    const el = document.getElementById(id);
    if (!el) return;
    setTimeout(() => {
        el.style.transition = 'opacity .5s';
        el.style.opacity    = '0';
        setTimeout(() => el.remove(), 500);
    }, 7000);
});
</script>
</body>
</html>