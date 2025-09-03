<script lang="ts">
	import { goto } from '$app/navigation';
	import RecipeForm from '$lib/components/RecipeForm.svelte';
	import { recipesApi } from '$lib/api/recipes.js';
	import type { RecipeRequest } from '$lib/types/recipe.js';

	let isSubmitting = false;
	let error: string | null = null;

	async function handleSubmit(event: CustomEvent<RecipeRequest>) {
		const recipeData = event.detail;
		isSubmitting = true;
		error = null;

		try {
			const newRecipe = await recipesApi.create(recipeData);
			// Redirect to the new recipe's detail page
			goto(`/recipes/internal/${newRecipe.id}`);
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to create recipe';
		} finally {
			isSubmitting = false;
		}
	}

	function handleCancel() {
		goto('/');
	}
</script>

<svelte:head>
	<title>Create New Recipe - Recipe Discovery</title>
	<meta name="description" content="Create a new recipe to share with the world" />
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

		<!-- Error Message -->
		{#if error}
			<div class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md mb-6">
				{error}
			</div>
		{/if}

		<!-- Recipe Form -->
		<RecipeForm
			mode="create"
			{isSubmitting}
			on:submit={handleSubmit}
			on:cancel={handleCancel}
		/>
	</main>
</div>
