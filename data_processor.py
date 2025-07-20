import pandas as pd
import plotly.graph_objs as go
import plotly.utils
from datetime import datetime
import json
import numpy as np

class DataProcessor:
    def __init__(self):
        pass
    
    def _convert_numpy_types(self, obj):
        """Convert numpy types to native Python types for JSON serialization"""
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {key: self._convert_numpy_types(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_numpy_types(item) for item in obj]
        else:
            return obj
    
    def process_data(self, flight_data):
        """Process raw flight data and extract insights"""
        df = pd.DataFrame(flight_data)
        
        insights = {
            'total_flights': int(len(df)),
            'average_price': float(round(df['price'].mean(), 2)),
            'price_range': {
                'min': int(df['price'].min()),
                'max': int(df['price'].max())
            },
            'popular_airlines': self._convert_numpy_types(df['airline'].value_counts().to_dict()),
            'daily_trends': self._analyze_daily_trends(df),
            'price_trends': self._analyze_price_trends(df),
            'demand_analysis': self._analyze_demand(df),
            'recommendations': self._generate_recommendations(df)
        }
        
        return insights
    
    def _analyze_daily_trends(self, df):
        """Analyze flight trends by day"""
        daily_stats = df.groupby('date').agg({
            'price': ['mean', 'count'],
            'available_seats': 'mean'
        }).round(2)
        
        trends = {}
        for date in daily_stats.index:
            trends[date] = {
                'avg_price': float(daily_stats.loc[date, ('price', 'mean')]),
                'flight_count': int(daily_stats.loc[date, ('price', 'count')]),
                'avg_seats': float(daily_stats.loc[date, ('available_seats', 'mean')])
            }
        
        return trends
    
    def _analyze_price_trends(self, df):
        """Analyze price trends across different factors"""
        price_by_airline = df.groupby('airline')['price'].mean()
        price_by_time = df.groupby(df['departure_time'].str[:2])['price'].mean()
        
        return {
            'by_airline': self._convert_numpy_types(price_by_airline.to_dict()),
            'by_time_of_day': self._convert_numpy_types(price_by_time.to_dict())
        }
    
    def _analyze_demand(self, df):
        """Analyze demand patterns"""
        df = df.copy()  # Avoid modifying original dataframe
        df['occupancy_rate'] = ((180 - df['available_seats']) / 180) * 100
        
        high_demand_threshold = 70
        high_demand_flights = df[df['occupancy_rate'] >= high_demand_threshold]
        
        demand_analysis = {
            'average_occupancy': float(round(df['occupancy_rate'].mean(), 2)),
            'high_demand_flights': int(len(high_demand_flights)),
            'peak_demand_airlines': self._convert_numpy_types(
                high_demand_flights['airline'].value_counts().to_dict()
            ),
            'peak_demand_times': self._convert_numpy_types(
                high_demand_flights['departure_time'].str[:2].value_counts().to_dict()
            )
        }
        
        return demand_analysis
    
    def _generate_recommendations(self, df):
        """Generate actionable recommendations"""
        recommendations = []
        
        try:
            # Price recommendations
            cheapest_airline = df.groupby('airline')['price'].mean().idxmin()
            cheapest_price = float(df.groupby('airline')['price'].mean().min())
            recommendations.append(f"💰 Best value airline: {cheapest_airline} (avg $${cheapest_price:.0f})")
            
            # Time recommendations
            time_prices = df.groupby(df['departure_time'].str[:2])['price'].mean()
            cheapest_time = time_prices.idxmin()
            cheapest_time_price = float(time_prices.min())
            recommendations.append(f"🕐 Cheapest departure time: {cheapest_time}:00 (avg $${cheapest_time_price:.0f})")
            
            # Demand recommendations
            df_copy = df.copy()
            df_copy['occupancy_rate'] = ((180 - df_copy['available_seats']) / 180) * 100
            low_demand_days = df_copy.groupby('date')['occupancy_rate'].mean().sort_values()
            
            if len(low_demand_days) > 0:
                best_date = low_demand_days.index[0]
                best_occupancy = float(low_demand_days.iloc[0])
                recommendations.append(f"📅 Best availability on: {best_date} ({best_occupancy:.1f}% occupied)")
            
            # Price range insight
            price_std = float(df['price'].std())
            if price_std > 30:
                recommendations.append(f"📊 High price variation detected (±${price_std:.0f}) - timing matters!")
            else:
                recommendations.append(f"📊 Consistent pricing across flights (±${price_std:.0f})")
            
            # Availability insight
            avg_seats = float(df['available_seats'].mean())
            if avg_seats < 30:
                recommendations.append(f"⚠️ High demand route - book early! (avg {avg_seats:.0f} seats left)")
            else:
                recommendations.append(f"✅ Good availability - flexible booking possible (avg {avg_seats:.0f} seats)")
        
        except Exception as e:
            print(f"Error generating recommendations: {e}")
            recommendations.append("📊 Data analysis completed - check charts for insights")
        
        return recommendations
    
    def generate_charts(self, insights):
        """Generate Plotly charts for visualization"""
        charts = {}
        
        try:
            # Price trend chart
            dates = list(insights['daily_trends'].keys())
            prices = [insights['daily_trends'][date]['avg_price'] for date in dates]
            
            price_chart = go.Figure()
            price_chart.add_trace(go.Scatter(
                x=dates,
                y=prices,
                mode='lines+markers',
                name='Average Price',
                line=dict(color='#1f77b4', width=3),
                marker=dict(size=8)
            ))
            price_chart.update_layout(
                title='Daily Price Trends',
                xaxis_title='Date',
                yaxis_title='Average Price (AUD $)',
                template='plotly_white',
                height=400,
                showlegend=False
            )
            
            charts['price_trend'] = json.dumps(price_chart, cls=plotly.utils.PlotlyJSONEncoder)
            
            # Airline popularity chart
            airlines = list(insights['popular_airlines'].keys())
            counts = list(insights['popular_airlines'].values())
            
            airline_chart = go.Figure()
            airline_chart.add_trace(go.Bar(
                x=airlines,
                y=counts,
                marker_color=['#ff7f0e', '#2ca02c', '#d62728', '#9467bd'],
                text=counts,
                textposition='auto'
            ))
            airline_chart.update_layout(
                title='Flight Frequency by Airline',
                xaxis_title='Airline',
                yaxis_title='Number of Flights',
                template='plotly_white',
                height=400,
                showlegend=False
            )
            
            charts['airline_popularity'] = json.dumps(airline_chart, cls=plotly.utils.PlotlyJSONEncoder)
            
        except Exception as e:
            print(f"Error generating charts: {e}")
            # Return empty charts if there's an error
            charts = {
                'price_trend': json.dumps({'data': [], 'layout': {}}),
                'airline_popularity': json.dumps({'data': [], 'layout': {}})
            }
        
        return charts