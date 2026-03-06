---
name: nextjs-frontend-optimization
description: Next.js 前端性能优化技能。包含加载优化、状态管理、错误处理、用户体验。
---

# Next.js 前端优化

## 1. 加载优化

### 路由懒加载
```typescript
const HeavyComponent = dynamic(() => import('./HeavyComponent'), {
  loading: () => <p>Loading...</p>,
  ssr: false
})
```

### 图片优化
```typescript
import Image from 'next/image'

<Image
  src="/image.jpg"
  width={500}
  height={300}
  alt="Description"
  loading="lazy"
/>
```

### 骨架屏
```typescript
function Skeleton() {
  return (
    <div className="animate-pulse">
      <div className="h-4 bg-gray-200 rounded w-3/4"></div>
    </div>
  )
}
```

## 2. 状态管理

### API 状态管理
```typescript
import { useState, useEffect } from 'react'

function useFetch<T>(url: string) {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    fetch(url)
      .then(r => r.json())
      .then(setData)
      .catch(setError)
      .finally(() => setLoading(false))
  }, [url])

  return { data, loading, error }
}
```

### 全局状态
```typescript
// 使用 React Context
const AppContext = createContext()

function AppProvider({ children }) {
  const [state, setState] = useState({})
  return (
    <AppContext.Provider value={{ state, setState }}>
      {children}
    </AppContext.Provider>
  )
}
```

## 3. 错误处理

### API 错误处理
```typescript
async function fetchWithErrorHandling(url: string) {
  try {
    const res = await fetch(url)
    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`)
    }
    return await res.json()
  } catch (error) {
    console.error('Fetch error:', error)
    throw error
  }
}
```

### Error Boundary
```typescript
class ErrorBoundary extends React.Component {
  state = { hasError: false }
  
  static getDerivedStateFromError(error) {
    return { hasError: true }
  }
  
  render() {
    if (this.state.hasError) {
      return <div>Something went wrong.</div>
    }
    return this.props.children
  }
}
```

## 4. 用户体验

### 防抖/节流
```typescript
import { useMemo } from 'react'
import { debounce } from 'lodash'

function SearchInput() {
  const debouncedSearch = useMemo(
    () => debounce((q) => search(q), 300),
    []
  )
  
  return <input onChange={(e) => debouncedSearch(e.target.value)} />
}
```

### 重试机制
```typescript
async function fetchWithRetry(url, retries = 3) {
  for (let i = 0; i < retries; i++) {
    try {
      return await fetch(url)
    } catch (error) {
      if (i === retries - 1) throw error
      await new Promise(r => setTimeout(r, 1000 * (i + 1)))
    }
  }
}
```

### Loading 状态
```typescript
function LoadingButton({ loading, children, ...props }) {
  return (
    <button disabled={loading} {...props}>
      {loading ? <Spin /> : children}
    </button>
  )
}
```

## 5. 性能工具

### Web Vitals
```typescript
import { useReportWebVitals } from 'next/web-vitals'

export function WebVitals() {
  useReportWebVitals((metric) => {
    console.log(metric)
  })
}
```
