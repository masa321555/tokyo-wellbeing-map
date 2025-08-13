'use client';

import React, { useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { Area } from '@/types/area';

// Leafletのデフォルトアイコンの問題を修正
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: '/marker-icon-2x.png',
  iconUrl: '/marker-icon.png',
  shadowUrl: '/marker-shadow.png',
});

interface AreaMapProps {
  areas: Area[];
  selectedAreaIds?: string[];  // MongoDB ObjectId
  onAreaClick?: (area: Area) => void;
  center?: [number, number];
  zoom?: number;
}

// 地図の中心を調整するコンポーネント
const MapController: React.FC<{ center: [number, number]; zoom: number }> = ({ center, zoom }) => {
  const map = useMap();
  
  useEffect(() => {
    map.setView(center, zoom);
  }, [map, center, zoom]);
  
  return null;
};

export const AreaMap: React.FC<AreaMapProps> = ({
  areas,
  selectedAreaIds = [],
  onAreaClick,
  center = [35.6762, 139.6503], // 東京都庁
  zoom = 11,
}) => {
  const mapRef = useRef<L.Map | null>(null);

  // カスタムアイコンの作成
  const createIcon = (isSelected: boolean, score?: number) => {
    const color = isSelected ? '#3B82F6' : score && score >= 80 ? '#10B981' : '#6B7280';
    const size = isSelected ? 40 : 30;
    
    return L.divIcon({
      html: `
        <div style="
          background-color: ${color};
          border: 3px solid white;
          border-radius: 50%;
          width: ${size}px;
          height: ${size}px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: bold;
          color: white;
          font-size: ${isSelected ? '14px' : '12px'};
          box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        ">
          ${score ? Math.round(score) : ''}
        </div>
      `,
      className: 'custom-div-icon',
      iconSize: [size, size],
      iconAnchor: [size / 2, size / 2],
    });
  };

  return (
    <div className="h-full w-full rounded-lg overflow-hidden shadow-lg">
      <MapContainer
        center={center}
        zoom={zoom}
        className="h-full w-full"
        ref={mapRef}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <MapController center={center} zoom={zoom} />
        
        {areas.map((area) => {
          if (!area.center_lat || !area.center_lng) return null;
          
          const isSelected = selectedAreaIds.includes(area.id);
          
          return (
            <Marker
              key={area.id}
              position={[area.center_lat, area.center_lng]}
              icon={createIcon(isSelected, area.wellbeing_score)}
              eventHandlers={{
                click: () => onAreaClick?.(area),
              }}
            >
              <Popup>
                <div className="p-2">
                  <h3 className="font-bold text-lg mb-1">{area.name}</h3>
                  <div className="space-y-1 text-sm">
                    <p>スコア: <span className="font-semibold">{area.wellbeing_score?.toFixed(1) || '-'}</span></p>
                    <p>人口: {area.population?.toLocaleString() || '-'}人</p>
                    <p>面積: {area.area_km2?.toFixed(1) || '-'}km²</p>
                  </div>
                  {onAreaClick && (
                    <button
                      onClick={() => onAreaClick(area)}
                      className="mt-2 px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 transition-colors"
                    >
                      詳細を見る
                    </button>
                  )}
                </div>
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>
    </div>
  );
};