export interface Area {
  id: number;
  code: string;
  name: string;
  name_kana?: string;
  name_en?: string;
  center_lat?: number;
  center_lng?: number;
  area_km2?: number;
  population?: number;
  households?: number;
  population_density?: number;
  age_distribution?: Record<string, number>;
  wellbeing_score?: number;
}

export interface HousingData {
  rent_1r?: number;
  rent_1k?: number;
  rent_1dk?: number;
  rent_1ldk?: number;
  rent_2ldk?: number;
  rent_3ldk?: number;
  price_per_sqm?: number;
  total_housing?: number;
  vacant_rate?: number;
}

export interface ParkData {
  total_parks?: number;
  total_area_sqm?: number;
  parks_per_capita?: number;
  city_parks?: number;
  neighborhood_parks?: number;
  children_parks?: number;
  with_playground?: number;
  with_sports?: number;
  large_parks?: number;
}

export interface SchoolData {
  elementary_schools?: number;
  junior_high_schools?: number;
  high_schools?: number;
  students_per_elementary?: number;
  students_per_junior_high?: number;
  cram_schools?: number;
  libraries?: number;
}

export interface SafetyData {
  total_crimes?: number;
  violent_crimes?: number;
  property_crimes?: number;
  crime_rate_per_1000?: number;
  security_cameras?: number;
  police_boxes?: number;
  street_lights?: number;
  traffic_accidents?: number;
  police_stations?: number;
  fire_stations?: number;
}

export interface MedicalData {
  hospitals?: number;
  clinics?: number;
  pediatric_clinics?: number;
  obstetric_clinics?: number;
  doctors_per_1000?: number;
  hospital_beds?: number;
  emergency_hospitals?: number;
  avg_ambulance_time?: number;
}

export interface CultureData {
  libraries?: number;
  museums?: number;
  community_centers?: number;
  sports_facilities?: number;
  movie_theaters?: number;
  theme_parks?: number;
  shopping_malls?: number;
  game_centers?: number;
  library_books_per_capita?: number;
  cultural_events_yearly?: number;
}

export interface ChildcareData {
  nursery_schools?: number;
  kindergartens?: number;
  certified_centers?: number;
  nursery_capacity?: number;
  waiting_children?: number;
  enrollment_rate?: number;
  child_support_centers?: number;
  after_school_programs?: number;
  childcare_subsidy_max?: number;
  medical_subsidy_age?: number;
}

export interface WasteSeparation {
  separation_types?: string[];
  collection_days?: Record<string, string>;
  strictness_level?: number;
  special_rules?: string[];
  features?: string;
  item_details?: Record<string, string>;
  data_source?: string;
}

export interface AreaDetail extends Area {
  housing_data?: HousingData;
  park_data?: ParkData;
  school_data?: SchoolData;
  safety_data?: SafetyData;
  medical_data?: MedicalData;
  culture_data?: CultureData;
  childcare_data?: ChildcareData;
  waste_separation?: WasteSeparation;
  created_at: string;
  updated_at: string;
}

export interface WellbeingWeights {
  rent: number;
  safety: number;
  education: number;
  parks: number;
  medical: number;
  culture: number;
}

export interface WellbeingScore {
  total_score: number;
  category_scores: {
    rent: number;
    safety: number;
    education: number;
    parks: number;
    medical: number;
    culture: number;
  };
  weights: WellbeingWeights;
}