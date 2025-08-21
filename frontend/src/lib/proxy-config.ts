// プロキシ設定の一元管理
export const PROXY_CONFIG = {
  // APIベースURL
  API_BASE_URL: process.env.API_BASE_URL || 'https://tokyo-wellbeing-map-api-mongo.onrender.com',
  
  // タイムアウト設定
  TIMEOUT: 30000, // 30秒
  
  // リトライ設定
  MAX_RETRIES: 3,
  RETRY_DELAY: 1000, // 1秒（指数バックオフで増加）
  
  // リトライ対象のステータスコード
  RETRY_STATUS_CODES: [502, 503],
  
  // キャッシュ設定
  CACHE_SETTINGS: {
    areas: {
      maxAge: 300, // 5分
      staleWhileRevalidate: 600, // 10分
    },
    areaDetail: {
      maxAge: 60, // 1分
      staleWhileRevalidate: 300, // 5分
    },
    weightPresets: {
      maxAge: 300, // 5分
      staleWhileRevalidate: 600, // 10分
    },
  },
};

// エラーログフォーマット
export interface ErrorLog {
  requestId: string;
  endpoint: string;
  error: string;
  type: 'timeout' | 'network' | 'upstream';
  latency: number;
  timestamp: string;
  details?: any;
}

// アクセスログフォーマット
export interface AccessLog {
  requestId: string;
  endpoint: string;
  upstream: string;
  status: number;
  latency: number;
  timestamp: string;
  params?: any;
}

// リトライ可能なfetch関数
export async function fetchWithRetry(
  url: string,
  options: RequestInit,
  retries = PROXY_CONFIG.MAX_RETRIES
): Promise<Response> {
  for (let i = 0; i < retries; i++) {
    try {
      const response = await fetch(url, options);
      
      // リトライ対象のステータスコードの場合
      if (PROXY_CONFIG.RETRY_STATUS_CODES.includes(response.status) && i < retries - 1) {
        // 指数バックオフで待機
        await new Promise(resolve => 
          setTimeout(resolve, PROXY_CONFIG.RETRY_DELAY * Math.pow(2, i))
        );
        continue;
      }
      
      return response;
    } catch (error: any) {
      // 最後の試行でない場合はリトライ
      if (i === retries - 1) throw error;
      
      // 指数バックオフで待機
      await new Promise(resolve => 
        setTimeout(resolve, PROXY_CONFIG.RETRY_DELAY * Math.pow(2, i))
      );
    }
  }
  
  throw new Error('Max retries exceeded');
}

// エラーログ出力関数
export function logError(log: ErrorLog): void {
  console.error(JSON.stringify(log));
}

// アクセスログ出力関数
export function logAccess(log: AccessLog): void {
  console.log(JSON.stringify(log));
}

// キャッシュヘッダー生成関数
export function getCacheHeaders(cacheKey: keyof typeof PROXY_CONFIG.CACHE_SETTINGS): Record<string, string> {
  const settings = PROXY_CONFIG.CACHE_SETTINGS[cacheKey];
  return {
    'Cache-Control': `public, s-maxage=${settings.maxAge}, stale-while-revalidate=${settings.staleWhileRevalidate}`,
  };
}