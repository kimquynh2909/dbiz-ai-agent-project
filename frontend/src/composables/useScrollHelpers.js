import { nextTick } from 'vue'

export const useScrollHelpers = (containerRef) => {
  const scrollToBottom = async () => {
    await nextTick()
    if (containerRef?.value) {
      containerRef.value.scrollTop = containerRef.value.scrollHeight
    }
  }

  const scrollToTop = async () => {
    await nextTick()
    if (containerRef?.value) {
      containerRef.value.scrollTop = 0
    }
  }

  return {
    scrollToBottom,
    scrollToTop
  }
}
