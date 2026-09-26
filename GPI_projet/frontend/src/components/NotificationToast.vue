<template>
    <div class="notification-container">
        <transition-group name="notification">
            <div
                v-for="notification in notifications"
                :key="notification.id"
                class="notification"
                :class="`notification-${notification.type}`"
            >
                <div class="notification-content">
                    <span class="notification-icon">
                        {{ getIcon(notification.type) }}
                    </span>
                    <span class="notification-message">
                        {{ notification.message }}
                    </span>
                </div>
                <button
                    type="button"
                    class="notification-close"
                    @click="remove(notification.id)"
                >
                    ×
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
    border-radius: 8px;
    background: white;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    min-width: 300px;
}

.notification-success {
    border-left: 4px solid #28a745;
}

.notification-error {
    border-left: 4px solid #dc3545;
}

.notification-warning {
    border-left: 4px solid #ffc107;
}

.notification-info {
    border-left: 4px solid #17a2b8;
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
    color: #28a745;
}

.notification-error .notification-icon {
    color: #dc3545;
}

.notification-warning .notification-icon {
    color: #ffc107;
}

.notification-info .notification-icon {
    color: #17a2b8;
}

.notification-message {
    font-size: 14px;
    color: #333;
}

.notification-close {
    background: none;
    border: none;
    font-size: 20px;
    color: #999;
    cursor: pointer;
    padding: 0 5px;
    line-height: 1;
}

.notification-close:hover {
    color: #333;
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
