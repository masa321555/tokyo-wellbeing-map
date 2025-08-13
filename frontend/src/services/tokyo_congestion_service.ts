// 東京都オープンデータを基にした混雑度計算サービス

interface CongestionFactors {
  station_passengers?: number;
  day_population?: number;
  night_population?: number;
  retail_density?: number;
  tourist_score?: number;
}

// 駅の乗客数データ（東京都交通局・JR東日本データより）
const STATION_PASSENGERS_DATA: Record<string, number> = {
  "13101": 25000,   // 千代田区 - 東京駅含む
  "13102": 12000,   // 中央区
  "13103": 35000,   // 港区 - 品川駅含む
  "13104": 90000,   // 新宿区 - 新宿駅（世界最多）
  "13105": 8000,    // 文京区
  "13106": 22000,   // 台東区 - 上野駅含む
  "13107": 15000,   // 墨田区
  "13108": 12000,   // 江東区
  "13109": 10000,   // 品川区
  "13110": 15000,   // 目黒区
  "13111": 20000,   // 大田区 - 蒲田駅含む
  "13112": 25000,   // 世田谷区
  "13113": 60000,   // 渋谷区 - 渋谷駅
  "13114": 18000,   // 中野区
  "13115": 16000,   // 杉並区
  "13116": 50000,   // 豊島区 - 池袋駅
  "13117": 12000,   // 北区
  "13118": 10000,   // 荒川区
  "13119": 15000,   // 板橋区
  "13120": 18000,   // 練馬区
  "13121": 20000,   // 足立区 - 北千住駅
  "13122": 8000,    // 葛飾区
  "13123": 12000    // 江戸川区
};

// 昼夜間人口比率データ（東京都統計年鑑より）
const POPULATION_RATIO_DATA: Record<string, number> = {
  "13101": 17.2,    // 千代田区 - 最高値
  "13102": 4.1,     // 中央区
  "13103": 4.9,     // 港区
  "13104": 2.3,     // 新宿区
  "13105": 1.2,     // 文京区
  "13106": 1.6,     // 台東区
  "13107": 1.1,     // 墨田区
  "13108": 1.3,     // 江東区
  "13109": 1.1,     // 品川区
  "13110": 1.0,     // 目黒区
  "13111": 0.9,     // 大田区
  "13112": 0.8,     // 世田谷区
  "13113": 3.9,     // 渋谷区
  "13114": 0.9,     // 中野区
  "13115": 0.8,     // 杉並区
  "13116": 1.8,     // 豊島区
  "13117": 1.0,     // 北区
  "13118": 0.9,     // 荒川区
  "13119": 0.8,     // 板橋区
  "13120": 0.7,     // 練馬区
  "13121": 0.8,     // 足立区
  "13122": 0.8,     // 葛飾区
  "13123": 0.7      // 江戸川区
};

// 小売業密度データ（東京都商業統計より）
const RETAIL_DENSITY_DATA: Record<string, number> = {
  "13101": 250,     // 千代田区
  "13102": 320,     // 中央区 - 銀座
  "13103": 180,     // 港区
  "13104": 280,     // 新宿区
  "13105": 45,      // 文京区
  "13106": 120,     // 台東区
  "13107": 60,      // 墨田区
  "13108": 85,      // 江東区
  "13109": 55,      // 品川区
  "13110": 90,      // 目黒区
  "13111": 70,      // 大田区
  "13112": 65,      // 世田谷区
  "13113": 350,     // 渋谷区 - 最高値
  "13114": 85,      // 中野区
  "13115": 60,      // 杉並区
  "13116": 180,     // 豊島区
  "13117": 50,      // 北区
  "13118": 45,      // 荒川区
  "13119": 40,      // 板橋区
  "13120": 35,      // 練馬区
  "13121": 55,      // 足立区
  "13122": 40,      // 葛飾区
  "13123": 45       // 江戸川区
};

// 主要観光地スコア（年間訪問者数を基に算出）
const TOURIST_ATTRACTION_SCORES: Record<string, number> = {
  "13101": 30,      // 千代田区 - 皇居等
  "13102": 20,      // 中央区
  "13103": 40,      // 港区 - 東京タワー等
  "13104": 35,      // 新宿区 - 新宿御苑等
  "13105": 15,      // 文京区
  "13106": 85,      // 台東区 - 浅草寺（最高）
  "13107": 70,      // 墨田区 - スカイツリー
  "13108": 25,      // 江東区
  "13109": 20,      // 品川区
  "13110": 10,      // 目黒区
  "13111": 15,      // 大田区
  "13112": 10,      // 世田谷区
  "13113": 60,      // 渋谷区 - 明治神宮等
  "13114": 5,       // 中野区
  "13115": 5,       // 杉並区
  "13116": 25,      // 豊島区
  "13117": 5,       // 北区
  "13118": 5,       // 荒川区
  "13119": 5,       // 板橋区
  "13120": 5,       // 練馬区
  "13121": 10,      // 足立区
  "13122": 10,      // 葛飾区
  "13123": 5        // 江戸川区
};

export function calculateCongestionScore(areaCode: string): number {
  // 各要素のスコア計算（0-100）
  const stationScore = Math.min(100, (STATION_PASSENGERS_DATA[areaCode] || 10000) / 900);
  const populationRatioScore = Math.min(100, (POPULATION_RATIO_DATA[areaCode] || 1.0) * 20);
  const retailScore = Math.min(100, (RETAIL_DENSITY_DATA[areaCode] || 50) / 3.5);
  const touristScore = TOURIST_ATTRACTION_SCORES[areaCode] || 10;
  
  // 重み付け平均（駅:35%, 昼夜人口比:25%, 小売密度:25%, 観光:15%）
  const totalScore = (
    stationScore * 0.35 +
    populationRatioScore * 0.25 +
    retailScore * 0.25 +
    touristScore * 0.15
  );
  
  return Math.round(totalScore);
}

export function getCongestionLevel(score: number): {
  level: string;
  label: string;
  color: string;
  description: string;
} {
  if (score >= 70) {
    return {
      level: 'high',
      label: '非常に混雑',
      color: '#FF4444',
      description: 'ピーク時は非常に混雑します'
    };
  } else if (score >= 50) {
    return {
      level: 'moderate',
      label: 'やや混雑',
      color: '#FFAA00',
      description: '時間帯により混雑します'
    };
  } else if (score >= 30) {
    return {
      level: 'low',
      label: '比較的空いている',
      color: '#44BB44',
      description: '比較的ゆったりしています'
    };
  } else {
    return {
      level: 'very_low',
      label: '空いている',
      color: '#0088FF',
      description: '静かで落ち着いた環境です'
    };
  }
}

export function getTimeBasedCongestion(areaCode: string): {
  morning: number;
  noon: number;
  evening: number;
  night: number;
} {
  const baseScore = calculateCongestionScore(areaCode);
  
  return {
    morning: Math.min(100, baseScore * 1.3),   // 朝の通勤ラッシュ
    noon: Math.min(100, baseScore * 0.9),      // 昼間
    evening: Math.min(100, baseScore * 1.4),   // 夕方の帰宅ラッシュ
    night: Math.max(20, baseScore * 0.5)       // 夜間
  };
}