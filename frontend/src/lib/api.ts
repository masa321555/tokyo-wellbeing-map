import axios from 'axios';
import { Area, AreaDetail, WellbeingScore, WellbeingWeights } from '@/types/area';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// エリア関連API
export const areaApi = {
  // 全エリア一覧取得
  getAreas: async (skip = 0, limit = 100) => {
    const response = await api.get<Area[]>('/areas/', {
      params: { skip, limit },
    });
    return response.data;
  },

  // エリア詳細取得
  getAreaDetail: async (areaId: string) => {
    const response = await api.get<AreaDetail>(`/areas/${areaId}`);
    return response.data;
  },

  // エリア比較
  compareAreas: async (areaIds: string[]) => {
    const response = await api.post('/areas/compare', { area_ids: areaIds });
    return response.data;
  },
};

// ウェルビーイング関連API
export const wellbeingApi = {
  // スコア計算
  calculateScore: async (
    areaId: string,
    weights: WellbeingWeights,
    targetRent?: number,
    familySize = 4
  ) => {
    const response = await api.post<WellbeingScore>('/wellbeing/calculate/', {
      area_id: areaId,
      weights,
      target_rent: targetRent,
      family_size: familySize,
    });
    return response.data;
  },

  // ランキング取得
  getRanking: async (weights: WellbeingWeights, targetRent?: number, limit = 10) => {
    const response = await api.post('/wellbeing/ranking/', {
      weights,
      target_rent: targetRent,
      limit,
    });
    return response.data;
  },

  // レコメンド取得
  getRecommendations: async (
    preferences: WellbeingWeights,
    constraints: Record<string, any>
  ) => {
    const response = await api.post('/wellbeing/recommend/', {
      preferences,
      constraints,
    });
    return response.data;
  },

  // プリセット重み取得
  getWeightPresets: async () => {
    const response = await api.get('/wellbeing/weights/presets/');
    return response.data;
  },
};

// 検索関連API
export const searchApi = {
  // エリア検索
  searchAreas: async (params: {
    max_rent?: number;
    min_rent?: number;
    room_type?: string;
    area_names?: string[];
    min_elementary_schools?: number;
    max_waiting_children?: number;
    min_parks?: number;
    max_crime_rate?: number;
    sort_by?: string;
    sort_order?: string;
    skip?: number;
    limit?: number;
  }) => {
    const response = await api.post('/search/', params);
    return response.data;
  },

  // 検索候補取得
  getSuggestions: async (query: string) => {
    const response = await api.get('/search/suggestions/', {
      params: { q: query },
    });
    return response.data;
  },
};

// シミュレーション関連API
export const simulationApi = {
  // 家計シミュレーション
  simulateHousehold: async (params: {
    area_id: string;  // MongoDBのObjectIdは文字列
    adults: number;
    children: number;
    annual_income: number;
    room_type: string;
    commute_destinations?: Array<{ station: string; days_per_week: number }>;
    car_ownership?: boolean;
    childcare_needed?: boolean;
  }) => {
    const response = await api.post('/simulation/household/', params);
    return response.data;
  },

  // 生活スタイルシミュレーション
  simulateLifestyle: async (params: {
    current_area_id: string;  // MongoDBのObjectIdは文字列
    target_area_id: string;    // MongoDBのObjectIdは文字列
    work_from_home_days?: number;
    children_ages?: number[];
    important_facilities?: string[];
  }) => {
    const response = await api.post('/simulation/lifestyle/', params);
    return response.data;
  },

  // 通勤時間推定
  estimateCommuteTime: async (fromAreaId: string, toStation: string) => {
    const response = await api.get('/simulation/commute-time/', {
      params: { from_area_id: fromAreaId, to_station: toStation },
    });
    return response.data;
  },
};

// オープンデータ関連API
export const opendataApi = {
  // データセット一覧
  getDatasets: async (category?: string, limit = 50) => {
    const response = await api.get('/opendata/datasets/', {
      params: { category, limit },
    });
    return response.data;
  },

  // カテゴリ一覧
  getCategories: async () => {
    const response = await api.get('/opendata/categories/');
    return response.data;
  },
};

// 混雑度関連API
export const congestionApi = {
  // エリアの混雑度取得
  getAreaCongestion: async (areaId: string) => {
    const response = await api.get(`/congestion/area/${areaId}/`);
    return response.data;
  },

  // Google Places APIからリアルタイム混雑度データ取得
  getLiveCongestion: async (areaCode: string) => {
    const response = await api.get(`/congestion-google/area/${areaCode}/live`);
    return response.data;
  },

  // エリアの混雑度更新
  updateAreaCongestion: async (areaId: string) => {
    const response = await api.post(`/congestion/update/${areaId}/`);
    return response.data;
  },

  // 複数エリアの混雑度比較
  compareCongestion: async (areaIds: string[]) => {
    const response = await api.get('/congestion/compare', {
      params: { area_ids: areaIds.join(',') },
    });
    return response.data;
  },
};