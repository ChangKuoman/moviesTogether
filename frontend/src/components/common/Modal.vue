<script setup>
defineEmits(['close'])
</script>

<template>
  <Teleport to="body">
    <div class="modal-overlay" @click.self="$emit('close')">
      <div class="modal-panel">
        <button type="button" class="modal-panel__close" aria-label="Close" @click="$emit('close')">
          ×
        </button>
        <slot />
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  padding: 1rem;
}
.modal-panel {
  position: relative;
  background: #1a1a1a;
  border: 1px solid #333;
  border-radius: 10px;
  padding: 1.5rem;
  max-width: 480px;
  width: 100%;
  max-height: 85vh;
  overflow-y: auto;
}
.modal-panel__close {
  position: absolute;
  top: 0.75rem;
  right: 0.75rem;
  background: none;
  border: none;
  color: #888;
  font-size: 1.4rem;
  line-height: 1;
  cursor: pointer;
  padding: 0;
}
.modal-panel__close:hover {
  color: #e5484d;
}
</style>
