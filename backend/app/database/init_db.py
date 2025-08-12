import asyncio
from sqlalchemy.orm import Session
from app.database.database import SessionLocal, engine, init_db
from app.models.area import Base, Area, HousingData, ParkData, SchoolData, SafetyData, MedicalData, CultureData, ChildcareData
from app.models.waste_separation import WasteSeparation
from app.services.tokyo_opendata_client import tokyo_opendata_client
import pandas as pd
import json


# 東京23区の基本データ
TOKYO_WARDS = [
    {"code": "13101", "name": "千代田区", "name_kana": "ちよだく", "center_lat": 35.6940, "center_lng": 139.7534, "area_km2": 11.66, "population": 67000},
    {"code": "13102", "name": "中央区", "name_kana": "ちゅうおうく", "center_lat": 35.6706, "center_lng": 139.7720, "area_km2": 10.21, "population": 170000},
    {"code": "13103", "name": "港区", "name_kana": "みなとく", "center_lat": 35.6581, "center_lng": 139.7515, "area_km2": 20.37, "population": 260000},
    {"code": "13104", "name": "新宿区", "name_kana": "しんじゅくく", "center_lat": 35.6938, "center_lng": 139.7036, "area_km2": 18.22, "population": 350000},
    {"code": "13105", "name": "文京区", "name_kana": "ぶんきょうく", "center_lat": 35.7081, "center_lng": 139.7524, "area_km2": 11.29, "population": 240000},
    {"code": "13106", "name": "台東区", "name_kana": "たいとうく", "center_lat": 35.7121, "center_lng": 139.7799, "area_km2": 10.11, "population": 210000},
    {"code": "13107", "name": "墨田区", "name_kana": "すみだく", "center_lat": 35.7107, "center_lng": 139.8013, "area_km2": 13.77, "population": 275000},
    {"code": "13108", "name": "江東区", "name_kana": "こうとうく", "center_lat": 35.6731, "center_lng": 139.8171, "area_km2": 40.16, "population": 525000},
    {"code": "13109", "name": "品川区", "name_kana": "しながわく", "center_lat": 35.6090, "center_lng": 139.7302, "area_km2": 22.84, "population": 420000},
    {"code": "13110", "name": "目黒区", "name_kana": "めぐろく", "center_lat": 35.6414, "center_lng": 139.6982, "area_km2": 14.67, "population": 285000},
    {"code": "13111", "name": "大田区", "name_kana": "おおたく", "center_lat": 35.5614, "center_lng": 139.7161, "area_km2": 60.66, "population": 740000},
    {"code": "13112", "name": "世田谷区", "name_kana": "せたがやく", "center_lat": 35.6464, "center_lng": 139.6530, "area_km2": 58.05, "population": 940000},
    {"code": "13113", "name": "渋谷区", "name_kana": "しぶやく", "center_lat": 35.6639, "center_lng": 139.6982, "area_km2": 15.11, "population": 240000},
    {"code": "13114", "name": "中野区", "name_kana": "なかのく", "center_lat": 35.7074, "center_lng": 139.6637, "area_km2": 15.59, "population": 340000},
    {"code": "13115", "name": "杉並区", "name_kana": "すぎなみく", "center_lat": 35.6994, "center_lng": 139.6364, "area_km2": 34.06, "population": 590000},
    {"code": "13116", "name": "豊島区", "name_kana": "としまく", "center_lat": 35.7260, "center_lng": 139.7166, "area_km2": 13.01, "population": 300000},
    {"code": "13117", "name": "北区", "name_kana": "きたく", "center_lat": 35.7528, "center_lng": 139.7337, "area_km2": 20.61, "population": 355000},
    {"code": "13118", "name": "荒川区", "name_kana": "あらかわく", "center_lat": 35.7362, "center_lng": 139.7830, "area_km2": 10.16, "population": 220000},
    {"code": "13119", "name": "板橋区", "name_kana": "いたばしく", "center_lat": 35.7512, "center_lng": 139.7095, "area_km2": 32.22, "population": 585000},
    {"code": "13120", "name": "練馬区", "name_kana": "ねりまく", "center_lat": 35.7357, "center_lng": 139.6516, "area_km2": 48.08, "population": 750000},
    {"code": "13121", "name": "足立区", "name_kana": "あだちく", "center_lat": 35.7751, "center_lng": 139.8046, "area_km2": 53.25, "population": 695000},
    {"code": "13122", "name": "葛飾区", "name_kana": "かつしかく", "center_lat": 35.7435, "center_lng": 139.8473, "area_km2": 34.80, "population": 465000},
    {"code": "13123", "name": "江戸川区", "name_kana": "えどがわく", "center_lat": 35.7068, "center_lng": 139.8687, "area_km2": 49.90, "population": 700000},
]

# サンプルデータ（実際のデータが取得できない場合の仮データ）
SAMPLE_DATA = {
    "housing": {
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
    },
    "parks": {
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
    },
    "schools": {
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
    },
    "safety": {
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
    },
    "childcare": {
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
    },
    "medical": {
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
    },
    "culture": {
        "13101": {"libraries": 5, "museums": 8, "community_centers": 6, "sports_facilities": 4, "movie_theaters": 2, "theme_parks": 0, "shopping_malls": 3, "game_centers": 5},
        "13102": {"libraries": 8, "museums": 6, "community_centers": 10, "sports_facilities": 8, "movie_theaters": 3, "theme_parks": 0, "shopping_malls": 5, "game_centers": 8},
        "13103": {"libraries": 10, "museums": 12, "community_centers": 15, "sports_facilities": 12, "movie_theaters": 5, "theme_parks": 0, "shopping_malls": 8, "game_centers": 10},
        "13104": {"libraries": 12, "museums": 10, "community_centers": 18, "sports_facilities": 15, "movie_theaters": 8, "theme_parks": 0, "shopping_malls": 10, "game_centers": 15},
        "13105": {"libraries": 11, "museums": 9, "community_centers": 12, "sports_facilities": 10, "movie_theaters": 3, "theme_parks": 0, "shopping_malls": 4, "game_centers": 6},
        "13106": {"libraries": 8, "museums": 15, "community_centers": 10, "sports_facilities": 8, "movie_theaters": 4, "theme_parks": 1, "shopping_malls": 6, "game_centers": 12},
        "13107": {"libraries": 9, "museums": 5, "community_centers": 12, "sports_facilities": 10, "movie_theaters": 2, "theme_parks": 0, "shopping_malls": 3, "game_centers": 7},
        "13108": {"libraries": 15, "museums": 8, "community_centers": 20, "sports_facilities": 18, "movie_theaters": 5, "theme_parks": 1, "shopping_malls": 8, "game_centers": 10},
        "13109": {"libraries": 12, "museums": 6, "community_centers": 16, "sports_facilities": 14, "movie_theaters": 4, "theme_parks": 0, "shopping_malls": 6, "game_centers": 9},
        "13110": {"libraries": 10, "museums": 7, "community_centers": 14, "sports_facilities": 12, "movie_theaters": 3, "theme_parks": 0, "shopping_malls": 5, "game_centers": 8},
        "13111": {"libraries": 16, "museums": 5, "community_centers": 22, "sports_facilities": 20, "movie_theaters": 6, "theme_parks": 0, "shopping_malls": 9, "game_centers": 12},
        "13112": {"libraries": 21, "museums": 9, "community_centers": 26, "sports_facilities": 24, "movie_theaters": 7, "theme_parks": 0, "shopping_malls": 11, "game_centers": 14},
        "13113": {"libraries": 9, "museums": 8, "community_centers": 12, "sports_facilities": 10, "movie_theaters": 6, "theme_parks": 0, "shopping_malls": 7, "game_centers": 10},
        "13114": {"libraries": 10, "museums": 4, "community_centers": 14, "sports_facilities": 12, "movie_theaters": 3, "theme_parks": 0, "shopping_malls": 4, "game_centers": 8},
        "13115": {"libraries": 14, "museums": 6, "community_centers": 18, "sports_facilities": 16, "movie_theaters": 4, "theme_parks": 0, "shopping_malls": 6, "game_centers": 9},
        "13116": {"libraries": 9, "museums": 5, "community_centers": 12, "sports_facilities": 10, "movie_theaters": 5, "theme_parks": 1, "shopping_malls": 7, "game_centers": 11},
        "13117": {"libraries": 11, "museums": 4, "community_centers": 15, "sports_facilities": 13, "movie_theaters": 3, "theme_parks": 0, "shopping_malls": 5, "game_centers": 7},
        "13118": {"libraries": 7, "museums": 3, "community_centers": 10, "sports_facilities": 8, "movie_theaters": 2, "theme_parks": 1, "shopping_malls": 3, "game_centers": 5},
        "13119": {"libraries": 13, "museums": 5, "community_centers": 18, "sports_facilities": 16, "movie_theaters": 4, "theme_parks": 0, "shopping_malls": 7, "game_centers": 9},
        "13120": {"libraries": 17, "museums": 6, "community_centers": 22, "sports_facilities": 20, "movie_theaters": 5, "theme_parks": 1, "shopping_malls": 8, "game_centers": 10},
        "13121": {"libraries": 15, "museums": 4, "community_centers": 20, "sports_facilities": 18, "movie_theaters": 4, "theme_parks": 0, "shopping_malls": 7, "game_centers": 8},
        "13122": {"libraries": 12, "museums": 3, "community_centers": 16, "sports_facilities": 14, "movie_theaters": 3, "theme_parks": 0, "shopping_malls": 5, "game_centers": 7},
        "13123": {"libraries": 14, "museums": 4, "community_centers": 18, "sports_facilities": 16, "movie_theaters": 4, "theme_parks": 1, "shopping_malls": 6, "game_centers": 8},
    }
}


async def init_sample_data(db: Session):
    """サンプルデータでデータベースを初期化"""
    print("Initializing database with sample data...")
    
    # 既存データをクリア
    db.query(ChildcareData).delete()
    db.query(CultureData).delete()
    db.query(MedicalData).delete()
    db.query(SafetyData).delete()
    db.query(SchoolData).delete()
    db.query(ParkData).delete()
    db.query(HousingData).delete()
    db.query(Area).delete()
    db.commit()
    
    # エリアデータを投入
    for ward_data in TOKYO_WARDS:
        area = Area(
            code=ward_data["code"],
            name=ward_data["name"],
            name_kana=ward_data["name_kana"],
            center_lat=ward_data["center_lat"],
            center_lng=ward_data["center_lng"],
            area_km2=ward_data["area_km2"],
            population=ward_data["population"],
            households=int(ward_data["population"] * 0.45),  # 仮の世帯数
            population_density=ward_data["population"] / ward_data["area_km2"]
        )
        db.add(area)
        db.flush()  # IDを取得するため
        
        # 住宅データ
        if ward_data["code"] in SAMPLE_DATA["housing"]:
            housing = HousingData(
                area_id=area.id,
                **SAMPLE_DATA["housing"][ward_data["code"]],
                total_housing=int(ward_data["population"] * 0.5),
                data_source="Sample Data"
            )
            db.add(housing)
        
        # 公園データ
        if ward_data["code"] in SAMPLE_DATA["parks"]:
            park_data = SAMPLE_DATA["parks"][ward_data["code"]]
            park = ParkData(
                area_id=area.id,
                **park_data,
                parks_per_capita=park_data["total_area_sqm"] / ward_data["population"],
                data_source="Sample Data"
            )
            db.add(park)
        
        # 学校データ
        if ward_data["code"] in SAMPLE_DATA["schools"]:
            school = SchoolData(
                area_id=area.id,
                **SAMPLE_DATA["schools"][ward_data["code"]],
                data_source="Sample Data"
            )
            db.add(school)
        
        # 治安データ
        if ward_data["code"] in SAMPLE_DATA["safety"]:
            safety = SafetyData(
                area_id=area.id,
                **SAMPLE_DATA["safety"][ward_data["code"]],
                data_source="Sample Data"
            )
            db.add(safety)
        
        # 子育てデータ
        if ward_data["code"] in SAMPLE_DATA["childcare"]:
            childcare = ChildcareData(
                area_id=area.id,
                **SAMPLE_DATA["childcare"][ward_data["code"]],
                enrollment_rate=85.0,  # 仮の値
                medical_subsidy_age=15,
                data_source="Sample Data"
            )
            db.add(childcare)
        
        # 医療データ
        if ward_data["code"] in SAMPLE_DATA["medical"]:
            medical = MedicalData(
                area_id=area.id,
                **SAMPLE_DATA["medical"][ward_data["code"]],
                emergency_hospitals=2,
                avg_ambulance_time=8.5,
                data_source="Sample Data"
            )
            db.add(medical)
        
        # 文化データ
        if ward_data["code"] in SAMPLE_DATA["culture"]:
            culture = CultureData(
                area_id=area.id,
                **SAMPLE_DATA["culture"][ward_data["code"]],
                library_books_per_capita=3.2,
                cultural_events_yearly=120,
                data_source="Sample Data"
            )
            db.add(culture)
    
    # ゴミ分別データを追加
    print("Adding waste separation data...")
    db.query(WasteSeparation).delete()
    db.commit()
    
    waste_data = {
        "千代田区": {
            "separation_types": ["可燃ごみ", "不燃ごみ", "資源", "粗大ごみ"],
            "collection_days": {
                "可燃ごみ": "月・木",
                "不燃ごみ": "第1・3水曜",
                "資源": "火曜",
                "粗大ごみ": "申込制"
            },
            "strictness_level": 2.5,
            "special_rules": ["ペットボトルはキャップとラベルを外す", "新聞・雑誌は紐で縛る"],
            "features": "ビジネス街のため事業系ごみの分別も重要"
        },
        "中央区": {
            "separation_types": ["燃やすごみ", "燃やさないごみ", "資源", "粗大ごみ"],
            "collection_days": {
                "燃やすごみ": "火・金",
                "燃やさないごみ": "第2・4月曜",
                "資源": "水曜",
                "粗大ごみ": "申込制"
            },
            "strictness_level": 3.0,
            "special_rules": ["資源は種類ごとに分別", "プラスチック製容器包装は別途回収"],
            "features": "集合住宅が多く分別ルールが徹底されている"
        },
        "港区": {
            "separation_types": ["可燃ごみ", "不燃ごみ", "資源", "粗大ごみ"],
            "collection_days": {
                "可燃ごみ": "月・水・金",
                "不燃ごみ": "第1・3火曜",
                "資源": "木曜",
                "粗大ごみ": "申込制"
            },
            "strictness_level": 3.5,
            "special_rules": ["生ごみは水切りを徹底", "古紙は種類別に分別", "外国語表記あり"],
            "features": "国際的な地域で多言語対応の分別ガイドあり"
        }
    }
    
    # 各区のゴミ分別データを追加（サンプルを参考に全区分作成）
    for area in db.query(Area).all():
        if area.name in waste_data:
            data = waste_data[area.name]
        else:
            # デフォルトデータ
            data = {
                "separation_types": ["可燃ごみ", "不燃ごみ", "資源", "粗大ごみ"],
                "collection_days": {
                    "可燃ごみ": "月・木",
                    "不燃ごみ": "第2・4水曜",
                    "資源": "金曜",
                    "粗大ごみ": "申込制"
                },
                "strictness_level": 2.0,
                "special_rules": ["指定袋の使用推奨", "資源は洗って出す"],
                "features": "標準的な分別ルール"
            }
        
        waste_separation = WasteSeparation(
            area_id=area.id,
            separation_types=data["separation_types"],
            collection_days=data["collection_days"],
            strictness_level=data["strictness_level"],
            special_rules=data["special_rules"],
            features=data["features"]
        )
        db.add(waste_separation)
    
    # 年齢層別人口データを追加
    print("Adding age distribution data...")
    age_data = {
        "千代田区": {"0-14": 7821, "15-64": 45823, "65+": 11356, "0-4": 2607, "5-9": 2607, "10-14": 2607},
        "中央区": {"0-14": 23619, "15-64": 123456, "65+": 26925, "0-4": 7873, "5-9": 7873, "10-14": 7873},
        "港区": {"0-14": 37843, "15-64": 197562, "65+": 42595, "0-4": 12614, "5-9": 12614, "10-14": 12615}
    }
    
    for area in db.query(Area).all():
        if area.name in age_data:
            data = age_data[area.name]
        else:
            # デフォルトの年齢分布データ（総人口の比率で計算）
            total_pop = area.population
            data = {
                "0-14": int(total_pop * 0.12),
                "15-64": int(total_pop * 0.65),
                "65+": int(total_pop * 0.23),
                "0-4": int(total_pop * 0.04),
                "5-9": int(total_pop * 0.04),
                "10-14": int(total_pop * 0.04)
            }
        
        # 年齢層別人口データを area.age_distribution に設定
        area.age_distribution = data
        db.add(area)
    
    db.commit()
    print("Sample data initialization completed!")


async def fetch_and_import_opendata(db: Session):
    """東京都オープンデータから実際のデータを取得して投入"""
    print("Fetching data from Tokyo Open Data Portal...")
    
    try:
        # 各カテゴリのデータセットを検索
        housing_datasets = await tokyo_opendata_client.get_dataset_by_category("housing")
        park_datasets = await tokyo_opendata_client.get_dataset_by_category("parks")
        education_datasets = await tokyo_opendata_client.get_dataset_by_category("education")
        safety_datasets = await tokyo_opendata_client.get_dataset_by_category("safety")
        
        print(f"Found {len(housing_datasets)} housing datasets")
        print(f"Found {len(park_datasets)} park datasets")
        print(f"Found {len(education_datasets)} education datasets")
        print(f"Found {len(safety_datasets)} safety datasets")
        
        # データセットからCSVファイルをダウンロードして処理
        # （実際の実装では、各データセットの形式に応じた処理が必要）
        
        # 現時点では、実際のデータ取得が難しい場合はサンプルデータを使用
        print("Note: Using sample data as actual data fetching requires dataset-specific parsing")
        
    except Exception as e:
        print(f"Error fetching open data: {e}")
        print("Falling back to sample data")


async def main():
    """データベース初期化のメイン関数"""
    # データベーステーブルを作成
    init_db()
    
    # セッションを作成
    db = SessionLocal()
    
    try:
        # 実際のオープンデータを取得（可能であれば）
        # await fetch_and_import_opendata(db)
        
        # サンプルデータで初期化
        await init_sample_data(db)
        
    finally:
        db.close()
        await tokyo_opendata_client.close()


if __name__ == "__main__":
    asyncio.run(main())