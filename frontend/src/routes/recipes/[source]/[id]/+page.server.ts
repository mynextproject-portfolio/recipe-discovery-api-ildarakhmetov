import type { PageServerLoad } from './$types';
import type { RecipeResponse } from '$lib/types/recipe.js';
import { getServerApiUrl } from '$lib/config';

export const load: PageServerLoad = async ({ params, fetch }) => {
	const recipeId = parseInt(params.id);
	const source = params.source;
	
	if (isNaN(recipeId)) {
		return {
			recipe: null,
			error: 'Invalid recipe ID'
		};
	}

	if (!['internal', 'mealdb'].includes(source)) {
		return {
			recipe: null,
			error: 'Invalid recipe source'
		};
	}

	try {
		// Server-side fetch using environment-aware API URL
		const serverApiUrl = getServerApiUrl();
		let apiPath: string;
		
		if (source === 'internal') {
			apiPath = `/recipes/internal/${recipeId}`;
		} else {
			apiPath = `/recipes/external/${source}/${recipeId}`;
		}
		
		const response = await fetch(`${serverApiUrl}${apiPath}`);
		
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
		console.log(`Loaded ${source} recipe ${recipeId}:`, recipe.title);
		
		return {
			recipe,
			source,
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
