<script lang="ts">
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import LoadingSpinner from '$lib/components/LoadingSpinner.svelte';
	import CacheIndicator from '$lib/components/CacheIndicator.svelte';
	import type { RecipeResponse } from '$lib/types/recipe.js';
	import type { PageData } from './$types';

	export let data: PageData;

	let recipe: RecipeResponse | null = data.recipe;
	let loading = false;
	let error: string | null = data.error;

	$: source = $page.params.source || '';
	$: recipeId = parseInt($page.params.id || '0');
	$: isExternalRecipe = source !== 'internal';
	$: isEditable = !isExternalRecipe;

	function formatTime(time: string): string {
		return time.replace(/(\d+)/, '$1');
	}

	function getDifficultyColor(difficulty: string): string {
		switch (difficulty.toLowerCase()) {
			case 'easy':
				return 'bg-green-100 text-green-800';
			case 'medium':
				return 'bg-yellow-100 text-yellow-800';
			case 'hard':
				return 'bg-red-100 text-red-800';
			default:
				return 'bg-gray-100 text-gray-800';
		}
	}
</script>

<svelte:head>
	<title>{recipe?.title || 'Recipe'} - Recipe Discovery</title>
	<meta name="description" content={recipe?.title ? `Learn how to make ${recipe.title}` : 'Recipe details'} />
</svelte:head>

<div class="min-h-screen bg-gray-50">
	<main class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
		<!-- Back Button -->
		<div class="mb-6">
			<button
				on:click={() => goto('/')}
				class="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
			>
				<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
				</svg>
				Back to Recipes
			</button>
		</div>

		{#if loading}
			<div class="flex justify-center py-12">
				<LoadingSpinner size="lg" message="Loading recipe..." />
			</div>
		{:else if error}
			<div class="text-center py-12">
				<div class="text-6xl mb-4">😞</div>
				<h2 class="text-xl font-semibold text-gray-900 mb-2">Recipe Not Found</h2>
				<p class="text-gray-600 mb-6">{error}</p>
				<button
					on:click={() => goto('/')}
					class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md font-medium transition-colors duration-200"
				>
					Go Back Home
				</button>
			</div>
		{:else if recipe}
			<div class="bg-white rounded-lg shadow-md overflow-hidden">
				<!-- Header -->
				<div class="p-6 border-b border-gray-200">
									<div class="flex justify-between items-start mb-4">
					<h1 class="text-3xl font-bold text-gray-900">{recipe.title}</h1>
					{#if recipe.difficulty}
						<span class="px-3 py-1 text-sm font-medium rounded-full {getDifficultyColor(recipe.difficulty)}">
							{recipe.difficulty}
						</span>
					{/if}
				</div>

					<!-- Recipe Meta Info -->
					<div class="flex flex-wrap gap-6 text-sm text-gray-600">
						{#if recipe.cuisine}
							<div class="flex items-center gap-1">
								🍽️ <span class="font-medium">{recipe.cuisine}</span>
							</div>
						{/if}
						{#if recipe.prepTime}
							<div class="flex items-center gap-1">
								⏱️ Prep: <span class="font-medium">{formatTime(recipe.prepTime)}</span>
							</div>
						{/if}
						{#if recipe.cookTime}
							<div class="flex items-center gap-1">
								🔥 Cook: <span class="font-medium">{formatTime(recipe.cookTime)}</span>
							</div>
						{/if}
						{#if isExternalRecipe}
							<div class="flex items-center gap-2">
								<span class="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wide">
									🌐 {recipe.source}
								</span>
								<span class="bg-amber-100 text-amber-800 px-2 py-1 rounded text-xs font-medium">
									Read Only
								</span>
								{#if recipe.cache_info}
									<CacheIndicator cacheInfo={recipe.cache_info} size="md" />
								{/if}
							</div>
						{/if}
					</div>

					<!-- Actions -->
					<div class="flex gap-3 mt-6">
						{#if isEditable}
							<a
								href="/recipes/{source}/{recipe.id}/edit"
								class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md font-medium transition-colors duration-200"
							>
								Edit Recipe
							</a>
						{:else}
							<div class="flex items-center gap-2 bg-gray-50 text-gray-500 px-4 py-2 rounded-md cursor-not-allowed">
								<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m0 0v2m0-2h2m-2 0H10m4-6V9a4 4 0 1 0-8 0v2m0 0V9a4 4 0 1 0 8 0v2"></path>
								</svg>
								<span class="text-sm font-medium">View Only</span>
							</div>
						{/if}
						<button
							on:click={() => goto('/')}
							class="bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-md font-medium transition-colors duration-200"
						>
							Back to All Recipes
						</button>
					</div>
				</div>

				<div class="p-6">
					<div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
						<!-- Ingredients -->
						<div>
							<h2 class="text-xl font-semibold text-gray-900 mb-4">
								Ingredients ({recipe.ingredients.length})
							</h2>
							<ul class="space-y-2">
								{#each recipe.ingredients as ingredient, index}
									<li class="flex items-start gap-3">
										<span class="flex-shrink-0 w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-medium">
											{index + 1}
										</span>
										<span class="text-gray-700">{ingredient}</span>
									</li>
								{/each}
							</ul>
						</div>

						<!-- Instructions -->
						<div>
							<h2 class="text-xl font-semibold text-gray-900 mb-4">
								Instructions ({recipe.steps.length} steps)
							</h2>
							<ol class="space-y-4">
								{#each recipe.steps as step, index}
									<li class="flex items-start gap-3">
										<span class="flex-shrink-0 w-8 h-8 bg-green-100 text-green-600 rounded-full flex items-center justify-center text-sm font-bold">
											{index + 1}
										</span>
										<p class="text-gray-700 leading-relaxed">{step}</p>
									</li>
								{/each}
							</ol>
						</div>
					</div>
				</div>
			</div>
		{/if}
	</main>
</div>
