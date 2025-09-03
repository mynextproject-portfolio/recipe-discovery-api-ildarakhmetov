<script lang="ts">
	import { createEventDispatcher } from 'svelte';

	export let value = '';
	export let placeholder = 'Search recipes...';
	export let isLoading = false;

	const dispatch = createEventDispatcher<{
		search: string;
		clear: void;
	}>();

	function handleInput(event: Event) {
		const target = event.target as HTMLInputElement;
		value = target.value;
		// No auto-search - only search on button click or form submit
	}

	function handleClear() {
		value = '';
		dispatch('clear');
	}

	function handleSubmit(event: Event) {
		event.preventDefault();
		if (value.trim()) {
			dispatch('search', value.trim());
		} else {
			dispatch('clear');
		}
	}

	function handleSearchClick() {
		if (value.trim()) {
			dispatch('search', value.trim());
		} else {
			dispatch('clear');
		}
	}
</script>

<form on:submit={handleSubmit} class="w-full max-w-2xl mx-auto">
	<div class="relative">
		<input
			type="text"
			bind:value
			on:input={handleInput}
			{placeholder}
			disabled={isLoading}
			class="w-full px-4 py-3 pl-12 pr-36 text-gray-900 placeholder-gray-500 bg-white border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-50 disabled:cursor-not-allowed"
		/>

		<!-- Search Icon -->
		<div class="absolute inset-y-0 left-0 flex items-center pl-4">
			<svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
				></path>
			</svg>
		</div>

		<!-- Search Button -->
		<div class="absolute inset-y-0 right-0 flex items-center">
			{#if value}
				<button
					type="button"
					on:click={handleClear}
					class="flex items-center px-3 py-2 text-gray-400 hover:text-gray-600"
					aria-label="Clear search"
				>
					<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M6 18L18 6M6 6l12 12"
						></path>
					</svg>
				</button>
			{/if}
			<button
				type="submit"
				on:click={handleSearchClick}
				disabled={isLoading}
				class="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white px-4 py-2 mr-1 rounded-md font-medium transition-colors duration-200 disabled:cursor-not-allowed"
			>
				{#if isLoading}
					<div class="w-4 h-4 animate-spin">
						<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24">
							<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
							<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
						</svg>
					</div>
					Searching...
				{:else}
					<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
					</svg>
					Search
				{/if}
			</button>
		</div>
	</div>
</form>
