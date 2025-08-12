'use client';

import React, { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { useStore } from '@/store/useStore';
import { areaApi, simulationApi } from '@/lib/api';
import { Area } from '@/types/area';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

function SimulationContent() {
  const searchParams = useSearchParams();
  const areaIdParam = searchParams.get('area_id');
  const { familyProfile, setFamilyProfile } = useStore();
  
  const [areas, setAreas] = useState<Area[]>([]);
  const [selectedAreaId, setSelectedAreaId] = useState<number | null>(
    areaIdParam ? parseInt(areaIdParam) : null
  );
  const [simulationResult, setSimulationResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  
  // フォーム状態
  const [formData, setFormData] = useState({
    adults: familyProfile.adults,
    children: familyProfile.children,
    annualIncome: familyProfile.annualIncome,
    roomType: '2LDK',
    carOwnership: false,
    childcareNeeded: familyProfile.children > 0,
    commuteDestination: '東京',
  });

  useEffect(() => {
    loadAreas();
  }, []);

  const loadAreas = async () => {
    try {
      const allAreas = await areaApi.getAreas();
      setAreas(allAreas);
    } catch (error) {
      console.error('Failed to load areas:', error);
    }
  };

  const runSimulation = async () => {
    if (!selectedAreaId) return;
    
    setLoading(true);
    try {
      const result = await simulationApi.simulateHousehold({
        area_id: selectedAreaId,
        adults: formData.adults,
        children: formData.children,
        annual_income: formData.annualIncome,
        room_type: formData.roomType,
        commute_destinations: [{
          station: formData.commuteDestination,
          days_per_week: 5,
        }],
        car_ownership: formData.carOwnership,
        childcare_needed: formData.childcareNeeded,
      });
      setSimulationResult(result);
      
      // 家族構成を保存
      setFamilyProfile({
        adults: formData.adults,
        children: formData.children,
        annualIncome: formData.annualIncome,
      });
    } catch (error) {
      console.error('Failed to run simulation:', error);
    } finally {
      setLoading(false);
    }
  };

  // 円グラフ用データの準備
  const pieData = simulationResult ? 
    Object.entries(simulationResult.monthly_breakdown).map(([key, value]) => ({
      name: key,
      value: value as number,
    })) : [];

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D'];

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">家計シミュレーション</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* 入力フォーム */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-6">シミュレーション条件</h2>
          
          <div className="space-y-4">
            {/* エリア選択 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                エリア
              </label>
              <select
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={selectedAreaId || ''}
                onChange={(e) => setSelectedAreaId(Number(e.target.value))}
              >
                <option value="">選択してください</option>
                {areas.map(area => (
                  <option key={area.id} value={area.id}>
                    {area.name}
                  </option>
                ))}
              </select>
            </div>

            {/* 家族構成 */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  大人の人数
                </label>
                <input
                  type="number"
                  min="1"
                  max="10"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  value={formData.adults}
                  onChange={(e) => setFormData({...formData, adults: parseInt(e.target.value)})}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  子供の人数
                </label>
                <input
                  type="number"
                  min="0"
                  max="10"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  value={formData.children}
                  onChange={(e) => setFormData({...formData, children: parseInt(e.target.value)})}
                />
              </div>
            </div>

            {/* 世帯年収 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                世帯年収（万円）
              </label>
              <input
                type="number"
                min="0"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={formData.annualIncome}
                onChange={(e) => setFormData({...formData, annualIncome: parseInt(e.target.value)})}
              />
            </div>

            {/* 間取り */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                間取り
              </label>
              <select
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={formData.roomType}
                onChange={(e) => setFormData({...formData, roomType: e.target.value})}
              >
                <option value="1R">1R</option>
                <option value="1K">1K</option>
                <option value="1DK">1DK</option>
                <option value="1LDK">1LDK</option>
                <option value="2LDK">2LDK</option>
                <option value="3LDK">3LDK</option>
              </select>
            </div>

            {/* 通勤先 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                主な通勤先
              </label>
              <select
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={formData.commuteDestination}
                onChange={(e) => setFormData({...formData, commuteDestination: e.target.value})}
              >
                <option value="東京">東京駅</option>
                <option value="新宿">新宿駅</option>
                <option value="渋谷">渋谷駅</option>
                <option value="品川">品川駅</option>
                <option value="池袋">池袋駅</option>
              </select>
            </div>

            {/* オプション */}
            <div className="space-y-2">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  className="mr-2"
                  checked={formData.carOwnership}
                  onChange={(e) => setFormData({...formData, carOwnership: e.target.checked})}
                />
                <span className="text-sm text-gray-700">車を所有</span>
              </label>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  className="mr-2"
                  checked={formData.childcareNeeded}
                  onChange={(e) => setFormData({...formData, childcareNeeded: e.target.checked})}
                />
                <span className="text-sm text-gray-700">保育園を利用</span>
              </label>
            </div>

            {/* シミュレーション実行ボタン */}
            <button
              onClick={runSimulation}
              disabled={!selectedAreaId || loading}
              className={`w-full px-4 py-3 font-medium rounded-md transition-colors ${
                !selectedAreaId || loading
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-blue-600 text-white hover:bg-blue-700'
              }`}
            >
              {loading ? 'シミュレーション中...' : 'シミュレーション実行'}
            </button>
          </div>
        </div>

        {/* 結果表示 */}
        <div>
          {simulationResult ? (
            <div className="space-y-6">
              {/* サマリー */}
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-semibold mb-4">{simulationResult.area_name} の家計シミュレーション結果</h2>
                
                <div className="grid grid-cols-2 gap-4 mb-6">
                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">
                      {(simulationResult.annual_total / 10000).toFixed(0)}万円
                    </div>
                    <p className="text-sm text-gray-600">年間支出</p>
                  </div>
                  <div className="text-center p-4 bg-green-50 rounded-lg">
                    <div className="text-2xl font-bold text-green-600">
                      {(simulationResult.disposable_income / 10000).toFixed(0)}万円/月
                    </div>
                    <p className="text-sm text-gray-600">可処分所得</p>
                  </div>
                </div>

                <div className="mb-4">
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-sm text-gray-600">貯蓄率</span>
                    <span className="text-sm font-medium">{simulationResult.savings_rate}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full"
                      style={{ width: `${simulationResult.savings_rate}%` }}
                    />
                  </div>
                </div>

                <div className="mb-4">
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-sm text-gray-600">住居費負担度</span>
                    <span className="text-sm font-medium">{simulationResult.affordability_score.toFixed(0)}/100</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${
                        simulationResult.affordability_score >= 70 ? 'bg-green-600' :
                        simulationResult.affordability_score >= 50 ? 'bg-yellow-600' : 'bg-red-600'
                      }`}
                      style={{ width: `${simulationResult.affordability_score}%` }}
                    />
                  </div>
                </div>
              </div>

              {/* 支出内訳 */}
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold mb-4">月間支出内訳</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={pieData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${((percent ?? 0) * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {pieData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value: number) => `${(value / 10000).toFixed(1)}万円`} />
                  </PieChart>
                </ResponsiveContainer>
                
                <div className="mt-4 space-y-2">
                  {Object.entries(simulationResult.monthly_breakdown).map(([key, value]) => (
                    <div key={key} className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">{key}</span>
                      <span className="text-sm font-medium">{((value as number) / 10000).toFixed(1)}万円</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* アドバイス */}
              {simulationResult.recommendations.length > 0 && (
                <div className="bg-white rounded-lg shadow p-6">
                  <h3 className="text-lg font-semibold mb-4">アドバイス</h3>
                  <ul className="space-y-2">
                    {simulationResult.recommendations.map((rec: string, index: number) => (
                      <li key={index} className="flex items-start">
                        <span className="text-blue-500 mr-2">•</span>
                        <span className="text-sm text-gray-700">{rec}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ) : (
            <div className="bg-gray-50 rounded-lg p-8 text-center text-gray-500">
              <p>条件を入力してシミュレーションを実行してください</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default function SimulationPage() {
  return (
    <Suspense fallback={<div className="flex items-center justify-center h-64">読み込み中...</div>}>
      <SimulationContent />
    </Suspense>
  );
}