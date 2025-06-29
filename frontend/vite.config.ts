import { sveltekit } from '@sveltejs/kit/vite';
import tailwindcss from '@tailwindcss/vite';
import { defineConfig, loadEnv } from 'vite';

export default defineConfig(({ mode }) => {
	// Load env file based on `mode` in the current working directory.
	const env = loadEnv(mode, process.cwd(), '');
	
	// Determine the API target based on environment
	// In Docker, use the service name; in development, use localhost
	const apiTarget = env.VITE_API_PROXY_TARGET || 'http://localhost:8000';
	
	return {
		plugins: [tailwindcss(), sveltekit()],
		server: {
			host: '0.0.0.0', // Allow external connections
			proxy: {
				'/api': {
					target: apiTarget,
					changeOrigin: true,
					secure: false,
					// Add logging for debugging
					configure: (proxy, _options) => {
						proxy.on('error', (err, _req, _res) => {
							console.log('proxy error', err);
						});
						proxy.on('proxyReq', (proxyReq, req, _res) => {
							console.log('Sending Request to the Target:', req.method, req.url);
						});
						proxy.on('proxyRes', (proxyRes, req, _res) => {
							console.log('Received Response from the Target:', proxyRes.statusCode, req.url);
						});
					},
				}
			}
		}
	};
});
