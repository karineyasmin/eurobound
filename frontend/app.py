import streamlit as st
import httpx
import folium
import asyncio
from streamlit_folium import st_folium  # type: ignore
from shapely.wkt import loads
from shapely.geometry import mapping
from typing import Any
from http import HTTPStatus

st.set_page_config(
    page_title="EuroBound | Spatial Planning", page_icon="🗺️", layout="wide"
)

BACKEND_URL: str = "http://localhost:8000"


async def check_backend_health_async() -> dict[str, Any] | None:
    """Performs a non-blocking health check against the FastAPI engine."""
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(f"{BACKEND_URL}")
            if response.status_code == HTTPStatus.OK:
                return response.json()
            return response.json()
    except httpx.ConnectError:
        return None


async def fetch_spatial_regions_async() -> list[dict[str, Any]]:
    """Asynchronously fetches mapped target regions from PostGIS backend."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{BACKEND_URL}/regions/")
            if response.status_code == HTTPStatus.OK:
                return list(response.json())
            return []

    except Exception:
        return []


backend_status = asyncio.run(check_backend_health_async())
regions_data = asyncio.run(fetch_spatial_regions_async())

st.sidebar.title("🧭 EuroBound Navigation")
st.sidebar.markdown("---")


if backend_status:
    st.sidebar.success(
        f"🟢 Connected to Backend\n\n"
        f"Engine: {backend_status.get('spatial_engine')}\n\n"
        f"Status: Operational"
    )
else:
    st.sidebar.error(
        "🔴 Cannot connect to FastAPI.\n\nRun 'make run-api' in another terminal."
    )

st.title("🗺️ EuroBound: Hexagonal Cartographic Planning")
st.subheader(
    "Analyze cost of living, temperatures, and map European target regions using strict UUIDs."
)

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### 📊 Regional Filters")
    max_budget: float = st.slider(
        "Maximum Monthly Cost of Living (€)", 500.0, 5000.0, 2000.0, step=100.0
    )
    min_temp: float = st.slider(
        "Minimum Winter Temperature (°C)", -20.0, 20.0, 5.0, step=1.0
    )

    st.markdown("---")
    st.markdown("### 🏛️ Mapped Regions (UUID Anchored)")

    if regions_data:
        for r in regions_data:
            # We cut the UUID string short just for visual elegance on screen (.iloc style)
            short_uuid: str = str(r["id"])[:8]
            st.info(
                f"**{r['name']}** ({r['country']})\n\n"
                f"ID: `...{short_uuid}`\n\n"
                f"Cost: €{r['estimated_cost_of_living']}/mo | Temp: {r['average_winter_temperature']}°C"
            )
    else:
        st.warning("No regions found or database is currently empty.")

with col2:
    st.markdown("### 🌍 Interactive Geographic Map")
    european_map: folium.Map = folium.Map(
        location=[43.0, 2.0], zoom_start=5, tiles="CartoDB positron"
    )

    for r in regions_data:
        if "geom_wkt" in r and r["geom_wkt"]:
            try:
                shapely_geom = loads(r["geom_wkt"])
                geojson_layer = mapping(shapely_geom)

                folium.GeoJson(
                    geojson_layer,
                    name=r["name"],
                    style_function=lambda _: {  # type: ignore
                        "fillColor": "#1a73e8",
                        "color": "#0d47a1",
                        "weight": 2.5,
                        "fillOpacity": 0.35,
                    },
                    tooltip=(
                        f"<b>Region:</b> {r['name']}<br>"
                        f"<b>Country:</b> {r['country']}<br>"
                        f"<b>Living Cost:</b> €{r['estimated_cost_of_living']}/mo"
                    ),
                ).add_to(european_map)

            except Exception as wkt_error:
                st.error(f"Failed to parse geometry for {r['name']}: {str(wkt_error)}")

    st_folium(european_map, use_container_width=True, height=550)
