<script>
    import { onMount } from "svelte";
    import ApiDependent from "./misc/ApiDependent.svelte";
    import api from "./services/api.js"

    // barebones implementation just to get api working
    export let name;

    let profile;

    async function loadData() {
        profile = await api.get(`profiles/${name}`, 'Failed getting profile info');
    }

    async function save() {
        await api.post(`profiles/${name}`, profile, `Failed saving profile`);
    }

    async function setAsActive() {
        await api.post(`profiles/active`, profile, `Failed saving profile`);
    }

    onMount(() => loadData());
</script>

<ApiDependent ready={profile != null}>
    <div class="bg-secondary text-light px-3 py-2 mb-3">
        <b>{ profile.name }</b>
    </div>
</ApiDependent>

<div class="container">
    <ApiDependent ready={profile != null}>
        <div class="row p-3">
            <textarea placeholder="Description" bind:value={profile.description}></textarea>
        </div>
        <div class="row mb-3">
            <div class="col-6">
                Sensitivity
            </div>
            <div class="col">
                <input type="number" bind:value={ profile.sensitivity } />
            </div>
        </div>
        <div class="row mb-3">
            <div class="col-6">
                Damping amount
            </div>
            <div class="col">
                <input type="number" bind:value={ profile.damping } />
            </div>
        </div>
        <div class="row mb-3">
            <div class="col-6">
                Slop amount (rotations)
            </div>
            <div class="col">
                <input type="number" bind:value={ profile.slop } />
            </div>
        </div>
        <div class="row mb-3">
            <div class="col-6">
                Total rotations lock to lock
            </div>
            <div class="col">
                <input type="number" bind:value={ profile.total_rotations } />
            </div>
        </div>
    </ApiDependent>
    <div class="d-flex flex-row gap-2 align-items-center justify-content-center">
        <button class="btn btn-primary"gacp  on:click={save}><i class="bi-floppy" /> Save</button>
        <button class="btn btn-secondary" on:click={setAsActive}><i class="bi-lightning" /> Activate</button>
        <button class="btn btn-secondary" on:click={loadData}><i class="bi-x-lg" /> Reset</button>
    </div>
</div>
