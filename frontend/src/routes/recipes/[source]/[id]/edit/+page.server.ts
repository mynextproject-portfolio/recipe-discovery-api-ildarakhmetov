import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import type { RecipeResponse } from '../../../../../lib/types/recipe.js';

export const load: PageServerLoad = async ({ params, fetch }) => {
	const recipeId = parseInt(params.id);
	const source = params.source;
	
	if (isNaN(recipeId)) {
		throw redirect(307, '/');
	}

	// Only internal recipes can be edited
	if (source !== 'internal') {
		console.log(`Redirect: Cannot edit ${source} recipe ${recipeId}`);
		throw redirect(307, `/recipes/${source}/${recipeId}`);
	}

	try {
		// Server-side fetch to get the internal recipe
		const serverApiUrl = 'http://api:8000';
		const response = await fetch(`${serverApiUrl}/recipes/internal/${recipeId}`);
		
		if (!response.ok) {
			if (response.status === 404) {
				throw redirect(307, '/');
			}
			throw new Error(`API responded with ${response.status}: ${response.statusText}`);
		}
		
		const recipe: RecipeResponse = await response.json();
		console.log(`Loading editable internal recipe ${recipeId}:`, recipe.title);
		
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
