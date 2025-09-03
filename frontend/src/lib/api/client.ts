/**
 * API client for communicating with the Recipe Discovery API
 */

import { env } from '$env/dynamic/public';
import { browser } from '$app/environment';
import type { ApiError as ApiErrorType } from '../types/recipe.js';

export class ApiClientError extends Error {
	constructor(
		message: string,
		public status: number,
		public details?: string
	) {
		super(message);
		this.name = 'ApiClientError';
	}
}

class ApiClient {
	private baseURL: string;

	constructor() {
		// Use different URLs for server vs client
		if (browser) {
			// Client-side (browser) - use localhost
			this.baseURL = env.PUBLIC_API_URL || 'http://localhost:8000';
		} else {
			// Server-side - use Docker internal network
			this.baseURL = 'http://api:8000';
		}
	}

	async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
		const url = `${this.baseURL}${endpoint}`;
		
		try {
			const response = await fetch(url, {
				...options,
				headers: {
					'Content-Type': 'application/json',
					...options?.headers
				}
			});

			if (!response.ok) {
				let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
				let details: string | undefined;

				try {
					const errorData: ApiErrorType = await response.json();
					details = errorData.detail;
					errorMessage = details || errorMessage;
				} catch {
					// If we can't parse error as JSON, use the status text
				}

				throw new ApiClientError(errorMessage, response.status, details);
			}

			return await response.json();
		} catch (error) {
			if (error instanceof ApiClientError) {
				throw error;
			}
			throw new ApiClientError(`Network error: ${error}`, 0);
		}
	}

	async get<T>(endpoint: string): Promise<T> {
		return this.request<T>(endpoint, { method: 'GET' });
	}

	async post<T>(endpoint: string, data: unknown): Promise<T> {
		return this.request<T>(endpoint, {
			method: 'POST',
			body: JSON.stringify(data)
		});
	}

	async put<T>(endpoint: string, data: unknown): Promise<T> {
		return this.request<T>(endpoint, {
			method: 'PUT',
			body: JSON.stringify(data)
		});
	}

	async delete<T>(endpoint: string): Promise<T> {
		return this.request<T>(endpoint, { method: 'DELETE' });
	}
}

export const apiClient = new ApiClient();