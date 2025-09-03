<script lang="ts">
	import type { CacheInfo } from '../types/recipe.js';

	export let cacheInfo: CacheInfo | undefined;
	export let size: 'sm' | 'md' = 'sm';

	$: showIndicator = cacheInfo && cacheInfo.source !== 'internal';

	function formatTime(ms: number): string {
		if (ms < 1) return '<1ms';
		if (ms < 100) return `${Math.round(ms)}ms`;
		if (ms < 1000) return `${Math.round(ms)}ms`;
		return `${(ms / 1000).toFixed(1)}s`;
	}

	function getCacheColor(hit: boolean): string {
		return hit 
			? 'bg-green-100 text-green-700 border-green-200'
			: 'bg-orange-100 text-orange-700 border-orange-200';
	}

	function getCacheIcon(hit: boolean): string {
		return hit ? '⚡' : '🌐';
	}

	function getCacheText(cacheInfo: CacheInfo): string {
		return cacheInfo.hit ? 'CACHED' : 'API FETCH';
	}

	const sizeClasses = {
		sm: 'text-xs px-2 py-1',
		md: 'text-sm px-3 py-1'
	};
</script>

{#if showIndicator}
	<div class="flex items-center gap-1 border rounded-full {getCacheColor(cacheInfo.hit)} {sizeClasses[size]} font-medium">
		<span>{getCacheIcon(cacheInfo.hit)}</span>
		<span>{getCacheText(cacheInfo)}</span>
		<span class="opacity-75">{formatTime(cacheInfo.response_time_ms)}</span>
	</div>
{/if}
