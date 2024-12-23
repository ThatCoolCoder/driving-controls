<script>
    import { onMount } from "svelte";
    import ApiDependent from "./misc/ApiDependent.svelte";
    import api from "./services/api.js"
    import { get } from "svelte/store";

    // barebones implementation just to get api working
    export let name;
    
    let profile;
    
    async function loadData() {
        profile = await api.get(`profiles/${get(name)}`, 'Failed getting profile info');
    }
    
    async function apply() {
        await api.post(`profiles/${get(name)}`, profile, `Failed saving profile`);
        await api.post(`profiles/active`, profile, `Failed saving profile`);
    }
    
    onMount(() => {
        loadData();
        name.subscribe(loadData);
    });
</script>

<div class="container mb-3">
    <ApiDependent ready={profile != null}>
        <div class="row p-3">
            <textarea placeholder="Description" bind:value={profile.description}></textarea>
        </div>
        <div class="row mb-3">
            <div class="col-6">
                Sensitivity
            </div>
            <div class="col">
                <input type="number" bind:value={ profile.sensitivity } step="0.05" min="0" />
            </div>
        </div>
        <div class="row mb-3">
            <div class="col-6">
                Damping amount
            </div>
            <div class="col">
                <input type="number" bind:value={ profile.damping } step="0.05" min="0" />
            </div>
        </div>
        <div class="row mb-3">
            <div class="col-6">
                Latency compensation time (seconds)
            </div>
            <div class="col">
                <input type="number" bind:value={ profile.latency_compensation } step="0.001" min="0" />
            </div>
        </div>
        <div class="row mb-3">
            <div class="col-6">
                Total rotations lock to lock
            </div>
            <div class="col">
                <input type="number" bind:value={ profile.total_rotations } step="0.1" min="0" />
            </div>
        </div>
    </ApiDependent>
    <div class="d-flex flex-row gap-2 align-items-center justify-content-center">
        <button class="btn btn-primary"gacp  on:click={apply}><i class="bi-floppy" /> Apply</button>
        <button class="btn btn-secondary" on:click={loadData}><i class="bi-x-lg" /> Reset</button>
    </div>
</div>
