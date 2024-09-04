<script>
	import { onMount } from "svelte";
	import ErrorPopup from "./misc/ErrorPopup.svelte";
	import ProfileEditor from "./ProfileEditor.svelte";

	import api from "./services/api";
    import ApiDependent from "./misc/ApiDependent.svelte";

	let profileNames;

	async function getProfileNames() {
		profileNames = await api.get(`profilenames`, "Failed loading profile names");
	}

	async function createNewProfile() {
		var name = prompt("Enter name for new profile:");
		profileNames.push(name);
	}

	onMount(getProfileNames);
</script>

<ApiDependent ready={profileNames != null}>
	<div style="margin-top: 10px; margin-bottom: 10px; max-width: 500px; height:100%; border-right: 1px solid black; overflow: scroll">
		{#each profileNames as name}
			<ProfileEditor name={name}/>
		{/each}
		<!-- <hr />
		<div>
			<button class="btn btn-primary" on:click={createNewProfile}><i class="bi-plus" /></button>
		</div> -->
	</div>
</ApiDependent>

<ErrorPopup />