'use client';

import React from 'react';
import { Area, AreaDetail } from '@/types/area';

interface AreaCardProps {
  area: Area | AreaDetail | any;  // APIから返される様々な形式に対応
  isSelected?: boolean;
  onSelect?: () => void;
  onViewDetail?: () => void;
}

export const AreaCard: React.FC<AreaCardProps> = ({
  area,
  isSelected = false,
  onSelect,
  onViewDetail,
}) => {
  const getScoreColor = (score?: number) => {
    if (!score) return 'text-gray-400';
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  // データの取得を柔軟に行う
  const getRent2LDK = () => {
    // APIからの様々な形式に対応
    if (area.housing_data?.rent_2ldk) return area.housing_data.rent_2ldk;
    if (area.rent_info?.rent_2ldk) return area.rent_info.rent_2ldk;
    if (area.rent_2ldk !== undefined && area.rent_2ldk !== null) return area.rent_2ldk;
    return null;
  };

  const getTotalSchools = () => {
    let elementary = 0;
    let juniorHigh = 0;
    
    // 小学校数の取得
    if (area.school_data?.elementary_schools !== undefined) elementary = area.school_data.elementary_schools;
    else if (area.education_info?.elementary_schools !== undefined) elementary = area.education_info.elementary_schools;
    else if (area.elementary_schools !== undefined && area.elementary_schools !== null) elementary = area.elementary_schools;
    
    // 中学校数の取得
    if (area.school_data?.junior_high_schools !== undefined) juniorHigh = area.school_data.junior_high_schools;
    else if (area.education_info?.junior_high_schools !== undefined) juniorHigh = area.education_info.junior_high_schools;
    else if (area.junior_high_schools !== undefined && area.junior_high_schools !== null) juniorHigh = area.junior_high_schools;
    
    const total = elementary + juniorHigh;
    return total > 0 ? total : null;
  };

  const getWaitingChildren = () => {
    if (area.childcare_data?.waiting_children !== undefined) return area.childcare_data.waiting_children;
    if (area.childcare_info?.waiting_children !== undefined) return area.childcare_info.waiting_children;
    if (area.waiting_children !== undefined && area.waiting_children !== null) return area.waiting_children;
    return null;
  };

  const rent2ldk = getRent2LDK();
  const totalSchools = getTotalSchools();
  const waitingChildren = getWaitingChildren();

  return (
    <div
      className={`bg-white rounded-lg shadow-sm border p-4 hover:shadow-md transition-shadow ${
        isSelected ? 'ring-2 ring-blue-500' : ''
      }`}
    >
      <div className="flex justify-between items-start mb-3">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">{area.name || area.area_name}</h3>
          <p className="text-sm text-gray-500">
            人口: {area.population?.toLocaleString() || '-'}人
          </p>
        </div>
        <div className="text-right">
          <div className={`text-2xl font-bold ${getScoreColor(area.wellbeing_score || area.total_score)}`}>
            {(area.wellbeing_score || area.total_score)?.toFixed(1) || '-'}
          </div>
          <p className="text-xs text-gray-500">スコア</p>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-2 mb-4 text-sm">
        <div>
          <span className="text-gray-600">家賃相場(2LDK):</span>
          <span className="ml-1 font-medium">
            {rent2ldk ? `${rent2ldk.toFixed(1)}万円` : '-'}
          </span>
        </div>
        <div>
          <span className="text-gray-600">小中学校:</span>
          <span className="ml-1 font-medium">
            {totalSchools !== null ? `${totalSchools}校` : '-'}
          </span>
        </div>
        <div>
          <span className="text-gray-600">待機児童:</span>
          <span className="ml-1 font-medium">
            {waitingChildren !== null ? `${waitingChildren}人` : '-'}
          </span>
        </div>
        <div>
          <span className="text-gray-600">面積:</span>
          <span className="ml-1 font-medium">
            {area.area_km2 ? `${area.area_km2.toFixed(1)}km²` : '-'}
          </span>
        </div>
      </div>

      <div className="flex gap-2">
        {onSelect && (
          <button
            onClick={onSelect}
            className={`flex-1 px-3 py-2 text-sm font-medium rounded-md transition-colors ${
              isSelected
                ? 'bg-blue-100 text-blue-700 hover:bg-blue-200'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {isSelected ? '選択済み' : '選択'}
          </button>
        )}
        {onViewDetail && (
          <button
            onClick={onViewDetail}
            className="flex-1 px-3 py-2 text-sm font-medium bg-white text-blue-600 border border-blue-600 rounded-md hover:bg-blue-50 transition-colors"
          >
            詳細を見る
          </button>
        )}
      </div>
    </div>
  );
};