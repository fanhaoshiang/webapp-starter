from datetime import date
from typing import List

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI(title="Global Warming Monitor")


class Item(BaseModel):
    title: str
    price: float


class ClimatePoint(BaseModel):
    year: int
    temperature_anomaly_c: float
    co2_ppm: int
    sea_level_rise_mm: float


CLIMATE_DATA: List[ClimatePoint] = [
    ClimatePoint(year=1980, temperature_anomaly_c=0.22, co2_ppm=338, sea_level_rise_mm=0.0),
    ClimatePoint(year=1990, temperature_anomaly_c=0.38, co2_ppm=354, sea_level_rise_mm=12.5),
    ClimatePoint(year=2000, temperature_anomaly_c=0.52, co2_ppm=369, sea_level_rise_mm=24.3),
    ClimatePoint(year=2010, temperature_anomaly_c=0.7, co2_ppm=389, sea_level_rise_mm=36.9),
    ClimatePoint(year=2020, temperature_anomaly_c=1.02, co2_ppm=414, sea_level_rise_mm=52.7),
    ClimatePoint(year=2023, temperature_anomaly_c=1.15, co2_ppm=418, sea_level_rise_mm=58.4),
]


@app.get("/")
def root():
    return {"ok": True, "msg": "Welcome to the Global Warming Monitor API"}


# A) 帶參數 GET
@app.get("/hello")
def hello(name: str = "KKK"):
    return {"hello": name}


# B) POST JSON
@app.post("/items")
def create_item(item: Item):
    return {"ok": True, "item": item.model_dump()}


@app.get("/climate/data")
def climate_data():
    """Historical climate indicators for visualizations."""
    return {
        "updated": date.today().isoformat(),
        "points": [point.model_dump() for point in CLIMATE_DATA],
        "summary": {
            "latest_temp_anomaly_c": CLIMATE_DATA[-1].temperature_anomaly_c,
            "latest_co2_ppm": CLIMATE_DATA[-1].co2_ppm,
            "sea_level_rise_since_1980_mm": CLIMATE_DATA[-1].sea_level_rise_mm,
        },
    }


@app.get("/climate", response_class=HTMLResponse)
def climate_dashboard():
    """A simple dashboard page to observe global warming indicators."""
    years = [point.year for point in CLIMATE_DATA]
    temps = [point.temperature_anomaly_c for point in CLIMATE_DATA]
    co2 = [point.co2_ppm for point in CLIMATE_DATA]
    sea_levels = [point.sea_level_rise_mm for point in CLIMATE_DATA]

    html = f"""
    <!DOCTYPE html>
    <html lang=\"zh-Hant\">
    <head>
        <meta charset=\"UTF-8\" />
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
        <title>全球暖化觀測站</title>
        <script src=\"https://cdn.jsdelivr.net/npm/chart.js\"></script>
        <style>
            body {{ font-family: 'Segoe UI', system-ui, sans-serif; margin: 0; padding: 0; background: #0b1021; color: #f4f7ff; }}
            header {{ background: linear-gradient(120deg, #133c55, #2975a8); padding: 24px; text-align: center; }}
            h1 {{ margin: 0; font-size: 28px; letter-spacing: 1px; }}
            main {{ max-width: 1100px; margin: 0 auto; padding: 24px; }}
            section.card {{ background: rgba(255,255,255,0.06); border-radius: 16px; padding: 20px; margin-bottom: 20px; box-shadow: 0 20px 60px rgba(0,0,0,0.25); border: 1px solid rgba(255,255,255,0.08); backdrop-filter: blur(6px); }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 12px; }}
            .stat {{ background: rgba(255,255,255,0.08); padding: 16px; border-radius: 12px; text-align: center; }}
            .stat h3 {{ margin: 0 0 8px 0; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; opacity: 0.8; }}
            .stat p {{ margin: 0; font-size: 26px; font-weight: 700; }}
            canvas {{ max-width: 100%; height: 360px; }}
            footer {{ text-align: center; padding: 16px; color: #c1d7f5; opacity: 0.8; font-size: 14px; }}
            a {{ color: #6ed0ff; }}
        </style>
    </head>
    <body>
        <header>
            <h1>全球暖化觀測站</h1>
            <p>用簡單的圖表觀察地球升溫、二氧化碳濃度與海平面變化</p>
        </header>
        <main>
            <section class=\"card\">
                <div class=\"grid\">
                    <div class=\"stat\">
                        <h3>最近年份</h3>
                        <p>{years[-1]}</p>
                    </div>
                    <div class=\"stat\">
                        <h3>全球升溫 (°C)</h3>
                        <p>{temps[-1]:.2f}</p>
                    </div>
                    <div class=\"stat\">
                        <h3>大氣 CO₂ (ppm)</h3>
                        <p>{co2[-1]:.0f}</p>
                    </div>
                    <div class=\"stat\">
                        <h3>海平面上升 (mm)</h3>
                        <p>{sea_levels[-1]:.1f}</p>
                    </div>
                </div>
            </section>
            <section class=\"card\">
                <h2>趨勢圖</h2>
                <canvas id=\"climateChart\"></canvas>
            </section>
            <section class=\"card\">
                <h2>說明</h2>
                <p>這份資料來自公開的全球暖化趨勢，顯示自 1980 年以來地球平均溫度持續上升，CO₂ 濃度與海平面亦同步攀升。你可以透過 API 取得原始資料：<code>/climate/data</code>。</p>
            </section>
        </main>
        <footer>
            更新日期：{date.today().isoformat()} · 參考資料：<a href=\"https://climate.nasa.gov/\">NASA Climate</a>, <a href=\"https://gml.noaa.gov/ccgg/trends/\">NOAA</a>
        </footer>
        <script>
            const ctx = document.getElementById('climateChart').getContext('2d');
            new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: {years},
                    datasets: [
                        {{ label: '升溫 (°C)', data: {temps}, borderColor: '#ffa94d', backgroundColor: 'rgba(255,169,77,0.15)', tension: 0.3, fill: true }},
                        {{ label: 'CO₂ (ppm)', data: {co2}, borderColor: '#4dabf7', backgroundColor: 'rgba(77,171,247,0.1)', yAxisID: 'y1', tension: 0.3, fill: false }},
                        {{ label: '海平面 (mm)', data: {sea_levels}, borderColor: '#7bffb7', backgroundColor: 'rgba(123,255,183,0.12)', tension: 0.3, fill: true }}
                    ]
                }},
                options: {{
                    responsive: true,
                    scales: {{
                        y: {{
                            type: 'linear',
                            position: 'left',
                            ticks: {{ color: '#f4f7ff' }},
                            grid: {{ color: 'rgba(255,255,255,0.08)' }}
                        }},
                        y1: {{
                            type: 'linear',
                            position: 'right',
                            ticks: {{ color: '#9bc2ff' }},
                            grid: {{ drawOnChartArea: false }},
                        }},
                        x: {{ ticks: {{ color: '#c1d7f5' }}, grid: {{ color: 'rgba(255,255,255,0.05)' }} }}
                    }},
                    plugins: {{
                        legend: {{ labels: {{ color: '#f4f7ff' }} }},
                        tooltip: {{ mode: 'index', intersect: false }}
                    }},
                    interaction: {{ mode: 'index', intersect: false }}
                }}
            }});
        </script>
    </body>
    </html>
    """
    return HTMLResponse(html)
