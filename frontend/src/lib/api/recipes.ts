/**
 * Recipe service layer for API communication
 */

import { apiClient } from './client.js';
import type { RecipeRequest, RecipeResponse, SearchResultsResponse } from '../types/recipe.js';

export const recipesApi = {
	/**
	 * Get all recipes (internal only - external recipes come via search)
	 */
	async getAll(): Promise<RecipeResponse[]> {
		return apiClient.get<RecipeResponse[]>('/recipes');
	},

	/**
	 * Search recipes by query string (returns both internal and external)
	 */
	async search(query: string): Promise<SearchResultsResponse> {
		const params = new URLSearchParams({ q: query });
		return apiClient.get<SearchResultsResponse>(`/recipes/search?${params}`);
	},

	/**
	 * Get a specific internal recipe by ID
	 */
	async getInternal(id: number): Promise<RecipeResponse> {
		return apiClient.get<RecipeResponse>(`/recipes/internal/${id}`);
	},

	/**
	 * Get a specific external MealDB recipe by ID
	 */
	async getExternal(source: 'mealdb', id: number): Promise<RecipeResponse> {
		return apiClient.get<RecipeResponse>(`/recipes/external/${source}/${id}`);
	},

	/**
	 * Get a recipe by ID and source - smart wrapper
	 */
	async getByIdAndSource(id: number, source: string): Promise<RecipeResponse> {
		if (source === 'internal') {
			return this.getInternal(id);
		} else if (source === 'mealdb') {
			return this.getExternal('mealdb', id);
		} else {
			throw new Error(`Unsupported recipe source: ${source}`);
		}
	},

	/**
	 * Create a new internal recipe
	 */
	async create(recipe: RecipeRequest): Promise<RecipeResponse> {
		return apiClient.post<RecipeResponse>('/recipes', recipe);
	},

	/**
	 * Update an existing internal recipe
	 */
	async updateInternal(id: number, recipe: RecipeRequest): Promise<RecipeResponse> {
		return apiClient.put<RecipeResponse>(`/recipes/internal/${id}`, recipe);
	}
};
