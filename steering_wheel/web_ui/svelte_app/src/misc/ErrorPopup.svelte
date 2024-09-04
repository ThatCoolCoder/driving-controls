<script>
    import { onMount } from 'svelte';
    import { handler } from '../services/errorService';
     
    
    let isOpen = false;
    
    let _message;
    let _details;
    
    export function open(message, details) {
        isOpen = true;
        _message = message;
        _details = details;
    }
    
    export function close() {
        isOpen = false;
    }

    function showDetails() {
        let toShow = _details == '' ? 'no further details available' : _details;
        alert(`Error details (placeholder popup):\n${toShow}`)
    }

    onMount(() => handler.set(open));
</script>

<div class="footer fixed-bottom p-4 d-flex w-100 error-popup {isOpen ? 'error-popup-open' : 'error-popup-closed'}" aria-hidden={! isOpen}>
    <div class="flex-grow-1">
        <h5><i class="bi-exclamation-triangle"></i> Something went wrong</h5>
        <div class="d-flex gap-2">
            <p class="mb-1 fw-heading">{ _message }</p>
            <a role="button" href="#" on:click={showDetails}>(details)</a>
        </div>
        If this issue persists please raise an issue on the github <a href="https://github.com/ThatCoolCoder/driving-controls" target="_blank">https://github.com/ThatCoolCoder/driving-controls</a>
    </div>
    <button class="align-self-start" on:click={close}><i class="bi-x-lg"></i></button>
</div>

<style>
    .error-popup {
        background-color: var(--bs-danger-border-subtle);
        transition: transform 0.2s;
    }

    .error-popup-closed {
        transform: translateY(100%);
    }
</style>