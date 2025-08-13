'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useStore } from '@/store/useStore';
import { areaApi, congestionApi } from '@/lib/api';
import { AreaDetail } from '@/types/area';
import { CongestionData } from '@/types/congestion';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import { Download, ArrowLeft } from 'lucide-react';

export default function ComparePage() {
  const router = useRouter();
  const { selectedAreas } = useStore();
  const [areaDetails, setAreaDetails] = useState<AreaDetail[]>([]);
  const [comparisonData, setComparisonData] = useState<any>(null);
  const [congestionData, setCongestionData] = useState<Record<string, CongestionData>>({});
  const [loading, setLoading] = useState(true);

  // レーダーチャート用データの準備
  const calculateScores = (area: AreaDetail) => {
    // 簡易的なスコア計算（0-100）
    const scores = {
      rent: area.housing_data?.rent_2ldk ? Math.max(0, 100 - (area.housing_data.rent_2ldk - 10) * 2) : 50,
      safety: area.safety_data?.crime_rate_per_1000 ? Math.max(0, 100 - area.safety_data.crime_rate_per_1000 * 5) : 50,
      education: area.school_data?.elementary_schools ? Math.min(100, area.school_data.elementary_schools * 5) : 50,
      parks: area.park_data?.total_parks ? Math.min(100, area.park_data.total_parks * 2) : 50,
      medical: area.medical_data?.hospitals ? Math.min(100, area.medical_data.hospitals * 4) : 50,
      culture: area.culture_data?.libraries ? Math.min(100, area.culture_data.libraries * 10) : 50,
    };
    return scores;
  };

  useEffect(() => {
    console.log('Compare page - selectedAreas:', selectedAreas);
    if (selectedAreas.length > 0) {
      loadComparisonData();
    } else {
      setLoading(false);
    }
  }, [selectedAreas]);

  const loadComparisonData = async () => {
    setLoading(true);
    try {
      const areaIds = selectedAreas.map(a => a.id);
      console.log('Sending area IDs for comparison:', areaIds);
      const result = await areaApi.compareAreas(areaIds);
      setAreaDetails(result.areas);
      
      // ウェルビーイングスコアを計算
      const comparisonMetrics: any = {};
      for (const area of result.areas) {
        const scores = calculateScores(area);
        const totalScore = Object.values(scores).reduce((sum, score) => sum + score, 0) / Object.values(scores).length;
        comparisonMetrics[area.code] = {
          wellbeing_score: totalScore,
          category_scores: scores
        };
      }
      setComparisonData(comparisonMetrics);
      
      // 混雑度データを取得（エラーを個別に処理）
      const congestionMap: Record<string, CongestionData> = {};
      for (let i = 0; i < result.areas.length; i++) {
        const area = result.areas[i];
        try {
          const response = await congestionApi.getAreaCongestion(area.id);
          console.log(`Raw congestion response for ${area.name}:`, response);
          
          // APIレスポンスが{congestion: {...}}形式の場合と直接データの場合の両方に対応
          const congestionData = response.congestion || response;
          
          // データ構造を正規化
          const normalizedData = {
            congestion_score: congestionData.overall?.score || congestionData.congestion_score || 50,
            average_congestion: congestionData.average_congestion || 45,
            peak_congestion: congestionData.peak_congestion || congestionData.time_based?.morning || 65,
            facility_congestion: {
              train_station: { 
                peak: congestionData.facility_based?.station || 70, 
                average: 60 
              }
            }
          };
          
          congestionMap[area.id] = normalizedData as CongestionData;
          console.log(`Normalized congestion data for ${area.name}:`, normalizedData);
        } catch (error) {
          console.error(`Failed to load congestion data for area ${area.name} (ID: ${area.id}):`, error);
          // エラーが発生した場合は東京混雑度サービスからデータを取得
          try {
            const tokyoCongestionService = await import('@/services/tokyo_congestion_service');
            const congestionScore = tokyoCongestionService.calculateCongestionScore(area.code);
            congestionMap[area.id] = {
              congestion_score: congestionScore,
              average_congestion: congestionScore * 0.9,
              peak_congestion: Math.min(100, congestionScore * 1.3),
              facility_congestion: {
                train_station: { peak: Math.min(100, congestionScore * 1.2), average: congestionScore }
              }
            } as CongestionData;
          } catch {
            // フォールバックデータ
            congestionMap[area.id] = {
              congestion_score: 50,
              average_congestion: 45,
              peak_congestion: 65,
              facility_congestion: {
                train_station: { peak: 70, average: 60 }
              }
            } as CongestionData;
          }
        }
      }
      setCongestionData(congestionMap);
    } catch (error: any) {
      console.error('Failed to load comparison data:', error);
      if (error.response) {
        console.error('Error response:', error.response.data);
        console.error('Error status:', error.response.status);
      }
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="text-center text-gray-500">データを読み込み中...</div>
      </div>
    );
  }

  if (selectedAreas.length === 0) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">エリア比較</h2>
          <p className="text-gray-600 mb-6">比較するエリアが選択されていません</p>
          <button
            onClick={() => router.push('/')}
            className="px-6 py-3 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 transition-colors"
          >
            エリアを選択する
          </button>
        </div>
      </div>
    );
  }

  const radarData = ['rent', 'safety', 'education', 'parks', 'medical', 'culture'].map(metric => {
    const data: any = {
      category: {
        rent: '家賃',
        safety: '治安',
        education: '教育',
        parks: '公園',
        medical: '医療',
        culture: '文化',
      }[metric] || metric,
    };
    
    areaDetails.forEach(area => {
      const scores = calculateScores(area);
      data[area.name] = scores[metric as keyof typeof scores];
    });
    
    return data;
  });

  const colors = ['#3B82F6', '#EF4444', '#10B981', '#F59E0B', '#8B5CF6'];

  // カスタムツールチップ
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 shadow-lg rounded-lg border border-gray-200">
          <p className="text-sm font-semibold text-gray-900 mb-2">{label}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {entry.name}: {entry.value?.toFixed(1)}点
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  // 最高値・最低値を取得するヘルパー関数
  const getMinMaxIndices = (values: (number | null | undefined)[]) => {
    const validValues = values.map((v, i) => ({ value: v || 0, index: i })).filter(v => v.value > 0);
    if (validValues.length === 0) return { maxIndex: -1, minIndex: -1 };
    
    const maxIndex = validValues.reduce((max, curr) => 
      curr.value > max.value ? curr : max
    ).index;
    
    const minIndex = validValues.reduce((min, curr) => 
      curr.value < min.value ? curr : min
    ).index;
    
    return { maxIndex, minIndex };
  };

  // CSVエクスポート機能
  const exportToCSV = () => {
    const headers = ['項目', ...areaDetails.map(area => area.name)];
    const rows = [
      headers,
      ['人口', ...areaDetails.map(area => area.population?.toLocaleString() || '-')],
      ['面積(km²)', ...areaDetails.map(area => area.area_km2?.toFixed(1) || '-')],
      ['ウェルビーイングスコア', ...areaDetails.map(area => comparisonData?.[area.code]?.wellbeing_score?.toFixed(1) || '-')],
      ['2LDK家賃相場(万円)', ...areaDetails.map(area => area.housing_data?.rent_2ldk?.toFixed(1) || '-')],
      ['小学校数', ...areaDetails.map(area => area.school_data?.elementary_schools || '-')],
      ['待機児童数', ...areaDetails.map(area => area.childcare_data?.waiting_children || '-')],
      ['公園数', ...areaDetails.map(area => area.park_data?.total_parks || '-')],
      ['犯罪率(件/千人)', ...areaDetails.map(area => area.safety_data?.crime_rate_per_1000?.toFixed(1) || '-')],
      ['病院数', ...areaDetails.map(area => area.medical_data?.hospitals || '-')],
      ['映画館数', ...areaDetails.map(area => area.culture_data?.movie_theaters || '-')],
      ['テーマパーク数', ...areaDetails.map(area => area.culture_data?.theme_parks || '-')],
      ['総合混雑度', ...areaDetails.map(area => {
        const score = congestionData[area.id]?.congestion_score;
        return score ? `${score.toFixed(0)}/100` : '-';
      })],
      ['平均混雑度', ...areaDetails.map(area => {
        const score = congestionData[area.id]?.average_congestion;
        return score ? `${score.toFixed(0)}/100` : '-';
      })],
      ['ピーク時混雑度', ...areaDetails.map(area => {
        const score = congestionData[area.id]?.peak_congestion;
        return score ? `${score.toFixed(0)}/100` : '-';
      })],
    ];
    
    const csvContent = rows.map(row => row.join(',')).join('\n');
    const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `エリア比較_${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900">エリア比較</h1>
        <div className="flex gap-4">
          <button
            onClick={exportToCSV}
            className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white font-medium rounded-md hover:bg-green-700 transition-colors"
          >
            <Download className="w-4 h-4" />
            CSVダウンロード
          </button>
        </div>
      </div>

      {/* レーダーチャート */}
      <div className="bg-white rounded-lg shadow p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4">総合評価比較</h2>
        <ResponsiveContainer width="100%" height={400}>
          <RadarChart data={radarData}>
            <PolarGrid gridType="polygon" />
            <PolarAngleAxis 
              dataKey="category" 
              tick={{ fontSize: 14 }}
              className="text-gray-700"
            />
            <PolarRadiusAxis 
              angle={90} 
              domain={[0, 100]} 
              tickCount={6}
              tick={{ fontSize: 12 }}
            />
            {areaDetails.map((area, index) => (
              <Radar
                key={area.id}
                name={area.name}
                dataKey={area.name}
                stroke={colors[index % colors.length]}
                fill={colors[index % colors.length]}
                fillOpacity={0.3}
                strokeWidth={2}
              />
            ))}
            <Tooltip content={<CustomTooltip />} />
            <Legend 
              wrapperStyle={{ paddingTop: '20px' }}
              iconType="circle"
            />
          </RadarChart>
        </ResponsiveContainer>
      </div>

      {/* 詳細比較テーブル */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="px-6 py-4 border-b">
          <h2 className="text-xl font-semibold">詳細比較</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  項目
                </th>
                {areaDetails.map(area => (
                  <th key={area.id} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {area.name}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {/* 基本情報 */}
              <tr className="bg-gray-50">
                <td colSpan={areaDetails.length + 1} className="px-6 py-2 text-sm font-semibold text-gray-900">
                  基本情報
                </td>
              </tr>
              <tr>
                <td className="px-6 py-4 text-sm text-gray-600">人口</td>
                {areaDetails.map(area => (
                  <td key={area.id} className="px-6 py-4 text-sm">
                    {area.population?.toLocaleString()}人
                  </td>
                ))}
              </tr>
              <tr>
                <td className="px-6 py-4 text-sm text-gray-600">面積</td>
                {areaDetails.map(area => (
                  <td key={area.id} className="px-6 py-4 text-sm">
                    {area.area_km2?.toFixed(1)}km²
                  </td>
                ))}
              </tr>
              <tr>
                <td className="px-6 py-4 text-sm text-gray-600">ウェルビーイングスコア</td>
                {areaDetails.map(area => {
                  const score = comparisonData?.[area.code]?.wellbeing_score;
                  return (
                    <td key={area.id} className="px-6 py-4 text-sm font-semibold text-blue-600">
                      {score ? score.toFixed(1) : '-'}
                    </td>
                  );
                })}
              </tr>

              {/* 住宅情報 */}
              <tr className="bg-gray-50">
                <td colSpan={areaDetails.length + 1} className="px-6 py-2 text-sm font-semibold text-gray-900">
                  住宅・家賃
                </td>
              </tr>
              <tr>
                <td className="px-6 py-4 text-sm text-gray-600">2LDK家賃相場</td>
                {areaDetails.map(area => (
                  <td key={area.id} className="px-6 py-4 text-sm">
                    {area.housing_data?.rent_2ldk?.toFixed(1)}万円
                  </td>
                ))}
              </tr>

              {/* 教育環境 */}
              <tr className="bg-gray-50">
                <td colSpan={areaDetails.length + 1} className="px-6 py-2 text-sm font-semibold text-gray-900">
                  教育・子育て
                </td>
              </tr>
              <tr>
                <td className="px-6 py-4 text-sm text-gray-600">小学校数</td>
                {areaDetails.map(area => (
                  <td key={area.id} className="px-6 py-4 text-sm">
                    {area.school_data?.elementary_schools}校
                  </td>
                ))}
              </tr>
              <tr>
                <td className="px-6 py-4 text-sm text-gray-600">待機児童数</td>
                {areaDetails.map(area => (
                  <td key={area.id} className="px-6 py-4 text-sm">
                    {area.childcare_data?.waiting_children}人
                  </td>
                ))}
              </tr>

              {/* 生活環境 */}
              <tr className="bg-gray-50">
                <td colSpan={areaDetails.length + 1} className="px-6 py-2 text-sm font-semibold text-gray-900">
                  生活環境
                </td>
              </tr>
              <tr>
                <td className="px-6 py-4 text-sm text-gray-600">公園数</td>
                {areaDetails.map(area => (
                  <td key={area.id} className="px-6 py-4 text-sm">
                    {area.park_data?.total_parks}箇所
                  </td>
                ))}
              </tr>
              <tr>
                <td className="px-6 py-4 text-sm text-gray-600">犯罪率</td>
                {areaDetails.map(area => (
                  <td key={area.id} className="px-6 py-4 text-sm">
                    {area.safety_data?.crime_rate_per_1000?.toFixed(1)}件/千人
                  </td>
                ))}
              </tr>
              <tr>
                <td className="px-6 py-4 text-sm text-gray-600">病院数</td>
                {areaDetails.map(area => (
                  <td key={area.id} className="px-6 py-4 text-sm">
                    {area.medical_data?.hospitals}施設
                  </td>
                ))}
              </tr>

              {/* レジャー施設 */}
              <tr className="bg-gray-50">
                <td colSpan={areaDetails.length + 1} className="px-6 py-2 text-sm font-semibold text-gray-900">
                  レジャー施設
                </td>
              </tr>
              <tr>
                <td className="px-6 py-4 text-sm text-gray-600">映画館</td>
                {areaDetails.map(area => (
                  <td key={area.id} className="px-6 py-4 text-sm">
                    {area.culture_data?.movie_theaters || 0}施設
                  </td>
                ))}
              </tr>
              <tr>
                <td className="px-6 py-4 text-sm text-gray-600">テーマパーク</td>
                {areaDetails.map(area => (
                  <td key={area.id} className="px-6 py-4 text-sm">
                    {area.culture_data?.theme_parks || 0}施設
                  </td>
                ))}
              </tr>
              <tr>
                <td className="px-6 py-4 text-sm text-gray-600">ショッピングモール</td>
                {areaDetails.map(area => (
                  <td key={area.id} className="px-6 py-4 text-sm">
                    {area.culture_data?.shopping_malls || 0}施設
                  </td>
                ))}
              </tr>
              <tr>
                <td className="px-6 py-4 text-sm text-gray-600">ゲームセンター</td>
                {areaDetails.map(area => (
                  <td key={area.id} className="px-6 py-4 text-sm">
                    {area.culture_data?.game_centers || 0}施設
                  </td>
                ))}
              </tr>

              {/* 混雑度 */}
              <tr className="bg-gray-50">
                <td colSpan={areaDetails.length + 1} className="px-6 py-2 text-sm font-semibold text-gray-900">
                  混雑度
                </td>
              </tr>
              <tr>
                <td className="px-6 py-4 text-sm text-gray-600">総合混雑度</td>
                {areaDetails.map(area => {
                  const congestion = congestionData[area.id];
                  console.log(`Congestion data for ${area.name} (ID: ${area.id}):`, congestion);
                  const score = congestion?.congestion_score || 0;
                  const level = score > 70 ? 'high' : score > 40 ? 'moderate' : 'low';
                  const label = score > 70 ? '高' : score > 40 ? '中' : '低';
                  const color = level === 'high' ? 'text-red-600' : level === 'moderate' ? 'text-yellow-600' : 'text-green-600';
                  return (
                    <td key={area.id} className={`px-6 py-4 text-sm font-medium ${color}`}>
                      {score ? `${label} (${score.toFixed(0)}/100)` : '-'}
                    </td>
                  );
                })}
              </tr>
              <tr>
                <td className="px-6 py-4 text-sm text-gray-600">ピーク時混雑度</td>
                {areaDetails.map(area => {
                  const congestion = congestionData[area.id];
                  const peakScore = congestion?.peak_congestion || 0;
                  return (
                    <td key={area.id} className="px-6 py-4 text-sm">
                      {peakScore ? `${peakScore.toFixed(0)}/100` : '-'}
                    </td>
                  );
                })}
              </tr>
              <tr>
                <td className="px-6 py-4 text-sm text-gray-600">駅周辺混雑度</td>
                {areaDetails.map(area => {
                  const congestion = congestionData[area.id];
                  const stationScore = congestion?.facility_congestion?.train_station?.peak || 0;
                  return (
                    <td key={area.id} className="px-6 py-4 text-sm">
                      {stationScore ? `${stationScore.toFixed(0)}/100` : '-'}
                    </td>
                  );
                })}
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* アクションボタン */}
      <div className="mt-8 flex gap-4">
        <button
          onClick={() => router.push('/')}
          className="flex items-center gap-2 px-6 py-3 bg-gray-200 text-gray-700 font-medium rounded-md hover:bg-gray-300 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          エリア選択に戻る
        </button>
      </div>
    </div>
  );
}