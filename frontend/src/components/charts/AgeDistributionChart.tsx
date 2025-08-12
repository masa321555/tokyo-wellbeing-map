'use client';

import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Users } from 'lucide-react';

interface AgeDistributionProps {
  data: Record<string, number> | null;
  areaName: string;
}

export const AgeDistributionChart: React.FC<AgeDistributionProps> = ({ data, areaName }) => {
  if (!data) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <Users className="w-5 h-5" />
          年齢層別人口分布
        </h3>
        <p className="text-gray-500 text-center py-8">
          年齢層データがありません
        </p>
      </div>
    );
  }

  // 詳細な年齢層データ
  const detailedData = [
    { age: '0-4歳', count: data['0-4'] || 0, color: '#FFB6C1' },
    { age: '5-9歳', count: data['5-9'] || 0, color: '#FFA07A' },
    { age: '10-14歳', count: data['10-14'] || 0, color: '#FFD700' },
    { age: '15-19歳', count: data['15-19'] || 0, color: '#98FB98' },
    { age: '20-29歳', count: data['20-29'] || 0, color: '#87CEEB' },
    { age: '30-39歳', count: data['30-39'] || 0, color: '#6495ED' },
    { age: '40-49歳', count: data['40-49'] || 0, color: '#9370DB' },
    { age: '50-59歳', count: data['50-59'] || 0, color: '#DDA0DD' },
    { age: '60-64歳', count: data['60-64'] || 0, color: '#F0E68C' },
    { age: '65-74歳', count: data['65-74'] || 0, color: '#DEB887' },
    { age: '75歳以上', count: data['75+'] || 0, color: '#D2691E' },
  ];

  // 3区分データ（円グラフ用）
  const threeCategories = [
    { name: '年少人口（0-14歳）', value: data['0-14'] || 0, color: '#3B82F6' },
    { name: '生産年齢人口（15-64歳）', value: data['15-64'] || 0, color: '#10B981' },
    { name: '高齢者人口（65歳以上）', value: data['65+'] || 0, color: '#F59E0B' },
  ];

  const totalPopulation = threeCategories.reduce((sum, cat) => sum + cat.value, 0);

  // カスタムツールチップ
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const percentage = ((payload[0].value / totalPopulation) * 100).toFixed(1);
      return (
        <div className="bg-white p-3 shadow-lg rounded-lg border border-gray-200">
          <p className="text-sm font-semibold">{label}</p>
          <p className="text-sm text-gray-600">
            人口: {payload[0].value.toLocaleString()}人
          </p>
          <p className="text-sm text-gray-600">
            割合: {percentage}%
          </p>
        </div>
      );
    }
    return null;
  };

  // カスタムラベル（円グラフ用）
  const renderCustomLabel = (entry: any) => {
    const percentage = ((entry.value / totalPopulation) * 100).toFixed(1);
    return `${percentage}%`;
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
        <Users className="w-5 h-5" />
        {areaName}の年齢層別人口分布
      </h3>

      {/* 3区分の概要 */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        {threeCategories.map((category) => (
          <div key={category.name} className="text-center p-3 bg-gray-50 rounded-lg">
            <div className="text-sm text-gray-600">{category.name}</div>
            <div className="text-2xl font-bold mt-1" style={{ color: category.color }}>
              {((category.value / totalPopulation) * 100).toFixed(1)}%
            </div>
            <div className="text-sm text-gray-500">
              {category.value.toLocaleString()}人
            </div>
          </div>
        ))}
      </div>

      {/* 円グラフ */}
      <div className="mb-8">
        <h4 className="text-sm font-medium text-gray-700 mb-3">人口構成比</h4>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={threeCategories}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={renderCustomLabel}
              outerRadius={100}
              fill="#8884d8"
              dataKey="value"
            >
              {threeCategories.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const data = payload[0];
                  return (
                    <div className="bg-white p-3 shadow-lg rounded-lg border border-gray-200">
                      <p className="text-sm font-semibold">{data.name}</p>
                      <p className="text-sm text-gray-600">
                        人口: {data.value.toLocaleString()}人
                      </p>
                      <p className="text-sm text-gray-600">
                        割合: {((data.value / totalPopulation) * 100).toFixed(1)}%
                      </p>
                    </div>
                  );
                }
                return null;
              }}
            />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* 詳細な年齢層別棒グラフ */}
      <div>
        <h4 className="text-sm font-medium text-gray-700 mb-3">詳細な年齢分布</h4>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={detailedData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="age" 
              angle={-45} 
              textAnchor="end" 
              height={70}
              fontSize={12}
            />
            <YAxis 
              tickFormatter={(value) => `${(value / 1000).toFixed(0)}k`}
              fontSize={12}
            />
            <Tooltip content={<CustomTooltip />} />
            <Bar dataKey="count" fill="#3B82F6">
              {detailedData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* 統計情報 */}
      <div className="mt-6 p-4 bg-blue-50 rounded-lg">
        <h4 className="text-sm font-medium text-gray-700 mb-2">人口統計の特徴</h4>
        <ul className="text-sm text-gray-600 space-y-1">
          <li>• 総人口: {totalPopulation.toLocaleString()}人</li>
          <li>• 平均年齢の推定: {calculateAverageAge(data)}歳</li>
          <li>• 高齢化率: {((threeCategories[2].value / totalPopulation) * 100).toFixed(1)}%</li>
          <li>• 年少人口率: {((threeCategories[0].value / totalPopulation) * 100).toFixed(1)}%</li>
        </ul>
      </div>
    </div>
  );
};

// 平均年齢を推定する補助関数
function calculateAverageAge(data: Record<string, number>): string {
  const ageRanges = [
    { range: '0-4', midpoint: 2, count: data['0-4'] || 0 },
    { range: '5-9', midpoint: 7, count: data['5-9'] || 0 },
    { range: '10-14', midpoint: 12, count: data['10-14'] || 0 },
    { range: '15-19', midpoint: 17, count: data['15-19'] || 0 },
    { range: '20-29', midpoint: 25, count: data['20-29'] || 0 },
    { range: '30-39', midpoint: 35, count: data['30-39'] || 0 },
    { range: '40-49', midpoint: 45, count: data['40-49'] || 0 },
    { range: '50-59', midpoint: 55, count: data['50-59'] || 0 },
    { range: '60-64', midpoint: 62, count: data['60-64'] || 0 },
    { range: '65-74', midpoint: 70, count: data['65-74'] || 0 },
    { range: '75+', midpoint: 80, count: data['75+'] || 0 },
  ];

  const totalWeightedAge = ageRanges.reduce((sum, range) => sum + range.midpoint * range.count, 0);
  const totalPopulation = ageRanges.reduce((sum, range) => sum + range.count, 0);

  return totalPopulation > 0 ? (totalWeightedAge / totalPopulation).toFixed(1) : '0';
}