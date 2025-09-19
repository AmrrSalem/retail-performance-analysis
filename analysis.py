import pandas as pd  # pannel data or python data analysis
import numpy as np  # numerical python
import matplotlib.pyplot as plt  # plotting and visualization
import seaborn as sns  # plotting and visualization
from datetime import datetime
import warnings  # control wornings
warnings.filterwarnings('ignore')  # disable wornings

# Set up plotting style
plt.style.use('default')
sns.set_palette("husl")

# Load the data with error handling
print("🔄 Loading Superstore Dataset...")

# Try different file reading approaches
try:
    # First attempt - standard reading
    df = pd.read_csv('data/Sample-Superstore.csv', encoding='utf-8')
    print("✅ File loaded successfully with UTF-8 encoding")
except:
    try:
        # Second attempt - different encoding
        df = pd.read_csv('data/Sample-Superstore.csv', encoding='latin-1')
        print("✅ File loaded successfully with Latin-1 encoding")
    except:
        try:
            # Third attempt - handle problematic lines
            df = pd.read_csv('data/Sample-Superstore.csv', encoding='utf-8', error_bad_lines=False, warn_bad_lines=True)
            print("✅ File loaded with some problematic lines skipped")
        except:
            # Fourth attempt - different separators
            try:
                df = pd.read_csv('data/Sample-Superstore.csv', encoding='utf-8', sep=';')
                print("✅ File loaded with semicolon separator")
            except:
                print("❌ Could not read file. Let's check the file structure...")
                # Check first few lines of the file
                with open('data/Sample-Superstore.csv', 'r', encoding='utf-8', errors='ignore') as f:
                    for i, line in enumerate(f):
                        print(f"Line {i + 1}: {line.strip()}")
                        if i >= 5:  # Show first 6 lines
                            break
                raise Exception("File reading failed")

# Basic dataset information
print("\n📊 DATASET OVERVIEW")
print("=" * 50)
print(f"Dataset Shape: {df.shape[0]} rows × {df.shape[1]} columns")
print(f"Memory Usage: {df.memory_usage(deep=True).sum() / 1024 ** 2:.2f} MB")

# Display column info
print("\n📋 COLUMN INFORMATION")
print("=" * 50)
for col in df.columns:
    print(f"{col:<20} | {str(df[col].dtype):<10} | {df[col].nunique():<6} unique values")

# Check for missing values
print("\n🔍 DATA QUALITY CHECK")
print("=" * 50)
missing_data = df.isnull().sum()
if missing_data.sum() == 0:
    print("✅ No missing values found!")
else:
    print("⚠️  Missing values detected:")
    print(missing_data[missing_data > 0])

# Data preparation
print("\n🛠️  DATA PREPARATION")
print("=" * 50)

# Convert date column
df['Order Date'] = pd.to_datetime(df['Order Date'])
df['Ship Date'] = pd.to_datetime(df['Ship Date'])

# Create additional time-based columns
df['Year'] = df['Order Date'].dt.year
df['Month'] = df['Order Date'].dt.month
df['Quarter'] = df['Order Date'].dt.quarter
df['Month_Name'] = df['Order Date'].dt.strftime('%B')
df['Weekday'] = df['Order Date'].dt.strftime('%A')

# Calculate additional metrics
df['Profit_Margin'] = (df['Profit'] / df['Sales'] * 100).round(2)
df['Days_to_Ship'] = (df['Ship Date'] - df['Order Date']).dt.days

print("✅ Date columns converted and additional metrics calculated")

# BUSINESS ANALYSIS BEGINS HERE
print("\n" + "=" * 60)
print("📈 BUSINESS INTELLIGENCE ANALYSIS")
print("=" * 60)

# 1. OVERALL PERFORMANCE METRICS
print("\n💰 KEY PERFORMANCE INDICATORS")
print("-" * 40)
total_sales = df['Sales'].sum()
total_profit = df['Profit'].sum()
total_orders = df['Order ID'].nunique()
avg_order_value = df.groupby('Order ID')['Sales'].sum().mean()
overall_margin = (total_profit / total_sales * 100)

print(f"Total Sales:        ${total_sales:,.2f}")
print(f"Total Profit:       ${total_profit:,.2f}")
print(f"Total Orders:       {total_orders:,}")
print(f"Average Order:      ${avg_order_value:.2f}")
print(f"Profit Margin:      {overall_margin:.2f}%")
print(
    f"Date Range:         {df['Order Date'].min().strftime('%Y-%m-%d')} to {df['Order Date'].max().strftime('%Y-%m-%d')}")

# 2. SALES TRENDS ANALYSIS
print("\n📅 SALES TRENDS ANALYSIS")
print("-" * 40)

# Monthly sales trend
monthly_sales = df.groupby(['Year', 'Month']).agg({
    'Sales': 'sum',
    'Profit': 'sum',
    'Order ID': 'nunique'
}).round(2)

# Find best and worst months
monthly_totals = df.groupby('Month_Name')['Sales'].sum().sort_values(ascending=False)
print(f"Best Month:         {monthly_totals.index[0]} (${monthly_totals.iloc[0]:,.2f})")
print(f"Worst Month:        {monthly_totals.index[-1]} (${monthly_totals.iloc[-1]:,.2f})")

# Year over year growth
yearly_sales = df.groupby('Year')['Sales'].sum()
if len(yearly_sales) > 1:
    growth_rates = yearly_sales.pct_change() * 100
    print(f"YoY Growth 2017:    {growth_rates[2017]:.1f}%" if 2017 in growth_rates.index else "N/A")
    print(f"YoY Growth 2018:    {growth_rates[2018]:.1f}%" if 2018 in growth_rates.index else "N/A")

# 3. CUSTOMER SEGMENTATION ANALYSIS
print("\n👥 CUSTOMER SEGMENTATION")
print("-" * 40)

customer_segment_analysis = df.groupby('Segment').agg({
    'Sales': 'sum',
    'Profit': 'sum',
    'Customer ID': 'nunique',
    'Order ID': 'nunique'
}).round(2)

customer_segment_analysis['Avg_Order_Value'] = (customer_segment_analysis['Sales'] /
                                                customer_segment_analysis['Order ID']).round(2)
customer_segment_analysis['Profit_Margin'] = (customer_segment_analysis['Profit'] /
                                              customer_segment_analysis['Sales'] * 100).round(2)

print("Segment Performance:")
for segment in customer_segment_analysis.index:
    row = customer_segment_analysis.loc[segment]
    print(
        f"{segment:<12} | Sales: ${row['Sales']:>8,.0f} | Profit: ${row['Profit']:>7,.0f} | Margin: {row['Profit_Margin']:>5.1f}%")

# 4. PRODUCT CATEGORY ANALYSIS
print("\n🛍️  PRODUCT CATEGORY PERFORMANCE")
print("-" * 40)

category_analysis = df.groupby('Category').agg({
    'Sales': 'sum',
    'Profit': 'sum',
    'Quantity': 'sum',
    'Order ID': 'nunique'
}).round(2)

category_analysis['Profit_Margin'] = (category_analysis['Profit'] / category_analysis['Sales'] * 100).round(2)
category_analysis['Avg_Order_Value'] = (category_analysis['Sales'] / category_analysis['Order ID']).round(2)

print("Category Performance:")
for category in category_analysis.index:
    row = category_analysis.loc[category]
    print(
        f"{category:<12} | Sales: ${row['Sales']:>8,.0f} | Margin: {row['Profit_Margin']:>5.1f}% | AOV: ${row['Avg_Order_Value']:>6.0f}")

# 5. REGIONAL ANALYSIS
print("\n🗺️  REGIONAL PERFORMANCE")
print("-" * 40)

regional_analysis = df.groupby('Region').agg({
    'Sales': 'sum',
    'Profit': 'sum',
    'Customer ID': 'nunique',
    'Order ID': 'nunique'
}).round(2)

regional_analysis['Profit_Margin'] = (regional_analysis['Profit'] / regional_analysis['Sales'] * 100).round(2)
regional_analysis['Sales_per_Customer'] = (regional_analysis['Sales'] / regional_analysis['Customer ID']).round(2)

print("Regional Performance:")
for region in regional_analysis.index:
    row = regional_analysis.loc[region]
    print(
        f"{region:<8} | Sales: ${row['Sales']:>8,.0f} | Customers: {row['Customer ID']:>4} | Sales/Customer: ${row['Sales_per_Customer']:>6.0f}")

# 6. TOP PERFORMERS ANALYSIS
print("\n🏆 TOP PERFORMERS")
print("-" * 40)

# Top products by sales
top_products_sales = df.groupby('Product Name')['Sales'].sum().sort_values(ascending=False).head(5)
print("Top 5 Products by Sales:")
for i, (product, sales) in enumerate(top_products_sales.items(), 1):
    print(f"{i}. {product[:50]:<50} ${sales:>8,.0f}")

# Top customers by sales
top_customers = df.groupby('Customer Name')['Sales'].sum().sort_values(ascending=False).head(5)
print(f"\nTop 5 Customers by Sales:")
for i, (customer, sales) in enumerate(top_customers.items(), 1):
    print(f"{i}. {customer:<30} ${sales:>8,.0f}")

# 7. KEY BUSINESS INSIGHTS
print("\n" + "=" * 60)
print("💡 KEY BUSINESS INSIGHTS")
print("=" * 60)

# Calculate insights
best_region = regional_analysis['Sales'].idxmax()
best_category = category_analysis['Profit_Margin'].idxmax()
best_segment = customer_segment_analysis['Profit_Margin'].idxmax()
worst_performers = category_analysis['Profit_Margin'].idxmin()

print(f"🎯 OPPORTUNITIES IDENTIFIED:")
print(f"   • {best_region} region generates highest sales (${regional_analysis.loc[best_region, 'Sales']:,.0f})")
print(
    f"   • {best_category} category has highest profit margin ({category_analysis.loc[best_category, 'Profit_Margin']:.1f}%)")
print(
    f"   • {best_segment} segment most profitable ({customer_segment_analysis.loc[best_segment, 'Profit_Margin']:.1f}% margin)")
print(
    f"   • Improvement needed in {worst_performers} category ({category_analysis.loc[worst_performers, 'Profit_Margin']:.1f}% margin)")

# Calculate potential impact
profit_opportunity = category_analysis.loc[best_category, 'Sales'] * 0.05  # 5% margin improvement
print(f"   • Potential profit increase: ${profit_opportunity:,.0f} (5% margin improvement on best category)")

print(f"\n📊 DASHBOARD READY METRICS:")
print(f"   • Total KPIs: Sales, Profit, Orders, AOV calculated ✅")
print(f"   • Time trends: Monthly, quarterly, yearly data prepared ✅")
print(f"   • Segmentation: Customer, product, regional analysis complete ✅")
print(f"   • Top performers: Products and customers identified ✅")

print(f"\n🎉 Day 1 Analysis Complete!")
print(f"Next: Create visualizations and dashboard (Day 2-3)")
