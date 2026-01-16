export function getExcerpt(content: string) {
    if (content.length < 150) return content
    return content.slice(0, 150) + '...'
}

export function formatDate(dateString?: string) {
    if (!dateString) return ''
    return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
    })
}

export function readTime(content: string) {
    const wordsPerMinute = 200
    const words = content.split(/\s+/).length
    return Math.ceil(words / wordsPerMinute)
}

export function debounce(func: (...args: any[]) => void, delay: number) {
    let timeout: ReturnType<typeof setTimeout>
    return function (...args: any[]) {
        clearTimeout(timeout)
        timeout = setTimeout(() => {
            func(...args)
        }, delay)
    }
}