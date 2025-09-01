<script lang="ts">
	import { onMount } from 'svelte';
	import RecipeCard from '../lib/components/RecipeCard.svelte';
	import SearchBar from '../lib/components/SearchBar.svelte';
	import LoadingSpinner from '../lib/components/LoadingSpinner.svelte';
	import { recipesApi } from '../lib/api/recipes.js';
	import { recipes, searchResults, isLoading, error, searchQuery, isSearching } from '../lib/stores/recipes.js';
	import type { RecipeResponse } from '../lib/types/recipe.js';
	import type { PageData } from './$types';

	export let data: PageData;

	let allRecipes: RecipeResponse[] = data.recipes || [];
	let displayedRecipes: RecipeResponse[] = data.recipes || [];
	let currentError: string | null = data.error || null;
	let loading = false;
	let searching = false;
	let query = '';           // What user is typing
	let activeQuery = '';     // What was actually searched

	onMount(() => {
		// Set initial data from server-side load
		if (allRecipes.length > 0) {
			recipes.set(allRecipes);
		}
		if (currentError) {
			error.set(currentError);
		}
		console.log('Client-side API URL:', data.apiUrl);
		console.log('Loaded recipes from server:', allRecipes.length);
	});

	async function loadAllRecipes() {
		loading = true;
		currentError = null;
		try {
			allRecipes = await recipesApi.getAll();
			displayedRecipes = allRecipes;
			recipes.set(allRecipes);
		} catch (err) {
			currentError = err instanceof Error ? err.message : 'Failed to load recipes';
			error.set(currentError);
		} finally {
			loading = false;
			isLoading.set(false);
		}
	}

	async function handleSearch(event: CustomEvent<string>) {
		const searchTerm = event.detail;
		activeQuery = searchTerm;  // Set the active search term
		searching = true;
		currentError = null;

		try {
			const results = await recipesApi.search(searchTerm);
			displayedRecipes = results;
			searchResults.set(results);
		} catch (err) {
			currentError = err instanceof Error ? err.message : 'Search failed';
			error.set(currentError);
		} finally {
			searching = false;
			isSearching.set(false);
		}
	}

	function handleClearSearch() {
		query = '';
		activeQuery = '';  // Clear both input and active query
		displayedRecipes = allRecipes;
		searchQuery.set('');
		searchResults.set([]);
	}
</script>

<svelte:head>
	<title>Recipe Discovery - Find Delicious Recipes</title>
	<meta name="description" content="Discover and manage your favorite recipes from around the world" />
</svelte:head>

<div class="min-h-screen bg-gray-50">
	<!-- Header -->
	<header class="bg-white shadow-sm border-b border-gray-200">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
			<h1 class="text-3xl font-bold text-gray-900 text-center mb-6">
				🍳 Recipe Discovery
			</h1>
			
			<!-- Search Bar -->
			<SearchBar 
				bind:value={query}
				isLoading={searching}
				on:search={handleSearch}
				on:clear={handleClearSearch}
			/>
		</div>
	</header>

	<!-- Main Content -->
	<main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
		<!-- Actions Bar -->
		<div class="flex justify-between items-center mb-8">
			<h2 class="text-xl font-semibold text-gray-900">
				{activeQuery ? `Search Results for "${activeQuery}"` : 'All Recipes'}
				<span class="text-gray-500 text-base font-normal">
					({displayedRecipes.length} {displayedRecipes.length === 1 ? 'recipe' : 'recipes'})
				</span>
			</h2>
			<a
				href="/recipes/internal/new"
				class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md font-medium transition-colors duration-200"
			>
				+ Add Recipe
			</a>
		</div>

		<!-- Error Message -->
		{#if currentError}
			<div class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md mb-6">
				{currentError}
			</div>
		{/if}

		<!-- Loading State -->
		{#if loading}
			<div class="flex justify-center py-12">
				<LoadingSpinner size="lg" message="Loading recipes..." />
			</div>
		{:else if displayedRecipes.length === 0 && !currentError}
			<!-- Empty State -->
			<div class="text-center py-12">
				<div class="text-6xl mb-4">🍽️</div>
				<h3 class="text-lg font-medium text-gray-900 mb-2">
					{activeQuery ? 'No recipes found' : 'No recipes yet'}
				</h3>
				<p class="text-gray-600 mb-6">
					{activeQuery 
						? `Try searching for something else or browse all recipes.`
						: 'Get started by adding your first recipe!'
					}
				</p>
				{#if activeQuery}
					<button
						on:click={handleClearSearch}
						class="bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-md font-medium transition-colors duration-200 mr-4"
					>
						Clear Search
					</button>
				{/if}
				<a
					href="/recipes/internal/new"
					class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md font-medium transition-colors duration-200"
				>
					Add First Recipe
				</a>
			</div>
		{:else}
			<!-- Recipe Grid -->
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
				{#each displayedRecipes as recipe (recipe.id)}
					<RecipeCard {recipe} />
				{/each}
			</div>
		{/if}
	</main>
</div>