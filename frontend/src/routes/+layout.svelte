<script lang="ts">
	import '../app.css';
</script>

<div class="min-h-screen bg-gray-50">
	<!-- Navigation -->
	<nav class="bg-white shadow-sm">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
			<div class="flex justify-between items-center h-16">
				<div class="flex items-center">
					<a href="/" class="text-xl font-bold text-gray-900">
						🍳 Recipe Discovery
					</a>
				</div>
				<div class="flex items-center space-x-4">
					<a
						href="/"
						class="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition-colors"
					>
						Home
					</a>
					<a
						href="/recipes"
						class="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition-colors"
					>
						Browse
					</a>
					<a
						href="/recipes/new"
						class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
					>
						Add Recipe
					</a>
				</div>
			</div>
		</div>
	</nav>

	<!-- Main Content -->
	<slot />
</div>