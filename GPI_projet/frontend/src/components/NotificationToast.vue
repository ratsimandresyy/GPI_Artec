<template>
    <div
        class="notification-container"
        role="region"
        aria-label="Notifications"
        aria-live="polite"
    >
        <transition-group name="notification">
            <div
                v-for="notification in notifications"
                :key="notification.id"
                class="notification"
                :class="`notification-${notification.type}`"
            >
                <div class="notification-content">
                    <span
                        class="notification-icon"
                        aria-hidden="true"
                    >
                        {{ getIcon(notification.type) }}
                    </span>
                    <span class="notification-message">
                        {{ notification.message }}
                    </span>
                </div>
                <button
                    type="button"
                    class="notification-close"
                    aria-label="Fermer la notification"
                    @click="remove(notification.id)"
                >
                    <span aria-hidden="true">×</span>
                </button>
            </div>
        </transition-group>
    </div>
</template>

<script setup>
import { useNotificationStore } from '../stores/notifications';

const notificationStore = useNotificationStore();
const { notifications, remove } = notificationStore;

function getIcon(type) {
    const icons = {
        success: '✓',
        error: '✕',
        warning: '⚠',
        info: 'ℹ'
    };
    return icons[type] || 'ℹ';
}
</script>

<style scoped>
/*
    Les notifications utilisent les mêmes jetons de couleur que le
    reste de l'application. Elles étaient alignées sur la palette
    Bootstrap par défaut, ce qui les détachait du design system.
*/
.notification-container {
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 9999;
    display: flex;
    flex-direction: column;
    gap: 10px;
    max-width: 400px;
}

.notification {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px 20px;
    border-radius: var(--radius-md);
    background-color: var(--bg-surface);
    border: 1px solid var(--border-light);
    box-shadow: var(--shadow-lg);
    min-width: 300px;
}

/*
    La bordure gauche et l'icône portent le type. Le texte du message
    reste la source principale : le type n'est jamais porté par la
    seule couleur.
*/
.notification-success {
    border-left: 4px solid var(--success);
}

.notification-error {
    border-left: 4px solid var(--danger);
}

.notification-warning {
    border-left: 4px solid var(--warning);
}

.notification-info {
    border-left: 4px solid var(--info);
}

.notification-content {
    display: flex;
    align-items: center;
    gap: 10px;
    flex: 1;
}

.notification-icon {
    font-size: 20px;
    font-weight: bold;
}

.notification-success .notification-icon {
    color: var(--success-text);
}

.notification-error .notification-icon {
    color: var(--danger-text);
}

.notification-warning .notification-icon {
    color: var(--warning-text);
}

.notification-info .notification-icon {
    color: var(--info-text);
}

.notification-message {
    font-size: 14px;
    color: var(--text-main);
}

.notification-close {
    background: none;
    border: none;
    font-size: 20px;
    color: var(--text-light);
    cursor: pointer;
    padding: 0 5px;
    line-height: 1;
}

.notification-close:hover {
    color: var(--text-main);
}

/* Cible de focus visible au clavier. */
.notification-close:focus-visible {
    outline: 2px solid var(--primary);
    outline-offset: 2px;
    border-radius: var(--radius-sm);
}

/* Animation */
.notification-enter-active,
.notification-leave-active {
    transition: all 0.3s ease;
}

.notification-enter-from {
    opacity: 0;
    transform: translateX(100%);
}

.notification-leave-to {
    opacity: 0;
    transform: translateX(100%);
}

.notification-move {
    transition: transform 0.3s ease;
}
</style>
