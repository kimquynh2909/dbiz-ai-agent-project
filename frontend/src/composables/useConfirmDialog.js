import { ref } from 'vue'

export const useConfirmDialog = () => {
  const visible = ref(false)
  const message = ref('')
  let onConfirmHandler = null

  const open = ({ message: msg, onConfirm } = {}) => {
    message.value = msg || ''
    onConfirmHandler = typeof onConfirm === 'function' ? onConfirm : null
    visible.value = true
  }

  const close = () => {
    visible.value = false
    message.value = ''
    onConfirmHandler = null
  }

  const accept = async () => {
    try {
      if (onConfirmHandler) {
        await onConfirmHandler()
      }
    } finally {
      close()
    }
  }

  return {
    visible,
    message,
    open,
    close,
    accept
  }
}
