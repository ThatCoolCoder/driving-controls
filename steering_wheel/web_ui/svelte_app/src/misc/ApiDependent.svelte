<!-- Thing for showing loading if waiting for data to finish loading. Todo: figure out how to use this and then document that -->

<script>
    export let ready;
    let initialTimeoutOver = false; // have a short period before displaying the loading so people on fast connections loading small resources don't get stuff flashing around
    
    setTimeout(() => initialTimeoutOver = true, 100)
</script>

{#if ready}
    <slot />
{:else if initialTimeoutOver}
    <slot name="loading">
        Loading...
    </slot>
{/if}