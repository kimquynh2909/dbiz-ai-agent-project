import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useNotificationStore = defineStore('notifications', () => {
  const notifications = ref([])

  const add = (notification) => {
    const id = Date.now() + Math.random()
    notifications.value.push({
      id,
      ...notification,
      duration: notification.duration !== undefined ? notification.duration : 3000,
    })

    if (notification.duration !== 0) {
      setTimeout(
        () => {
          remove(id)
        },
        notification.duration !== undefined ? notification.duration : 3000
      )
    }
  }

  const remove = (id) => {
    notifications.value = notifications.value.filter((n) => n.id !== id)
  }

  const notify = (message, type = 'info', duration = 3000) => {
    add({ message, type, duration })
  }

  return {
    notifications,
    add,
    remove,
    notify,
  }
})
