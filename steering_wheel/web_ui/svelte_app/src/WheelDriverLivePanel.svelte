<script>
    import { onMount } from "svelte";
    import ApiDependent from "./misc/ApiDependent.svelte";
    import api from "./services/api.js";

	let wheelDriverActive;

    async function pause() {
        await api.post(`wheeldriver/pause`);
    }

    async function unpause() {
        await api.post(`wheeldriver/unpause`);
    }

    async function clearErrors() {
        await api.post(`wheeldriver/clearerrors`);
    }

    async function disconnectOdrive() {
        await api.post(`wheeldriver/disconnectodrive`);
    }

    async function reconnectOdrive() {
        await api.post(`wheeldriver/reconnectodrive`);
    }

	onMount(async () => {
		wheelDriverActive = (await api.get(`wheeldriver/status`, "Failed getting wheel driver status")).active;
	});
</script>

<div class="bg-secondary text-light px-3 py-2 mb-3">
    <b>Wheel Driver Live Panel</b>
</div>

<div class="d-flex flex-column gap-3 px-3">
    {#if wheelDriverActive}
        <div>
            <h5>Monitoring</h5>
            <hr class="mt-1" />
            <p>Nothing</p>
        </div>
        <div>
            <h5>Actions</h5>
            <hr class="mt-1" />
            <div class="row gx-2 gy-2">
                <div class="col-6"><button class="btn btn-secondary w-100" on:click={pause}>Pause ODrive</button></div>
                <div class="col-6"><button class="btn btn-secondary w-100" on:click={unpause}>Unpause ODrive</button></div>
                <div class="col-6"><button class="btn btn-secondary w-100" on:click={disconnectOdrive}>Disconnect ODrive</button></div>
                <div class="col-6"><button class="btn btn-secondary w-100" on:click={reconnectOdrive}>Reconnect ODrive</button></div>
                <div class="col-6"><button class="btn btn-secondary w-100" on:click={clearErrors}>Clear errors</button></div>
            </div>
        </div>
    {:else}
        <p>Wheel driver not active</p>
    {/if}
</div>