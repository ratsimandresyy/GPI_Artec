import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useNotificationStore = defineStore('notifications', () => {
    const notifications = ref([]);

    function add(message, type = 'info', duration = 5000) {
        const id = Date.now();
        const notification = {
            id,
            message,
            type,
            duration
        };

        notifications.value.push(notification);

        // Auto-remove after duration
        if (duration > 0) {
            setTimeout(() => {
                remove(id);
            }, duration);
        }

        return id;
    }

    function remove(id) {
        const index = notifications.value.findIndex(n => n.id === id);
        if (index !== -1) {
            notifications.value.splice(index, 1);
        }
    }

    function success(message, duration = 5000) {
        return add(message, 'success', duration);
    }

    function error(message, duration = 5000) {
        return add(message, 'error', duration);
    }

    function warning(message, duration = 5000) {
        return add(message, 'warning', duration);
    }

    function info(message, duration = 5000) {
        return add(message, 'info', duration);
    }

    function clear() {
        notifications.value = [];
    }

    return {
        notifications,
        add,
        remove,
        success,
        error,
        warning,
        info,
        clear
    };
});
