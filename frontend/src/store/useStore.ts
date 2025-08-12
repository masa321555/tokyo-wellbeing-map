import { create } from 'zustand';
import { Area, WellbeingWeights } from '@/types/area';

interface AppState {
  // 選択中のエリア
  selectedAreas: Area[];
  addSelectedArea: (area: Area) => void;
  removeSelectedArea: (areaId: number) => void;
  clearSelectedAreas: () => void;

  // ウェルビーイング重み設定
  weights: WellbeingWeights;
  setWeights: (weights: WellbeingWeights) => void;
  resetWeights: () => void;

  // 検索条件
  searchParams: {
    maxRent?: number;
    minRent?: number;
    roomType?: string;
    areaNames?: string[];
    minElementarySchools?: number;
    minSchools?: number;
    maxWaitingChildren?: number;
    minParks?: number;
    maxCrimeRate?: number;
    minMovieTheaters?: number;
    hasThemeParks?: string;
  };
  setSearchParams: (params: Partial<typeof searchParams>) => void;
  resetSearchParams: () => void;

  // 家族構成
  familyProfile: {
    adults: number;
    children: number;
    childrenAges: number[];
    annualIncome: number;
  };
  setFamilyProfile: (profile: Partial<typeof familyProfile>) => void;

  // UI状態
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

const defaultWeights: WellbeingWeights = {
  rent: 0.25,
  safety: 0.20,
  education: 0.20,
  parks: 0.15,
  medical: 0.10,
  culture: 0.10,
};

export const useStore = create<AppState>((set) => ({
  // 選択中のエリア
  selectedAreas: [],
  addSelectedArea: (area) =>
    set((state) => {
      if (state.selectedAreas.find((a) => a.id === area.id)) {
        console.log('Area already selected:', area.id);
        return state;
      }
      const newSelectedAreas = [...state.selectedAreas, area];
      console.log('Adding area to selection:', area.name, 'Total:', newSelectedAreas.length);
      return { selectedAreas: newSelectedAreas };
    }),
  removeSelectedArea: (areaId) =>
    set((state) => ({
      selectedAreas: state.selectedAreas.filter((a) => a.id !== areaId),
    })),
  clearSelectedAreas: () => set({ selectedAreas: [] }),

  // ウェルビーイング重み設定
  weights: defaultWeights,
  setWeights: (weights) => set({ weights }),
  resetWeights: () => set({ weights: defaultWeights }),

  // 検索条件
  searchParams: {},
  setSearchParams: (params) =>
    set((state) => ({
      searchParams: { ...state.searchParams, ...params },
    })),
  resetSearchParams: () => set({ searchParams: {} }),

  // 家族構成
  familyProfile: {
    adults: 2,
    children: 2,
    childrenAges: [5, 8],
    annualIncome: 800,
  },
  setFamilyProfile: (profile) =>
    set((state) => ({
      familyProfile: { ...state.familyProfile, ...profile },
    })),

  // UI状態
  activeTab: 'search',
  setActiveTab: (tab) => set({ activeTab: tab }),
}));