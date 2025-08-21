import { NextRequest, NextResponse } from 'next/server';

const API_BASE_URL = process.env.API_BASE_URL || 'https://tokyo-wellbeing-map-api-mongo.onrender.com';
const HEALTH_CHECK_TIMEOUT = 10000; // 10秒のタイムアウト

export async function GET(request: NextRequest) {
  const results = {
    timestamp: new Date().toISOString(),
    upstreamUrl: API_BASE_URL,
    checks: {
      root: { status: 'unknown', latency: 0 },
      areas: { status: 'unknown', latency: 0 },
      wellbeing: { status: 'unknown', latency: 0 },
    },
  };
  
  // ルートエンドポイントのチェック
  try {
    const startTime = Date.now();
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), HEALTH_CHECK_TIMEOUT);
    
    const response = await fetch(`${API_BASE_URL}/`, {
      signal: controller.signal,
    });
    
    clearTimeout(timeoutId);
    
    results.checks.root = {
      status: response.ok ? 'healthy' : 'unhealthy',
      latency: Date.now() - startTime,
    };
  } catch (error: any) {
    results.checks.root = {
      status: 'error',
      latency: 0,
    };
  }
  
  // Areas APIのチェック
  try {
    const startTime = Date.now();
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), HEALTH_CHECK_TIMEOUT);
    
    const response = await fetch(`${API_BASE_URL}/api/v1/areas/?skip=0&limit=1`, {
      signal: controller.signal,
    });
    
    clearTimeout(timeoutId);
    
    results.checks.areas = {
      status: response.ok ? 'healthy' : 'unhealthy',
      latency: Date.now() - startTime,
    };
  } catch (error: any) {
    results.checks.areas = {
      status: 'error',
      latency: 0,
    };
  }
  
  // Wellbeing presetsのチェック
  try {
    const startTime = Date.now();
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), HEALTH_CHECK_TIMEOUT);
    
    const response = await fetch(`${API_BASE_URL}/api/v1/wellbeing/weights/presets`, {
      signal: controller.signal,
    });
    
    clearTimeout(timeoutId);
    
    results.checks.wellbeing = {
      status: response.ok ? 'healthy' : 'unhealthy',
      latency: Date.now() - startTime,
    };
  } catch (error: any) {
    results.checks.wellbeing = {
      status: 'error',
      latency: 0,
    };
  }
  
  // 全体のステータスを判定
  const allHealthy = Object.values(results.checks).every(
    check => check.status === 'healthy'
  );
  
  return NextResponse.json(results, {
    status: allHealthy ? 200 : 503,
    headers: {
      'Cache-Control': 'no-store',
    },
  });
}