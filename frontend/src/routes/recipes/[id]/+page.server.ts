import type { PageServerLoad } from './$types';
import type { RecipeResponse } from '../../../lib/types/recipe.js';

export const load: PageServerLoad = async ({ params, fetch }) => {
	const recipeId = parseInt(params.id);
	
	if (isNaN(recipeId)) {
		return {
			recipe: null,
			error: 'Invalid recipe ID'
		};
	}

	try {
		// Server-side fetch using Docker internal network
		const serverApiUrl = 'http://api:8000';
		const response = await fetch(`${serverApiUrl}/recipes/${recipeId}`);
		
		if (!response.ok) {
			if (response.status === 404) {
				return {
					recipe: null,
					error: 'Recipe not found'
				};
			}
			throw new Error(`API responded with ${response.status}: ${response.statusText}`);
		}
		
		const recipe: RecipeResponse = await response.json();
		console.log(`Loaded recipe ${recipeId} from API:`, recipe.title, `(source: ${recipe.source})`);
		
		return {
			recipe,
			error: null
		};
	} catch (error) {
		console.error('Server-side recipe fetch failed:', error);
		
		return {
			recipe: null,
			error: error instanceof Error ? error.message : 'Failed to load recipe'
		};
	}
};
