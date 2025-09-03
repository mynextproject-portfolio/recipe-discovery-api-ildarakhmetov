import type { PageServerLoad } from './$types';
import type { RecipeResponse } from '../lib/types/recipe.js';
import { getServerApiUrl } from '../lib/config';

export const load: PageServerLoad = async ({ fetch }) => {
	try {
		// Server-side fetch - use environment-aware API URL
		const serverApiUrl = getServerApiUrl();
		console.log('Server-side API URL:', serverApiUrl);
		
		const response = await fetch(`${serverApiUrl}/recipes`);
		
		if (!response.ok) {
			throw new Error(`API responded with ${response.status}: ${response.statusText}`);
		}
		
		const recipes: RecipeResponse[] = await response.json();
		console.log(`Loaded ${recipes.length} recipes from API`);
		
		return {
			recipes
		};
	} catch (error) {
		console.error('Server-side API fetch failed:', error);
		
		return {
			recipes: [],
			error: error instanceof Error ? error.message : 'Failed to load recipes'
		};
	}
};
