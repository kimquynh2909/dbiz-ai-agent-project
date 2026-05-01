import MarkdownIt from 'markdown-it'
import * as markdownItKatexModule from 'markdown-it-katex'
import 'katex/dist/katex.min.css'

const markdownItKatex = markdownItKatexModule.default || markdownItKatexModule

const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true
}).use(markdownItKatex, {
  throwOnError: false,
  errorColor: '#cc0000'
})

const escapeRegExp = (str) => str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')

const escapeHtml = (input) => {
  if (!input) return ''
  return String(input)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

const buildInlineImageHtml = (img, index, messageKey) => {
  const rawSrc = img?.image_url || img?.url || img?.file_url
  const src = escapeHtml(rawSrc)
  if (!src) return ''

  const safeId = escapeHtml(img?.id || '')
  const title = escapeHtml(img?.title || '')
  const description = escapeHtml(img?.description || '')
  const dataAttrs = [`data-inline-image-src="${src}"`]

  if (safeId) dataAttrs.push(`data-inline-image-id="${safeId}"`)
  if (title) dataAttrs.push(`data-inline-image-title="${title}"`)
  if (description) dataAttrs.push(`data-inline-image-description="${description}"`)
  if (typeof index === 'number') dataAttrs.push(`data-inline-image-index="${index}"`)
  if (messageKey) dataAttrs.push(`data-inline-message-id="${messageKey}"`)

  return `
    <figure class="chat-inline-image">
      <img src="${src}" alt="${title || safeId || 'Image'}" class="chat-inline-image__img" ${dataAttrs.join(' ')} />
    </figure>
  `
}

const collectImagePlaceholders = (message) => {
  const placeholders = new Map()
  const images = (message && Array.isArray(message.images)) ? message.images : []
  const messageKey = message && message.id ? escapeHtml(String(message.id)) : ''

  images.forEach((img, index) => {
    const html = buildInlineImageHtml(img, index, messageKey)
    if (!html) return

    const keys = new Set()
    if (img.placeholder) keys.add(img.placeholder)
    if (img.alt_text) keys.add(img.alt_text)
    if (typeof img.id === 'string') {
      keys.add(`[[IMAGE::${img.id}]]`)
      keys.add(`[[image::${img.id}]]`)
    }

    keys.forEach((key) => {
      if (key) {
        placeholders.set(key, html)
      }
    })
  })

  return placeholders
}

const convertLaTeXBrackets = (text) => {
  if (!text) return text

  const skipReplacement = (raw) => raw.toUpperCase().includes('IMAGE::')

  let result = text.replace(/(?<!\[)\[\s*(\\[a-zA-Z]+[^\]]*)\s*\](?!\])/g, (match, formula) => {
    if (skipReplacement(match)) {
      return match
    }
    return `$${formula}$`
  })

  result = result.replace(/(?<!\[)\[\s*([^\[\]]+?)\s*\](?!\])/g, (match, inner) => {
    if (skipReplacement(match)) {
      return match
    }

    const expression = inner.trim()
    if (!expression) {
      return match
    }

    const hasMathSymbol =
      /[=±<>×÷√∑∏_]/.test(expression) ||
      /[+\-*/^]/.test(expression)

    if (!hasMathSymbol) {
      return match
    }

    return `$${expression}$`
  })

  return result
}

export const useChatFormatter = (messages, selectedImage) => {
  const formatMessage = (message) => {
    if (!message) return ''
    let content = typeof message === 'string' ? message : (message.content || '')

    content = convertLaTeXBrackets(content)
    content = content
      .replace(/\$\s+/g, '$')
      .replace(/\s+\$/g, '$')

    const rendered = md.render(content)
    const placeholders = collectImagePlaceholders(message)

    // Step 1: replace explicit placeholders (alt_text / [[IMAGE::id]])
    let output = rendered
    if (placeholders.size > 0) {
      placeholders.forEach((html, placeholder) => {
        const pattern = new RegExp(`(<p>\\s*)?${escapeRegExp(placeholder)}(\\s*</p>)?`, 'gi')
        output = output.replace(pattern, html)
      })
    }

    // Step 2: progressively replace generic placeholders like [image] or [image:2]
    // as images arrive during streaming. This lets images appear mid-stream.
    const imgs = Array.isArray(message.images) ? message.images : []
    if (imgs.length > 0) {
      // Find already placed image ids to avoid duplicates
      const placedIds = new Set()
      try {
        const idRegex = /data-inline-image-id=\"([^\"]+)\"/g
        let m
        while ((m = idRegex.exec(output)) !== null) {
          if (m[1]) placedIds.add(String(m[1]))
        }
      } catch (_) { /* noop */ }

      // Helper to get image by 1-based index or next unplaced
      const getImageByIndex = (oneBased) => {
        const idx = Number(oneBased) - 1
        if (!Number.isNaN(idx) && idx >= 0 && idx < imgs.length) return { img: imgs[idx], index: idx }
        return null
      }
      let seqPtr = 0
      const nextUnplaced = () => {
        while (seqPtr < imgs.length) {
          const candidate = imgs[seqPtr]
          const cid = candidate?.id ? String(candidate.id) : null
          seqPtr += 1
          if (!cid || !placedIds.has(cid)) {
            return { img: candidate, index: seqPtr - 1 }
          }
        }
        return null
      }

      // Replace [image:n] first (explicit index), then plain [image]
      const buildAndReplace = (regex, resolver) => {
        output = output.replace(regex, (...args) => {
          const match = args[0]
          const resolved = resolver(args)
          if (!resolved) return match
          const { img, index } = resolved
          const html = buildInlineImageHtml(img, index, (message && message.id) ? String(message.id) : undefined)
          return html || match
        })
      }

      // Matches: optional <p> wrapper, then [image: N]
      const imageWithIndex = /(<p>\s*)?\[\s*image\s*:\s*(\d+)\s*\](\s*<\/p>)?/gi
      buildAndReplace(imageWithIndex, (args) => {
        const num = args[2]
        const chosen = getImageByIndex(num)
        if (chosen && chosen.img?.id) placedIds.add(String(chosen.img.id))
        return chosen
      })

      // Matches: optional <p> wrapper, then plain [image]
      const plainImage = /(<p>\s*)?\[\s*image\s*\](\s*<\/p>)?/gi
      buildAndReplace(plainImage, () => {
        const chosen = nextUnplaced()
        if (chosen && chosen.img?.id) placedIds.add(String(chosen.img.id))
        return chosen
      })
    }

    return output
  }

  const handleInlineImageClick = (event) => {
    const target = event.target
    if (!(target instanceof HTMLElement)) return
    if (!target.classList.contains('chat-inline-image__img')) return

    const imageId = target.dataset.inlineImageId
    const imageSrc = target.dataset.inlineImageSrc
    const imageTitle = target.dataset.inlineImageTitle
    const imageDescription = target.dataset.inlineImageDescription
    const imageIndexAttr = target.dataset.inlineImageIndex
    const messageId = target.dataset.inlineMessageId

    let imageData = null
    let hostMessage = null

    if (messageId) {
      hostMessage = messages.value.find((msg) => String(msg.id) === String(messageId))
    }

    if (!hostMessage) {
      hostMessage = messages.value.find((msg) => Array.isArray(msg.images) && msg.images.some((img) => {
        if (imageId && img.id && String(img.id) === String(imageId)) return true
        const srcCandidate = img.image_url || img.url || img.file_url
        return imageSrc && srcCandidate === imageSrc
      }))
    }

    if (hostMessage && Array.isArray(hostMessage.images)) {
      if (imageId) {
        imageData = hostMessage.images.find((img) => String(img.id) === String(imageId)) || imageData
      }
      if (!imageData && imageIndexAttr !== undefined) {
        const parsedIndex = Number(imageIndexAttr)
        if (!Number.isNaN(parsedIndex) && hostMessage.images[parsedIndex]) {
          imageData = hostMessage.images[parsedIndex]
        }
      }
      if (!imageData && imageSrc) {
        imageData = hostMessage.images.find((img) => (img.image_url || img.url || img.file_url) === imageSrc) || imageData
      }
    }

    if (!imageData && imageSrc) {
      imageData = {
        id: imageId || imageSrc,
        image_url: imageSrc,
        title: imageTitle,
        description: imageDescription
      }
    }

    if (imageData) {
      selectedImage.value = {
        ...imageData,
        image_url: imageData.image_url || imageData.url || imageSrc,
        url: imageData.url || imageData.image_url || imageSrc
      }
    }
  }

  const attachInlineImageHandler = (containerRef) => {
    if (!containerRef?.value) return
    containerRef.value.addEventListener('click', handleInlineImageClick)
  }

  const detachInlineImageHandler = (containerRef) => {
    if (!containerRef?.value) return
    containerRef.value.removeEventListener('click', handleInlineImageClick)
  }

  return {
    formatMessage,
    attachInlineImageHandler,
    detachInlineImageHandler
  }
}
