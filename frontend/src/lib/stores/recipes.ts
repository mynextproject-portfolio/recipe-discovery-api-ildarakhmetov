/**
 * Svelte stores for recipe state management
 */

import { writable } from 'svelte/store';
import type { RecipeResponse } from '../types/recipe.js';

export const recipes = writable<RecipeResponse[]>([]);
export const searchResults = writable<RecipeResponse[]>([]);
export const currentRecipe = writable<RecipeResponse | null>(null);
export const isLoading = writable(false);
export const error = writable<string | null>(null);

// Search state
export const searchQuery = writable('');
export const isSearching = writable(false);
