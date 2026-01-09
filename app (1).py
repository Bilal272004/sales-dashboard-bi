import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Page Configuration
st.set_page_config(
    page_title="Sales Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    h1 {
        color: #1f77b4;
        font-family: 'Arial', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# Cache data loading for performance
@st.cache_data
def load_data():
    """Load and preprocess the sales dataset"""
    try:
        # Load data
        df = pd.read_excel('Sales_Data_PowerBI.xlsx')
        
        # Handle missing values
        df = df.dropna()
        
        # Convert Order_Date to datetime - FIXED VERSION
        df['Order_Date'] = pd.to_datetime(df['Order_Date'])
        
        # Add calculated columns
        df['Profit_Percentage'] = (df['Profit'] / df['Sales']) * 100
        df['Month'] = df['Order_Date'].dt.month_name()
        df['Month_Number'] = df['Order_Date'].dt.month
        df['Year'] = df['Order_Date'].dt.year
        df['Quarter'] = 'Q' + df['Order_Date'].dt.quarter.astype(str)
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

# Load data
df = load_data()

if df is not None:
    # ===== HEADER =====
    st.title("📊 Sales Dashboard - Business Intelligence")
    st.markdown("""
    **Interactive Sales Analytics Dashboard**  
    This dashboard provides comprehensive insights into sales performance across products, 
    categories, regions, and customer segments. Use the sidebar filters to explore data dynamically.
    """)
    st.markdown("---")

    # ===== SIDEBAR FILTERS =====
    st.sidebar.header("🔍 Filters")
    
    # Date Range Filter
    st.sidebar.subheader("📅 Date Range")
    min_date = df['Order_Date'].min().date()
    max_date = df['Order_Date'].max().date()
    
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Category Filter
    st.sidebar.subheader("📦 Category")
    categories = ['All'] + sorted(df['Category'].unique().tolist())
    selected_category = st.sidebar.selectbox("Select Category", categories)
    
    # Region Filter
    st.sidebar.subheader("🌍 Region")
    regions = ['All'] + sorted(df['Region'].unique().tolist())
    selected_region = st.sidebar.selectbox("Select Region", regions)
    
    # Customer Segment Filter
    st.sidebar.subheader("👥 Customer Segment")
    segments = ['All'] + sorted(df['Customer_Segment'].unique().tolist())
    selected_segment = st.sidebar.selectbox("Select Segment", segments)
    
    # Price Range Slider
    st.sidebar.subheader("💰 Sales Range")
    min_sales = float(df['Sales'].min())
    max_sales = float(df['Sales'].max())
    sales_range = st.sidebar.slider(
        "Select Sales Range",
        min_value=min_sales,
        max_value=max_sales,
        value=(min_sales, max_sales)
    )
    
    # ===== APPLY FILTERS =====
    filtered_df = df.copy()
    
    # Filter by date range
    if len(date_range) == 2:
        start_date = pd.to_datetime(date_range[0])
        end_date = pd.to_datetime(date_range[1])
        filtered_df = filtered_df[
            (filtered_df['Order_Date'] >= start_date) & 
            (filtered_df['Order_Date'] <= end_date)
        ]
    
    # Filter by category
    if selected_category != 'All':
        filtered_df = filtered_df[filtered_df['Category'] == selected_category]
    
    # Filter by region
    if selected_region != 'All':
        filtered_df = filtered_df[filtered_df['Region'] == selected_region]
    
    # Filter by segment
    if selected_segment != 'All':
        filtered_df = filtered_df[filtered_df['Customer_Segment'] == selected_segment]
    
    # Filter by sales range
    filtered_df = filtered_df[
        (filtered_df['Sales'] >= sales_range[0]) & 
        (filtered_df['Sales'] <= sales_range[1])
    ]
    
    # ===== KPI METRICS =====
    st.subheader("📈 Key Performance Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_sales = filtered_df['Sales'].sum()
    total_profit = filtered_df['Profit'].sum()
    total_quantity = filtered_df['Quantity'].sum()
    avg_order_value = filtered_df['Sales'].mean()
    
    with col1:
        st.metric(
            label="💰 Total Sales",
            value=f"${total_sales:,.0f}",
            delta=f"{len(filtered_df)} orders"
        )
    
    with col2:
        st.metric(
            label="📊 Total Profit",
            value=f"${total_profit:,.0f}",
            delta=f"{(total_profit/total_sales)*100:.1f}% margin"
        )
    
    with col3:
        st.metric(
            label="📦 Total Quantity",
            value=f"{total_quantity:,}",
            delta="units sold"
        )
    
    with col4:
        st.metric(
            label="🛒 Avg Order Value",
            value=f"${avg_order_value:,.2f}",
            delta="per order"
        )
    
    st.markdown("---")
    
    # ===== VISUALIZATIONS =====
    
    # Row 1: Line Chart and Bar Chart
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Monthly Sales Trend")
        # Group by month and calculate total sales
        monthly_sales = filtered_df.groupby('Month_Number')['Sales'].sum().reset_index()
        monthly_sales = monthly_sales.sort_values('Month_Number')
        
        # Create line chart
        fig_line = px.line(
            monthly_sales,
            x='Month_Number',
            y='Sales',
            title='Sales Trend Over Time',
            labels={'Month_Number': 'Month', 'Sales': 'Total Sales ($)'},
            markers=True
        )
        fig_line.update_traces(line_color='#1f77b4', line_width=3)
        fig_line.update_layout(
            xaxis=dict(tickmode='linear', tick0=1, dtick=1),
            hovermode='x unified'
        )
        st.plotly_chart(fig_line, use_container_width=True)
    
    with col2:
        st.subheader("📊 Sales by Category")
        # Group by category
        category_sales = filtered_df.groupby('Category')['Sales'].sum().reset_index()
        category_sales = category_sales.sort_values('Sales', ascending=False)
        
        # Create bar chart
        fig_bar = px.bar(
            category_sales,
            x='Category',
            y='Sales',
            title='Category-wise Performance',
            labels={'Sales': 'Total Sales ($)'},
            color='Sales',
            color_continuous_scale='Blues'
        )
        fig_bar.update_layout(showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Row 2: Pie Chart and Top 10 Table
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🥧 Sales by Region")
        # Group by region
        region_sales = filtered_df.groupby('Region')['Sales'].sum().reset_index()
        
        # Create pie chart
        fig_pie = px.pie(
            region_sales,
            values='Sales',
            names='Region',
            title='Regional Distribution',
            hole=0.4,  # Makes it a donut chart
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        st.subheader("🏆 Top 10 Products by Sales")
        # Get top 10 products
        top_products = filtered_df.groupby('Product').agg({
            'Sales': 'sum',
            'Quantity': 'sum',
            'Profit': 'sum'
        }).reset_index()
        top_products = top_products.sort_values('Sales', ascending=False).head(10)
        top_products = top_products.reset_index(drop=True)
        top_products.index = top_products.index + 1
        
        # Format numbers
        top_products['Sales'] = top_products['Sales'].apply(lambda x: f"${x:,.2f}")
        top_products['Profit'] = top_products['Profit'].apply(lambda x: f"${x:,.2f}")
        
        # Display table
        st.dataframe(
            top_products,
            use_container_width=True,
            height=400
        )
    
    st.markdown("---")
    
    # Row 3: Customer Segment Distribution
    st.subheader("👥 Sales by Customer Segment")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Segment bar chart
        segment_sales = filtered_df.groupby('Customer_Segment')['Sales'].sum().reset_index()
        segment_sales = segment_sales.sort_values('Sales', ascending=False)
        
        fig_segment = px.bar(
            segment_sales,
            x='Customer_Segment',
            y='Sales',
            title='Sales Distribution by Customer Segment',
            labels={'Customer_Segment': 'Segment', 'Sales': 'Total Sales ($)'},
            color='Customer_Segment',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig_segment, use_container_width=True)
    
    with col2:
        # Summary statistics
        st.markdown("### 📊 Summary Statistics")
        st.metric("Total Orders", len(filtered_df))
        st.metric("Unique Products", filtered_df['Product'].nunique())
        st.metric("Avg Profit %", f"{filtered_df['Profit_Percentage'].mean():.1f}%")
        st.metric("Date Range", f"{len(filtered_df['Order_Date'].dt.date.unique())} days")
    
    # ===== FOOTER =====
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray;'>
        <p>📊 Business Intelligence Dashboard | Created with Streamlit & Python</p>
        <p>Muhammad Bilal | CMS: 22F-BSBIS-37 | CSE-4771</p>
    </div>
    """, unsafe_allow_html=True)

else:
    st.error("⚠️ Unable to load data. Please ensure 'Sales_Data_PowerBI.xlsx' is in the same folder as this script.")
    st.info("Expected file: Sales_Data_PowerBI.xlsx")
