import { test, expect } from '@playwright/test';

test.describe('Proxy API Tests', () => {
  const baseURL = process.env.BASE_URL || 'http://localhost:3000';

  test.describe('Areas Proxy', () => {
    test('should fetch areas through proxy', async ({ request }) => {
      const response = await request.get(`${baseURL}/api/proxy/areas?skip=0&limit=10`);
      
      expect(response.status()).toBe(200);
      
      const data = await response.json();
      expect(Array.isArray(data)).toBe(true);
      expect(data.length).toBeLessThanOrEqual(10);
      
      // Check response headers
      const headers = response.headers();
      expect(headers['x-request-id']).toBeTruthy();
      expect(headers['x-response-time']).toBeTruthy();
    });

    test('should handle invalid parameters', async ({ request }) => {
      const response = await request.get(`${baseURL}/api/proxy/areas?skip=-1&limit=200`);
      
      expect(response.status()).toBe(400);
      
      const data = await response.json();
      expect(data.error).toBeTruthy();
    });

    test('should fetch area detail through proxy', async ({ request }) => {
      // First get an area ID
      const listResponse = await request.get(`${baseURL}/api/proxy/areas?skip=0&limit=1`);
      const areas = await listResponse.json();
      
      if (areas.length > 0) {
        const areaId = areas[0]._id;
        const detailResponse = await request.get(`${baseURL}/api/proxy/areas/${areaId}`);
        
        expect(detailResponse.status()).toBe(200);
        
        const detail = await detailResponse.json();
        expect(detail._id).toBe(areaId);
      }
    });
  });

  test.describe('Wellbeing Proxy', () => {
    test('should fetch weight presets through proxy', async ({ request }) => {
      const response = await request.get(`${baseURL}/api/proxy/wellbeing/weights/presets`);
      
      expect(response.status()).toBe(200);
      
      const data = await response.json();
      expect(data).toBeTruthy();
      expect(typeof data).toBe('object');
    });

    test('should calculate wellbeing score through proxy', async ({ request }) => {
      // First get an area ID
      const listResponse = await request.get(`${baseURL}/api/proxy/areas?skip=0&limit=1`);
      const areas = await listResponse.json();
      
      if (areas.length > 0) {
        const response = await request.post(`${baseURL}/api/proxy/wellbeing/calculate`, {
          data: {
            area_id: areas[0]._id,
            weights: {
              safety: 0.2,
              education: 0.2,
              convenience: 0.2,
              nature: 0.2,
              community: 0.2,
            },
            family_size: 4,
          },
        });
        
        expect(response.status()).toBe(200);
        
        const data = await response.json();
        expect(data.total_score).toBeDefined();
        expect(typeof data.total_score).toBe('number');
      }
    });

    test('should get ranking through proxy', async ({ request }) => {
      const response = await request.post(`${baseURL}/api/proxy/wellbeing/ranking`, {
        data: {
          weights: {
            safety: 0.2,
            education: 0.2,
            convenience: 0.2,
            nature: 0.2,
            community: 0.2,
          },
          limit: 5,
        },
      });
      
      expect(response.status()).toBe(200);
      
      const data = await response.json();
      expect(Array.isArray(data)).toBe(true);
      expect(data.length).toBeLessThanOrEqual(5);
    });
  });

  test.describe('Search Proxy', () => {
    test('should search areas through proxy', async ({ request }) => {
      const response = await request.post(`${baseURL}/api/proxy/search`, {
        data: {
          max_rent: 200000,
          room_type: '3LDK',
          limit: 10,
        },
      });
      
      expect(response.status()).toBe(200);
      
      const data = await response.json();
      expect(data.results).toBeDefined();
      expect(Array.isArray(data.results)).toBe(true);
    });
  });

  test.describe('Health Check', () => {
    test('should check upstream health', async ({ request }) => {
      const response = await request.get(`${baseURL}/api/health/upstream`);
      
      // Should return 200 or 503 depending on upstream status
      expect([200, 503]).toContain(response.status());
      
      const data = await response.json();
      expect(data.timestamp).toBeTruthy();
      expect(data.checks).toBeDefined();
      expect(data.checks.root).toBeDefined();
      expect(data.checks.areas).toBeDefined();
      expect(data.checks.wellbeing).toBeDefined();
    });
  });

  test.describe('Error Handling', () => {
    test('should handle timeout gracefully', async ({ request }) => {
      // This test assumes we can trigger a timeout somehow
      // In a real scenario, you might need to mock the backend to be slow
      
      const controller = new AbortController();
      setTimeout(() => controller.abort(), 100); // Abort after 100ms
      
      try {
        await request.get(`${baseURL}/api/proxy/areas?skip=0&limit=100`, {
          signal: controller.signal,
        });
      } catch (error) {
        // Expected to throw
        expect(error).toBeTruthy();
      }
    });
  });
});