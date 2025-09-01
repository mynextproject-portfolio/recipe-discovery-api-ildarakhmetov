import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import type { RecipeResponse } from '../../../../lib/types/recipe.js';

export const load: PageServerLoad = async ({ params, fetch }) => {
	const recipeId = parseInt(params.id);
	
	if (isNaN(recipeId)) {
		throw redirect(307, '/');
	}

	try {
		// Server-side fetch to check if recipe exists and is editable
		const serverApiUrl = 'http://api:8000';
		const response = await fetch(`${serverApiUrl}/recipes/${recipeId}`);
		
		if (!response.ok) {
			if (response.status === 404) {
				throw redirect(307, '/');
			}
			throw new Error(`API responded with ${response.status}: ${response.statusText}`);
		}
		
		const recipe: RecipeResponse = await response.json();
		
		// Redirect if this is an external recipe (not editable)
		if (recipe.source !== 'internal') {
			console.log(`Redirect: Recipe ${recipeId} is from ${recipe.source}, not editable`);
			throw redirect(307, `/recipes/${recipeId}?error=external-recipe`);
		}
		
		console.log(`Loading editable recipe ${recipeId}:`, recipe.title);
		
		return {
			recipe,
			error: null
		};
	} catch (error) {
		if (error instanceof Response && error.status >= 300 && error.status < 400) {
			// This is a redirect, re-throw it
			throw error;
		}
		
		console.error('Server-side recipe edit load failed:', error);
		throw redirect(307, '/');
	}
};
