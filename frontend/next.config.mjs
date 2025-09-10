/** @type {import('next').NextConfig} */

const nextConfig = {

    basePath: '/ui',

    async rewrites() {
      return [
        {
          source: "/api/:path*",
          destination: "http://backend-iot:8000/api/:path*", // FastAPI backend
        },
      ];
    },
  };

export default nextConfig;
  