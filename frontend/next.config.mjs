/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    // Determine the backend URL. In docker-compose it's http://backend:8000
    // But for local dev it might be localhost:8000.
    // We can use an environment variable or default to localhost:8000
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
    return [
      {
        source: '/api/:path*',
        destination: `${apiUrl}/:path*`, // Proxy to Backend
      },
    ];
  },
};

export default nextConfig;
