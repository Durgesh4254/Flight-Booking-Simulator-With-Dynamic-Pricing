# Comprehensive global and Indian airport directory with 260+ destinations

DESTINATIONS_DATA = [
    # --- INDIA DOMESTIC AIRPORTS (65 Major & Regional) ---
    {
        "code": "BOM", "icao": "VABB", "name": "Chhatrapati Shivaji Maharaj International Airport",
        "city": "Mumbai", "country": "India", "country_code": "IN", "region": "South Asia",
        "terminal": "T1 (Domestic) / T2 (Intl)", "timezone": "UTC+05:30", "is_international": True,
        "lat": 19.0896, "lon": 72.8656, "popularity": 98, "category": "CITY",
        "avg_fare": 4800, "best_season": "Nov - Feb"
    },
    {
        "code": "DEL", "icao": "VIDP", "name": "Indira Gandhi International Airport",
        "city": "Delhi", "country": "India", "country_code": "IN", "region": "South Asia",
        "terminal": "T1/T2/T3", "timezone": "UTC+05:30", "is_international": True,
        "lat": 28.5562, "lon": 77.1000, "popularity": 99, "category": "CITY",
        "avg_fare": 4600, "best_season": "Oct - Mar"
    },
    {
        "code": "BLR", "icao": "VOBL", "name": "Kempegowda International Airport",
        "city": "Bengaluru", "country": "India", "country_code": "IN", "region": "South Asia",
        "terminal": "T1 / T2", "timezone": "UTC+05:30", "is_international": True,
        "lat": 13.1986, "lon": 77.7066, "popularity": 95, "category": "CITY",
        "avg_fare": 4200, "best_season": "Sep - Mar"
    },
    {
        "code": "HYD", "icao": "VOHS", "name": "Rajiv Gandhi International Airport",
        "city": "Hyderabad", "country": "India", "country_code": "IN", "region": "South Asia",
        "terminal": "T1", "timezone": "UTC+05:30", "is_international": True,
        "lat": 17.2403, "lon": 78.4294, "popularity": 92, "category": "CITY",
        "avg_fare": 4100, "best_season": "Oct - Mar"
    },
    {
        "code": "MAA", "icao": "VOMM", "name": "Chennai International Airport",
        "city": "Chennai", "country": "India", "country_code": "IN", "region": "South Asia",
        "terminal": "T1 (Dom) / T4 (Intl)", "timezone": "UTC+05:30", "is_international": True,
        "lat": 12.9941, "lon": 80.1709, "popularity": 90, "category": "CITY",
        "avg_fare": 4300, "best_season": "Nov - Feb"
    },
    {
        "code": "CCU", "icao": "VECC", "name": "Netaji Subhas Chandra Bose International Airport",
        "city": "Kolkata", "country": "India", "country_code": "IN", "region": "South Asia",
        "terminal": "Integrated T2", "timezone": "UTC+05:30", "is_international": True,
        "lat": 22.6547, "lon": 88.4467, "popularity": 89, "category": "HERITAGE",
        "avg_fare": 4400, "best_season": "Oct - Mar"
    },
    {
        "code": "GOI", "icao": "VOGO", "name": "Dabolim International Airport",
        "city": "Goa", "country": "India", "country_code": "IN", "region": "South Asia",
        "terminal": "T1 / T2", "timezone": "UTC+05:30", "is_international": True,
        "lat": 15.3808, "lon": 73.8314, "popularity": 97, "category": "BEACH",
        "avg_fare": 3900, "best_season": "Oct - Apr"
    },
    {
        "code": "GOX", "icao": "VOGA", "name": "Manohar International Airport (Mopa)",
        "city": "North Goa", "country": "India", "country_code": "IN", "region": "South Asia",
        "terminal": "T1", "timezone": "UTC+05:30", "is_international": True,
        "lat": 15.7533, "lon": 73.8647, "popularity": 91, "category": "BEACH",
        "avg_fare": 3800, "best_season": "Oct - May"
    },
    {
        "code": "PNQ", "icao": "VAPO", "name": "Pune International Airport",
        "city": "Pune", "country": "India", "country_code": "IN", "region": "South Asia",
        "terminal": "T1 / New Terminal", "timezone": "UTC+05:30", "is_international": True,
        "lat": 18.5822, "lon": 73.9197, "popularity": 87, "category": "CITY",
        "avg_fare": 3700, "best_season": "Jul - Feb"
    },
    {
        "code": "AMD", "icao": "VAAH", "name": "Sardar Vallabhbhai Patel International Airport",
        "city": "Ahmedabad", "country": "India", "country_code": "IN", "region": "South Asia",
        "terminal": "T1 / T2", "timezone": "UTC+05:30", "is_international": True,
        "lat": 23.0772, "lon": 72.6347, "popularity": 88, "category": "HERITAGE",
        "avg_fare": 3900, "best_season": "Nov - Feb"
    },
    {
        "code": "COK", "icao": "VOCI", "name": "Cochin International Airport",
        "city": "Kochi", "country": "India", "country_code": "IN", "region": "South Asia",
        "terminal": "T1 / T3 (Intl)", "timezone": "UTC+05:30", "is_international": True,
        "lat": 10.1556, "lon": 76.3917, "popularity": 89, "category": "BEACH",
        "avg_fare": 4200, "best_season": "Sep - Mar"
    },
    {
        "code": "JAI", "icao": "VIJP", "name": "Jaipur International Airport",
        "city": "Jaipur", "country": "India", "country_code": "IN", "region": "South Asia",
        "terminal": "T2", "timezone": "UTC+05:30", "is_international": True,
        "lat": 26.8242, "lon": 75.8122, "popularity": 93, "category": "HERITAGE",
        "avg_fare": 3600, "best_season": "Oct - Mar"
    },
    {
        "code": "LKO", "icao": "VILK", "name": "Chaudhary Charan Singh International Airport",
        "city": "Lucknow", "country": "India", "country_code": "IN", "region": "South Asia",
        "terminal": "T3", "timezone": "UTC+05:30", "is_international": True,
        "lat": 26.7606, "lon": 80.8893, "popularity": 86, "category": "HERITAGE",
        "avg_fare": 3700, "best_season": "Oct - Mar"
    },
    {
        "code": "TRV", "icao": "VOTV", "name": "Thiruvananthapuram International Airport",
        "city": "Thiruvananthapuram", "country": "India", "country_code": "IN", "region": "South Asia",
        "terminal": "T1 / T2", "timezone": "UTC+05:30", "is_international": True,
        "lat": 8.4821, "lon": 76.9200, "popularity": 84, "category": "BEACH",
        "avg_fare": 4400, "best_season": "Sep - Mar"
    },
    {
        "code": "SXR", "icao": "VISR", "name": "Sheikh ul-Alam International Airport",
        "city": "Srinagar", "country": "India", "country_code": "IN", "region": "South Asia",
        "terminal": "T1", "timezone": "UTC+05:30", "is_international": True,
        "lat": 33.9871, "lon": 74.7741, "popularity": 95, "category": "MOUNTAINS",
        "avg_fare": 5200, "best_season": "Apr - Oct / Dec - Feb"
    },
    {
        "code": "IXZ", "icao": "VOPB", "name": "Veer Savarkar International Airport",
        "city": "Port Blair", "country": "India", "country_code": "IN", "region": "South Asia",
        "terminal": "New Integrated T1", "timezone": "UTC+05:30", "is_international": True,
        "lat": 11.6410, "lon": 92.7297, "popularity": 94, "category": "BEACH",
        "avg_fare": 6500, "best_season": "Oct - May"
    },
    {
        "code": "IXC", "icao": "VICG", "name": "Shaheed Bhagat Singh International Airport",
        "city": "Chandigarh", "country": "India", "country_code": "IN", "region": "South Asia",
        "terminal": "Integrated T1", "timezone": "UTC+05:30", "is_international": True,
        "lat": 30.6735, "lon": 76.7885, "popularity": 85, "category": "CITY",
        "avg_fare": 3600, "best_season": "Oct - Mar"
    },
    {
        "code": "IXB", "icao": "VEBD", "name": "Bagdogra Airport",
        "city": "Siliguri / Darjeeling", "country": "India", "country_code": "IN", "region": "South Asia",
        "terminal": "T1", "timezone": "UTC+05:30", "is_international": False,
        "lat": 26.6812, "lon": 88.3286, "popularity": 89, "category": "MOUNTAINS",
        "avg_fare": 4600, "best_season": "Mar - Jun / Sep - Dec"
    },
    {
        "code": "GAU", "icao": "VEGT", "name": "Lokpriya Gopinath Bordoloi International Airport",
        "city": "Guwahati", "country": "India", "country_code": "IN", "region": "South Asia",
        "terminal": "T1", "timezone": "UTC+05:30", "is_international": True,
        "lat": 26.1061, "lon": 91.5859, "popularity": 84, "category": "ADVENTURE",
        "avg_fare": 4900, "best_season": "Oct - Apr"
    },
    {
        "code": "BBI", "icao": "VEBS", "name": "Biju Patnaik International Airport",
        "city": "Bhubaneswar", "country": "India", "country_code": "IN", "region": "South Asia",
        "terminal": "T1 / T2", "timezone": "UTC+05:30", "is_international": True,
        "lat": 20.2444, "lon": 85.8178, "popularity": 82, "category": "HERITAGE",
        "avg_fare": 3800, "best_season": "Oct - Mar"
    },
    {
        "code": "PAT", "icao": "VEPT", "name": "Jay Prakash Narayan Airport",
        "city": "Patna", "country": "India", "country_code": "IN", "region": "South Asia",
        "terminal": "T1", "timezone": "UTC+05:30", "is_international": False,
        "lat": 25.5913, "lon": 85.0880, "popularity": 83, "category": "HERITAGE",
        "avg_fare": 4100, "best_season": "Oct - Mar"
    },
    {
        "code": "VNS", "icao": "VEBN", "name": "Lal Bahadur Shastri International Airport",
        "city": "Varanasi", "country": "India", "country_code": "IN", "region": "South Asia",
        "terminal": "T1", "timezone": "UTC+05:30", "is_international": True,
        "lat": 25.4524, "lon": 82.8593, "popularity": 96, "category": "HERITAGE",
        "avg_fare": 3600, "best_season": "Oct - Mar"
    },
    {
        "code": "ATQ", "icao": "VIAR", "name": "Sri Guru Ram Dass Jee International Airport",
        "city": "Amritsar", "country": "India", "country_code": "IN", "region": "South Asia",
        "terminal": "T1", "timezone": "UTC+05:30", "is_international": True,
        "lat": 31.7096, "lon": 74.7973, "popularity": 91, "category": "HERITAGE",
        "avg_fare": 3900, "best_season": "Oct - Mar"
    },
    {
        "code": "DED", "icao": "VIDN", "name": "Jolly Grant Airport",
        "city": "Dehradun / Rishikesh", "country": "India", "country_code": "IN", "region": "South Asia",
        "terminal": "T1", "timezone": "UTC+05:30", "is_international": False,
        "lat": 30.1897, "lon": 78.1803, "popularity": 92, "category": "ADVENTURE",
        "avg_fare": 3800, "best_season": "Mar - Jun / Sep - Nov"
    },
    {
        "code": "UDR", "icao": "VAUD", "name": "Maharana Pratap Airport",
        "city": "Udaipur", "country": "India", "country_code": "IN", "region": "South Asia",
        "terminal": "T1", "timezone": "UTC+05:30", "is_international": False,
        "lat": 24.6177, "lon": 73.8961, "popularity": 94, "category": "HERITAGE",
        "avg_fare": 4200, "best_season": "Sep - Mar"
    },
    {
        "code": "IXL", "icao": "VILH", "name": "Kushok Bakula Rimpochee Airport",
        "city": "Leh Ladakh", "country": "India", "country_code": "IN", "region": "South Asia",
        "terminal": "T1", "timezone": "UTC+05:30", "is_international": False,
        "lat": 34.1359, "lon": 77.5465, "popularity": 98, "category": "MOUNTAINS",
        "avg_fare": 7200, "best_season": "May - Sep"
    },
    {
        "code": "IXU", "icao": "VAAU", "name": "Chhatrapati Sambhaji Nagar Airport",
        "city": "Aurangabad", "country": "India", "country_code": "IN", "region": "South Asia",
        "terminal": "T1", "timezone": "UTC+05:30", "is_international": False,
        "lat": 19.8631, "lon": 75.3981, "popularity": 79, "category": "HERITAGE",
        "avg_fare": 3400, "best_season": "Oct - Mar"
    },
    {
        "code": "IXE", "icao": "VOML", "name": "Mangaluru International Airport",
        "city": "Mangalore", "country": "India", "country_code": "IN", "region": "South Asia",
        "terminal": "T1 / T2", "timezone": "UTC+05:30", "is_international": True,
        "lat": 12.9613, "lon": 74.8900, "popularity": 81, "category": "BEACH",
        "avg_fare": 3900, "best_season": "Oct - Mar"
    },
    {
        "code": "CJB", "icao": "VOCB", "name": "Coimbatore International Airport",
        "city": "Coimbatore", "country": "India", "country_code": "IN", "region": "South Asia",
        "terminal": "T1", "timezone": "UTC+05:30", "is_international": True,
        "lat": 11.0299, "lon": 77.0434, "popularity": 82, "category": "CITY",
        "avg_fare": 3700, "best_season": "Sep - Mar"
    },
    {
        "code": "IXM", "icao": "VOMD", "name": "Madurai Airport",
        "city": "Madurai", "country": "India", "country_code": "IN", "region": "South Asia",
        "terminal": "T1", "timezone": "UTC+05:30", "is_international": True,
        "lat": 9.8345, "lon": 78.0934, "popularity": 80, "category": "HERITAGE",
        "avg_fare": 3900, "best_season": "Oct - Mar"
    },
    {
        "code": "TRZ", "icao": "VOTR", "name": "Tiruchirappalli International Airport",
        "city": "Tiruchirappalli", "country": "India", "country_code": "IN", "region": "South Asia",
        "terminal": "New Terminal", "timezone": "UTC+05:30", "is_international": True,
        "lat": 10.7654, "lon": 78.7097, "popularity": 81, "category": "HERITAGE",
        "avg_fare": 4100, "best_season": "Nov - Feb"
    },
    {
        "code": "VTZ", "icao": "VOVZ", "name": "Visakhapatnam International Airport",
        "city": "Visakhapatnam", "country": "India", "country_code": "IN", "region": "South Asia",
        "terminal": "T1", "timezone": "UTC+05:30", "is_international": True,
        "lat": 17.7212, "lon": 83.2245, "popularity": 83, "category": "BEACH",
        "avg_fare": 3800, "best_season": "Oct - Mar"
    },
    {
        "code": "VGA", "icao": "VOBZ", "name": "Vijayawada Airport",
        "city": "Vijayawada", "country": "India", "country_code": "IN", "region": "South Asia",
        "terminal": "T1", "timezone": "UTC+05:30", "is_international": True,
        "lat": 16.5304, "lon": 80.7968, "popularity": 79, "category": "CITY",
        "avg_fare": 3500, "best_season": "Nov - Feb"
    },
    {
        "code": "RPR", "icao": "VARP", "name": "Swami Vivekananda Airport",
        "city": "Raipur", "country": "India", "country_code": "IN", "region": "South Asia",
        "terminal": "T1", "timezone": "UTC+05:30", "is_international": False,
        "lat": 21.1804, "lon": 81.7388, "popularity": 78, "category": "CITY",
        "avg_fare": 3600, "best_season": "Oct - Mar"
    },
    {
        "code": "NAG", "icao": "VANP", "name": "Dr. Babasaheb Ambedkar International Airport",
        "city": "Nagpur", "country": "India", "country_code": "IN", "region": "South Asia",
        "terminal": "T1", "timezone": "UTC+05:30", "is_international": True,
        "lat": 21.0922, "lon": 79.0472, "popularity": 83, "category": "CITY",
        "avg_fare": 3500, "best_season": "Oct - Mar"
    },
    {
        "code": "IDR", "icao": "VAID", "name": "Devi Ahilyabai Holkar Airport",
        "city": "Indore", "country": "India", "country_code": "IN", "region": "South Asia",
        "terminal": "T1", "timezone": "UTC+05:30", "is_international": True,
        "lat": 22.7217, "lon": 75.8011, "popularity": 85, "category": "CITY",
        "avg_fare": 3400, "best_season": "Oct - Mar"
    },
    {
        "code": "BHO", "icao": "VABP", "name": "Raja Bhoj Airport",
        "city": "Bhopal", "country": "India", "country_code": "IN", "region": "South Asia",
        "terminal": "T1", "timezone": "UTC+05:30", "is_international": False,
        "lat": 23.2875, "lon": 77.3378, "popularity": 79, "category": "HERITAGE",
        "avg_fare": 3500, "best_season": "Oct - Mar"
    },
    {
        "code": "AYJ", "icao": "VEAY", "name": "Maharishi Valmiki International Airport",
        "city": "Ayodhya", "country": "India", "country_code": "IN", "region": "South Asia",
        "terminal": "T1", "timezone": "UTC+05:30", "is_international": True,
        "lat": 26.7486, "lon": 82.1558, "popularity": 96, "category": "HERITAGE",
        "avg_fare": 3800, "best_season": "Oct - Mar"
    },
    {
        "code": "AGX", "icao": "VOAT", "name": "Agatti Airport",
        "city": "Lakshadweep", "country": "India", "country_code": "IN", "region": "South Asia",
        "terminal": "T1", "timezone": "UTC+05:30", "is_international": False,
        "lat": 10.8236, "lon": 72.1761, "popularity": 96, "category": "BEACH",
        "avg_fare": 6800, "best_season": "Oct - May"
    },
    {
        "code": "JDH", "icao": "VIJO", "name": "Jodhpur Airport",
        "city": "Jodhpur", "country": "India", "country_code": "IN", "region": "South Asia",
        "terminal": "T1", "timezone": "UTC+05:30", "is_international": False,
        "lat": 26.2511, "lon": 73.0489, "popularity": 91, "category": "HERITAGE",
        "avg_fare": 4100, "best_season": "Oct - Mar"
    },
    {
        "code": "JSA", "icao": "VIJR", "name": "Jaisalmer Airport",
        "city": "Jaisalmer", "country": "India", "country_code": "IN", "region": "South Asia",
        "terminal": "T1", "timezone": "UTC+05:30", "is_international": False,
        "lat": 26.8894, "lon": 70.8653, "popularity": 93, "category": "HERITAGE",
        "avg_fare": 4600, "best_season": "Oct - Mar"
    },
    {
        "code": "BDQ", "icao": "VABO", "name": "Vadodara Airport",
        "city": "Vadodara", "country": "India", "country_code": "IN", "region": "South Asia",
        "terminal": "Integrated T1", "timezone": "UTC+05:30", "is_international": False,
        "lat": 22.3361, "lon": 73.2264, "popularity": 81, "category": "CITY",
        "avg_fare": 3400, "best_season": "Oct - Mar"
    },
    {
        "code": "STV", "icao": "VASU", "name": "Surat International Airport",
        "city": "Surat", "country": "India", "country_code": "IN", "region": "South Asia",
        "terminal": "T1", "timezone": "UTC+05:30", "is_international": True,
        "lat": 21.1139, "lon": 72.7417, "popularity": 84, "category": "CITY",
        "avg_fare": 3500, "best_season": "Oct - Mar"
    },
    {
        "code": "RAJ", "icao": "VARK", "name": "Rajkot International Airport (Hirasar)",
        "city": "Rajkot", "country": "India", "country_code": "IN", "region": "South Asia",
        "terminal": "New Terminal", "timezone": "UTC+05:30", "is_international": True,
        "lat": 22.3619, "lon": 71.0114, "popularity": 79, "category": "CITY",
        "avg_fare": 3600, "best_season": "Oct - Mar"
    },
    {
        "code": "IXJ", "icao": "VIJU", "name": "Jammu Airport",
        "city": "Jammu", "country": "India", "country_code": "IN", "region": "South Asia",
        "terminal": "T1", "timezone": "UTC+05:30", "is_international": False,
        "lat": 32.6892, "lon": 74.8375, "popularity": 85, "category": "HERITAGE",
        "avg_fare": 4300, "best_season": "Sep - Apr"
    },
    {
        "code": "CNN", "icao": "VOCP", "name": "Kannur International Airport",
        "city": "Kannur", "country": "India", "country_code": "IN", "region": "South Asia",
        "terminal": "Integrated T1", "timezone": "UTC+05:30", "is_international": True,
        "lat": 11.9189, "lon": 75.5489, "popularity": 80, "category": "BEACH",
        "avg_fare": 4100, "best_season": "Oct - Mar"
    },
    {
        "code": "CCJ", "icao": "VOCL", "name": "Calicut International Airport",
        "city": "Kozhikode", "country": "India", "country_code": "IN", "region": "South Asia",
        "terminal": "T1 / T2", "timezone": "UTC+05:30", "is_international": True,
        "lat": 11.1367, "lon": 75.9553, "popularity": 82, "category": "BEACH",
        "avg_fare": 4000, "best_season": "Oct - Mar"
    },
    {
        "code": "TIR", "icao": "VOTP", "name": "Tirupati Airport",
        "city": "Tirupati", "country": "India", "country_code": "IN", "region": "South Asia",
        "terminal": "Garuda Terminal", "timezone": "UTC+05:30", "is_international": True,
        "lat": 13.6325, "lon": 79.5433, "popularity": 91, "category": "HERITAGE",
        "avg_fare": 3600, "best_season": "Sep - Feb"
    },

    # --- MIDDLE EAST & GULF (20) ---
    {
        "code": "DXB", "icao": "OMDB", "name": "Dubai International Airport",
        "city": "Dubai", "country": "United Arab Emirates", "country_code": "AE", "region": "Middle East",
        "terminal": "T1/T2/T3", "timezone": "UTC+04:00", "is_international": True,
        "lat": 25.2532, "lon": 55.3657, "popularity": 99, "category": "INTERNATIONAL",
        "avg_fare": 18500, "best_season": "Nov - Apr"
    },
    {
        "code": "AUH", "icao": "OMAA", "name": "Zayed International Airport (Abu Dhabi)",
        "city": "Abu Dhabi", "country": "United Arab Emirates", "country_code": "AE", "region": "Middle East",
        "terminal": "Terminal A", "timezone": "UTC+04:00", "is_international": True,
        "lat": 24.4330, "lon": 54.6511, "popularity": 93, "category": "INTERNATIONAL",
        "avg_fare": 17200, "best_season": "Nov - Apr"
    },
    {
        "code": "SHJ", "icao": "OMSJ", "name": "Sharjah International Airport",
        "city": "Sharjah", "country": "United Arab Emirates", "country_code": "AE", "region": "Middle East",
        "terminal": "T1", "timezone": "UTC+04:00", "is_international": True,
        "lat": 25.3286, "lon": 55.5172, "popularity": 88, "category": "INTERNATIONAL",
        "avg_fare": 15500, "best_season": "Nov - Apr"
    },
    {
        "code": "DOH", "icao": "OTHH", "name": "Hamad International Airport",
        "city": "Doha", "country": "Qatar", "country_code": "QA", "region": "Middle East",
        "terminal": "T1", "timezone": "UTC+03:00", "is_international": True,
        "lat": 25.2731, "lon": 51.6081, "popularity": 96, "category": "INTERNATIONAL",
        "avg_fare": 19200, "best_season": "Nov - Mar"
    },
    {
        "code": "BAH", "icao": "OBBI", "name": "Bahrain International Airport",
        "city": "Manama", "country": "Bahrain", "country_code": "BH", "region": "Middle East",
        "terminal": "T1", "timezone": "UTC+03:00", "is_international": True,
        "lat": 26.2708, "lon": 50.6336, "popularity": 85, "category": "INTERNATIONAL",
        "avg_fare": 16800, "best_season": "Nov - Mar"
    },
    {
        "code": "KWI", "icao": "OKBK", "name": "Kuwait International Airport",
        "city": "Kuwait City", "country": "Kuwait", "country_code": "KW", "region": "Middle East",
        "terminal": "T1/T4/T5", "timezone": "UTC+03:00", "is_international": True,
        "lat": 29.2269, "lon": 47.9689, "popularity": 87, "category": "INTERNATIONAL",
        "avg_fare": 17500, "best_season": "Nov - Mar"
    },
    {
        "code": "MCT", "icao": "OOMS", "name": "Muscat International Airport",
        "city": "Muscat", "country": "Oman", "country_code": "OM", "region": "Middle East",
        "terminal": "T1 / T2", "timezone": "UTC+04:00", "is_international": True,
        "lat": 23.5933, "lon": 58.2844, "popularity": 86, "category": "HERITAGE",
        "avg_fare": 15800, "best_season": "Oct - Mar"
    },
    {
        "code": "RUH", "icao": "OERK", "name": "King Khalid International Airport",
        "city": "Riyadh", "country": "Saudi Arabia", "country_code": "SA", "region": "Middle East",
        "terminal": "T1/T2/T5", "timezone": "UTC+03:00", "is_international": True,
        "lat": 24.9576, "lon": 46.6988, "popularity": 90, "category": "INTERNATIONAL",
        "avg_fare": 19500, "best_season": "Nov - Mar"
    },
    {
        "code": "JED", "icao": "OEJN", "name": "King Abdulaziz International Airport",
        "city": "Jeddah", "country": "Saudi Arabia", "country_code": "SA", "region": "Middle East",
        "terminal": "T1 / Hajj Terminal", "timezone": "UTC+03:00", "is_international": True,
        "lat": 21.6796, "lon": 39.1565, "popularity": 94, "category": "HERITAGE",
        "avg_fare": 21000, "best_season": "Nov - Mar"
    },
    {
        "code": "DMM", "icao": "OEDF", "name": "King Fahd International Airport",
        "city": "Dammam", "country": "Saudi Arabia", "country_code": "SA", "region": "Middle East",
        "terminal": "T1", "timezone": "UTC+03:00", "is_international": True,
        "lat": 26.4712, "lon": 49.7978, "popularity": 85, "category": "INTERNATIONAL",
        "avg_fare": 18200, "best_season": "Nov - Mar"
    },
    {
        "code": "MED", "icao": "OEMA", "name": "Prince Mohammad bin Abdulaziz International Airport",
        "city": "Medina", "country": "Saudi Arabia", "country_code": "SA", "region": "Middle East",
        "terminal": "T1", "timezone": "UTC+03:00", "is_international": True,
        "lat": 24.5534, "lon": 39.7051, "popularity": 91, "category": "HERITAGE",
        "avg_fare": 22500, "best_season": "Nov - Mar"
    },
    {
        "code": "AMM", "icao": "OJAI", "name": "Queen Alia International Airport",
        "city": "Amman / Petra", "country": "Jordan", "country_code": "JO", "region": "Middle East",
        "terminal": "T1", "timezone": "UTC+03:00", "is_international": True,
        "lat": 31.7226, "lon": 35.9932, "popularity": 87, "category": "HERITAGE",
        "avg_fare": 24500, "best_season": "Mar - May / Sep - Nov"
    },
    {
        "code": "BEY", "icao": "OLBA", "name": "Beirut–Rafic Hariri International Airport",
        "city": "Beirut", "country": "Lebanon", "country_code": "LB", "region": "Middle East",
        "terminal": "T1", "timezone": "UTC+03:00", "is_international": True,
        "lat": 33.8209, "lon": 35.4884, "popularity": 82, "category": "BEACH",
        "avg_fare": 23000, "best_season": "Apr - Jun / Sep - Nov"
    },
    {
        "code": "IST", "icao": "LTFM", "name": "Istanbul Airport",
        "city": "Istanbul", "country": "Turkey", "country_code": "TR", "region": "Europe/Asia",
        "terminal": "Main Terminal", "timezone": "UTC+03:00", "is_international": True,
        "lat": 41.2753, "lon": 28.7519, "popularity": 98, "category": "HERITAGE",
        "avg_fare": 26500, "best_season": "Apr - Jun / Sep - Nov"
    },
    {
        "code": "SAW", "icao": "LTFJ", "name": "Istanbul Sabiha Gökçen International Airport",
        "city": "Istanbul (Asian Side)", "country": "Turkey", "country_code": "TR", "region": "Europe/Asia",
        "terminal": "T1", "timezone": "UTC+03:00", "is_international": True,
        "lat": 40.8986, "lon": 29.3092, "popularity": 89, "category": "INTERNATIONAL",
        "avg_fare": 24000, "best_season": "Apr - Oct"
    },
    {
        "code": "AYT", "icao": "LTAI", "name": "Antalya Airport",
        "city": "Antalya", "country": "Turkey", "country_code": "TR", "region": "Europe",
        "terminal": "T1/T2", "timezone": "UTC+03:00", "is_international": True,
        "lat": 36.8987, "lon": 30.8005, "popularity": 92, "category": "BEACH",
        "avg_fare": 27500, "best_season": "May - Oct"
    },

    # --- SOUTHEAST & EAST ASIA (30) ---
    {
        "code": "SIN", "icao": "WSSS", "name": "Singapore Changi Airport",
        "city": "Singapore", "country": "Singapore", "country_code": "SG", "region": "Southeast Asia",
        "terminal": "T1/T2/T3/T4", "timezone": "UTC+08:00", "is_international": True,
        "lat": 1.3644, "lon": 103.9915, "popularity": 99, "category": "INTERNATIONAL",
        "avg_fare": 16500, "best_season": "Nov - Jul"
    },
    {
        "code": "BKK", "icao": "VTBS", "name": "Suvarnabhumi Airport",
        "city": "Bangkok", "country": "Thailand", "country_code": "TH", "region": "Southeast Asia",
        "terminal": "Main Terminal", "timezone": "UTC+07:00", "is_international": True,
        "lat": 13.6900, "lon": 100.7501, "popularity": 98, "category": "INTERNATIONAL",
        "avg_fare": 14200, "best_season": "Nov - Mar"
    },
    {
        "code": "HKT", "icao": "VTSP", "name": "Phuket International Airport",
        "city": "Phuket", "country": "Thailand", "country_code": "TH", "region": "Southeast Asia",
        "terminal": "T1 (Dom) / T2 (Intl)", "timezone": "UTC+07:00", "is_international": True,
        "lat": 8.1132, "lon": 98.3169, "popularity": 97, "category": "BEACH",
        "avg_fare": 15800, "best_season": "Nov - Apr"
    },
    {
        "code": "KBV", "icao": "VTSG", "name": "Krabi International Airport",
        "city": "Krabi", "country": "Thailand", "country_code": "TH", "region": "Southeast Asia",
        "terminal": "T1", "timezone": "UTC+07:00", "is_international": True,
        "lat": 8.0984, "lon": 98.9863, "popularity": 93, "category": "BEACH",
        "avg_fare": 16400, "best_season": "Nov - Apr"
    },
    {
        "code": "CNX", "icao": "VTCC", "name": "Chiang Mai International Airport",
        "city": "Chiang Mai", "country": "Thailand", "country_code": "TH", "region": "Southeast Asia",
        "terminal": "T1", "timezone": "UTC+07:00", "is_international": True,
        "lat": 18.7677, "lon": 98.9626, "popularity": 91, "category": "HERITAGE",
        "avg_fare": 16900, "best_season": "Nov - Feb"
    },
    {
        "code": "KUL", "icao": "WMKK", "name": "Kuala Lumpur International Airport",
        "city": "Kuala Lumpur", "country": "Malaysia", "country_code": "MY", "region": "Southeast Asia",
        "terminal": "KLIA1 / KLIA2", "timezone": "UTC+08:00", "is_international": True,
        "lat": 2.7456, "lon": 101.7072, "popularity": 95, "category": "INTERNATIONAL",
        "avg_fare": 13800, "best_season": "Dec - Feb / May - Jul"
    },
    {
        "code": "PEN", "icao": "WMKP", "name": "Penang International Airport",
        "city": "Penang", "country": "Malaysia", "country_code": "MY", "region": "Southeast Asia",
        "terminal": "T1", "timezone": "UTC+08:00", "is_international": True,
        "lat": 5.2971, "lon": 100.2769, "popularity": 89, "category": "HERITAGE",
        "avg_fare": 15200, "best_season": "Nov - Jan"
    },
    {
        "code": "LGK", "icao": "WMKL", "name": "Langkawi International Airport",
        "city": "Langkawi", "country": "Malaysia", "country_code": "MY", "region": "Southeast Asia",
        "terminal": "T1", "timezone": "UTC+08:00", "is_international": True,
        "lat": 6.3297, "lon": 99.7287, "popularity": 92, "category": "BEACH",
        "avg_fare": 15800, "best_season": "Dec - Apr"
    },
    {
        "code": "DPS", "icao": "WADD", "name": "Ngurah Rai International Airport (Bali)",
        "city": "Bali", "country": "Indonesia", "country_code": "ID", "region": "Southeast Asia",
        "terminal": "International / Domestic", "timezone": "UTC+08:00", "is_international": True,
        "lat": -8.7482, "lon": 115.1672, "popularity": 98, "category": "BEACH",
        "avg_fare": 21500, "best_season": "Apr - Oct"
    },
    {
        "code": "CGK", "icao": "WIII", "name": "Soekarno–Hatta International Airport",
        "city": "Jakarta", "country": "Indonesia", "country_code": "ID", "region": "Southeast Asia",
        "terminal": "T1/T2/T3", "timezone": "UTC+07:00", "is_international": True,
        "lat": -6.1275, "lon": 106.6537, "popularity": 89, "category": "CITY",
        "avg_fare": 19500, "best_season": "May - Sep"
    },
    {
        "code": "SGN", "icao": "VVTS", "name": "Tan Son Nhat International Airport",
        "city": "Ho Chi Minh City", "country": "Vietnam", "country_code": "VN", "region": "Southeast Asia",
        "terminal": "T1 / T2", "timezone": "UTC+07:00", "is_international": True,
        "lat": 10.8188, "lon": 106.6520, "popularity": 93, "category": "CITY",
        "avg_fare": 14900, "best_season": "Dec - Apr"
    },
    {
        "code": "HAN", "icao": "VVNB", "name": "Noi Bai International Airport",
        "city": "Hanoi / Halong Bay", "country": "Vietnam", "country_code": "VN", "region": "Southeast Asia",
        "terminal": "T1 / T2", "timezone": "UTC+07:00", "is_international": True,
        "lat": 21.2212, "lon": 105.8072, "popularity": 94, "category": "HERITAGE",
        "avg_fare": 15400, "best_season": "Oct - Apr"
    },
    {
        "code": "DAD", "icao": "VVDN", "name": "Da Nang International Airport",
        "city": "Da Nang / Hoi An", "country": "Vietnam", "country_code": "VN", "region": "Southeast Asia",
        "terminal": "T1 / T2", "timezone": "UTC+07:00", "is_international": True,
        "lat": 16.0439, "lon": 108.1994, "popularity": 92, "category": "BEACH",
        "avg_fare": 16200, "best_season": "Feb - May"
    },
    {
        "code": "PQC", "icao": "VVPQ", "name": "Phu Quoc International Airport",
        "city": "Phu Quoc", "country": "Vietnam", "country_code": "VN", "region": "Southeast Asia",
        "terminal": "T1", "timezone": "UTC+07:00", "is_international": True,
        "lat": 10.1697, "lon": 103.9931, "popularity": 90, "category": "BEACH",
        "avg_fare": 16800, "best_season": "Nov - Apr"
    },
    {
        "code": "REP", "icao": "VDSR", "name": "Siem Reap–Angkor International Airport",
        "city": "Siem Reap / Angkor Wat", "country": "Cambodia", "country_code": "KH", "region": "Southeast Asia",
        "terminal": "T1", "timezone": "UTC+07:00", "is_international": True,
        "lat": 13.3644, "lon": 104.2217, "popularity": 93, "category": "HERITAGE",
        "avg_fare": 18200, "best_season": "Nov - Mar"
    },
    {
        "code": "MNL", "icao": "RPLL", "name": "Ninoy Aquino International Airport",
        "city": "Manila", "country": "Philippines", "country_code": "PH", "region": "Southeast Asia",
        "terminal": "T1/T2/T3", "timezone": "UTC+08:00", "is_international": True,
        "lat": 14.5086, "lon": 121.0194, "popularity": 87, "category": "CITY",
        "avg_fare": 19800, "best_season": "Dec - Apr"
    },
    {
        "code": "MLE", "icao": "VRMM", "name": "Velana International Airport",
        "city": "Maldives", "country": "Maldives", "country_code": "MV", "region": "South Asia",
        "terminal": "T1 / Seaplane Terminal", "timezone": "UTC+05:00", "is_international": True,
        "lat": 4.1918, "lon": 73.5291, "popularity": 99, "category": "BEACH",
        "avg_fare": 19500, "best_season": "Nov - Apr"
    },
    {
        "code": "CMB", "icao": "VCBI", "name": "Bandaranaike International Airport",
        "city": "Colombo", "country": "Sri Lanka", "country_code": "LK", "region": "South Asia",
        "terminal": "T1", "timezone": "UTC+05:30", "is_international": True,
        "lat": 7.1808, "lon": 79.8841, "popularity": 93, "category": "BEACH",
        "avg_fare": 11500, "best_season": "Dec - Apr"
    },
    {
        "code": "KTM", "icao": "VNKT", "name": "Tribhuvan International Airport",
        "city": "Kathmandu / Everest", "country": "Nepal", "country_code": "NP", "region": "South Asia",
        "terminal": "T1", "timezone": "UTC+05:45", "is_international": True,
        "lat": 27.6966, "lon": 85.3591, "popularity": 94, "category": "MOUNTAINS",
        "avg_fare": 9800, "best_season": "Sep - Nov / Mar - May"
    },
    {
        "code": "HKG", "icao": "VHHH", "name": "Hong Kong International Airport",
        "city": "Hong Kong", "country": "Hong Kong", "country_code": "HK", "region": "East Asia",
        "terminal": "T1", "timezone": "UTC+08:00", "is_international": True,
        "lat": 22.3080, "lon": 113.9185, "popularity": 96, "category": "INTERNATIONAL",
        "avg_fare": 22000, "best_season": "Oct - Dec"
    },
    {
        "code": "HND", "icao": "RJTT", "name": "Tokyo Haneda Airport",
        "city": "Tokyo", "country": "Japan", "country_code": "JP", "region": "East Asia",
        "terminal": "T1/T2/T3", "timezone": "UTC+09:00", "is_international": True,
        "lat": 35.5494, "lon": 139.7798, "popularity": 99, "category": "INTERNATIONAL",
        "avg_fare": 36000, "best_season": "Mar - May (Sakura) / Sep - Nov"
    },
    {
        "code": "NRT", "icao": "RJAA", "name": "Narita International Airport",
        "city": "Tokyo Narita", "country": "Japan", "country_code": "JP", "region": "East Asia",
        "terminal": "T1/T2/T3", "timezone": "UTC+09:00", "is_international": True,
        "lat": 35.7720, "lon": 140.3929, "popularity": 94, "category": "INTERNATIONAL",
        "avg_fare": 34000, "best_season": "Mar - May / Sep - Nov"
    },
    {
        "code": "KIX", "icao": "RJBB", "name": "Kansai International Airport",
        "city": "Osaka / Kyoto", "country": "Japan", "country_code": "JP", "region": "East Asia",
        "terminal": "T1 / T2", "timezone": "UTC+09:00", "is_international": True,
        "lat": 34.4320, "lon": 135.2304, "popularity": 95, "category": "HERITAGE",
        "avg_fare": 35000, "best_season": "Mar - May / Sep - Nov"
    },
    {
        "code": "ICN", "icao": "RKSI", "name": "Incheon International Airport",
        "city": "Seoul", "country": "South Korea", "country_code": "KR", "region": "East Asia",
        "terminal": "T1 / T2", "timezone": "UTC+09:00", "is_international": True,
        "lat": 37.4602, "lon": 126.4407, "popularity": 97, "category": "INTERNATIONAL",
        "avg_fare": 31000, "best_season": "Mar - May / Sep - Nov"
    },
    {
        "code": "TPE", "icao": "RCTP", "name": "Taoyuan International Airport",
        "city": "Taipei", "country": "Taiwan", "country_code": "TW", "region": "East Asia",
        "terminal": "T1 / T2", "timezone": "UTC+08:00", "is_international": True,
        "lat": 25.0797, "lon": 121.2342, "popularity": 90, "category": "CITY",
        "avg_fare": 27500, "best_season": "Oct - Apr"
    },
    {
        "code": "PEK", "icao": "ZBAA", "name": "Beijing Capital International Airport",
        "city": "Beijing", "country": "China", "country_code": "CN", "region": "East Asia",
        "terminal": "T2 / T3", "timezone": "UTC+08:00", "is_international": True,
        "lat": 40.0799, "lon": 116.6031, "popularity": 92, "category": "HERITAGE",
        "avg_fare": 29000, "best_season": "Sep - Nov"
    },
    {
        "code": "PVG", "icao": "ZSPD", "name": "Shanghai Pudong International Airport",
        "city": "Shanghai", "country": "China", "country_code": "CN", "region": "East Asia",
        "terminal": "T1 / T2", "timezone": "UTC+08:00", "is_international": True,
        "lat": 31.1443, "lon": 121.8083, "popularity": 93, "category": "INTERNATIONAL",
        "avg_fare": 28500, "best_season": "Oct - Nov"
    },

    # --- EUROPE (30) ---
    {
        "code": "LHR", "icao": "EGLL", "name": "Heathrow Airport",
        "city": "London", "country": "United Kingdom", "country_code": "GB", "region": "Europe",
        "terminal": "T2/T3/T4/T5", "timezone": "UTC+01:00", "is_international": True,
        "lat": 51.4700, "lon": -0.4543, "popularity": 99, "category": "INTERNATIONAL",
        "avg_fare": 38000, "best_season": "May - Sep"
    },
    {
        "code": "MAN", "icao": "EGCC", "name": "Manchester Airport",
        "city": "Manchester", "country": "United Kingdom", "country_code": "GB", "region": "Europe",
        "terminal": "T1/T2/T3", "timezone": "UTC+01:00", "is_international": True,
        "lat": 53.3537, "lon": -2.2750, "popularity": 88, "category": "CITY",
        "avg_fare": 39000, "best_season": "Jun - Aug"
    },
    {
        "code": "EDI", "icao": "EGPH", "name": "Edinburgh Airport",
        "city": "Edinburgh", "country": "United Kingdom", "country_code": "GB", "region": "Europe",
        "terminal": "T1", "timezone": "UTC+01:00", "is_international": True,
        "lat": 55.9508, "lon": -3.3725, "popularity": 93, "category": "HERITAGE",
        "avg_fare": 42000, "best_season": "May - Sep"
    },
    {
        "code": "CDG", "icao": "LFPG", "name": "Charles de Gaulle Airport",
        "city": "Paris", "country": "France", "country_code": "FR", "region": "Europe",
        "terminal": "T1/T2A-G/T3", "timezone": "UTC+02:00", "is_international": True,
        "lat": 49.0097, "lon": 2.5479, "popularity": 99, "category": "INTERNATIONAL",
        "avg_fare": 39500, "best_season": "Apr - Oct"
    },
    {
        "code": "NCE", "icao": "LFMN", "name": "Nice Côte d'Azur Airport",
        "city": "Nice / French Riviera", "country": "France", "country_code": "FR", "region": "Europe",
        "terminal": "T1 / T2", "timezone": "UTC+02:00", "is_international": True,
        "lat": 43.6584, "lon": 7.2159, "popularity": 95, "category": "BEACH",
        "avg_fare": 43000, "best_season": "May - Oct"
    },
    {
        "code": "FRA", "icao": "EDDF", "name": "Frankfurt Airport",
        "city": "Frankfurt", "country": "Germany", "country_code": "DE", "region": "Europe",
        "terminal": "T1 / T2", "timezone": "UTC+02:00", "is_international": True,
        "lat": 50.0379, "lon": 8.5622, "popularity": 97, "category": "INTERNATIONAL",
        "avg_fare": 37500, "best_season": "May - Oct"
    },
    {
        "code": "MUC", "icao": "EDDM", "name": "Munich Airport",
        "city": "Munich", "country": "Germany", "country_code": "DE", "region": "Europe",
        "terminal": "T1 / T2", "timezone": "UTC+02:00", "is_international": True,
        "lat": 48.3537, "lon": 11.7860, "popularity": 95, "category": "HERITAGE",
        "avg_fare": 38500, "best_season": "May - Oct"
    },
    {
        "code": "AMS", "icao": "EHAM", "name": "Amsterdam Airport Schiphol",
        "city": "Amsterdam", "country": "Netherlands", "country_code": "NL", "region": "Europe",
        "terminal": "Single Terminal", "timezone": "UTC+02:00", "is_international": True,
        "lat": 52.3105, "lon": 4.7683, "popularity": 98, "category": "INTERNATIONAL",
        "avg_fare": 37000, "best_season": "Apr - Oct"
    },
    {
        "code": "ZRH", "icao": "LSZH", "name": "Zurich Airport",
        "city": "Zurich / Swiss Alps", "country": "Switzerland", "country_code": "CH", "region": "Europe",
        "terminal": "Airside Center", "timezone": "UTC+02:00", "is_international": True,
        "lat": 47.4582, "lon": 8.5555, "popularity": 98, "category": "MOUNTAINS",
        "avg_fare": 44000, "best_season": "Jun - Sep / Dec - Mar"
    },
    {
        "code": "GVA", "icao": "LSGG", "name": "Geneva Airport",
        "city": "Geneva", "country": "Switzerland", "country_code": "CH", "region": "Europe",
        "terminal": "T1", "timezone": "UTC+02:00", "is_international": True,
        "lat": 46.2370, "lon": 6.1092, "popularity": 92, "category": "MOUNTAINS",
        "avg_fare": 43500, "best_season": "Jun - Sep / Dec - Mar"
    },
    {
        "code": "FCO", "icao": "LIRF", "name": "Leonardo da Vinci–Fiumicino Airport",
        "city": "Rome", "country": "Italy", "country_code": "IT", "region": "Europe",
        "terminal": "T1 / T3", "timezone": "UTC+02:00", "is_international": True,
        "lat": 41.8003, "lon": 12.2389, "popularity": 98, "category": "HERITAGE",
        "avg_fare": 38500, "best_season": "Apr - Jun / Sep - Oct"
    },
    {
        "code": "MXP", "icao": "LIMC", "name": "Milan Malpensa Airport",
        "city": "Milan", "country": "Italy", "country_code": "IT", "region": "Europe",
        "terminal": "T1 / T2", "timezone": "UTC+02:00", "is_international": True,
        "lat": 45.6301, "lon": 8.7255, "popularity": 94, "category": "CITY",
        "avg_fare": 37800, "best_season": "Apr - Oct"
    },
    {
        "code": "VCE", "icao": "LIPZ", "name": "Venice Marco Polo Airport",
        "city": "Venice", "country": "Italy", "country_code": "IT", "region": "Europe",
        "terminal": "T1", "timezone": "UTC+02:00", "is_international": True,
        "lat": 45.5053, "lon": 12.3519, "popularity": 96, "category": "HERITAGE",
        "avg_fare": 41000, "best_season": "Apr - Oct"
    },
    {
        "code": "BCN", "icao": "LEBL", "name": "Josep Tarradellas Barcelona-El Prat Airport",
        "city": "Barcelona", "country": "Spain", "country_code": "ES", "region": "Europe",
        "terminal": "T1 / T2", "timezone": "UTC+02:00", "is_international": True,
        "lat": 41.2974, "lon": 2.0833, "popularity": 97, "category": "BEACH",
        "avg_fare": 38000, "best_season": "May - Oct"
    },
    {
        "code": "MAD", "icao": "LEMD", "name": "Adolfo Suárez Madrid–Barajas Airport",
        "city": "Madrid", "country": "Spain", "country_code": "ES", "region": "Europe",
        "terminal": "T1/T2/T4", "timezone": "UTC+02:00", "is_international": True,
        "lat": 40.4839, "lon": -3.5680, "popularity": 94, "category": "CITY",
        "avg_fare": 38500, "best_season": "Apr - Jun / Sep - Oct"
    },
    {
        "code": "IBZ", "icao": "LEIB", "name": "Ibiza Airport",
        "city": "Ibiza", "country": "Spain", "country_code": "ES", "region": "Europe",
        "terminal": "T1", "timezone": "UTC+02:00", "is_international": True,
        "lat": 38.8729, "lon": 1.3731, "popularity": 95, "category": "BEACH",
        "avg_fare": 42500, "best_season": "May - Oct"
    },
    {
        "code": "LIS", "icao": "LPPT", "name": "Humberto Delgado Airport",
        "city": "Lisbon", "country": "Portugal", "country_code": "PT", "region": "Europe",
        "terminal": "T1 / T2", "timezone": "UTC+01:00", "is_international": True,
        "lat": 38.7742, "lon": -9.1342, "popularity": 93, "category": "HERITAGE",
        "avg_fare": 39500, "best_season": "Mar - Jun / Sep - Oct"
    },
    {
        "code": "VIE", "icao": "LOWW", "name": "Vienna International Airport",
        "city": "Vienna", "country": "Austria", "country_code": "AT", "region": "Europe",
        "terminal": "T1/T3", "timezone": "UTC+02:00", "is_international": True,
        "lat": 48.1103, "lon": 16.5697, "popularity": 94, "category": "HERITAGE",
        "avg_fare": 38500, "best_season": "Apr - May / Sep - Oct"
    },
    {
        "code": "PRG", "icao": "LKPR", "name": "Václav Havel Airport Prague",
        "city": "Prague", "country": "Czech Republic", "country_code": "CZ", "region": "Europe",
        "terminal": "T1 / T2", "timezone": "UTC+02:00", "is_international": True,
        "lat": 50.1008, "lon": 14.2600, "popularity": 95, "category": "HERITAGE",
        "avg_fare": 37200, "best_season": "May - Sep"
    },
    {
        "code": "ATH", "icao": "LGAV", "name": "Athens International Airport",
        "city": "Athens", "country": "Greece", "country_code": "GR", "region": "Europe",
        "terminal": "Main Terminal", "timezone": "UTC+03:00", "is_international": True,
        "lat": 37.9364, "lon": 23.9445, "popularity": 96, "category": "HERITAGE",
        "avg_fare": 36000, "best_season": "Apr - Jun / Sep - Oct"
    },
    {
        "code": "JTR", "icao": "LGSR", "name": "Santorini (Thira) Airport",
        "city": "Santorini", "country": "Greece", "country_code": "GR", "region": "Europe",
        "terminal": "T1", "timezone": "UTC+03:00", "is_international": True,
        "lat": 36.3992, "lon": 25.4793, "popularity": 98, "category": "BEACH",
        "avg_fare": 42000, "best_season": "May - Oct"
    },
    {
        "code": "CPH", "icao": "EKCH", "name": "Copenhagen Airport",
        "city": "Copenhagen", "country": "Denmark", "country_code": "DK", "region": "Europe",
        "terminal": "T2 / T3", "timezone": "UTC+02:00", "is_international": True,
        "lat": 55.6180, "lon": 12.6508, "popularity": 91, "category": "CITY",
        "avg_fare": 38000, "best_season": "May - Aug"
    },
    {
        "code": "OSL", "icao": "ENGM", "name": "Oslo Airport, Gardermoen",
        "city": "Oslo / Fjordland", "country": "Norway", "country_code": "NO", "region": "Europe",
        "terminal": "T1", "timezone": "UTC+02:00", "is_international": True,
        "lat": 60.1976, "lon": 11.1004, "popularity": 93, "category": "MOUNTAINS",
        "avg_fare": 42000, "best_season": "May - Aug / Dec - Feb"
    },
    {
        "code": "KEF", "icao": "BIKF", "name": "Keflavík International Airport",
        "city": "Reykjavik", "country": "Iceland", "country_code": "IS", "region": "Europe",
        "terminal": "T1", "timezone": "UTC+00:00", "is_international": True,
        "lat": 63.9850, "lon": -22.6056, "popularity": 97, "category": "ADVENTURE",
        "avg_fare": 49000, "best_season": "Jun - Aug / Oct - Mar"
    },
    {
        "code": "DUB", "icao": "EIDW", "name": "Dublin Airport",
        "city": "Dublin", "country": "Ireland", "country_code": "IE", "region": "Europe",
        "terminal": "T1 / T2", "timezone": "UTC+01:00", "is_international": True,
        "lat": 53.4264, "lon": -6.2499, "popularity": 91, "category": "HERITAGE",
        "avg_fare": 41000, "best_season": "May - Sep"
    },

    # --- NORTH AMERICA (20) ---
    {
        "code": "JFK", "icao": "KJFK", "name": "John F. Kennedy International Airport",
        "city": "New York", "country": "United States", "country_code": "US", "region": "North America",
        "terminal": "T1/T4/T5/T7/T8", "timezone": "UTC-04:00", "is_international": True,
        "lat": 40.6413, "lon": -73.7781, "popularity": 99, "category": "INTERNATIONAL",
        "avg_fare": 52000, "best_season": "Apr - Jun / Sep - Nov"
    },
    {
        "code": "EWR", "icao": "KEWR", "name": "Newark Liberty International Airport",
        "city": "New York Newark", "country": "United States", "country_code": "US", "region": "North America",
        "terminal": "Terminal A/B/C", "timezone": "UTC-04:00", "is_international": True,
        "lat": 40.6895, "lon": -74.1745, "popularity": 95, "category": "INTERNATIONAL",
        "avg_fare": 49500, "best_season": "Apr - Nov"
    },
    {
        "code": "SFO", "icao": "KSFO", "name": "San Francisco International Airport",
        "city": "San Francisco", "country": "United States", "country_code": "US", "region": "North America",
        "terminal": "International / T1/T2/T3", "timezone": "UTC-07:00", "is_international": True,
        "lat": 37.6213, "lon": -122.3790, "popularity": 98, "category": "INTERNATIONAL",
        "avg_fare": 54000, "best_season": "Sep - Nov"
    },
    {
        "code": "LAX", "icao": "KLAX", "name": "Los Angeles International Airport",
        "city": "Los Angeles", "country": "United States", "country_code": "US", "region": "North America",
        "terminal": "Tom Bradley Intl / T1-T8", "timezone": "UTC-07:00", "is_international": True,
        "lat": 33.9416, "lon": -118.4085, "popularity": 98, "category": "BEACH",
        "avg_fare": 53500, "best_season": "Mar - May / Sep - Nov"
    },
    {
        "code": "ORD", "icao": "KORD", "name": "O'Hare International Airport",
        "city": "Chicago", "country": "United States", "country_code": "US", "region": "North America",
        "terminal": "T1/T2/T3/T5", "timezone": "UTC-05:00", "is_international": True,
        "lat": 41.9742, "lon": -87.9073, "popularity": 96, "category": "CITY",
        "avg_fare": 51000, "best_season": "May - Oct"
    },
    {
        "code": "DFW", "icao": "KDFW", "name": "Dallas/Fort Worth International Airport",
        "city": "Dallas", "country": "United States", "country_code": "US", "region": "North America",
        "terminal": "Terminal A-E", "timezone": "UTC-05:00", "is_international": True,
        "lat": 32.8998, "lon": -97.0403, "popularity": 93, "category": "CITY",
        "avg_fare": 52500, "best_season": "Mar - May / Sep - Nov"
    },
    {
        "code": "MIA", "icao": "KMIA", "name": "Miami International Airport",
        "city": "Miami", "country": "United States", "country_code": "US", "region": "North America",
        "terminal": "Concourse D-J", "timezone": "UTC-04:00", "is_international": True,
        "lat": 25.7959, "lon": -80.2870, "popularity": 97, "category": "BEACH",
        "avg_fare": 53000, "best_season": "Nov - Apr"
    },
    {
        "code": "MCO", "icao": "KMCO", "name": "Orlando International Airport",
        "city": "Orlando / Disney", "country": "United States", "country_code": "US", "region": "North America",
        "terminal": "Terminal A/B/C", "timezone": "UTC-04:00", "is_international": True,
        "lat": 28.4312, "lon": -81.3081, "popularity": 96, "category": "ADVENTURE",
        "avg_fare": 52000, "best_season": "Jan - Apr / Oct - Dec"
    },
    {
        "code": "LAS", "icao": "KLAS", "name": "Harry Reid International Airport",
        "city": "Las Vegas", "country": "United States", "country_code": "US", "region": "North America",
        "terminal": "T1 / T3", "timezone": "UTC-07:00", "is_international": True,
        "lat": 36.0840, "lon": -115.1537, "popularity": 97, "category": "CITY",
        "avg_fare": 54500, "best_season": "Mar - May / Sep - Nov"
    },
    {
        "code": "SEA", "icao": "KSEA", "name": "Seattle-Tacoma International Airport",
        "city": "Seattle", "country": "United States", "country_code": "US", "region": "North America",
        "terminal": "Main Terminal", "timezone": "UTC-07:00", "is_international": True,
        "lat": 47.4502, "lon": -122.3088, "popularity": 94, "category": "CITY",
        "avg_fare": 53000, "best_season": "Jun - Sep"
    },
    {
        "code": "BOS", "icao": "KBOS", "name": "Boston Logan International Airport",
        "city": "Boston", "country": "United States", "country_code": "US", "region": "North America",
        "terminal": "Terminal A/B/C/E", "timezone": "UTC-04:00", "is_international": True,
        "lat": 42.3656, "lon": -71.0096, "popularity": 93, "category": "HERITAGE",
        "avg_fare": 51500, "best_season": "Jun - Oct"
    },
    {
        "code": "IAD", "icao": "KIAD", "name": "Washington Dulles International Airport",
        "city": "Washington, D.C.", "country": "United States", "country_code": "US", "region": "North America",
        "terminal": "Main Terminal", "timezone": "UTC-04:00", "is_international": True,
        "lat": 38.9531, "lon": -77.4565, "popularity": 94, "category": "HERITAGE",
        "avg_fare": 51000, "best_season": "Mar - May / Sep - Nov"
    },
    {
        "code": "DEN", "icao": "KDEN", "name": "Denver International Airport",
        "city": "Denver / Rockies", "country": "United States", "country_code": "US", "region": "North America",
        "terminal": "Jeppesen Terminal", "timezone": "UTC-06:00", "is_international": True,
        "lat": 39.8561, "lon": -104.6737, "popularity": 94, "category": "MOUNTAINS",
        "avg_fare": 54000, "best_season": "Jun - Aug / Dec - Mar"
    },
    {
        "code": "HNL", "icao": "PHNL", "name": "Daniel K. Inouye International Airport",
        "city": "Honolulu / Hawaii", "country": "United States", "country_code": "US", "region": "North America",
        "terminal": "T1 / T2", "timezone": "UTC-10:00", "is_international": True,
        "lat": 21.3187, "lon": -157.9225, "popularity": 98, "category": "BEACH",
        "avg_fare": 68000, "best_season": "Apr - May / Sep - Nov"
    },
    {
        "code": "YYZ", "icao": "CYYZ", "name": "Toronto Pearson International Airport",
        "city": "Toronto", "country": "Canada", "country_code": "CA", "region": "North America",
        "terminal": "T1 / T3", "timezone": "UTC-04:00", "is_international": True,
        "lat": 43.6777, "lon": -79.6248, "popularity": 98, "category": "INTERNATIONAL",
        "avg_fare": 53000, "best_season": "May - Oct"
    },
    {
        "code": "YVR", "icao": "CYVR", "name": "Vancouver International Airport",
        "city": "Vancouver", "country": "Canada", "country_code": "CA", "region": "North America",
        "terminal": "Main / South", "timezone": "UTC-07:00", "is_international": True,
        "lat": 49.1967, "lon": -123.1815, "popularity": 97, "category": "MOUNTAINS",
        "avg_fare": 55000, "best_season": "Jun - Sep"
    },
    {
        "code": "YUL", "icao": "CYUL", "name": "Montréal–Trudeau International Airport",
        "city": "Montreal", "country": "Canada", "country_code": "CA", "region": "North America",
        "terminal": "T1", "timezone": "UTC-04:00", "is_international": True,
        "lat": 45.4706, "lon": -73.7408, "popularity": 92, "category": "HERITAGE",
        "avg_fare": 54000, "best_season": "Jun - Sep"
    },
    {
        "code": "YYC", "icao": "CYYC", "name": "Calgary International Airport",
        "city": "Calgary / Banff", "country": "Canada", "country_code": "CA", "region": "North America",
        "terminal": "T1", "timezone": "UTC-06:00", "is_international": True,
        "lat": 51.1215, "lon": -114.0076, "popularity": 95, "category": "MOUNTAINS",
        "avg_fare": 57000, "best_season": "Jun - Aug / Dec - Mar"
    },
    {
        "code": "CUN", "icao": "MMUN", "name": "Cancún International Airport",
        "city": "Cancun / Riviera Maya", "country": "Mexico", "country_code": "MX", "region": "North America",
        "terminal": "T2/T3/T4", "timezone": "UTC-05:00", "is_international": True,
        "lat": 21.0365, "lon": -86.8771, "popularity": 98, "category": "BEACH",
        "avg_fare": 58000, "best_season": "Dec - Apr"
    },
    {
        "code": "MEX", "icao": "MMMX", "name": "Mexico City International Airport",
        "city": "Mexico City", "country": "Mexico", "country_code": "MX", "region": "North America",
        "terminal": "T1 / T2", "timezone": "UTC-06:00", "is_international": True,
        "lat": 19.4361, "lon": -99.0719, "popularity": 92, "category": "HERITAGE",
        "avg_fare": 56000, "best_season": "Mar - May"
    },

    # --- OCEANIA, AFRICA & SOUTH AMERICA (20) ---
    {
        "code": "SYD", "icao": "YSSY", "name": "Sydney Kingsford Smith Airport",
        "city": "Sydney", "country": "Australia", "country_code": "AU", "region": "Oceania",
        "terminal": "T1 (Intl) / T2/T3", "timezone": "UTC+10:00", "is_international": True,
        "lat": -33.9399, "lon": 151.1753, "popularity": 98, "category": "BEACH",
        "avg_fare": 46000, "best_season": "Sep - Nov / Mar - May"
    },
    {
        "code": "MEL", "icao": "YMML", "name": "Melbourne Airport",
        "city": "Melbourne", "country": "Australia", "country_code": "AU", "region": "Oceania",
        "terminal": "T1/T2/T3/T4", "timezone": "UTC+10:00", "is_international": True,
        "lat": -37.6690, "lon": 144.8410, "popularity": 96, "category": "CITY",
        "avg_fare": 45000, "best_season": "Mar - May / Sep - Nov"
    },
    {
        "code": "BNE", "icao": "YBBN", "name": "Brisbane Airport",
        "city": "Brisbane / Gold Coast", "country": "Australia", "country_code": "AU", "region": "Oceania",
        "terminal": "Domestic / International", "timezone": "UTC+10:00", "is_international": True,
        "lat": -27.3842, "lon": 153.1175, "popularity": 93, "category": "BEACH",
        "avg_fare": 47500, "best_season": "Apr - Oct"
    },
    {
        "code": "PER", "icao": "YPPH", "name": "Perth Airport",
        "city": "Perth", "country": "Australia", "country_code": "AU", "region": "Oceania",
        "terminal": "T1/T2/T3/T4", "timezone": "UTC+08:00", "is_international": True,
        "lat": -31.9403, "lon": 115.9669, "popularity": 91, "category": "BEACH",
        "avg_fare": 42000, "best_season": "Sep - Nov / Mar - May"
    },
    {
        "code": "AKL", "icao": "NZAA", "name": "Auckland Airport",
        "city": "Auckland", "country": "New Zealand", "country_code": "NZ", "region": "Oceania",
        "terminal": "Domestic / International", "timezone": "UTC+12:00", "is_international": True,
        "lat": -37.0082, "lon": 174.7850, "popularity": 96, "category": "ADVENTURE",
        "avg_fare": 54000, "best_season": "Nov - Apr"
    },
    {
        "code": "ZQN", "icao": "NZQN", "name": "Queenstown Airport",
        "city": "Queenstown", "country": "New Zealand", "country_code": "NZ", "region": "Oceania",
        "terminal": "T1", "timezone": "UTC+12:00", "is_international": True,
        "lat": -45.0217, "lon": 168.7392, "popularity": 98, "category": "MOUNTAINS",
        "avg_fare": 58000, "best_season": "Dec - Feb / Jun - Aug"
    },
    {
        "code": "NAN", "icao": "NFFN", "name": "Nadi International Airport",
        "city": "Fiji", "country": "Fiji", "country_code": "FJ", "region": "Oceania",
        "terminal": "T1", "timezone": "UTC+12:00", "is_international": True,
        "lat": -17.7554, "lon": 177.4434, "popularity": 94, "category": "BEACH",
        "avg_fare": 62000, "best_season": "May - Oct"
    },
    {
        "code": "JNB", "icao": "FAOR", "name": "O. R. Tambo International Airport",
        "city": "Johannesburg", "country": "South Africa", "country_code": "ZA", "region": "Africa",
        "terminal": "T1 / T2", "timezone": "UTC+02:00", "is_international": True,
        "lat": -26.1392, "lon": 28.2460, "popularity": 91, "category": "ADVENTURE",
        "avg_fare": 43000, "best_season": "May - Sep"
    },
    {
        "code": "CPT", "icao": "FACT", "name": "Cape Town International Airport",
        "city": "Cape Town", "country": "South Africa", "country_code": "ZA", "region": "Africa",
        "terminal": "Central Terminal", "timezone": "UTC+02:00", "is_international": True,
        "lat": -33.9715, "lon": 18.6021, "popularity": 97, "category": "BEACH",
        "avg_fare": 46000, "best_season": "Nov - Mar"
    },
    {
        "code": "NBO", "icao": "HKJK", "name": "Jomo Kenyatta International Airport",
        "city": "Nairobi / Masai Mara", "country": "Kenya", "country_code": "KE", "region": "Africa",
        "terminal": "T1A-E / T2", "timezone": "UTC+03:00", "is_international": True,
        "lat": -1.3192, "lon": 36.9278, "popularity": 94, "category": "ADVENTURE",
        "avg_fare": 32000, "best_season": "Jul - Oct"
    },
    {
        "code": "CAI", "icao": "HECA", "name": "Cairo International Airport",
        "city": "Cairo / Pyramids", "country": "Egypt", "country_code": "EG", "region": "Africa",
        "terminal": "T1/T2/T3", "timezone": "UTC+03:00", "is_international": True,
        "lat": 30.1219, "lon": 31.4056, "popularity": 96, "category": "HERITAGE",
        "avg_fare": 27000, "best_season": "Oct - Apr"
    },
    {
        "code": "MRU", "icao": "FIMP", "name": "Sir Seewoosagur Ramgoolam International Airport",
        "city": "Mauritius", "country": "Mauritius", "country_code": "MU", "region": "Africa",
        "terminal": "T1", "timezone": "UTC+04:00", "is_international": True,
        "lat": -20.4302, "lon": 57.6836, "popularity": 96, "category": "BEACH",
        "avg_fare": 29500, "best_season": "May - Dec"
    },
    {
        "code": "SEZ", "icao": "FSIA", "name": "Seychelles International Airport",
        "city": "Mahe / Seychelles", "country": "Seychelles", "country_code": "SC", "region": "Africa",
        "terminal": "T1", "timezone": "UTC+04:00", "is_international": True,
        "lat": -4.6743, "lon": 55.5219, "popularity": 95, "category": "BEACH",
        "avg_fare": 36000, "best_season": "Apr - May / Oct - Nov"
    },
    {
        "code": "RAK", "icao": "GMMX", "name": "Marrakesh Menara Airport",
        "city": "Marrakech", "country": "Morocco", "country_code": "MA", "region": "Africa",
        "terminal": "T1 / T2", "timezone": "UTC+01:00", "is_international": True,
        "lat": 31.6069, "lon": -8.0363, "popularity": 94, "category": "HERITAGE",
        "avg_fare": 39500, "best_season": "Mar - May / Sep - Nov"
    },
    {
        "code": "GRU", "icao": "SBGR", "name": "São Paulo/Guarulhos International Airport",
        "city": "São Paulo", "country": "Brazil", "country_code": "BR", "region": "South America",
        "terminal": "T1/T2/T3", "timezone": "UTC-03:00", "is_international": True,
        "lat": -23.4356, "lon": -46.4731, "popularity": 91, "category": "CITY",
        "avg_fare": 74000, "best_season": "Mar - May / Oct - Nov"
    },
    {
        "code": "GIG", "icao": "SBGL", "name": "Rio de Janeiro/Galeão International Airport",
        "city": "Rio de Janeiro", "country": "Brazil", "country_code": "BR", "region": "South America",
        "terminal": "T1 / T2", "timezone": "UTC-03:00", "is_international": True,
        "lat": -22.8089, "lon": -43.2436, "popularity": 95, "category": "BEACH",
        "avg_fare": 76000, "best_season": "Dec - Mar"
    },
    {
        "code": "EZE", "icao": "SAEZ", "name": "Ministro Pistarini International Airport",
        "city": "Buenos Aires", "country": "Argentina", "country_code": "AR", "region": "South America",
        "terminal": "Terminal A/B/C", "timezone": "UTC-03:00", "is_international": True,
        "lat": -34.8222, "lon": -58.5358, "popularity": 92, "category": "HERITAGE",
        "avg_fare": 79000, "best_season": "Mar - May / Sep - Nov"
    },
    {
        "code": "SCL", "icao": "SCEL", "name": "Arturo Merino Benítez International Airport",
        "city": "Santiago / Patagonia", "country": "Chile", "country_code": "CL", "region": "South America",
        "terminal": "T1 / T2", "timezone": "UTC-04:00", "is_international": True,
        "lat": -33.3930, "lon": -70.7858, "popularity": 90, "category": "MOUNTAINS",
        "avg_fare": 82000, "best_season": "Oct - Apr"
    },
    {
        "code": "LIM", "icao": "SPJC", "name": "Jorge Chávez International Airport",
        "city": "Lima / Machu Picchu", "country": "Peru", "country_code": "PE", "region": "South America",
        "terminal": "T1", "timezone": "UTC-05:00", "is_international": True,
        "lat": -12.0219, "lon": -77.1143, "popularity": 95, "category": "HERITAGE",
        "avg_fare": 81000, "best_season": "May - Oct"
    },
    {
        "code": "BOG", "icao": "SKBO", "name": "El Dorado International Airport",
        "city": "Bogota", "country": "Colombia", "country_code": "CO", "region": "South America",
        "terminal": "T1", "timezone": "UTC-05:00", "is_international": True,
        "lat": 4.7016, "lon": -74.1469, "popularity": 88, "category": "HERITAGE",
        "avg_fare": 77000, "best_season": "Dec - Mar"
    }
]

# Map for instant coordinate and attribute lookup
AIRPORT_MAP = {d["code"]: d for d in DESTINATIONS_DATA}
