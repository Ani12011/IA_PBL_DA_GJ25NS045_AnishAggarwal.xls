import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns

# Set page config
st.set_page_config(page_title="Health Drink Sales Insights", layout="wide")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("Clean Data.csv", parse_dates=['Date'])
    return df

df = load_data()

# --- Sidebar filters ---
st.sidebar.header("Filter Data")
date_range = st.sidebar.date_input("Select Date Range", [df['Date'].min(), df['Date'].max()])
selected_genders = st.sidebar.multiselect("Select Gender", options=df['Gender'].dropna().unique(), default=df['Gender'].dropna().unique())
selected_products = st.sidebar.multiselect("Product Variant", options=df['ProductVariant'].unique(), default=df['ProductVariant'].unique())
selected_locations = st.sidebar.multiselect("Location", options=df['Location'].unique(), default=df['Location'].unique())
selected_channel = st.sidebar.multiselect("Channel", options=df['Channel'].unique(), default=df['Channel'].unique())
selected_payment = st.sidebar.multiselect("Payment Type", options=df['PaymentType'].unique(), default=df['PaymentType'].unique())
feedback_min, feedback_max = st.sidebar.slider("Feedback Score Range", float(df['FeedbackScore'].min()), float(df['FeedbackScore'].max()), (float(df['FeedbackScore'].min()), float(df['FeedbackScore'].max())))

# Filter data
filtered_df = df[
    (df['Date'] >= pd.to_datetime(date_range[0])) &
    (df['Date'] <= pd.to_datetime(date_range[1])) &
    (df['Gender'].isin(selected_genders)) &
    (df['ProductVariant'].isin(selected_products)) &
    (df['Location'].isin(selected_locations)) &
    (df['Channel'].isin(selected_channel)) &
    (df['PaymentType'].isin(selected_payment)) &
    (df['FeedbackScore'] >= feedback_min) &
    (df['FeedbackScore'] <= feedback_max)
]

# ---- Main Dashboard ----
st.title("Health Drink Sales Analytics Dashboard")
st.markdown("Welcome! This dashboard provides a 360-degree view of factors influencing health drink sales. Use the sidebar to filter and interact with the data. Each chart includes a brief explanation.")

tabs = st.tabs([
    "Executive Summary", "Sales Trends", "Product Insights", 
    "Customer Insights", "Channel Analysis", "Advanced Analytics"
])

# -- Tab 1: Executive Summary --
with tabs[0]:
    st.subheader("Key Sales Metrics")
    st.markdown("A high-level overview for quick insight into overall performance.")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Sales", f"${filtered_df['Total Sale Value'].sum():,.2f}")
    col2.metric("Total Units Sold", f"{filtered_df['UnitsPurchased'].sum():,.0f}")
    col3.metric("Unique Customers", filtered_df['CustomerID'].nunique())
    col4.metric("Avg. Feedback Score", f"{filtered_df['FeedbackScore'].mean():.2f}")

    st.markdown("**Monthly Sales Trend:** How sales are evolving over time.")
    monthly_sales = filtered_df.groupby(filtered_df['Date'].dt.to_period('M')).agg({'Total Sale Value':'sum'}).reset_index()
    monthly_sales['Date'] = monthly_sales['Date'].astype(str)
    fig = px.line(monthly_sales, x='Date', y='Total Sale Value', title="Monthly Sales Trend")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Sales by Product Variant:** Snapshot of top-performing products.")
    sales_by_variant = filtered_df.groupby('ProductVariant')['Total Sale Value'].sum().reset_index()
    fig = px.bar(sales_by_variant, x='ProductVariant', y='Total Sale Value', title="Sales by Product Variant")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Sales by Channel:** Where are most of our sales coming from?")
    fig = px.pie(filtered_df, values='Total Sale Value', names='Channel', title='Sales Distribution by Channel', hole=0.4)
    st.plotly_chart(fig, use_container_width=True)

# -- Tab 2: Sales Trends --
with tabs[1]:
    st.subheader("Sales Trends & Seasonality")
    st.markdown("Detailed breakdown of sales over different dimensions to spot patterns and seasonality.")

    st.markdown("**Daily Sales Line Plot:** Track daily fluctuations in sales.")
    daily_sales = filtered_df.groupby('Date')['Total Sale Value'].sum().reset_index()
    fig = px.line(daily_sales, x='Date', y='Total Sale Value', title='Daily Sales')
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Sales by Day of Week:** Identify best and worst performing days.")
    filtered_df['DayOfWeek'] = filtered_df['Date'].dt.day_name()
    day_sales = filtered_df.groupby('DayOfWeek')['Total Sale Value'].sum().reset_index()
    day_order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    day_sales['DayOfWeek'] = pd.Categorical(day_sales['DayOfWeek'], categories=day_order, ordered=True)
    day_sales = day_sales.sort_values('DayOfWeek')
    fig = px.bar(day_sales, x='DayOfWeek', y='Total Sale Value', title='Sales by Day of Week')
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Units Sold by Month:** Seasonality in product demand.")
    filtered_df['Month'] = filtered_df['Date'].dt.strftime('%b')
    month_units = filtered_df.groupby('Month')['UnitsPurchased'].sum().reindex(
        ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']).reset_index()
    fig = px.bar(month_units, x='Month', y='UnitsPurchased', title='Units Sold by Month')
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Heatmap of Sales by Day and Product:** Visualize weekly product demand.")
    pivot = pd.pivot_table(filtered_df, index='DayOfWeek', columns='ProductVariant', values='Total Sale Value', aggfunc='sum')
    fig, ax = plt.subplots()
    sns.heatmap(pivot, annot=True, fmt=".0f", cmap='Blues', ax=ax)
    st.pyplot(fig, use_container_width=True)

# -- Tab 3: Product Insights --
with tabs[2]:
    st.subheader("Product Variant Performance")
    st.markdown("Analyze which product variants drive the most value and why.")

    st.markdown("**Sales by Product Variant:** Top and bottom performers.")
    fig = px.bar(sales_by_variant, x='ProductVariant', y='Total Sale Value', color='ProductVariant', title='Sales by Product Variant')
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Average Feedback Score by Product:** Customer satisfaction for each variant.")
    feedback_by_prod = filtered_df.groupby('ProductVariant')['FeedbackScore'].mean().reset_index()
    fig = px.bar(feedback_by_prod, x='ProductVariant', y='FeedbackScore', title='Avg Feedback Score by Product')
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Units Sold Distribution per Product:** Spread of sales for each variant.")
    fig = px.box(filtered_df, x='ProductVariant', y='UnitsPurchased', title='Units Purchased Distribution by Product')
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Product Sales by Channel:** Which products sell where?")
    fig = px.bar(filtered_df, x='ProductVariant', y='Total Sale Value', color='Channel', barmode='group', title='Product Sales by Channel')
    st.plotly_chart(fig, use_container_width=True)

# -- Tab 4: Customer Insights --
with tabs[3]:
    st.subheader("Customer Demographics & Behaviour")
    st.markdown("Who is buying our drinks and how do their characteristics affect sales?")

    st.markdown("**Sales by Age Group:** Are there age trends in consumption?")
    bins = [0, 18, 25, 35, 45, 60, 100]
    labels = ['<18', '18-25', '26-35', '36-45', '46-60', '60+']
    filtered_df['AgeGroup'] = pd.cut(filtered_df['Age'], bins=bins, labels=labels, right=False)
    age_sales = filtered_df.groupby('AgeGroup')['Total Sale Value'].sum().reset_index()
    fig = px.bar(age_sales, x='AgeGroup', y='Total Sale Value', title='Sales by Age Group')
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Gender-wise Sales:** Distribution between male and female buyers.")
    fig = px.pie(filtered_df, names='Gender', values='Total Sale Value', title='Sales by Gender', hole=0.3)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Location-wise Sales:** Geographical concentration of sales.")
    fig = px.bar(filtered_df.groupby('Location')['Total Sale Value'].sum().reset_index(), x='Location', y='Total Sale Value', title='Sales by Location')
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Feedback Score Distribution:** How do customers rate their experience?")
    fig = px.histogram(filtered_df, x='FeedbackScore', nbins=20, title='Feedback Score Distribution')
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Sales by Payment Type:** Customer preferences in payment.")
    fig = px.bar(filtered_df.groupby('PaymentType')['Total Sale Value'].sum().reset_index(), x='PaymentType', y='Total Sale Value', title='Sales by Payment Type')
    st.plotly_chart(fig, use_container_width=True)

# -- Tab 5: Channel Analysis --
with tabs[4]:
    st.subheader("Channel & Payment Analysis")
    st.markdown("Deep dive into how different channels and payment methods drive performance.")

    st.markdown("**Sales Split by Channel and Month:** Are there seasonal patterns by channel?")
    channel_month = filtered_df.copy()
    channel_month['Month'] = channel_month['Date'].dt.strftime('%b')
    sales_by_channel_month = channel_month.groupby(['Channel', 'Month'])['Total Sale Value'].sum().reset_index()
    fig = px.bar(sales_by_channel_month, x='Month', y='Total Sale Value', color='Channel', barmode='group', title='Channel-wise Sales by Month')
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Units Sold by Channel:** Which channel sells more units?")
    fig = px.box(filtered_df, x='Channel', y='UnitsPurchased', title='Units Purchased by Channel')
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Average Sale Value per Transaction by Channel:**")
    avg_sale = filtered_df.groupby('Channel')['Total Sale Value'].mean().reset_index()
    fig = px.bar(avg_sale, x='Channel', y='Total Sale Value', title='Avg Sale Value per Transaction by Channel')
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Sales by Channel & Payment Type:** How are people paying across channels?")
    sales_pay = filtered_df.groupby(['Channel', 'PaymentType'])['Total Sale Value'].sum().reset_index()
    fig = px.bar(sales_pay, x='Channel', y='Total Sale Value', color='PaymentType', barmode='group', title='Channel vs Payment Type Sales')
    st.plotly_chart(fig, use_container_width=True)

# -- Tab 6: Advanced Analytics --
with tabs[5]:
    st.subheader("Advanced Analytics & Correlations")
    st.markdown("Explore relationships between sales drivers and outcomes.")

    st.markdown("**Correlation Heatmap:** See how factors move together.")
    cols = ['UnitsPurchased', 'UnitPrice', 'FeedbackScore', 'Total Sale Value', 'Age']
    fig, ax = plt.subplots()
    sns.heatmap(filtered_df[cols].corr(), annot=True, cmap='viridis', ax=ax)
    st.pyplot(fig, use_container_width=True)

    st.markdown("**Units Purchased vs. Feedback Score:** Any relationship?")
    fig = px.scatter(filtered_df, x='FeedbackScore', y='UnitsPurchased', trendline='ols', title='Units Purchased vs Feedback Score')
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Total Sale Value vs. Age:** Do older customers spend more?")
    fig = px.scatter(filtered_df, x='Age', y='Total Sale Value', trendline='ols', title='Sale Value vs Age')
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Boxplot: Sale Value by Payment Type**")
    fig = px.box(filtered_df, x='PaymentType', y='Total Sale Value', title='Sale Value Distribution by Payment')
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Top 10 Customers by Sales Value:**")
    top_cust = filtered_df.groupby('CustomerID')['Total Sale Value'].sum().reset_index().sort_values('Total Sale Value', ascending=False).head(10)
    fig = px.bar(top_cust, x='CustomerID', y='Total Sale Value', title='Top 10 Customers by Sales')
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Distribution of Unit Price:**")
    fig = px.histogram(filtered_df, x='UnitPrice', nbins=20, title='Distribution of Unit Price')
    st.plotly_chart(fig, use_container_width=True)

# ---- End of dashboard ----
