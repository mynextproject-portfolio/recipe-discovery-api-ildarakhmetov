<script lang="ts">
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import RecipeForm from '$lib/components/RecipeForm.svelte';
	import { recipesApi } from '$lib/api/recipes.js';
	import type { RecipeResponse, RecipeRequest } from '$lib/types/recipe.js';
	import type { PageData } from './$types';

	export let data: PageData;

	let recipe: RecipeResponse | null = data.recipe;
	let isLoading = false;
	let isSubmitting = false;
	let error: string | null = data.error;

	$: source = $page.params.source;
	$: recipeId = parseInt($page.params.id);

	async function handleSubmit(event: CustomEvent<RecipeRequest>) {
		const recipeData = event.detail;
		isSubmitting = true;
		error = null;

		try {
			const updatedRecipe = await recipesApi.updateInternal(recipeId, recipeData);
			// Redirect to the updated recipe's detail page
			goto(`/recipes/internal/${updatedRecipe.id}`);
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to update recipe';
		} finally {
			isSubmitting = false;
		}
	}

	function handleCancel() {
		goto(`/recipes/${source}/${recipeId}`);
	}
</script>

<svelte:head>
	<title>{recipe?.title ? `Edit ${recipe.title}` : 'Edit Recipe'} - Recipe Discovery</title>
	<meta name="description" content={recipe?.title ? `Edit ${recipe.title} recipe` : 'Edit recipe'} />
</svelte:head>

<div class="min-h-screen bg-gray-50">
	<main class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
		<!-- Back Button -->
		<div class="mb-6">
			<button
				on:click={() => goto(`/recipes/${recipeId}`)}
				class="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
			>
				<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
				</svg>
				Back to Recipe
			</button>
		</div>

		{#if error && !recipe}
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
			<!-- Error Message for Submit Errors -->
			{#if error}
				<div class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md mb-6">
					{error}
				</div>
			{/if}

			<!-- Recipe Form -->
			<RecipeForm
				recipe={recipe}
				mode="edit"
				{isSubmitting}
				on:submit={handleSubmit}
				on:cancel={handleCancel}
			/>
		{/if}
	</main>
</div>
