import { NextRequest, NextResponse } from 'next/server';

const API_BASE_URL = process.env.API_BASE_URL || 'https://tokyo-wellbeing-map-api-mongo.onrender.com';
const TIMEOUT = 30000; // 30秒のタイムアウト
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000; // 1秒

async function fetchWithRetry(url: string, options: RequestInit, retries = MAX_RETRIES): Promise<Response> {
  for (let i = 0; i < retries; i++) {
    try {
      const response = await fetch(url, options);
      
      // 503/502エラーの場合はリトライ
      if ((response.status === 502 || response.status === 503) && i < retries - 1) {
        await new Promise(resolve => setTimeout(resolve, RETRY_DELAY * Math.pow(2, i)));
        continue;
      }
      
      return response;
    } catch (error: any) {
      if (i === retries - 1) throw error;
      await new Promise(resolve => setTimeout(resolve, RETRY_DELAY * Math.pow(2, i)));
    }
  }
  
  throw new Error('Max retries exceeded');
}

export async function POST(request: NextRequest) {
  const requestId = crypto.randomUUID();
  const startTime = Date.now();
  
  try {
    const body = await request.json();
    
    // タイムアウト付きfetch with retry
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), TIMEOUT);
    
    const response = await fetchWithRetry(
      `${API_BASE_URL}/api/v1/search/`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Request-ID': requestId,
        },
        body: JSON.stringify(body),
        signal: controller.signal,
      }
    );
    
    clearTimeout(timeoutId);
    
    const latency = Date.now() - startTime;
    
    // ログ出力
    console.log(JSON.stringify({
      requestId,
      endpoint: '/api/proxy/search',
      upstream: `${API_BASE_URL}/api/v1/search/`,
      status: response.status,
      latency,
      timestamp: new Date().toISOString(),
      searchParams: {
        max_rent: body.max_rent,
        min_rent: body.min_rent,
        room_type: body.room_type,
        area_names: body.area_names,
      },
    }));
    
    // エラーレスポンスの場合
    if (!response.ok) {
      const errorText = await response.text();
      return NextResponse.json(
        { error: `Upstream returned ${response.status}`, details: errorText, requestId },
        { status: response.status }
      );
    }
    
    const data = await response.json();
    
    return NextResponse.json(data, {
      headers: {
        'X-Request-ID': requestId,
        'X-Response-Time': latency.toString(),
      },
    });
    
  } catch (error: any) {
    const latency = Date.now() - startTime;
    
    // エラーログ
    console.error(JSON.stringify({
      requestId,
      endpoint: '/api/proxy/search',
      error: error.message,
      type: error.name === 'AbortError' ? 'timeout' : 'network',
      latency,
      timestamp: new Date().toISOString(),
    }));
    
    if (error.name === 'AbortError') {
      return NextResponse.json(
        { error: 'Request timeout', requestId },
        { status: 504 }
      );
    }
    
    return NextResponse.json(
      { error: 'Network error', requestId },
      { status: 503 }
    );
  }
}