'use client';

import React from 'react';
import * as Slider from '@radix-ui/react-slider';

interface WeightSliderProps {
  label: string;
  value: number;
  onChange: (value: number) => void;
  icon?: React.ReactNode;
  color?: string;
}

export const WeightSlider: React.FC<WeightSliderProps> = ({
  label,
  value,
  onChange,
  icon,
  color = 'blue',
}) => {
  // NaNチェックとデフォルト値の設定
  const safeValue = isNaN(value) || value === null || value === undefined ? 0 : value;
  const percentage = Math.round(safeValue * 100);

  const colorClasses = {
    blue: 'bg-blue-500',
    green: 'bg-green-500',
    yellow: 'bg-yellow-500',
    red: 'bg-red-500',
    purple: 'bg-purple-500',
    orange: 'bg-orange-500',
  };

  const bgColor = colorClasses[color as keyof typeof colorClasses] || colorClasses.blue;

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          {icon && <span className="text-gray-600">{icon}</span>}
          <label className="text-sm font-medium text-gray-700">{label}</label>
        </div>
        <span className="text-sm font-semibold text-gray-900">{percentage}%</span>
      </div>
      <Slider.Root
        className="relative flex items-center select-none touch-none w-full h-5"
        value={[safeValue]}
        onValueChange={([newValue]) => onChange(newValue)}
        max={1}
        step={0.05}
      >
        <Slider.Track className="bg-gray-200 relative grow rounded-full h-2">
          <Slider.Range className={`absolute ${bgColor} rounded-full h-full`} />
        </Slider.Track>
        <Slider.Thumb
          className="block w-5 h-5 bg-white shadow-md rounded-full hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
          aria-label={label}
        />
      </Slider.Root>
    </div>
  );
};