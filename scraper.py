import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import random
import time
import os

class AirlineScraper:
    def __init__(self):
        """Initialize the scraper with proper headers"""
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Australian city codes and names
        self.cities = {
            'SYD': 'Sydney',
            'MEL': 'Melbourne', 
            'BNE': 'Brisbane',
            'PER': 'Perth',
            'ADL': 'Adelaide',
            'DRW': 'Darwin',
            'CBR': 'Canberra',
            'HBA': 'Hobart'
        }
        
    def scrape_flight_data(self, origin='SYD', destination='MEL', days=7):
        """
        Simulate flight data scraping with realistic airline booking data
        In a real scenario, this would scrape from actual airline websites or APIs
        """
        print(f"🛫 Scraping flight data from {self.cities.get(origin, origin)} to {self.cities.get(destination, destination)} for {days} days...")
        
        # Simulate API call delay
        time.sleep(random.uniform(1, 3))
        
        # Generate realistic sample data
        flights = []
        airlines = ['Jetstar', 'Virgin Australia', 'Qantas', 'Tiger Air']
        base_prices = {
            'Jetstar': 120,
            'Tiger Air': 110, 
            'Virgin Australia': 170,
            'Qantas': 200
        }
        
        # Flight prefixes for each airline
        airline_prefixes = {
            'Jetstar': 'JQ',
            'Virgin Australia': 'VA',
            'Qantas': 'QF',
            'Tiger Air': 'TT'
        }
        
        aircraft_types = ['Boeing 737', 'Airbus A320', 'Boeing 787', 'Airbus A330']
        
        for day in range(days):
            date = datetime.now() + timedelta(days=day)
            date_str = date.strftime('%Y-%m-%d')
            
            # More flights on weekdays, fewer on weekends
            is_weekend = date.weekday() >= 5
            daily_flights = random.randint(12, 20) if is_weekend else random.randint(18, 30)
            
            # Generate departure times throughout the day
            departure_times = self._generate_departure_times(daily_flights)
            
            for i, departure_time in enumerate(departure_times):
                airline = random.choice(airlines)
                base_price = base_prices[airline]
                
                # Price variations based on time of day and demand
                time_hour = int(departure_time.split(':')[0])
                
                # Peak hours (7-9am, 5-7pm) are more expensive
                if (7 <= time_hour <= 9) or (17 <= time_hour <= 19):
                    price_multiplier = random.uniform(1.2, 1.5)
                # Late night/early morning cheaper
                elif time_hour <= 6 or time_hour >= 22:
                    price_multiplier = random.uniform(0.8, 1.0)
                else:
                    price_multiplier = random.uniform(0.9, 1.2)
                
                # Weekend vs weekday pricing
                if is_weekend:
                    price_multiplier *= random.uniform(1.1, 1.3)
                
                # Advance booking discount (further dates cheaper)
                advance_discount = max(0.8, 1 - (day * 0.02))
                
                final_price = int(base_price * price_multiplier * advance_discount + random.randint(-20, 30))
                final_price = max(80, final_price)  # Minimum price floor
                
                # Seat availability (higher demand = fewer seats)
                if price_multiplier > 1.3:  # High demand
                    available_seats = random.randint(5, 30)
                elif price_multiplier < 0.9:  # Low demand
                    available_seats = random.randint(60, 120)
                else:  # Normal demand
                    available_seats = random.randint(25, 80)
                
                flight = {
                    'airline': airline,
                    'flight_number': f"{airline_prefixes[airline]}{random.randint(100, 999)}",
                    'origin': origin,
                    'destination': destination,
                    'departure_time': departure_time,
                    'price': final_price,
                    'date': date_str,
                    'available_seats': available_seats,
                    'aircraft_type': random.choice(aircraft_types),
                    'duration': self._calculate_duration(origin, destination)
                }
                flights.append(flight)
        
        # Sort flights by date and time
        flights.sort(key=lambda x: (x['date'], x['departure_time']))
        
        # Save data
        self._save_data(flights)
        print(f"✅ Successfully scraped {len(flights)} flights!")
        
        return flights
    
    def _generate_departure_times(self, count):
        """Generate realistic departure times throughout the day"""
        times = []
        
        # Common departure time slots
        time_slots = [
            '06:00', '06:30', '07:00', '07:30', '08:00', '08:30', '09:00', '09:30',
            '10:00', '10:30', '11:00', '11:30', '12:00', '12:30', '13:00', '13:30',
            '14:00', '14:30', '15:00', '15:30', '16:00', '16:30', '17:00', '17:30',
            '18:00', '18:30', '19:00', '19:30', '20:00', '20:30', '21:00', '21:30'
        ]
        
        # Select random times, but ensure variety
        selected_times = random.sample(time_slots, min(count, len(time_slots)))
        
        # If we need more flights than available slots, add some with :15 and :45 minutes
        if count > len(selected_times):
            additional_times = []
            for i in range(count - len(selected_times)):
                hour = random.randint(6, 21)
                minute = random.choice(['15', '45'])
                additional_times.append(f"{hour:02d}:{minute}")
            selected_times.extend(additional_times)
        
        return sorted(selected_times[:count])
    
    def _calculate_duration(self, origin, destination):
        """Calculate realistic flight duration between cities"""
        # Approximate flight durations between major Australian cities (in minutes)
        durations = {
            ('SYD', 'MEL'): 85, ('MEL', 'SYD'): 85,
            ('SYD', 'BNE'): 95, ('BNE', 'SYD'): 95,
            ('SYD', 'PER'): 300, ('PER', 'SYD'): 300,
            ('SYD', 'ADL'): 120, ('ADL', 'SYD'): 120,
            ('MEL', 'BNE'): 140, ('BNE', 'MEL'): 140,
            ('MEL', 'PER'): 210, ('PER', 'MEL'): 210,
            ('MEL', 'ADL'): 80, ('ADL', 'MEL'): 80,
            ('BNE', 'PER'): 280, ('PER', 'BNE'): 280,
            ('BNE', 'ADL'): 140, ('ADL', 'BNE'): 140,
            ('PER', 'ADL'): 135, ('ADL', 'PER'): 135,
        }
        
        route = (origin, destination)
        base_duration = durations.get(route, 120)  # Default 2 hours
        
        # Add some variation (±15 minutes)
        actual_duration = base_duration + random.randint(-15, 15)
        
        hours = actual_duration // 60
        minutes = actual_duration % 60
        
        return f"{hours}h {minutes}m"
    
    def _save_data(self, data):
        """Save scraped data to JSON file"""
        try:
            os.makedirs('data', exist_ok=True)
            
            flight_data = {
                'timestamp': datetime.now().isoformat(),
                'total_flights': len(data),
                'routes': f"{data[0]['origin']} → {data[0]['destination']}" if data else "Unknown",
                'date_range': {
                    'start': data[0]['date'] if data else None,
                    'end': data[-1]['date'] if data else None
                },
                'flights': data
            }
            
            with open('data/airline_data.json', 'w') as f:
                json.dump(flight_data, f, indent=2, default=str)
            
            print(f"💾 Data saved to data/airline_data.json")
            
        except Exception as e:
            print(f"❌ Error saving data: {e}")
    
    def get_available_routes(self):
        """Return available city routes"""
        return {
            'cities': self.cities,
            'popular_routes': [
                ('SYD', 'MEL'), ('MEL', 'SYD'),
                ('SYD', 'BNE'), ('BNE', 'SYD'),
                ('MEL', 'BNE'), ('BNE', 'MEL'),
                ('SYD', 'PER'), ('PER', 'SYD')
            ]
        }
        
    def scrape_real_data(self, origin, destination, days):
        """
        Placeholder for real web scraping functionality
        This would implement actual scraping from airline websites
        """
        # This is where you would implement real scraping logic
        # using requests and BeautifulSoup to scrape actual airline websites
        # For now, it falls back to simulated data
        
        print("🚧 Real scraping not implemented yet - using simulated data")
        return self.scrape_flight_data(origin, destination, days)