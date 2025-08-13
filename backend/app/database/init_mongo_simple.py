"""
MongoDB初期化スクリプト（簡略版）
"""
import asyncio
import os
import json
from app.database.mongodb import connect_to_mongo, close_mongo_connection, db
from app.models_mongo.area import Area, HousingData, ParkData, SchoolData, SafetyData, MedicalData, CultureData, ChildcareData
from app.models_mongo.waste_separation import WasteSeparation
from app.models_mongo.congestion import CongestionData
from app.services.tokyo_congestion_service import tokyo_congestion_service
from beanie import init_beanie

async def init_mongodb():
    """MongoDB接続とBeanie初期化"""
    await connect_to_mongo()
    await init_beanie(
        database=db.database,
        document_models=[
            Area,
            WasteSeparation,
            CongestionData
        ]
    )

async def init_all_areas():
    """全23区のデータを初期化"""
    
    # 既存データをクリア
    await Area.delete_all()
    await WasteSeparation.delete_all()
    await CongestionData.delete_all()
    
    # tokyo_age_population_ckan_simple.jsonから年齢分布データを読み込む
    json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'tokyo_age_population_ckan_simple.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        age_population_data = json.load(f)
    
    # 23区の基本データ
    # データソース: 東京都総務局統計部「東京都の人口（推計）」及び「住民基本台帳による世帯と人口」
    # 更新日: 令和6年4月1日現在
    areas_data = [
        {"code": "13101", "name": "千代田区", "lat": 35.6940, "lng": 139.7534, "area": 11.66, "pop": 68856, "households": 40940, "density": 5905.8},
        {"code": "13102", "name": "中央区", "lat": 35.6706, "lng": 139.7720, "area": 10.21, "pop": 181845, "households": 104227, "density": 17813.6},
        {"code": "13103", "name": "港区", "lat": 35.6581, "lng": 139.7515, "area": 20.36, "pop": 267250, "households": 154970, "density": 13124.5},
        {"code": "13104", "name": "新宿区", "lat": 35.6938, "lng": 139.7036, "area": 18.22, "pop": 349318, "households": 228690, "density": 19169.9},
        {"code": "13105", "name": "文京区", "lat": 35.7081, "lng": 139.7524, "area": 11.29, "pop": 232790, "households": 130035, "density": 20619.7},
        {"code": "13106", "name": "台東区", "lat": 35.7121, "lng": 139.7799, "area": 10.11, "pop": 213486, "households": 131270, "density": 21115.2},
        {"code": "13107", "name": "墨田区", "lat": 35.7107, "lng": 139.8013, "area": 13.77, "pop": 285784, "households": 154370, "density": 20753.8},
        {"code": "13108", "name": "江東区", "lat": 35.6731, "lng": 139.8171, "area": 42.99, "pop": 539439, "households": 288890, "density": 12544.1},
        {"code": "13109", "name": "品川区", "lat": 35.6090, "lng": 139.7302, "area": 22.85, "pop": 410260, "households": 235990, "density": 17952.5},
        {"code": "13110", "name": "目黒区", "lat": 35.6414, "lng": 139.6982, "area": 14.67, "pop": 280126, "households": 160480, "density": 19096.3},
        {"code": "13111", "name": "大田区", "lat": 35.5614, "lng": 139.7161, "area": 61.86, "pop": 736652, "households": 413090, "density": 11909.8},
        {"code": "13112", "name": "世田谷区", "lat": 35.6464, "lng": 139.6530, "area": 58.05, "pop": 920596, "households": 500550, "density": 15857.6},
        {"code": "13113", "name": "渋谷区", "lat": 35.6639, "lng": 139.6982, "area": 15.11, "pop": 231499, "households": 148870, "density": 15317.7},
        {"code": "13114", "name": "中野区", "lat": 35.7074, "lng": 139.6637, "area": 15.59, "pop": 338800, "households": 215520, "density": 21731.5},
        {"code": "13115", "name": "杉並区", "lat": 35.6994, "lng": 139.6364, "area": 34.06, "pop": 574841, "households": 336890, "density": 16880.4},
        {"code": "13116", "name": "豊島区", "lat": 35.7260, "lng": 139.7166, "area": 13.01, "pop": 292339, "households": 186640, "density": 22464.3},
        {"code": "13117", "name": "北区", "lat": 35.7528, "lng": 139.7337, "area": 20.61, "pop": 358516, "households": 203170, "density": 17393.5},
        {"code": "13118", "name": "荒川区", "lat": 35.7362, "lng": 139.7830, "area": 10.16, "pop": 219813, "households": 122730, "density": 21635.3},
        {"code": "13119", "name": "板橋区", "lat": 35.7512, "lng": 139.7095, "area": 32.22, "pop": 574768, "households": 325090, "density": 17837.4},
        {"code": "13120", "name": "練馬区", "lat": 35.7357, "lng": 139.6516, "area": 48.08, "pop": 743428, "households": 395140, "density": 15458.8},
        {"code": "13121", "name": "足立区", "lat": 35.7751, "lng": 139.8046, "area": 53.25, "pop": 694725, "households": 367480, "density": 13048.4},
        {"code": "13122", "name": "葛飾区", "lat": 35.7435, "lng": 139.8473, "area": 34.80, "pop": 467922, "households": 242760, "density": 13446.6},
        {"code": "13123", "name": "江戸川区", "lat": 35.7068, "lng": 139.8687, "area": 49.90, "pop": 690476, "households": 352230, "density": 13835.2},
    ]
    
    # SQLite版のサンプルデータ
    housing_data = {
        "13101": {"rent_1r": 10.5, "rent_1k": 11.2, "rent_1dk": 12.8, "rent_1ldk": 18.5, "rent_2ldk": 28.5, "rent_3ldk": 40.2, "vacant_rate": 8.5},
        "13102": {"rent_1r": 9.8, "rent_1k": 10.5, "rent_1dk": 12.0, "rent_1ldk": 17.0, "rent_2ldk": 25.0, "rent_3ldk": 35.0, "vacant_rate": 7.2},
        "13103": {"rent_1r": 12.0, "rent_1k": 13.0, "rent_1dk": 15.0, "rent_1ldk": 22.0, "rent_2ldk": 35.0, "rent_3ldk": 50.0, "vacant_rate": 9.0},
        "13104": {"rent_1r": 9.0, "rent_1k": 9.8, "rent_1dk": 11.5, "rent_1ldk": 16.0, "rent_2ldk": 23.0, "rent_3ldk": 32.0, "vacant_rate": 6.5},
        "13105": {"rent_1r": 8.5, "rent_1k": 9.2, "rent_1dk": 10.8, "rent_1ldk": 15.0, "rent_2ldk": 21.0, "rent_3ldk": 28.0, "vacant_rate": 5.8},
        "13106": {"rent_1r": 8.0, "rent_1k": 8.5, "rent_1dk": 10.0, "rent_1ldk": 14.0, "rent_2ldk": 19.0, "rent_3ldk": 25.0, "vacant_rate": 6.0},
        "13107": {"rent_1r": 7.5, "rent_1k": 8.0, "rent_1dk": 9.5, "rent_1ldk": 13.0, "rent_2ldk": 18.0, "rent_3ldk": 24.0, "vacant_rate": 5.5},
        "13108": {"rent_1r": 8.2, "rent_1k": 8.8, "rent_1dk": 10.2, "rent_1ldk": 14.5, "rent_2ldk": 20.0, "rent_3ldk": 27.0, "vacant_rate": 4.8},
        "13109": {"rent_1r": 8.8, "rent_1k": 9.5, "rent_1dk": 11.0, "rent_1ldk": 15.5, "rent_2ldk": 22.0, "rent_3ldk": 30.0, "vacant_rate": 5.2},
        "13110": {"rent_1r": 9.5, "rent_1k": 10.2, "rent_1dk": 12.0, "rent_1ldk": 17.0, "rent_2ldk": 24.0, "rent_3ldk": 33.0, "vacant_rate": 6.0},
        "13111": {"rent_1r": 7.0, "rent_1k": 7.5, "rent_1dk": 8.8, "rent_1ldk": 12.5, "rent_2ldk": 17.0, "rent_3ldk": 23.0, "vacant_rate": 4.5},
        "13112": {"rent_1r": 8.5, "rent_1k": 9.0, "rent_1dk": 10.5, "rent_1ldk": 15.0, "rent_2ldk": 21.0, "rent_3ldk": 28.0, "vacant_rate": 4.2},
        "13113": {"rent_1r": 10.0, "rent_1k": 11.0, "rent_1dk": 13.0, "rent_1ldk": 18.5, "rent_2ldk": 26.0, "rent_3ldk": 36.0, "vacant_rate": 7.5},
        "13114": {"rent_1r": 7.8, "rent_1k": 8.3, "rent_1dk": 9.8, "rent_1ldk": 13.5, "rent_2ldk": 18.5, "rent_3ldk": 25.0, "vacant_rate": 5.0},
        "13115": {"rent_1r": 7.5, "rent_1k": 8.0, "rent_1dk": 9.5, "rent_1ldk": 13.0, "rent_2ldk": 18.0, "rent_3ldk": 24.0, "vacant_rate": 4.8},
        "13116": {"rent_1r": 8.0, "rent_1k": 8.5, "rent_1dk": 10.0, "rent_1ldk": 14.0, "rent_2ldk": 19.5, "rent_3ldk": 26.0, "vacant_rate": 6.2},
        "13117": {"rent_1r": 6.8, "rent_1k": 7.2, "rent_1dk": 8.5, "rent_1ldk": 12.0, "rent_2ldk": 16.5, "rent_3ldk": 22.0, "vacant_rate": 5.5},
        "13118": {"rent_1r": 6.5, "rent_1k": 7.0, "rent_1dk": 8.2, "rent_1ldk": 11.5, "rent_2ldk": 16.0, "rent_3ldk": 21.0, "vacant_rate": 5.8},
        "13119": {"rent_1r": 6.5, "rent_1k": 7.0, "rent_1dk": 8.0, "rent_1ldk": 11.0, "rent_2ldk": 15.5, "rent_3ldk": 20.5, "vacant_rate": 4.5},
        "13120": {"rent_1r": 6.8, "rent_1k": 7.3, "rent_1dk": 8.5, "rent_1ldk": 12.0, "rent_2ldk": 16.5, "rent_3ldk": 22.0, "vacant_rate": 4.0},
        "13121": {"rent_1r": 5.8, "rent_1k": 6.2, "rent_1dk": 7.5, "rent_1ldk": 10.5, "rent_2ldk": 14.5, "rent_3ldk": 19.0, "vacant_rate": 6.5},
        "13122": {"rent_1r": 5.5, "rent_1k": 6.0, "rent_1dk": 7.2, "rent_1ldk": 10.0, "rent_2ldk": 14.0, "rent_3ldk": 18.5, "vacant_rate": 5.2},
        "13123": {"rent_1r": 6.0, "rent_1k": 6.5, "rent_1dk": 7.8, "rent_1ldk": 11.0, "rent_2ldk": 15.0, "rent_3ldk": 20.0, "vacant_rate": 4.8},
    }
    
    parks_data = {
        "13101": {"total_parks": 15, "total_area_sqm": 200000, "children_parks": 5, "with_playground": 8},
        "13102": {"total_parks": 20, "total_area_sqm": 180000, "children_parks": 8, "with_playground": 12},
        "13103": {"total_parks": 35, "total_area_sqm": 450000, "children_parks": 12, "with_playground": 20},
        "13104": {"total_parks": 45, "total_area_sqm": 380000, "children_parks": 18, "with_playground": 25},
        "13105": {"total_parks": 25, "total_area_sqm": 220000, "children_parks": 10, "with_playground": 15},
        "13106": {"total_parks": 22, "total_area_sqm": 150000, "children_parks": 9, "with_playground": 13},
        "13107": {"total_parks": 28, "total_area_sqm": 180000, "children_parks": 12, "with_playground": 16},
        "13108": {"total_parks": 55, "total_area_sqm": 680000, "children_parks": 22, "with_playground": 30},
        "13109": {"total_parks": 40, "total_area_sqm": 320000, "children_parks": 16, "with_playground": 22},
        "13110": {"total_parks": 30, "total_area_sqm": 250000, "children_parks": 12, "with_playground": 18},
        "13111": {"total_parks": 65, "total_area_sqm": 520000, "children_parks": 28, "with_playground": 35},
        "13112": {"total_parks": 80, "total_area_sqm": 750000, "children_parks": 35, "with_playground": 45},
        "13113": {"total_parks": 25, "total_area_sqm": 200000, "children_parks": 10, "with_playground": 15},
        "13114": {"total_parks": 35, "total_area_sqm": 280000, "children_parks": 15, "with_playground": 20},
        "13115": {"total_parks": 60, "total_area_sqm": 480000, "children_parks": 25, "with_playground": 32},
        "13116": {"total_parks": 28, "total_area_sqm": 180000, "children_parks": 12, "with_playground": 16},
        "13117": {"total_parks": 40, "total_area_sqm": 350000, "children_parks": 18, "with_playground": 22},
        "13118": {"total_parks": 25, "total_area_sqm": 160000, "children_parks": 11, "with_playground": 14},
        "13119": {"total_parks": 55, "total_area_sqm": 450000, "children_parks": 24, "with_playground": 30},
        "13120": {"total_parks": 75, "total_area_sqm": 680000, "children_parks": 32, "with_playground": 40},
        "13121": {"total_parks": 70, "total_area_sqm": 620000, "children_parks": 30, "with_playground": 38},
        "13122": {"total_parks": 58, "total_area_sqm": 480000, "children_parks": 25, "with_playground": 32},
        "13123": {"total_parks": 65, "total_area_sqm": 580000, "children_parks": 28, "with_playground": 35},
    }
    
    schools_data = {
        "13101": {"elementary_schools": 8, "junior_high_schools": 4, "high_schools": 3, "libraries": 5},
        "13102": {"elementary_schools": 16, "junior_high_schools": 7, "high_schools": 5, "libraries": 8},
        "13103": {"elementary_schools": 18, "junior_high_schools": 8, "high_schools": 7, "libraries": 10},
        "13104": {"elementary_schools": 29, "junior_high_schools": 11, "high_schools": 10, "libraries": 12},
        "13105": {"elementary_schools": 20, "junior_high_schools": 8, "high_schools": 6, "libraries": 11},
        "13106": {"elementary_schools": 19, "junior_high_schools": 7, "high_schools": 5, "libraries": 8},
        "13107": {"elementary_schools": 25, "junior_high_schools": 10, "high_schools": 6, "libraries": 9},
        "13108": {"elementary_schools": 45, "junior_high_schools": 23, "high_schools": 12, "libraries": 15},
        "13109": {"elementary_schools": 37, "junior_high_schools": 15, "high_schools": 9, "libraries": 12},
        "13110": {"elementary_schools": 22, "junior_high_schools": 9, "high_schools": 7, "libraries": 10},
        "13111": {"elementary_schools": 59, "junior_high_schools": 28, "high_schools": 14, "libraries": 16},
        "13112": {"elementary_schools": 61, "junior_high_schools": 29, "high_schools": 17, "libraries": 21},
        "13113": {"elementary_schools": 18, "junior_high_schools": 8, "high_schools": 6, "libraries": 9},
        "13114": {"elementary_schools": 25, "junior_high_schools": 11, "high_schools": 7, "libraries": 10},
        "13115": {"elementary_schools": 41, "junior_high_schools": 23, "high_schools": 12, "libraries": 14},
        "13116": {"elementary_schools": 22, "junior_high_schools": 8, "high_schools": 8, "libraries": 9},
        "13117": {"elementary_schools": 35, "junior_high_schools": 12, "high_schools": 8, "libraries": 11},
        "13118": {"elementary_schools": 24, "junior_high_schools": 10, "high_schools": 5, "libraries": 7},
        "13119": {"elementary_schools": 51, "junior_high_schools": 23, "high_schools": 11, "libraries": 13},
        "13120": {"elementary_schools": 65, "junior_high_schools": 33, "high_schools": 15, "libraries": 17},
        "13121": {"elementary_schools": 69, "junior_high_schools": 36, "high_schools": 12, "libraries": 15},
        "13122": {"elementary_schools": 49, "junior_high_schools": 24, "high_schools": 10, "libraries": 12},
        "13123": {"elementary_schools": 70, "junior_high_schools": 33, "high_schools": 13, "libraries": 14},
    }
    
    safety_data = {
        "13101": {"total_crimes": 1200, "crime_rate_per_1000": 17.9, "police_boxes": 15, "security_cameras": 450},
        "13102": {"total_crimes": 2100, "crime_rate_per_1000": 12.4, "police_boxes": 18, "security_cameras": 380},
        "13103": {"total_crimes": 3500, "crime_rate_per_1000": 13.5, "police_boxes": 25, "security_cameras": 520},
        "13104": {"total_crimes": 4800, "crime_rate_per_1000": 13.7, "police_boxes": 28, "security_cameras": 480},
        "13105": {"total_crimes": 1800, "crime_rate_per_1000": 7.5, "police_boxes": 20, "security_cameras": 320},
        "13106": {"total_crimes": 2600, "crime_rate_per_1000": 12.4, "police_boxes": 18, "security_cameras": 280},
        "13107": {"total_crimes": 2200, "crime_rate_per_1000": 8.0, "police_boxes": 22, "security_cameras": 250},
        "13108": {"total_crimes": 3800, "crime_rate_per_1000": 7.2, "police_boxes": 35, "security_cameras": 420},
        "13109": {"total_crimes": 3200, "crime_rate_per_1000": 7.6, "police_boxes": 30, "security_cameras": 380},
        "13110": {"total_crimes": 2000, "crime_rate_per_1000": 7.0, "police_boxes": 25, "security_cameras": 350},
        "13111": {"total_crimes": 4500, "crime_rate_per_1000": 6.1, "police_boxes": 45, "security_cameras": 480},
        "13112": {"total_crimes": 5200, "crime_rate_per_1000": 5.5, "police_boxes": 50, "security_cameras": 550},
        "13113": {"total_crimes": 3100, "crime_rate_per_1000": 12.9, "police_boxes": 22, "security_cameras": 420},
        "13114": {"total_crimes": 2800, "crime_rate_per_1000": 8.2, "police_boxes": 25, "security_cameras": 280},
        "13115": {"total_crimes": 3500, "crime_rate_per_1000": 5.9, "police_boxes": 38, "security_cameras": 350},
        "13116": {"total_crimes": 3600, "crime_rate_per_1000": 12.0, "police_boxes": 24, "security_cameras": 320},
        "13117": {"total_crimes": 2400, "crime_rate_per_1000": 6.8, "police_boxes": 28, "security_cameras": 250},
        "13118": {"total_crimes": 1800, "crime_rate_per_1000": 8.2, "police_boxes": 20, "security_cameras": 180},
        "13119": {"total_crimes": 3800, "crime_rate_per_1000": 6.5, "police_boxes": 40, "security_cameras": 320},
        "13120": {"total_crimes": 4200, "crime_rate_per_1000": 5.6, "police_boxes": 48, "security_cameras": 380},
        "13121": {"total_crimes": 5500, "crime_rate_per_1000": 7.9, "police_boxes": 45, "security_cameras": 350},
        "13122": {"total_crimes": 3600, "crime_rate_per_1000": 7.7, "police_boxes": 35, "security_cameras": 280},
        "13123": {"total_crimes": 4800, "crime_rate_per_1000": 6.9, "police_boxes": 42, "security_cameras": 320},
    }
    
    childcare_data = {
        "13101": {"nursery_schools": 12, "kindergartens": 6, "waiting_children": 15, "child_support_centers": 3},
        "13102": {"nursery_schools": 25, "kindergartens": 10, "waiting_children": 28, "child_support_centers": 5},
        "13103": {"nursery_schools": 35, "kindergartens": 15, "waiting_children": 45, "child_support_centers": 8},
        "13104": {"nursery_schools": 45, "kindergartens": 18, "waiting_children": 38, "child_support_centers": 10},
        "13105": {"nursery_schools": 28, "kindergartens": 12, "waiting_children": 20, "child_support_centers": 6},
        "13106": {"nursery_schools": 26, "kindergartens": 10, "waiting_children": 18, "child_support_centers": 5},
        "13107": {"nursery_schools": 32, "kindergartens": 14, "waiting_children": 22, "child_support_centers": 6},
        "13108": {"nursery_schools": 58, "kindergartens": 25, "waiting_children": 15, "child_support_centers": 12},
        "13109": {"nursery_schools": 48, "kindergartens": 20, "waiting_children": 12, "child_support_centers": 10},
        "13110": {"nursery_schools": 35, "kindergartens": 15, "waiting_children": 8, "child_support_centers": 8},
        "13111": {"nursery_schools": 75, "kindergartens": 32, "waiting_children": 5, "child_support_centers": 15},
        "13112": {"nursery_schools": 82, "kindergartens": 35, "waiting_children": 0, "child_support_centers": 18},
        "13113": {"nursery_schools": 30, "kindergartens": 12, "waiting_children": 35, "child_support_centers": 7},
        "13114": {"nursery_schools": 38, "kindergartens": 16, "waiting_children": 25, "child_support_centers": 8},
        "13115": {"nursery_schools": 55, "kindergartens": 24, "waiting_children": 10, "child_support_centers": 12},
        "13116": {"nursery_schools": 32, "kindergartens": 14, "waiting_children": 30, "child_support_centers": 7},
        "13117": {"nursery_schools": 42, "kindergartens": 18, "waiting_children": 18, "child_support_centers": 9},
        "13118": {"nursery_schools": 28, "kindergartens": 12, "waiting_children": 20, "child_support_centers": 5},
        "13119": {"nursery_schools": 62, "kindergartens": 28, "waiting_children": 8, "child_support_centers": 13},
        "13120": {"nursery_schools": 78, "kindergartens": 35, "waiting_children": 0, "child_support_centers": 16},
        "13121": {"nursery_schools": 72, "kindergartens": 32, "waiting_children": 15, "child_support_centers": 14},
        "13122": {"nursery_schools": 55, "kindergartens": 25, "waiting_children": 12, "child_support_centers": 11},
        "13123": {"nursery_schools": 68, "kindergartens": 30, "waiting_children": 10, "child_support_centers": 13},
    }
    
    medical_data = {
        "13101": {"hospitals": 12, "clinics": 85, "pediatric_clinics": 8, "doctors_per_1000": 3.5},
        "13102": {"hospitals": 15, "clinics": 120, "pediatric_clinics": 12, "doctors_per_1000": 3.2},
        "13103": {"hospitals": 20, "clinics": 180, "pediatric_clinics": 18, "doctors_per_1000": 3.8},
        "13104": {"hospitals": 25, "clinics": 220, "pediatric_clinics": 22, "doctors_per_1000": 3.5},
        "13105": {"hospitals": 18, "clinics": 150, "pediatric_clinics": 15, "doctors_per_1000": 4.2},
        "13106": {"hospitals": 14, "clinics": 110, "pediatric_clinics": 10, "doctors_per_1000": 2.8},
        "13107": {"hospitals": 16, "clinics": 125, "pediatric_clinics": 12, "doctors_per_1000": 2.5},
        "13108": {"hospitals": 28, "clinics": 210, "pediatric_clinics": 20, "doctors_per_1000": 2.6},
        "13109": {"hospitals": 22, "clinics": 180, "pediatric_clinics": 18, "doctors_per_1000": 2.8},
        "13110": {"hospitals": 18, "clinics": 160, "pediatric_clinics": 16, "doctors_per_1000": 3.2},
        "13111": {"hospitals": 35, "clinics": 280, "pediatric_clinics": 28, "doctors_per_1000": 2.4},
        "13112": {"hospitals": 38, "clinics": 320, "pediatric_clinics": 32, "doctors_per_1000": 2.7},
        "13113": {"hospitals": 16, "clinics": 140, "pediatric_clinics": 14, "doctors_per_1000": 3.5},
        "13114": {"hospitals": 18, "clinics": 150, "pediatric_clinics": 15, "doctors_per_1000": 2.6},
        "13115": {"hospitals": 28, "clinics": 240, "pediatric_clinics": 24, "doctors_per_1000": 2.8},
        "13116": {"hospitals": 15, "clinics": 130, "pediatric_clinics": 13, "doctors_per_1000": 2.5},
        "13117": {"hospitals": 20, "clinics": 160, "pediatric_clinics": 16, "doctors_per_1000": 2.4},
        "13118": {"hospitals": 12, "clinics": 95, "pediatric_clinics": 9, "doctors_per_1000": 2.3},
        "13119": {"hospitals": 30, "clinics": 250, "pediatric_clinics": 25, "doctors_per_1000": 2.5},
        "13120": {"hospitals": 36, "clinics": 300, "pediatric_clinics": 30, "doctors_per_1000": 2.6},
        "13121": {"hospitals": 32, "clinics": 260, "pediatric_clinics": 26, "doctors_per_1000": 2.2},
        "13122": {"hospitals": 25, "clinics": 200, "pediatric_clinics": 20, "doctors_per_1000": 2.3},
        "13123": {"hospitals": 30, "clinics": 240, "pediatric_clinics": 24, "doctors_per_1000": 2.4},
    }
    
    culture_data = {
        "13101": {"libraries": 5, "museums": 8, "community_centers": 6, "sports_facilities": 4, "movie_theaters": 2, "theme_parks": 0, "shopping_malls": 3, "game_centers": 5},
        "13102": {"libraries": 8, "museums": 6, "community_centers": 10, "sports_facilities": 8, "movie_theaters": 3, "theme_parks": 0, "shopping_malls": 5, "game_centers": 8},
        "13103": {"libraries": 10, "museums": 12, "community_centers": 15, "sports_facilities": 12, "movie_theaters": 5, "theme_parks": 0, "shopping_malls": 8, "game_centers": 10},
        "13104": {"libraries": 12, "museums": 10, "community_centers": 18, "sports_facilities": 15, "movie_theaters": 8, "theme_parks": 0, "shopping_malls": 10, "game_centers": 15},
        "13105": {"libraries": 11, "museums": 9, "community_centers": 12, "sports_facilities": 10, "movie_theaters": 3, "theme_parks": 1, "shopping_malls": 4, "game_centers": 6},  # 文京区: 東京ドームシティ
        "13106": {"libraries": 8, "museums": 15, "community_centers": 10, "sports_facilities": 8, "movie_theaters": 4, "theme_parks": 1, "shopping_malls": 6, "game_centers": 12},  # 台東区: 浅草花やしき
        "13107": {"libraries": 9, "museums": 5, "community_centers": 12, "sports_facilities": 10, "movie_theaters": 2, "theme_parks": 0, "shopping_malls": 3, "game_centers": 7},
        "13108": {"libraries": 15, "museums": 8, "community_centers": 20, "sports_facilities": 18, "movie_theaters": 5, "theme_parks": 1, "shopping_malls": 8, "game_centers": 10},
        "13109": {"libraries": 12, "museums": 6, "community_centers": 16, "sports_facilities": 14, "movie_theaters": 4, "theme_parks": 0, "shopping_malls": 6, "game_centers": 9},
        "13110": {"libraries": 10, "museums": 7, "community_centers": 14, "sports_facilities": 12, "movie_theaters": 3, "theme_parks": 0, "shopping_malls": 5, "game_centers": 8},
        "13111": {"libraries": 16, "museums": 5, "community_centers": 22, "sports_facilities": 20, "movie_theaters": 6, "theme_parks": 0, "shopping_malls": 9, "game_centers": 12},
        "13112": {"libraries": 21, "museums": 9, "community_centers": 26, "sports_facilities": 24, "movie_theaters": 7, "theme_parks": 0, "shopping_malls": 11, "game_centers": 14},
        "13113": {"libraries": 9, "museums": 8, "community_centers": 12, "sports_facilities": 10, "movie_theaters": 6, "theme_parks": 0, "shopping_malls": 7, "game_centers": 10},
        "13114": {"libraries": 10, "museums": 4, "community_centers": 14, "sports_facilities": 12, "movie_theaters": 3, "theme_parks": 0, "shopping_malls": 4, "game_centers": 8},
        "13115": {"libraries": 14, "museums": 6, "community_centers": 18, "sports_facilities": 16, "movie_theaters": 4, "theme_parks": 0, "shopping_malls": 6, "game_centers": 9},
        "13116": {"libraries": 9, "museums": 5, "community_centers": 12, "sports_facilities": 10, "movie_theaters": 5, "theme_parks": 2, "shopping_malls": 7, "game_centers": 11},  # 豊島区: サンシャインシティ、ナンジャタウン
        "13117": {"libraries": 11, "museums": 4, "community_centers": 15, "sports_facilities": 13, "movie_theaters": 3, "theme_parks": 0, "shopping_malls": 5, "game_centers": 7},
        "13118": {"libraries": 7, "museums": 3, "community_centers": 10, "sports_facilities": 8, "movie_theaters": 2, "theme_parks": 1, "shopping_malls": 3, "game_centers": 5},  # 荒川区: あらかわ遊園
        "13119": {"libraries": 13, "museums": 5, "community_centers": 18, "sports_facilities": 16, "movie_theaters": 4, "theme_parks": 0, "shopping_malls": 7, "game_centers": 9},
        "13120": {"libraries": 17, "museums": 6, "community_centers": 22, "sports_facilities": 20, "movie_theaters": 5, "theme_parks": 1, "shopping_malls": 8, "game_centers": 10},  # 練馬区: ハリー・ポッター スタジオツアー
        "13121": {"libraries": 15, "museums": 4, "community_centers": 20, "sports_facilities": 18, "movie_theaters": 4, "theme_parks": 0, "shopping_malls": 7, "game_centers": 8},
        "13122": {"libraries": 12, "museums": 3, "community_centers": 16, "sports_facilities": 14, "movie_theaters": 3, "theme_parks": 0, "shopping_malls": 5, "game_centers": 7},
        "13123": {"libraries": 14, "museums": 4, "community_centers": 18, "sports_facilities": 16, "movie_theaters": 4, "theme_parks": 1, "shopping_malls": 6, "game_centers": 8},  # 江戸川区: 葛西臨海公園
    }
    
    # 各区のデータを作成
    for area_data in areas_data:
        area_code = area_data["code"]
        
        # 年齢分布データをJSONから取得
        if area_data["name"] in age_population_data:
            json_age_data = age_population_data[area_data["name"]]
            # すべての年齢分布データを含める
            age_dist = {
                "0-4": json_age_data.get("0-4", 0),
                "5-9": json_age_data.get("5-9", 0),
                "10-14": json_age_data.get("10-14", 0),
                "15-19": json_age_data.get("15-19", 0),
                "20-29": json_age_data.get("20-29", 0),
                "30-39": json_age_data.get("30-39", 0),
                "40-49": json_age_data.get("40-49", 0),
                "50-59": json_age_data.get("50-59", 0),
                "60-64": json_age_data.get("60-64", 0),
                "65-74": json_age_data.get("65-74", 0),
                "75+": json_age_data.get("75+", 0),
                "0-14": json_age_data.get("0-14", 0),
                "15-64": json_age_data.get("15-64", 0),
                "65+": json_age_data.get("65+", 0)
            }
            # 年齢別データから総人口を計算して更新
            total_population = age_dist["0-14"] + age_dist["15-64"] + age_dist["65+"]
            area_data["pop"] = total_population
        else:
            # フォールバック用のデフォルトデータ
            age_dist = {
                "0-4": int(area_data["pop"] * 0.05),
                "5-9": int(area_data["pop"] * 0.05),
                "10-14": int(area_data["pop"] * 0.05),
                "15-19": int(area_data["pop"] * 0.05),
                "20-29": int(area_data["pop"] * 0.15),
                "30-39": int(area_data["pop"] * 0.15),
                "40-49": int(area_data["pop"] * 0.15),
                "50-59": int(area_data["pop"] * 0.10),
                "60-64": int(area_data["pop"] * 0.05),
                "65-74": int(area_data["pop"] * 0.10),
                "75+": int(area_data["pop"] * 0.10),
                "0-14": int(area_data["pop"] * 0.15),
                "15-64": int(area_data["pop"] * 0.65),
                "65+": int(area_data["pop"] * 0.20)
            }
        
        # 各データを適切なモデルインスタンスとして作成（オリジナルデータを使用）
        housing = HousingData(
            rent_1r=housing_data[area_code]["rent_1r"],
            rent_1k=housing_data[area_code]["rent_1k"],
            rent_1dk=housing_data[area_code]["rent_1dk"],
            rent_1ldk=housing_data[area_code]["rent_1ldk"],
            rent_2ldk=housing_data[area_code]["rent_2ldk"],
            rent_3ldk=housing_data[area_code]["rent_3ldk"],
            vacant_rate=housing_data[area_code]["vacant_rate"]
        )
        
        schools = SchoolData(
            elementary_schools=schools_data[area_code]["elementary_schools"],
            junior_high_schools=schools_data[area_code]["junior_high_schools"],
            high_schools=schools_data[area_code]["high_schools"],
            universities=1 if area_data["pop"] > 300000 else 0,
            libraries=schools_data[area_code]["libraries"]
        )
        
        childcare = ChildcareData(
            nursery_schools=childcare_data[area_code]["nursery_schools"],
            kindergartens=childcare_data[area_code]["kindergartens"],
            total_capacity=int(childcare_data[area_code]["nursery_schools"] * 60 + childcare_data[area_code]["kindergartens"] * 30),
            waiting_children=childcare_data[area_code]["waiting_children"],
            acceptance_rate=100.0 if childcare_data[area_code]["waiting_children"] == 0 else 85.0
        )
        
        parks = ParkData(
            total_parks=parks_data[area_code]["total_parks"],
            total_area_m2=parks_data[area_code]["total_area_sqm"],
            park_per_capita=parks_data[area_code]["total_area_sqm"] / area_data["pop"],
            large_parks=max(1, parks_data[area_code]["total_parks"] // 10)
        )
        
        medical = MedicalData(
            hospitals=medical_data[area_code]["hospitals"],
            clinics=medical_data[area_code]["clinics"],
            doctors_per_1000=medical_data[area_code]["doctors_per_1000"],
            emergency_hospitals=max(1, medical_data[area_code]["hospitals"] // 10)
        )
        
        safety = SafetyData(
            crime_rate_per_1000=safety_data[area_code]["crime_rate_per_1000"],
            disaster_risk_score=3.0 if area_code in ["13107", "13108", "13123"] else 2.0,
            police_stations=safety_data[area_code]["police_boxes"],
            fire_stations=max(1, int(area_data["area"] / 5))
        )
        
        culture = CultureData(
            libraries=culture_data[area_code]["libraries"],
            museums=culture_data[area_code]["museums"],
            community_centers=culture_data[area_code]["community_centers"],
            sports_facilities=culture_data[area_code]["sports_facilities"],
            library_books_per_capita=5.0 if area_code in ["13101", "13104", "13112"] else 3.0,
            movie_theaters=culture_data[area_code]["movie_theaters"],
            theme_parks=culture_data[area_code]["theme_parks"],
            shopping_malls=culture_data[area_code]["shopping_malls"],
            game_centers=culture_data[area_code]["game_centers"]
        )
        
        area = Area(
            code=area_data["code"],
            name=area_data["name"],
            center_lat=area_data["lat"],
            center_lng=area_data["lng"],
            area_km2=area_data["area"],
            population=area_data["pop"],
            households=area_data["households"],
            population_density=area_data["density"],
            age_distribution=age_dist,
            housing_data=housing,
            school_data=schools,
            childcare_data=childcare,
            park_data=parks,
            medical_data=medical,
            safety_data=safety,
            culture_data=culture
        )
        
        await area.insert()
    
    print(f"Created {len(areas_data)} areas")
    
    # ゴミ分別データを追加
    from app.data.waste_separation_rules import WASTE_SEPARATION_RULES
    
    for area_data in areas_data:
        code = area_data["code"]
        if code in WASTE_SEPARATION_RULES:
            rule = WASTE_SEPARATION_RULES[code]
            waste_doc = WasteSeparation(
                area_code=code,
                area_name=area_data["name"],
                separation_types=rule["separation_types"],
                collection_days=rule["collection_days"],
                strictness_level=rule["strictness_level"],
                special_rules=rule["special_rules"],
                features=rule["features"]
            )
            await waste_doc.insert()
    
    print(f"Created waste separation data for {len(areas_data)} areas")
    
    # 東京都オープンデータサービスを使用して混雑度データを生成
    
    # 混雑度データを追加
    for area_data in areas_data:
        area_code = area_data["code"]
        
        # 東京都オープンデータに基づいた混雑度を計算
        congestion_result = tokyo_congestion_service.calculate_area_congestion(
            area_code,
            area_data["name"]
        )
        
        congestion_doc = CongestionData(
            area_code=area_code,
            area_name=area_data["name"],
            weekday_congestion=congestion_result["weekday_congestion"],
            weekend_congestion=congestion_result["weekend_congestion"],
            congestion_factors=congestion_result["congestion_factors"],
            congestion_score=congestion_result["congestion_score"],
            peak_times=congestion_result["peak_times"],
            quiet_times=congestion_result["quiet_times"],
            facility_congestion=congestion_result["facility_congestion"]
        )
        await congestion_doc.insert()
    
    print(f"Created congestion data for {len(areas_data)} areas")
    print("MongoDB initialization completed!")

async def main():
    """Main function"""
    try:
        await init_mongodb()
        await init_all_areas()
    finally:
        await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(main())