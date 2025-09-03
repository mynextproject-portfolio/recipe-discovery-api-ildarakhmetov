<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import type { RecipeRequest } from '../types/recipe.js';

	export let recipe: Partial<RecipeRequest> = {};
	export let isSubmitting = false;
	export let mode: 'create' | 'edit' = 'create';

	const dispatch = createEventDispatcher<{
		submit: RecipeRequest;
		cancel: void;
	}>();

	// Form data with defaults
	let formData: RecipeRequest = {
		title: recipe.title || '',
		ingredients: recipe.ingredients || [''],
		steps: recipe.steps || [''],
		prepTime: recipe.prepTime || '',
		cookTime: recipe.cookTime || '',
		difficulty: recipe.difficulty || 'Easy',
		cuisine: recipe.cuisine || ''
	};

	function addIngredient() {
		formData.ingredients = [...formData.ingredients, ''];
	}

	function removeIngredient(index: number) {
		if (formData.ingredients.length > 1) {
			formData.ingredients = formData.ingredients.filter((_, i) => i !== index);
		}
	}

	function addStep() {
		formData.steps = [...formData.steps, ''];
	}

	function removeStep(index: number) {
		if (formData.steps.length > 1) {
			formData.steps = formData.steps.filter((_, i) => i !== index);
		}
	}

	function handleSubmit(event: Event) {
		event.preventDefault();
		
		// Filter out empty ingredients and steps
		const cleanedData: RecipeRequest = {
			...formData,
			ingredients: formData.ingredients.filter(ing => ing.trim() !== ''),
			steps: formData.steps.filter(step => step.trim() !== '')
		};

		dispatch('submit', cleanedData);
	}

	function handleCancel() {
		dispatch('cancel');
	}

	const difficulties = ['Easy', 'Medium', 'Hard'];
	const cuisines = [
		'Italian', 'Mexican', 'Chinese', 'Indian', 'Thai', 'French', 
		'Japanese', 'Mediterranean', 'American', 'Other'
	];
</script>

<form on:submit={handleSubmit} class="max-w-2xl mx-auto bg-white p-6 rounded-lg shadow-md">
	<h2 class="text-2xl font-bold text-gray-900 mb-6">
		{mode === 'create' ? 'Create New Recipe' : 'Edit Recipe'}
	</h2>

	<!-- Title -->
	<div class="mb-6">
		<label for="title" class="block text-sm font-medium text-gray-700 mb-2">Recipe Title</label>
		<input
			id="title"
			type="text"
			bind:value={formData.title}
			required
			class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
			placeholder="Enter recipe title"
		/>
	</div>

	<!-- Cuisine and Difficulty -->
	<div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
		<div>
			<label for="cuisine" class="block text-sm font-medium text-gray-700 mb-2">Cuisine</label>
			<select
				id="cuisine"
				bind:value={formData.cuisine}
				required
				class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
			>
				<option value="">Select cuisine</option>
				{#each cuisines as cuisine}
					<option value={cuisine}>{cuisine}</option>
				{/each}
			</select>
		</div>
		<div>
			<label for="difficulty" class="block text-sm font-medium text-gray-700 mb-2">Difficulty</label>
			<select
				id="difficulty"
				bind:value={formData.difficulty}
				required
				class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
			>
				{#each difficulties as difficulty}
					<option value={difficulty}>{difficulty}</option>
				{/each}
			</select>
		</div>
	</div>

	<!-- Prep and Cook Time -->
	<div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
		<div>
			<label for="prepTime" class="block text-sm font-medium text-gray-700 mb-2">Prep Time</label>
			<input
				id="prepTime"
				type="text"
				bind:value={formData.prepTime}
				required
				class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
				placeholder="e.g., 15 minutes"
			/>
		</div>
		<div>
			<label for="cookTime" class="block text-sm font-medium text-gray-700 mb-2">Cook Time</label>
			<input
				id="cookTime"
				type="text"
				bind:value={formData.cookTime}
				required
				class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
				placeholder="e.g., 30 minutes"
			/>
		</div>
	</div>

	<!-- Ingredients -->
	<div class="mb-6">
		<label class="block text-sm font-medium text-gray-700 mb-2">Ingredients</label>
		{#each formData.ingredients as ingredient, index}
			<div class="flex gap-2 mb-2">
				<input
					type="text"
					bind:value={formData.ingredients[index]}
					required
					class="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
					placeholder="Enter ingredient"
				/>
				{#if formData.ingredients.length > 1}
					<button
						type="button"
						on:click={() => removeIngredient(index)}
						class="px-3 py-2 text-red-600 hover:text-red-800 hover:bg-red-50 rounded-md transition-colors"
					>
						Remove
					</button>
				{/if}
			</div>
		{/each}
		<button
			type="button"
			on:click={addIngredient}
			class="text-blue-600 hover:text-blue-800 text-sm font-medium"
		>
			+ Add Ingredient
		</button>
	</div>

	<!-- Steps -->
	<div class="mb-6">
		<label class="block text-sm font-medium text-gray-700 mb-2">Cooking Steps</label>
		{#each formData.steps as step, index}
			<div class="flex gap-2 mb-2">
				<span class="flex-shrink-0 w-8 h-8 bg-gray-100 text-gray-600 rounded-full flex items-center justify-center text-sm font-medium mt-1">
					{index + 1}
				</span>
				<div class="flex-1 flex gap-2">
					<textarea
						bind:value={formData.steps[index]}
						required
						rows="2"
						class="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
						placeholder="Describe this cooking step"
					></textarea>
					{#if formData.steps.length > 1}
						<button
							type="button"
							on:click={() => removeStep(index)}
							class="px-3 py-2 text-red-600 hover:text-red-800 hover:bg-red-50 rounded-md transition-colors"
						>
							Remove
						</button>
					{/if}
				</div>
			</div>
		{/each}
		<button
			type="button"
			on:click={addStep}
			class="text-blue-600 hover:text-blue-800 text-sm font-medium"
		>
			+ Add Step
		</button>
	</div>

	<!-- Form Actions -->
	<div class="flex gap-4 pt-6 border-t border-gray-200">
		<button
			type="submit"
			disabled={isSubmitting}
			class="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white py-3 px-4 rounded-md font-medium transition-colors duration-200 disabled:cursor-not-allowed"
		>
			{#if isSubmitting}
				<span class="flex items-center justify-center gap-2">
					<svg class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
						<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
						<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
					</svg>
					{mode === 'create' ? 'Creating...' : 'Updating...'}
				</span>
			{:else}
				{mode === 'create' ? 'Create Recipe' : 'Update Recipe'}
			{/if}
		</button>
		<button
			type="button"
			on:click={handleCancel}
			disabled={isSubmitting}
			class="px-6 py-3 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md font-medium transition-colors duration-200 disabled:cursor-not-allowed"
		>
			Cancel
		</button>
	</div>
</form>
