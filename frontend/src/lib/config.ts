import { env } from '$env/dynamic/public';
import { dev } from '$app/environment';

/**
 * Configuration for the frontend application.
 * Uses SvelteKit's environment variable system.
 */
export const config = {
	/** 
	 * API URL for client-side requests.
	 * Falls back to localhost for development.
	 */
	get apiUrl() {
		return env.PUBLIC_API_URL || 'http://localhost:8000';
	},
	
	/**
	 * Whether we're in development mode.
	 */
	get isDevelopment() {
		return dev;
	},
	
	/**
	 * Whether we're in production mode.
	 */
	get isProduction() {
		return !dev;
	}
};

/**
 * Get the appropriate API URL for server-side requests.
 * In production, this should use the backend service URL.
 */
export function getServerApiUrl(): string {
	// In production on Render, use the backend service URL
	if (env.PUBLIC_BACKEND_URL) {
		return env.PUBLIC_BACKEND_URL;
	}
	
	// For development with Docker, use the service name
	if (dev) {
		return 'http://api:8000';
	}
	
	// Fallback to the public API URL
	return config.apiUrl;
}
