/**
 * TypeScript types matching the Python Pydantic models from the Recipe Discovery API
 */

export interface Recipe {
	id?: number;
	title: string;
	ingredients: string[];
	steps: string[];
	prepTime?: string | null;  // Optional for external recipes
	cookTime?: string | null;  // Optional for external recipes
	difficulty?: string | null;  // Optional for external recipes
	cuisine?: string | null;  // Optional for external recipes
	source?: string;
}

export interface RecipeRequest {
	title: string;
	ingredients: string[];
	steps: string[];
	prepTime: string;
	cookTime: string;
	difficulty: string;
	cuisine: string;
}

export interface CacheInfo {
	hit: boolean;               // True if cache hit, False if cache miss
	response_time_ms: number;   // Response time in milliseconds
	source: string;             // "cache" or "api"
}

export interface RecipeResponse {
	id: number;
	title: string;
	ingredients: string[];
	steps: string[];
	prepTime?: string | null;  // Optional for external recipes
	cookTime?: string | null;  // Optional for external recipes
	difficulty?: string | null;  // Optional for external recipes
	cuisine?: string | null;  // Optional for external recipes
	source: string;
	cache_info?: CacheInfo;     // Cache performance data
}

export interface SearchResultsResponse {
	recipes: RecipeResponse[];
	mealdb_cache_info?: CacheInfo;
}

export interface ApiError {
	detail: string;
}
