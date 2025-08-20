/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ['tile.openstreetmap.org'],
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'https://tokyo-wellbeing-map-api-mongo.onrender.com',
  },
}

module.exports = nextConfig