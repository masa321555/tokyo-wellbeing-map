'use client';

import React, { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import { areaApi, wellbeingApi, congestionApi } from '@/lib/api';
import { AreaDetail, WellbeingScore } from '@/types/area';
import { useStore } from '@/store/useStore';
import CongestionDisplay from '@/components/CongestionDisplay';
import { AgeDistributionChart } from '@/components/charts/AgeDistributionChart';
import WasteSeparationDisplay from '@/components/WasteSeparationDisplay';

export default function AreaDetailPage() {
  const params = useParams();
  const areaId = params.id as string;
  const { weights } = useStore();
  
  const [area, setArea] = useState<AreaDetail | null>(null);
  const [wellbeingScore, setWellbeingScore] = useState<WellbeingScore | null>(null);
  const [congestionData, setCongestionData] = useState<any>(null);
  const [liveCongestionData, setLiveCongestionData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (areaId) {
      loadAreaData();
    }
  }, [areaId, weights]);

  const loadAreaData = async () => {
    setLoading(true);
    try {
      const [areaData, scoreData, congestionInfo] = await Promise.all([
        areaApi.getAreaDetail(areaId),
        wellbeingApi.calculateScore(areaId, weights),
        congestionApi.getAreaCongestion(areaId).catch(() => null),
      ]);
      setArea(areaData);
      setWellbeingScore(scoreData);
      setCongestionData(congestionInfo);
      
      // Google Places APIからリアルタイム混雑度データを取得
      if (areaData?.code) {
        try {
          const liveData = await congestionApi.getLiveCongestion(areaData.code);
          setLiveCongestionData(liveData);
        } catch (error) {
          console.error('Failed to load live congestion data:', error);
        }
      }
    } catch (error) {
      console.error('Failed to load area data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2 mb-8"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="h-64 bg-gray-200 rounded"></div>
            <div className="h-64 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  if (!area || !wellbeingScore) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="text-center text-gray-500">エリア情報が見つかりません</div>
      </div>
    );
  }

  const radarData = Object.entries(wellbeingScore.category_scores).map(([key, value]) => ({
    category: {
      rent: '家賃',
      safety: '治安',
      education: '教育',
      parks: '公園',
      medical: '医療',
      culture: '文化',
    }[key] || key,
    value: value,
  }));

  const barData = [
    { name: '総合スコア', value: wellbeingScore.total_score, fill: '#3B82F6' },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* ヘッダー */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">{area.name}</h1>
        <p className="text-gray-600">
          人口: {area.population?.toLocaleString()}人 | 面積: {area.area_km2?.toFixed(1)}km²
        </p>
      </div>

      {/* スコア概要 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">ウェルビーイングスコア</h2>
          <div className="text-center">
            <div className="text-5xl font-bold text-blue-600 mb-2">
              {wellbeingScore.total_score.toFixed(1)}
            </div>
            <p className="text-gray-600">総合評価（100点満点）</p>
          </div>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={barData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis domain={[0, 100]} />
              <Tooltip />
              <Bar dataKey="value" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">カテゴリ別評価</h2>
          <ResponsiveContainer width="100%" height={300}>
            <RadarChart data={radarData}>
              <PolarGrid />
              <PolarAngleAxis dataKey="category" />
              <PolarRadiusAxis angle={90} domain={[0, 100]} />
              <Radar
                name="スコア"
                dataKey="value"
                stroke="#3B82F6"
                fill="#3B82F6"
                fillOpacity={0.6}
              />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 詳細データ */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* 住宅情報 */}
        {area.housing_data && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">🏠 住宅・家賃</h3>
            <dl className="space-y-2">
              <div className="flex justify-between">
                <dt className="text-gray-600">2LDK家賃相場</dt>
                <dd className="font-medium">{area.housing_data.rent_2ldk?.toFixed(1)}万円</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-600">1LDK家賃相場</dt>
                <dd className="font-medium">{area.housing_data.rent_1ldk?.toFixed(1)}万円</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-600">空き家率</dt>
                <dd className="font-medium">{area.housing_data.vacant_rate?.toFixed(1)}%</dd>
              </div>
            </dl>
          </div>
        )}

        {/* 教育環境 */}
        {(area.school_data || area.childcare_data) && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">🎓 教育・子育て</h3>
            <dl className="space-y-2">
              {area.school_data && (
                <>
                  <div className="flex justify-between">
                    <dt className="text-gray-600">小学校数</dt>
                    <dd className="font-medium">{area.school_data.elementary_schools}校</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-gray-600">中学校数</dt>
                    <dd className="font-medium">{area.school_data.junior_high_schools}校</dd>
                  </div>
                </>
              )}
              {area.childcare_data && (
                <>
                  <div className="flex justify-between">
                    <dt className="text-gray-600">保育園数</dt>
                    <dd className="font-medium">{area.childcare_data.nursery_schools}園</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-gray-600">待機児童数</dt>
                    <dd className="font-medium">{area.childcare_data.waiting_children}人</dd>
                  </div>
                </>
              )}
            </dl>
          </div>
        )}

        {/* 公園・緑地 */}
        {area.park_data && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">🌳 公園・緑地</h3>
            <dl className="space-y-2">
              <div className="flex justify-between">
                <dt className="text-gray-600">公園総数</dt>
                <dd className="font-medium">{area.park_data.total_parks}箇所</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-600">一人当たり面積</dt>
                <dd className="font-medium">{area.park_data.park_per_capita?.toFixed(1)}m²</dd>
              </div>
              {area.park_data.large_parks !== undefined && (
                <div className="flex justify-between">
                  <dt className="text-gray-600">大規模公園数</dt>
                  <dd className="font-medium">{area.park_data.large_parks}箇所</dd>
                </div>
              )}
            </dl>
          </div>
        )}

        {/* 治安 */}
        {area.safety_data && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">🛡️ 治安・安全</h3>
            <dl className="space-y-2">
              <div className="flex justify-between">
                <dt className="text-gray-600">犯罪率</dt>
                <dd className="font-medium">{area.safety_data.crime_rate_per_1000?.toFixed(1)}件/千人</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-600">警察署数</dt>
                <dd className="font-medium">{area.safety_data.police_stations}箇所</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-600">消防署数</dt>
                <dd className="font-medium">{area.safety_data.fire_stations}箇所</dd>
              </div>
            </dl>
          </div>
        )}

        {/* 医療 */}
        {area.medical_data && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">🏥 医療・福祉</h3>
            <dl className="space-y-2">
              <div className="flex justify-between">
                <dt className="text-gray-600">病院数</dt>
                <dd className="font-medium">{area.medical_data.hospitals}施設</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-600">診療所数</dt>
                <dd className="font-medium">{area.medical_data.clinics}施設</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-600">救急病院</dt>
                <dd className="font-medium">{area.medical_data.emergency_hospitals}施設</dd>
              </div>
            </dl>
          </div>
        )}

        {/* 文化施設 */}
        {area.culture_data && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">🎭 文化・施設</h3>
            <dl className="space-y-2">
              <div className="flex justify-between">
                <dt className="text-gray-600">図書館</dt>
                <dd className="font-medium">{area.culture_data.libraries}施設</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-600">美術館・博物館</dt>
                <dd className="font-medium">{area.culture_data.museums}施設</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-600">スポーツ施設</dt>
                <dd className="font-medium">{area.culture_data.sports_facilities}施設</dd>
              </div>
            </dl>
          </div>
        )}

        {/* レジャー施設 */}
        {area.culture_data && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">🎬 レジャー施設</h3>
            <dl className="space-y-2">
              <div className="flex justify-between">
                <dt className="text-gray-600">映画館</dt>
                <dd className="font-medium">{area.culture_data.movie_theaters || 0}施設</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-600">テーマパーク</dt>
                <dd className="font-medium">{area.culture_data.theme_parks || 0}施設</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-600">ショッピングモール</dt>
                <dd className="font-medium">{area.culture_data.shopping_malls || 0}施設</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-600">ゲームセンター</dt>
                <dd className="font-medium">{area.culture_data.game_centers || 0}施設</dd>
              </div>
            </dl>
          </div>
        )}
      </div>

      {/* ゴミ分別情報 */}
      {area.waste_separation && (
        <div className="mt-8">
          <WasteSeparationDisplay data={area.waste_separation} />
        </div>
      )}

      {/* 混雑度情報 */}
      {liveCongestionData ? (
        <div className="mt-8">
          <CongestionDisplay congestion={liveCongestionData} />
          {liveCongestionData.data_source === 'google_places_api' && (
            <p className="text-xs text-gray-500 mt-2 text-right">
              データソース: Google Places API
            </p>
          )}
        </div>
      ) : congestionData && (
        <div className="mt-8">
          <CongestionDisplay congestion={congestionData.congestion} />
        </div>
      )}

      {/* 年齢層分布 */}
      {area?.age_distribution && (
        <div className="mt-8">
          <AgeDistributionChart 
            data={area.age_distribution} 
            areaName={area.name}
          />
        </div>
      )}

      {/* アクションボタン */}
      <div className="mt-8 flex gap-4">
        <button
          onClick={() => window.location.href = `/simulation?area_id=${areaId}`}
          className="px-6 py-3 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 transition-colors"
        >
          家計シミュレーション
        </button>
        <button
          onClick={() => window.history.back()}
          className="px-6 py-3 bg-gray-200 text-gray-700 font-medium rounded-md hover:bg-gray-300 transition-colors"
        >
          戻る
        </button>
      </div>
    </div>
  );
}