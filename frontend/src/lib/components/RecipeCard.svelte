<script lang="ts">
	import type { RecipeResponse } from '../types/recipe.js';
	import CacheIndicator from './CacheIndicator.svelte';

	export let recipe: RecipeResponse;
	export let showActions = true;

	$: isExternalRecipe = recipe.source !== 'internal';
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

<div class="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-200 overflow-hidden {isExternalRecipe ? 'border-l-4 border-blue-400' : ''}">
	<div class="p-6">
		<!-- Header -->
		<div class="flex justify-between items-start mb-4">
			<h3 class="text-xl font-semibold text-gray-900 line-clamp-2">
				{recipe.title}
			</h3>
			{#if recipe.difficulty}
				<span
					class="px-2 py-1 text-xs font-medium rounded-full {getDifficultyColor(recipe.difficulty)}"
				>
					{recipe.difficulty}
				</span>
			{/if}
		</div>

		<!-- Cuisine and Source -->
		<div class="flex items-center gap-2 mb-4 text-sm flex-wrap">
			{#if recipe.cuisine}
				<span class="flex items-center gap-1 text-gray-600">
					🍽️ {recipe.cuisine}
				</span>
			{/if}
			{#if isExternalRecipe}
				<span class="flex items-center gap-1 bg-blue-50 text-blue-700 px-2 py-1 rounded-full text-xs font-medium">
					🌐 {recipe.source.toUpperCase()}
				</span>
			{/if}
		</div>

		<!-- Timing Info -->
		{#if recipe.prepTime || recipe.cookTime}
			<div class="flex gap-4 mb-4 text-sm">
				{#if recipe.prepTime}
					<div class="flex items-center gap-1 text-gray-600">
						⏱️ Prep: {formatTime(recipe.prepTime)}
					</div>
				{/if}
				{#if recipe.cookTime}
					<div class="flex items-center gap-1 text-gray-600">
						🔥 Cook: {formatTime(recipe.cookTime)}
					</div>
				{/if}
			</div>
		{/if}

		<!-- Ingredients Preview -->
		<div class="mb-4">
			<h4 class="text-sm font-medium text-gray-700 mb-2">Ingredients:</h4>
			<div class="text-sm text-gray-600">
				{recipe.ingredients.slice(0, 3).join(', ')}
				{#if recipe.ingredients.length > 3}
					<span class="text-gray-400">... and {recipe.ingredients.length - 3} more</span>
				{/if}
			</div>
		</div>

		<!-- Actions -->
		{#if showActions}
			<div class="flex gap-2 pt-4 border-t border-gray-100">
				<a
					href="/recipes/{recipe.source}/{recipe.id}"
					class="flex-1 bg-blue-600 hover:bg-blue-700 text-white text-center py-2 px-4 rounded-md transition-colors duration-200 text-sm font-medium"
				>
					View Recipe
				</a>
				{#if isEditable}
					<a
						href="/recipes/{recipe.source}/{recipe.id}/edit"
						class="bg-gray-100 hover:bg-gray-200 text-gray-700 py-2 px-4 rounded-md transition-colors duration-200 text-sm font-medium"
					>
						Edit
					</a>
				{:else}
					<span class="bg-gray-50 text-gray-400 py-2 px-4 rounded-md text-sm font-medium cursor-not-allowed">
						Read Only
					</span>
				{/if}
			</div>
		{/if}
	</div>
</div>

<style>
	.line-clamp-2 {
		display: -webkit-box;
		-webkit-line-clamp: 2;
		-webkit-box-orient: vertical;
		line-clamp: 2; /* Standard property for compatibility */
		overflow: hidden;
	}
</style>
