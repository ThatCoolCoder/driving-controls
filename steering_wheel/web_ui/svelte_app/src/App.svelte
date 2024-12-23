<script>
	import { onMount } from "svelte";
	import ErrorPopup from "./misc/ErrorPopup.svelte";
	import ProfileEditor from "./ProfileEditor.svelte";

	import api from "./services/api";
    import ApiDependent from "./misc/ApiDependent.svelte";
    import ODriveSettingsEditor from "./ODriveSettingsEditor.svelte";
    import WheelDriverLivePanel from "./WheelDriverLivePanel.svelte";
    import { derived, writable } from "svelte/store";

	let profileNames;
	let selectedProfileIndex = writable(0);
	let selectedProfileName = derived(selectedProfileIndex, $a => profileNames[$a]);

	async function createNewProfile() {
		var name = prompt("Enter name for new profile:");
		profileNames.push(name);
		await api.post(`profiles/${name}/`, {
			name,
			profile: await api.get(`profiles/${profileNames[selectedProfileIndex]}`
		)});
	}

	onMount(async () => {
		profileNames = await api.get(`profilenames`, "Failed loading profile names");
		$selectedProfileIndex = 0;
	});
</script>

<ApiDependent ready={profileNames != null}>
	<div style="margin-top: 10px; margin-bottom: 10px; max-width: 500px; height:100%; border-right: 1px solid black; overflow: scroll">
		<ApiDependent ready={profileNames != null}>
			<div class="bg-secondary text-light px-3 py-2 mb-3 d-flex">
				<select class="form-select text-light bg-secondary border-dark" style="font-weight: bold; max-width: 30ch" bind:value={$selectedProfileIndex}>
					{#each profileNames as name}
						<option value={profileNames.indexOf(name)} >{name}</option>
					{/each}
				</select>
				<button class="btn btn-outline-dark ms-auto" title="New profile" on:click={createNewProfile}><i class="bi-plus-lg"></i></button>
			</div>
		</ApiDependent>
		{#if profileNames != null}
			<ProfileEditor name={selectedProfileName}/>
		{/if}

		<ODriveSettingsEditor />
		<br />
		<WheelDriverLivePanel />
	</div>
</ApiDependent>

<ErrorPopup />