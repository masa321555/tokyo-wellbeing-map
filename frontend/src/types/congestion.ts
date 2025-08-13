// Congestion data types for Tokyo Wellbeing Map
export interface CongestionData {
  area_id: string;  // MongoDB ObjectId
  average_congestion: number;
  peak_congestion: number;
  weekend_congestion: number;
  family_time_congestion: number;
  congestion_score: number;
  facility_congestion: {
    train_station?: {
      average: number;
      peak: number;
    };
    shopping_mall?: {
      average: number;
      peak: number;
    };
    park?: {
      average: number;
      peak: number;
    };
  };
  updated_at?: string;
}