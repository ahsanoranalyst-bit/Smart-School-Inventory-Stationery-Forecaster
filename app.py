import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(page_title="Inventory & Stationery Forecaster", layout="wide")

st.title("📦 Smart School Inventory & Stationery Forecaster")

# --- DATA INITIALIZATION ---
if 'inventory' not in st.session_state:
    st.session_state.inventory = pd.DataFrame([
        {"Item": "A4 Paper Reams", "Current Qty": 150, "Damage Rate (%)": 2, "Unit Cost": 5.0, "MOQ": 50, "Lead Time": 5},
        {"Item": "Whiteboard Markers", "Current Qty": 45, "Damage Rate (%)": 5, "Unit Cost": 1.2, "MOQ": 100, "Lead Time": 3},
        {"Item": "Science Lab Kits", "Current Qty": 12, "Damage Rate (%)": 10, "Unit Cost": 45.0, "MOQ": 5, "Lead Time": 14}
    ])

# --- SIDEBAR: SECTION B & C (USAGE & SUPPLY) ---
with st.sidebar:
    st.header("Section B: Usage Context")
    peak_season = st.checkbox("Is it a Peak Season? (e.g., Start of Term)", value=False)
    multiplier = 1.5 if peak_season else 1.0
    
    st.header("Section D: Budget Alerts")
    budget_cap = st.number_input("Monthly Budget Cap ($)", 500, 10000, 2000)

# --- MAIN INTERFACE ---
tab1, tab2, tab3 = st.tabs(["📊 Inventory Status", "📈 Forecasting", "💰 Procurement & Budget"])

with tab1:
    st.subheader("Section A: Current Stock Levels")
    # Interactive Data Entry
    edited_df = st.data_editor(st.session_state.inventory, num_rows="dynamic")
    st.session_state.inventory = edited_df

with tab2:
    st.subheader("Section B & C: Forecast & Reorder Alerts")
    
    # Simple Forecaster Logic
    # ROP = (Avg Daily Usage * Lead Time) + Safety Stock
    st.write("### Smart Reorder Recommendations")
    
    forecast_results = []
    for index, row in edited_df.iterrows():
        daily_usage = (row['Current Qty'] * 0.05) * multiplier # Simulated consumption
        rop = daily_usage * row['Lead Time']
        
        status = "✅ Sufficient"
        if row['Current Qty'] <= rop:
            status = "🚨 REORDER NOW"
        
        forecast_results.append({
            "Item": row['Item'],
            "Safety Stock Needed": round(rop, 1),
            "Status": status
        })
    
    st.table(pd.DataFrame(forecast_results))

with tab3:
    st.subheader("Section D: Financial Impact")
    
    # Calculate order costs for items needing reorder
    order_items = [res['Item'] for res in forecast_results if res['Status'] == "🚨 REORDER NOW"]
    procurement_df = edited_df[edited_df['Item'].isin(order_items)].copy()
    
    procurement_df['Order Total'] = procurement_df['MOQ'] * procurement_df['Unit Cost']
    total_spend = procurement_df['Order Total'].sum()
    
    c1, c2 = st.columns(2)
    c1.metric("Projected Spend", f"${total_spend:.2f}")
    c2.metric("Remaining Budget", f"${budget_cap - total_spend:.2f}")
    
    if total_spend > budget_cap:
        st.error("⚠️ Warning: Projected spend exceeds monthly budget!")
    

    st.dataframe(procurement_df[['Item', 'MOQ', 'Unit Cost', 'Order Total']])
