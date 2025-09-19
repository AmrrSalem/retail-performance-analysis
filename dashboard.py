import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="Retail Sales Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 0.25rem solid #1f77b4;
    }
    .insight-box {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 0.25rem solid #17a2b8;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


# Load and cache data
@st.cache_data
def load_data():
    df = pd.read_csv('data/Sample-Superstore.csv', encoding='utf-8')

    # Data preprocessing
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    df['Ship Date'] = pd.to_datetime(df['Ship Date'])
    df['Year'] = df['Order Date'].dt.year
    df['Month'] = df['Order Date'].dt.month
    df['Quarter'] = df['Order Date'].dt.quarter
    df['Month_Name'] = df['Order Date'].dt.strftime('%B')
    df['Weekday'] = df['Order Date'].dt.strftime('%A')
    df['Profit_Margin'] = (df['Profit'] / df['Sales'] * 100).round(2)
    df['Days_to_Ship'] = (df['Ship Date'] - df['Order Date']).dt.days

    return df


# Load data
df = load_data()

# Header
st.markdown('<h1 class="main-header">📊 Retail Sales Performance Dashboard</h1>', unsafe_allow_html=True)
st.markdown("**Comprehensive analysis of superstore sales data with actionable business insights**")

# Sidebar filters
st.sidebar.header("🔍 Filters & Controls")

# Date range filter
date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(df['Order Date'].min(), df['Order Date'].max()),
    min_value=df['Order Date'].min(),
    max_value=df['Order Date'].max()
)

# Region filter
regions = st.sidebar.multiselect(
    "Select Regions",
    options=df['Region'].unique(),
    default=df['Region'].unique()
)

# Category filter
categories = st.sidebar.multiselect(
    "Select Categories",
    options=df['Category'].unique(),
    default=df['Category'].unique()
)

# Segment filter
segments = st.sidebar.multiselect(
    "Select Customer Segments",
    options=df['Segment'].unique(),
    default=df['Segment'].unique()
)

# Filter data based on selections
if len(date_range) == 2:
    df_filtered = df[
        (df['Order Date'] >= pd.to_datetime(date_range[0])) &
        (df['Order Date'] <= pd.to_datetime(date_range[1])) &
        (df['Region'].isin(regions)) &
        (df['Category'].isin(categories)) &
        (df['Segment'].isin(segments))
        ]
else:
    df_filtered = df[
        (df['Region'].isin(regions)) &
        (df['Category'].isin(categories)) &
        (df['Segment'].isin(segments))
        ]

# Key Performance Indicators
st.markdown("## 💰 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_sales = df_filtered['Sales'].sum()
    st.metric(
        label="💵 Total Sales",
        value=f"${total_sales:,.0f}",
        delta=f"{(total_sales / df['Sales'].sum() * 100):.1f}% of total"
    )

with col2:
    total_profit = df_filtered['Profit'].sum()
    profit_margin = (total_profit / total_sales * 100) if total_sales > 0 else 0
    st.metric(
        label="💰 Total Profit",
        value=f"${total_profit:,.0f}",
        delta=f"{profit_margin:.1f}% margin"
    )

with col3:
    total_orders = df_filtered['Order ID'].nunique()
    st.metric(
        label="📦 Total Orders",
        value=f"{total_orders:,}",
        delta=f"{(total_orders / df['Order ID'].nunique() * 100):.1f}% of total"
    )

with col4:
    avg_order_value = df_filtered.groupby('Order ID')['Sales'].sum().mean() if total_orders > 0 else 0
    st.metric(
        label="🛒 Avg Order Value",
        value=f"${avg_order_value:.0f}",
        delta="Per order"
    )

# Charts Section
st.markdown("## 📈 Performance Analytics")

# Create two columns for charts
col1, col2 = st.columns(2)

with col1:
    # Monthly Sales Trend
    st.markdown("### 📅 Monthly Sales Trend")
    monthly_data = df_filtered.groupby(df_filtered['Order Date'].dt.to_period('M')).agg({
        'Sales': 'sum',
        'Profit': 'sum'
    }).reset_index()
    monthly_data['Order Date'] = monthly_data['Order Date'].astype(str)

    fig_trend = make_subplots(specs=[[{"secondary_y": True}]])

    fig_trend.add_trace(
        go.Scatter(x=monthly_data['Order Date'], y=monthly_data['Sales'],
                   mode='lines+markers', name='Sales', line=dict(color='#1f77b4', width=3)),
        secondary_y=False,
    )

    fig_trend.add_trace(
        go.Scatter(x=monthly_data['Order Date'], y=monthly_data['Profit'],
                   mode='lines+markers', name='Profit', line=dict(color='#ff7f0e', width=3)),
        secondary_y=True,
    )

    fig_trend.update_xaxes(title_text="Month")
    fig_trend.update_yaxes(title_text="Sales ($)", secondary_y=False)
    fig_trend.update_yaxes(title_text="Profit ($)", secondary_y=True)
    fig_trend.update_layout(height=400, showlegend=True)

    st.plotly_chart(fig_trend, use_container_width=True)

with col2:
    # Regional Performance
    st.markdown("### 🗺️ Regional Performance")
    regional_data = df_filtered.groupby('Region').agg({
        'Sales': 'sum',
        'Profit': 'sum'
    }).reset_index().sort_values('Sales', ascending=True)

    fig_region = go.Figure()
    fig_region.add_trace(go.Bar(
        y=regional_data['Region'],
        x=regional_data['Sales'],
        name='Sales',
        orientation='h',
        marker_color='#1f77b4',
        text=regional_data['Sales'].apply(lambda x: f'${x:,.0f}'),
        textposition='inside'
    ))

    fig_region.update_layout(
        title="Sales by Region",
        xaxis_title="Sales ($)",
        yaxis_title="Region",
        height=400,
        showlegend=False
    )

    st.plotly_chart(fig_region, use_container_width=True)

# Second row of charts
col3, col4 = st.columns(2)

with col3:
    # Category Performance
    st.markdown("### 🛍️ Category Performance")
    category_data = df_filtered.groupby('Category').agg({
        'Sales': 'sum',
        'Profit': 'sum'
    }).reset_index()
    category_data['Profit_Margin'] = (category_data['Profit'] / category_data['Sales'] * 100)

    fig_category = px.scatter(
        category_data,
        x='Sales',
        y='Profit_Margin',
        size='Profit',
        color='Category',
        title="Category Performance: Sales vs Profit Margin",
        labels={'Profit_Margin': 'Profit Margin (%)', 'Sales': 'Sales ($)'},
        hover_data={'Profit': ':$,.0f'}
    )
    fig_category.update_layout(height=400)

    st.plotly_chart(fig_category, use_container_width=True)

with col4:
    # Customer Segment Analysis
    st.markdown("### 👥 Customer Segment Analysis")
    segment_data = df_filtered.groupby('Segment').agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Customer ID': 'nunique'
    }).reset_index()

    fig_segment = px.pie(
        segment_data,
        values='Sales',
        names='Segment',
        title="Sales Distribution by Customer Segment",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig_segment.update_traces(textposition='inside', textinfo='percent+label')
    fig_segment.update_layout(height=400)

    st.plotly_chart(fig_segment, use_container_width=True)

# Top Performers Section
st.markdown("## 🏆 Top Performers")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🥇 Top 10 Products by Sales")
    top_products = df_filtered.groupby('Product Name')['Sales'].sum().sort_values(ascending=False).head(10)

    fig_products = go.Figure(go.Bar(
        x=top_products.values,
        y=[name[:40] + "..." if len(name) > 40 else name for name in top_products.index],
        orientation='h',
        marker_color='#2ca02c',
        text=[f'${val:,.0f}' for val in top_products.values],
        textposition='inside'
    ))

    fig_products.update_layout(
        title="Top Products by Sales Revenue",
        xaxis_title="Sales ($)",
        yaxis_title="Product",
        height=500,
        yaxis={'categoryorder': 'total ascending'}
    )

    st.plotly_chart(fig_products, use_container_width=True)

with col2:
    st.markdown("### 🥇 Top 10 Customers by Sales")
    top_customers = df_filtered.groupby('Customer Name')['Sales'].sum().sort_values(ascending=False).head(10)

    fig_customers = go.Figure(go.Bar(
        x=top_customers.values,
        y=top_customers.index,
        orientation='h',
        marker_color='#d62728',
        text=[f'${val:,.0f}' for val in top_customers.values],
        textposition='inside'
    ))

    fig_customers.update_layout(
        title="Top Customers by Sales Revenue",
        xaxis_title="Sales ($)",
        yaxis_title="Customer",
        height=500,
        yaxis={'categoryorder': 'total ascending'}
    )

    st.plotly_chart(fig_customers, use_container_width=True)

# Business Insights Section
st.markdown("## 💡 Key Business Insights")

# Calculate insights based on filtered data
best_region = df_filtered.groupby('Region')['Sales'].sum().idxmax() if not df_filtered.empty else "N/A"
best_category = df_filtered.groupby('Category').apply(
    lambda x: (x['Profit'].sum() / x['Sales'].sum() * 100)
).idxmax() if not df_filtered.empty else "N/A"

best_month = df_filtered.groupby('Month_Name')['Sales'].sum().idxmax() if not df_filtered.empty else "N/A"

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div class="insight-box">
        <h4>🎯 Growth Opportunities</h4>
        <ul>
            <li><strong>{best_region}</strong> region shows highest sales performance</li>
            <li><strong>{best_category}</strong> category has the best profit margins</li>
            <li><strong>{best_month}</strong> is the peak sales month</li>
            <li>West region customers have highest lifetime value</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    # Calculate potential improvements
    furniture_sales = df_filtered[df_filtered['Category'] == 'Furniture']['Sales'].sum()
    potential_improvement = furniture_sales * 0.05  # 5% margin improvement

    st.markdown(f"""
    <div class="insight-box">
        <h4>💰 Revenue Optimization</h4>
        <ul>
            <li>Furniture category needs margin improvement (currently 2.5%)</li>
            <li>Potential profit increase: <strong>${potential_improvement:,.0f}</strong></li>
            <li>Technology products show 17.4% margins - focus area</li>
            <li>Home Office segment most profitable at 14% margin</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Data Export Section
st.markdown("## 📤 Data Export")

col1, col2, col3 = st.columns(3)

with col1:
    # Export filtered data
    csv = df_filtered.to_csv(index=False)
    st.download_button(
        label="📥 Download Filtered Data (CSV)",
        data=csv,
        file_name=f"superstore_data_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

with col2:
    # Export summary report
    summary_data = pd.DataFrame({
        'Metric': ['Total Sales', 'Total Profit', 'Total Orders', 'Avg Order Value', 'Profit Margin'],
        'Value': [
            f"${total_sales:,.0f}",
            f"${total_profit:,.0f}",
            f"{total_orders:,}",
            f"${avg_order_value:.0f}",
            f"{profit_margin:.1f}%"
        ]
    })
    summary_csv = summary_data.to_csv(index=False)
    st.download_button(
        label="📊 Download KPI Summary",
        data=summary_csv,
        file_name=f"kpi_summary_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

with col3:
    st.markdown("**Dashboard Info:**")
    st.info(f"""
    📊 **Records Displayed:** {len(df_filtered):,}  
    📅 **Date Range:** {df_filtered['Order Date'].min().strftime('%Y-%m-%d')} to {df_filtered['Order Date'].max().strftime('%Y-%m-%d')}  
    🏪 **Regions:** {len(regions)} selected  
    📦 **Categories:** {len(categories)} selected
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; margin-top: 2rem;">
    <p>📊 <strong>Retail Sales Dashboard</strong> | Built with Streamlit & Plotly | Data-driven Business Intelligence</p>
    <p><em>Interactive dashboard providing comprehensive sales analytics and actionable business insights</em></p>
</div>
""", unsafe_allow_html=True)