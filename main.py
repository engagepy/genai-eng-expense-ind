import os
import openai
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def init_styling():
    st.markdown("""
        <style>
        .main {
            background-color: #0e1117;
        }
        .stApp {
            max-width: 100%;
            margin: 0 auto;
            padding: 0 20px;
        }
        .title-gradient {
            background: linear-gradient(90deg, #FF6B6B, #FF8E53);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.5rem;
            font-weight: bold;
            text-align: center;
            margin-bottom: 1rem;
            letter-spacing: -0.5px;
        }
        .subtitle-gradient {
            background: linear-gradient(90deg, #FF8E53, #FFA41B);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 1.5rem;
            text-align: center;
            margin-bottom: 2rem;
        }
        .cards-scroll-container {
            overflow-x: auto;
            padding: 20px 0;
            margin: 20px -20px;
            -webkit-overflow-scrolling: touch;
        }
        .card-container {
            display: flex;
            justify-content: center;
            gap: 20px;
            padding: 0 20px;
            min-width: min-content;
            margin: 0 auto;
            flex-wrap: wrap;
        }
        .card {
            background: linear-gradient(145deg, rgba(20, 20, 30, 0.9), rgba(30, 30, 45, 0.9));
            border: 1px solid rgba(255, 107, 107, 0.1);
            border-radius: 20px;
            padding: 25px;
            flex: 1 1 280px;
            max-width: 300px;
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 20px rgba(255, 107, 107, 0.2);
        }
        .card-title {
            background: linear-gradient(90deg, #FF6B6B, #FF8E53);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 1.4rem;
            font-weight: bold;
            margin-bottom: 15px;
            text-align: center;
        }
        .card-description {
            color: #E0E0E0;
            font-size: 1.1rem;
            line-height: 1.5;
            text-align: center;
        }
        /* Center button container */
        .button-container {
            display: flex;
            justify-content: center;
            width: 100%;
            margin: 20px 0;
        }
        /* Updated button styling */
        .stButton > button {
            background: linear-gradient(90deg, #FF6B6B, #FF8E53) !important;
            color: white !important;
            border: none !important;
            border-radius: 10px !important;
            padding: 12px 30px !important;
            font-size: 1.2rem !important;
            cursor: pointer !important;
            transition: transform 0.2s ease !important;
            width: auto !important;
        }
        .stButton > button:hover {
            transform: scale(1.05) !important;
            background: linear-gradient(90deg, #FF8E53, #FF6B6B) !important;
        }
        .metric-container {
            background: linear-gradient(145deg, rgba(20, 20, 30, 0.9), rgba(30, 30, 45, 0.9));
            border-radius: 15px;
            padding: 20px;
            margin: 10px 0;
        }
        .stMetric {
            background-color: transparent !important;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: rgba(255, 107, 107, 0.1);
            border-radius: 4px;
            color: #FF8E53;
        }
        .stTabs [data-baseweb="tab-highlight"] {
            background-color: #FF6B6B;
        }
        </style>
    """, unsafe_allow_html=True)


def calculate_expenses(junior_count=0, mid_count=0, senior_count=0):
    salary_expenses = {
        'Junior': junior_count * 1500000,
        'Mid': mid_count * 3000000,
        'Senior': senior_count * 6000000
    }
    
    total_employees = junior_count + mid_count + senior_count
    office_expense = total_employees * 15000 * 12
    legal_expense = total_employees * 5000
    accounting_expense = total_employees * 5000
    # Scale device and training cost by number of employees
    device_training = 200000 * total_employees

    total_expense = (sum(salary_expenses.values()) + 
                     office_expense + 
                     legal_expense + 
                     accounting_expense + 
                     device_training)
    
    return {
        'salary_breakdown': salary_expenses,
        'office_expense': office_expense,
        'legal_expense': legal_expense,
        'accounting_expense': accounting_expense,
        'device_training': device_training,
        'total_expense': total_expense,
        'total_employees': total_employees
    }

def project_growth(initial_expenses, years=5):
    inflation_rate = 0.09
    quarterly_team_growth = 0.015
    quarters = years * 4
    projections = []
    
    # Initialize starting values
    current_employees = initial_expenses['total_employees']
    base_salary = sum(initial_expenses['salary_breakdown'].values())
    base_office = initial_expenses['office_expense']
    base_legal = initial_expenses['legal_expense']
    base_accounting = initial_expenses['accounting_expense']
    device_training = initial_expenses['device_training']

    for quarter in range(quarters):
        year = quarter // 4
        # Update employee count
        current_employees = initial_expenses['total_employees'] * (1 + quarterly_team_growth)**(quarter + 1)
        
        # Calculate factors
        inflation_factor = (1 + inflation_rate)**(year + 1)
        employee_factor = current_employees / initial_expenses['total_employees']
        
        # Convert annual expenses to quarterly expenses
        quarterly_salary = (base_salary * inflation_factor * employee_factor) / 4
        quarterly_office = (base_office * inflation_factor * employee_factor) / 4
        quarterly_legal = (base_legal * inflation_factor * employee_factor) / 4
        quarterly_accounting = (base_accounting * inflation_factor * employee_factor) / 4

        total_expense = quarterly_salary + quarterly_office + quarterly_legal + quarterly_accounting

        # Add one-time device & training cost only in the first quarter
        if quarter == 0:
            total_expense += device_training
        
        projections.append({
            'Quarter': f'Q{(quarter % 4) + 1} Y{year + 1}',
            'Expenses': total_expense,
            'Employees': current_employees,
            'Salary_Expenses': quarterly_salary,
            'Office_Expenses': quarterly_office,
            'Legal_Expenses': quarterly_legal,
            'Accounting_Expenses': quarterly_accounting
        })
    
    return pd.DataFrame(projections)

def create_expense_breakdown_chart(expenses):
    labels = ['Salary', 'Office', 'Legal', 'Accounting', 'Device & Training']
    values = [
        sum(expenses['salary_breakdown'].values()),
        expenses['office_expense'],
        expenses['legal_expense'],
        expenses['accounting_expense'],
        expenses['device_training']
    ]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=.3,
        marker_colors=['#FF6B6B', '#FF8E53', '#FFA41B', '#FFB649', '#FFCE76']
    )])
    
    fig.update_layout(
        title_text="Expense Breakdown",
        showlegend=True,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    return fig

def create_expense_lines_chart(expenses, projections):
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=projections['Quarter'],
        y=projections['Salary_Expenses'],
        name='Salary',
        line=dict(color='#FF6B6B', width=2)
    ))
    fig.add_trace(go.Scatter(
        x=projections['Quarter'],
        y=projections['Office_Expenses'],
        name='Office',
        line=dict(color='#FF8E53', width=2)
    ))
    fig.add_trace(go.Scatter(
        x=projections['Quarter'],
        y=projections['Legal_Expenses'],
        name='Legal',
        line=dict(color='#FFA41B', width=2)
    ))
    fig.add_trace(go.Scatter(
        x=projections['Quarter'],
        y=projections['Accounting_Expenses'],
        name='Accounting',
        line=dict(color='#FFB649', width=2)
    ))
    
    fig.update_layout(
        title='Expense Category Projections',
        xaxis_title='Time Period',
        yaxis_title='Expenses (INR)',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        showlegend=True
    )
    
    return fig

def main():
   
    st.markdown("<div class='title-gradient'>Engineering Expense Calculator</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle-gradient'>Smart Financial Planning for GenAI Teams</div>", unsafe_allow_html=True)

    with st.container():
        col1, col2, col3 = st.columns(3)
        
        with col1:
            junior_count = st.number_input("Junior Engineers (₹15L/yr)", min_value=0, value=0, step=1)
        with col2:
            mid_count = st.number_input("Mid-Level Engineers (₹30L/yr)", min_value=0, value=0, step=1)
        with col3:
            senior_count = st.number_input("Senior Engineers (₹60L/yr)", min_value=0, value=0, step=1)

        if junior_count + mid_count + senior_count > 0:
            expenses = calculate_expenses(junior_count, mid_count, senior_count)
            projections = project_growth(expenses)
            
            # Calculate yearly totals (sum of all 4 quarters for each year)
            year1_total = projections['Expenses'].iloc[0:4].sum()   # Q1-Q4 Y1
            year2_total = projections['Expenses'].iloc[4:8].sum()   # Q1-Q4 Y2
            year3_total = projections['Expenses'].iloc[8:12].sum()  # Q1-Q4 Y3
            
            # Team size growth calculations for Year 1, Year 2, and Year 3
            team_growth_y1 = ((projections['Employees'].iloc[3] / projections['Employees'].iloc[0]) - 1) * 100
            team_growth_y2 = ((projections['Employees'].iloc[7] / projections['Employees'].iloc[3]) - 1) * 100
            team_growth_y3 = ((projections['Employees'].iloc[11] / projections['Employees'].iloc[7]) - 1) * 100
            
            # 3-year total from summing the first 12 quarters
            total_3_years = projections['Expenses'].iloc[:12].sum()
            
            st.markdown("### Projected Annual Totals")
            y1, y2, y3, total = st.columns(4)
            with y1:
                st.metric(
                    "Year 1 Total",
                    f"₹{year1_total/10000000:.2f}Cr",
                    delta=f"+{team_growth_y1:.2f}% Team | +9% Inf"
                )
            with y2:
                st.metric(
                    "Year 2 Total",
                    f"₹{year2_total/10000000:.2f}Cr",
                    delta=f"+{team_growth_y2:.2f}% Team | +9% Inf"
                )
            with y3:
                st.metric(
                    "Year 3 Total",
                    f"₹{year3_total/10000000:.2f}Cr",
                    delta=f"+{team_growth_y3:.2f}% Team | +9% Inf"
                )
            with total:
                st.metric(
                    "3-Year Total",
                    f"₹{total_3_years/10000000:.2f}Cr"
                )

            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(create_expense_breakdown_chart(expenses), use_container_width=True)
            with col2:
                st.plotly_chart(create_expense_lines_chart(expenses, projections), use_container_width=True)

            st.markdown("### Detailed Expense Projections")
            tab1, tab2, tab3, tab4 = st.tabs(["Salary", "Office", "Legal", "Accounting"])
            
            with tab1:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=projections['Quarter'], y=projections['Salary_Expenses'],
                                         name='Salary', line=dict(color='#FF6B6B')))
                fig.update_layout(title='Salary Expense Projection',
                                  paper_bgcolor='rgba(0,0,0,0)',
                                  plot_bgcolor='rgba(0,0,0,0)',
                                  font=dict(color='white'))
                st.plotly_chart(fig, use_container_width=True)
            
            with tab2:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=projections['Quarter'], y=projections['Office_Expenses'],
                                         name='Office', line=dict(color='#FF8E53')))
                fig.update_layout(title='Office Expense Projection',
                                  paper_bgcolor='rgba(0,0,0,0)',
                                  plot_bgcolor='rgba(0,0,0,0)',
                                  font=dict(color='white'))
                st.plotly_chart(fig, use_container_width=True)
            
            with tab3:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=projections['Quarter'], y=projections['Legal_Expenses'],
                                         name='Legal', line=dict(color='#FFA41B')))
                fig.update_layout(title='Legal Expense Projection',
                                  paper_bgcolor='rgba(0,0,0,0)',
                                  plot_bgcolor='rgba(0,0,0,0)',
                                  font=dict(color='white'))
                st.plotly_chart(fig, use_container_width=True)
            
            with tab4:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=projections['Quarter'], y=projections['Accounting_Expenses'],
                                         name='Accounting', line=dict(color='#FFB649')))
                fig.update_layout(title='Accounting Expense Projection',
                                  paper_bgcolor='rgba(0,0,0,0)',
                                  plot_bgcolor='rgba(0,0,0,0)',
                                  font=dict(color='white'))
                st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
        <div class='cards-scroll-container'>
            <div class='card-container'>
                <div class='card'>
                    <div class='card-title'>Expense Analysis</div>
                    <div class='card-description'>Comprehensive breakdown of team expenses with smart categorization.</div>
                </div>
                <div class='card'>
                    <div class='card-title'>Growth Projections</div>
                    <div class='card-description'>Advanced forecasting with inflation and team growth calculations.</div>
                </div>
                <div class='card'>
                    <div class='card-title'>Cost Optimization</div>
                    <div class='card-description'>Strategic insights for resource allocation and budget planning.</div>
                </div>
                <div class='card'>
                    <div class='card-title'>GenAI Planning</div>
                    <div class='card-description'>Data-driven decision making for sustainable team expansion.</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("<div class='footer-gradient'>© 2024 M37Labs - Augmented Growth Intelligence</div>", unsafe_allow_html=True)

# Initialize the app
st.set_page_config(layout="wide", page_title="Engineering Expense Calculator")
init_styling()

key = os.environ.get('OPENAI_API_KEY')
client = openai.OpenAI(api_key=str(key))

if __name__ == "__main__":
    main()
