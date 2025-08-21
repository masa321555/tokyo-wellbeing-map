import { NextRequest, NextResponse } from 'next/server';

// ランタイム指定（Node.jsランタイムを使用）
export const runtime = 'nodejs';

const API_BASE_URL = process.env.API_BASE_URL || 'https://tokyo-wellbeing-map-api-mongo.onrender.com';
const TIMEOUT = 30000; // 30秒のタイムアウト
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000; // 1秒から始まる指数バックオフ

async function fetchWithRetry(url: string, options: RequestInit, retries = 0): Promise<Response> {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), TIMEOUT);
    
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    });
    
    clearTimeout(timeoutId);
    
    // 5xxエラーの場合はリトライ
    if (response.status >= 500 && retries < MAX_RETRIES) {
      const delay = RETRY_DELAY * Math.pow(2, retries);
      await new Promise(resolve => setTimeout(resolve, delay));
      return fetchWithRetry(url, options, retries + 1);
    }
    
    return response;
  } catch (error: any) {
    if (error.name === 'AbortError' || retries >= MAX_RETRIES) {
      throw error;
    }
    
    const delay = RETRY_DELAY * Math.pow(2, retries);
    await new Promise(resolve => setTimeout(resolve, delay));
    return fetchWithRetry(url, options, retries + 1);
  }
}

export async function POST(request: NextRequest): Promise<Response> {
  const requestId = crypto.randomUUID();
  const startTime = Date.now();
  
  try {
    // リクエストボディの検証
    const body = await request.json();
    
    if (!body.weights || typeof body.weights !== 'object') {
      return NextResponse.json(
        { error: 'Invalid request: weights required', requestId },
        { status: 400 }
      );
    }
    
    // 上流APIへのリクエスト
    const response = await fetchWithRetry(
      `${API_BASE_URL}/api/v1/wellbeing/ranking`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Request-ID': requestId,
        },
        body: JSON.stringify(body),
      }
    );
    
    const latency = Date.now() - startTime;
    
    // ログ出力
    console.log(JSON.stringify({
      requestId,
      endpoint: '/api/proxy/wellbeing/ranking',
      upstream: `${API_BASE_URL}/api/v1/wellbeing/ranking`,
      status: response.status,
      latency,
      timestamp: new Date().toISOString(),
    }));
    
    // エラーレスポンスの場合
    if (!response.ok) {
      const errorData = await response.text();
      return NextResponse.json(
        { error: `Upstream returned ${response.status}`, detail: errorData, requestId },
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
      endpoint: '/api/proxy/wellbeing/ranking',
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

// OPTIONS対応（プリフライト）
export async function OPTIONS(request: NextRequest) {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    },
  });
}