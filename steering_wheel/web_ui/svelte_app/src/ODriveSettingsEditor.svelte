<script>
    import { onMount } from "svelte";
    import ApiDependent from "./misc/ApiDependent.svelte";
    import api from "./services/api.js"

    let settings;

    async function load() {
        settings = await api.get(`odrivesettings`, 'Failed getting odrive settings');
    }

    async function save() {
        await api.post(`odrivesettings`, settings, `Failed saving odrive settings`);
    }

    onMount(() => load());
</script>

<ApiDependent ready={settings != null}>
    <div class="bg-secondary text-light px-3 py-2 mb-3">
        <b>Global ODrive settings</b>
    </div>
</ApiDependent>

<div class="container">
    <ApiDependent ready={settings != null}>
        <div class="row mb-3">
            <div class="col-6">
                Ignore ODrive errors
            </div>
            <div class="col">
                <input type="checkbox" bind:checked={ settings.ignore_odrive_errors } />
            </div>
        </div>
        <div class="row mb-3">
            <div class="col-6">
                Print FFB debug
            </div>
            <div class="col">
                <input type="checkbox" bind:checked={ settings.print_ffb_debug } />
            </div>
        </div>
    </ApiDependent>
    <div class="d-flex flex-row gap-2 align-items-center justify-content-center">
        <button class="btn btn-primary"gacp  on:click={save}><i class="bi-floppy" /> Save</button>
        <button class="btn btn-secondary" on:click={load}><i class="bi-x-lg" /> Reset</button>
    </div>
</div>
