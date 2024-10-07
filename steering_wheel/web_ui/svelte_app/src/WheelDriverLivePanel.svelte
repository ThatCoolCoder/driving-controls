<script>
    import { onMount } from "svelte";
    import ApiDependent from "./misc/ApiDependent.svelte";
    import api from "./services/api.js";

	let wheelDriverActive;

	onMount(async () => {
		wheelDriverActive = (await api.get(`wheeldriver/status`, "Failed getting wheel driver status")).active;
        console.log(wheelDriverActive);
	});
</script>

<div class="bg-secondary text-light px-3 py-2 mb-3">
    <b>Wheel Driver Live Panel</b>
</div>

<div class="d-flex flex-column gap-3">
    {#if wheelDriverActive}
        <div class="px-3">
            <h5>Monitoring</h5>
            <hr class="mt-1" />
            <p>Nothing</p>
        </div>
        <div class="px-3">
            <h5>Actions</h5>
            <hr class="mt-1" />
            <button class="btn btn-secondary">Clear errors</button>
            <button class="btn btn-secondary">Set ODrive to idle</button>
        </div>
    {:else}
        <p>Wheel driver not active</p>
    {/if}
</div>
